#!/usr/bin/env python3
"""Summarize ASSA ABLOY A/B measurement exports from the Chrome extension."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path


TASK_PERSONA = {
    "O1": "Operational user",
    "O2": "Operational user",
    "O3": "Operational user",
    "O4": "Operational user",
    "T1": "Technical user",
    "T2": "Technical user",
    "T3": "Technical user",
    "T4": "Technical user",
}

TASK_MODULE = {
    "O1": "Monitoring",
    "O2": "Monitoring",
    "O3": "Analyses / Documentation",
    "O4": "Documentation / Analyses",
    "T1": "Documentation",
    "T2": "Documentation / Analyses",
    "T3": "Analyses",
    "T4": "Analyses / Documentation",
}


def parse_number(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def reduction(before: float, after: float) -> float | None:
    if before <= 0:
        return None
    return ((before - after) / before) * 100.0


def median(values: list[float]) -> float:
    clean = [value for value in values if value >= 0]
    return statistics.median(clean) if clean else 0.0


def avg(values: list[float | None]) -> float:
    clean = [value for value in values if value is not None]
    return sum(clean) / len(clean) if clean else 0.0


def load_records(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def summarize(records: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for record in records:
        task_id = (record.get("taskId") or "").strip()
        condition = (record.get("condition") or "").strip().upper()
        if task_id and condition in {"A", "B"}:
            grouped[(task_id, condition)].append(record)

    rows: list[dict[str, object]] = []
    for task_id in sorted(TASK_PERSONA):
        a_records = grouped.get((task_id, "A"), [])
        b_records = grouped.get((task_id, "B"), [])
        record_complete = bool(a_records and b_records)
        a_time = median([parse_number(row.get("elapsedSec", "")) for row in a_records])
        b_time = median([parse_number(row.get("elapsedSec", "")) for row in b_records])
        a_clicks = median([parse_number(row.get("clicks", "")) for row in a_records])
        b_clicks = median([parse_number(row.get("clicks", "")) for row in b_records])
        a_screens = median([parse_number(row.get("screens", "")) for row in a_records])
        b_screens = median([parse_number(row.get("screens", "")) for row in b_records])
        time_reduction = reduction(a_time, b_time)
        click_reduction = reduction(a_clicks, b_clicks)
        screen_reduction = reduction(a_screens, b_screens)
        effort_reduction = avg([time_reduction, click_reduction, screen_reduction])

        rows.append({
            "persona": TASK_PERSONA[task_id],
            "taskId": task_id,
            "module": TASK_MODULE[task_id],
            "recordComplete": 1 if record_complete else 0,
            "conditionAMedianSec": round(a_time, 1),
            "conditionBMedianSec": round(b_time, 1),
            "timeReductionPercent": round(time_reduction or 0.0, 2),
            "conditionAMedianClicks": round(a_clicks, 1),
            "conditionBMedianClicks": round(b_clicks, 1),
            "clickReductionPercent": round(click_reduction or 0.0, 2),
            "conditionAMedianScreens": round(a_screens, 1),
            "conditionBMedianScreens": round(b_screens, 1),
            "screenReductionPercent": round(screen_reduction or 0.0, 2),
            "measuredEffortReductionPercent": round(effort_reduction, 2) if record_complete else "",
            "conditionAExpertHelp": max([parse_number(row.get("expertHelp", "")) for row in a_records], default=0),
            "conditionBExpertHelp": max([parse_number(row.get("expertHelp", "")) for row in b_records], default=0),
            "conditionAManualReasoning": max([parse_number(row.get("manualReasoning", "")) for row in a_records], default=0),
            "conditionBManualReasoning": max([parse_number(row.get("manualReasoning", "")) for row in b_records], default=0),
            "conditionASuccess": min([parse_number(row.get("success", "")) for row in a_records], default=0),
            "conditionBSuccess": min([parse_number(row.get("success", "")) for row in b_records], default=0),
        })

    operational = [
        row["measuredEffortReductionPercent"]
        for row in rows
        if row["taskId"].startswith("O") and row["recordComplete"]
    ]
    technical = [
        row["measuredEffortReductionPercent"]
        for row in rows
        if row["taskId"].startswith("T") and row["recordComplete"]
    ]
    completed_rows = [row for row in rows if row["recordComplete"]]
    modules = sorted({row["module"] for row in completed_rows})
    operational_complete = len(operational) == 4
    technical_complete = len(technical) == 4
    summary = {
        "operationalEffortReductionPercent": round(avg(operational), 2),
        "technicalInterventionReductionPercent": round(avg(technical), 2),
        "operationalTargetMet": operational_complete and avg(operational) >= 30.0,
        "technicalTargetMet": technical_complete and avg(technical) >= 25.0,
        "operationalComplete": operational_complete,
        "technicalComplete": technical_complete,
        "completeOperationalTasks": len(operational),
        "completeTechnicalTasks": len(technical),
        "diaModulesCovered": "; ".join(modules),
        "monitoringCovered": any("Monitoring" in row["module"] for row in completed_rows),
        "analysesCovered": any("Analyses" in row["module"] for row in completed_rows),
        "documentationCovered": any("Documentation" in row["module"] for row in completed_rows),
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_csv", type=Path, help="Raw CSV exported by the Chrome extension")
    parser.add_argument("--out", type=Path, default=Path("evidence/measurements/assaabloy-kpi-summary.csv"))
    args = parser.parse_args()

    records = load_records(args.raw_csv)
    rows, summary = summarize(records)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_csv(args.out, rows)

    print(f"Wrote task summary: {args.out}")
    print(
        f"Operational effort reduction: {summary['operationalEffortReductionPercent']}% "
        f"target 30% met={summary['operationalTargetMet']} "
        f"complete_tasks={summary['completeOperationalTasks']}/4 "
        f"complete={summary['operationalComplete']}"
    )
    print(
        f"Technical intervention reduction: {summary['technicalInterventionReductionPercent']}% "
        f"target 25% met={summary['technicalTargetMet']} "
        f"complete_tasks={summary['completeTechnicalTasks']}/4 "
        f"complete={summary['technicalComplete']}"
    )
    print(
        "DIA module coverage: "
        f"Monitoring={summary['monitoringCovered']} "
        f"Analyses={summary['analysesCovered']} "
        f"Documentation={summary['documentationCovered']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

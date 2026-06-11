"""
Partner press-shop pilot API routes.

These endpoints expose the imported ASSA ABLOY / partner press-shop dataset
without mixing it with simulator assets. Energy remains at meter-group level;
press production remains available per press and as derived group totals.
"""

from datetime import datetime, timedelta
from decimal import Decimal
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query

from database import db, slugify_feature_name
from services.baseline_service import baseline_service
from services.forecast_service import ForecastService

router = APIRouter(prefix="/partner-press", tags=["Partner Press Shop"])
forecast_service = ForecastService()

PARTNER_FACTORY_NAME = os.getenv("PARTNER_PRESS_FACTORY_NAME", "Partner Press Shop")
PARTNER_DISPLAY_NAME = os.getenv("PARTNER_PRESS_DISPLAY_NAME", "ASSA ABLOY Partner Press Shop")
PARTNER_START = os.getenv("PARTNER_PRESS_START", "2025-05-01T00:00:00")
PARTNER_END = os.getenv("PARTNER_PRESS_END", "2026-06-01T00:00:00")
PARTNER_SOURCE_DATASET = os.getenv("PARTNER_PRESS_SOURCE_DATASET", "partner_press_shop_2026_06_10")

GROUP_LABELS = {
    "bret": "Bret Presses Meter Group",
    "raster": "Raster Presses Meter Group",
    "dimeco": "Dimeco Presses Meter Group",
}

PRESS_ALIASES = {
    "bret1251": "Bret125-1",
    "bret125-1": "Bret125-1",
    "bret 125 1": "Bret125-1",
    "bret1601": "Bret160-1",
    "bret160-1": "Bret160-1",
    "bret 160 1": "Bret160-1",
    "bret2501": "Bret250-1",
    "bret250-1": "Bret250-1",
    "bret 250 1": "Bret250-1",
    "bret2502": "Bret250-2",
    "bret250-2": "Bret250-2",
    "bret 250 2": "Bret250-2",
    "dimeco801": "Dimeco80-1",
    "dimeco80-1": "Dimeco80-1",
    "dimeco 80 1": "Dimeco80-1",
    "dimeco802": "Dimeco80-2",
    "dimeco80-2": "Dimeco80-2",
    "dimeco 80 2": "Dimeco80-2",
    "flexi1": "Flexi-1",
    "flexi-1": "Flexi-1",
    "flexi 1": "Flexi-1",
    "rast1251": "Rast125-1",
    "rast125-1": "Rast125-1",
    "rast 125 1": "Rast125-1",
    "raster1251": "Rast125-1",
    "raster 125 1": "Rast125-1",
    "rast1252": "Rast125-2",
    "rast125-2": "Rast125-2",
    "rast 125 2": "Rast125-2",
    "raster1252": "Rast125-2",
    "raster 125 2": "Rast125-2",
    "rast1601": "Rast160-1",
    "rast160-1": "Rast160-1",
    "rast 160 1": "Rast160-1",
    "raster160": "Rast160-1",
    "raster 160": "Rast160-1",
    "raster1601": "Rast160-1",
    "raster 160 1": "Rast160-1",
    "rast2501": "Rast250-1",
    "rast250-1": "Rast250-1",
    "rast 250 1": "Rast250-1",
    "raster2501": "Rast250-1",
    "raster 250 1": "Rast250-1",
    "rast2502": "Rast250-2",
    "rast250-2": "Rast250-2",
    "rast 250 2": "Rast250-2",
    "raster2502": "Rast250-2",
    "raster 250 2": "Rast250-2",
    "schu801": "Schu80-1",
    "schu80-1": "Schu80-1",
    "schu 80 1": "Schu80-1",
}


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def _number(value: Any, digits: int = 2) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        value = float(value)
    return round(float(value), digits)


def _group_key(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    normalized = value.lower()
    for key in GROUP_LABELS:
        if key in normalized:
            return key
    return None


def _normalize_press(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    normalized = " ".join(value.lower().replace("_", " ").split())
    compact = normalized.replace("-", "").replace(" ", "")
    candidates = {normalized, compact, normalized.replace(" ", "-")}
    for candidate in candidates:
        if candidate in PRESS_ALIASES:
            return PRESS_ALIASES[candidate]
    return None


def _period_label(start: datetime, end: datetime) -> str:
    return f"{start.date().isoformat()} to {end.date().isoformat()}"


async def _partner_factory(conn) -> Optional[dict]:
    row = await conn.fetchrow(
        """
        SELECT id, name, location, metadata
        FROM factories
        WHERE name = $1
        LIMIT 1
        """,
        PARTNER_FACTORY_NAME,
    )
    return dict(row) if row else None


async def _partner_meter_groups(conn) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT
            m.id,
            m.name,
            m.type,
            m.metadata->>'group' AS group_key,
            m.metadata->>'asset_level' AS asset_level,
            m.metadata->>'energy_scope' AS energy_scope
        FROM machines m
        JOIN factories f ON f.id = m.factory_id
        WHERE f.name = $1
          AND m.metadata->>'source_dataset' = $2
          AND m.metadata->>'asset_level' = 'meter_group'
        ORDER BY m.metadata->>'group'
        """,
        PARTNER_FACTORY_NAME,
        PARTNER_SOURCE_DATASET,
    )
    return [dict(row) for row in rows]


async def _partner_baseline_drivers(conn, group_key: str) -> list[str]:
    rows = await conn.fetch(
        """
        SELECT m.name
        FROM machines m
        JOIN factories f ON f.id = m.factory_id
        WHERE f.name = $1
          AND m.metadata->>'source_dataset' = $2
          AND m.metadata->>'asset_level' = 'press'
          AND m.metadata->>'group' = $3
        ORDER BY m.name
        """,
        PARTNER_FACTORY_NAME,
        PARTNER_SOURCE_DATASET,
        group_key,
    )
    production_drivers = [
        f"press_production_{slugify_feature_name(row['name'])}"
        for row in rows
    ]
    active_drivers = [
        f"press_active_{slugify_feature_name(row['name'])}"
        for row in rows
    ]
    return production_drivers + active_drivers + ["active_press_count", "is_working_day", "is_saturday"]


@router.get("/profile")
async def get_partner_press_profile() -> Dict[str, Any]:
    start = _parse_dt(PARTNER_START)
    end = _parse_dt(PARTNER_END)

    async with db.pool.acquire() as conn:
        factory = await _partner_factory(conn)
        assets = await conn.fetch(
            """
            SELECT
                m.id,
                m.name,
                m.metadata->>'group' AS group_key,
                m.metadata->>'asset_level' AS asset_level,
                m.metadata->>'energy_scope' AS energy_scope
            FROM machines m
            JOIN factories f ON f.id = m.factory_id
            WHERE f.name = $1
            ORDER BY
                CASE WHEN m.metadata->>'asset_level' = 'meter_group' THEN 0 ELSE 1 END,
                m.name
            """,
            PARTNER_FACTORY_NAME,
        )

    meter_groups = []
    presses = []
    for row in assets:
        item = {
            "id": str(row["id"]),
            "name": row["name"],
            "group": row["group_key"],
            "asset_level": row["asset_level"],
            "energy_scope": row["energy_scope"],
        }
        if row["asset_level"] == "meter_group":
            meter_groups.append(item)
        else:
            presses.append(item)

    return {
        "display_name": PARTNER_DISPLAY_NAME,
        "factory": {
            "id": str(factory["id"]) if factory else None,
            "name": factory["name"] if factory else PARTNER_FACTORY_NAME,
            "location": factory["location"] if factory else None,
        },
        "source_dataset": PARTNER_SOURCE_DATASET,
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "label": _period_label(start, end),
        },
        "meter_groups": meter_groups,
        "presses": presses,
        "modeling_note": (
            "Energy is represented honestly at the three imported meter-group assets. "
            "No per-press energy is allocated or invented."
        ),
    }


@router.get("/ml-readiness")
async def get_partner_press_ml_readiness() -> Dict[str, Any]:
    start = _parse_dt(PARTNER_START)
    end = _parse_dt(PARTNER_END)

    async with db.pool.acquire() as conn:
        meter_groups = await _partner_meter_groups(conn)
        forecast_table_exists = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = 'energy_forecasts'
            )
            """
        )

        readiness = []
        for group in meter_groups:
            machine_id = group["id"]
            stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) AS raw_energy_rows,
                    MIN(time) AS energy_start,
                    MAX(time) AS energy_end,
                    SUM(energy_kwh) AS energy_kwh
                FROM energy_readings
                WHERE machine_id = $1
                  AND time >= $2
                  AND time < $3
                """,
                machine_id,
                start,
                end,
            )
            hourly_rows = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM energy_readings_1hour
                WHERE machine_id = $1
                  AND bucket >= $2
                  AND bucket < $3
                """,
                machine_id,
                start,
                end,
            )
            baseline = await conn.fetchrow(
                """
                SELECT id, model_version, training_samples, r_squared, rmse, mae, created_at
                FROM energy_baselines
                WHERE machine_id = $1
                  AND is_active = TRUE
                ORDER BY model_version DESC
                LIMIT 1
                """,
                machine_id,
            )
            forecast_rows = 0
            if forecast_table_exists:
                forecast_rows = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM energy_forecasts
                    WHERE machine_id = $1
                    """,
                    machine_id,
                )

            readiness.append({
                "machine_id": str(machine_id),
                "name": group["name"],
                "group": group["group_key"],
                "asset_level": group["asset_level"],
                "energy_scope": group["energy_scope"],
                "raw_energy_rows": int(stats["raw_energy_rows"] or 0),
                "hourly_energy_rows": int(hourly_rows or 0),
                "energy_kwh": _number(stats["energy_kwh"]),
                "energy_start": stats["energy_start"].isoformat() if stats and stats["energy_start"] else None,
                "energy_end": stats["energy_end"].isoformat() if stats and stats["energy_end"] else None,
                "baseline": dict(baseline) if baseline else None,
                "baseline_trained": bool(baseline),
                "forecast_rows": int(forecast_rows or 0),
            })

    return {
        "display_name": PARTNER_DISPLAY_NAME,
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "label": _period_label(start, end),
        },
        "forecast_table_exists": bool(forecast_table_exists),
        "meter_groups": readiness,
        "scope_note": (
            "ML baselines and forecasts are trained only for Bret, Raster, and Dimeco "
            "meter-group energy assets. Presses have production data only."
        ),
    }


@router.post("/train-ml")
async def train_partner_press_ml(
    train_baselines: bool = Query(True, description="Train baseline models for meter groups"),
    train_arima: bool = Query(True, description="Train ARIMA forecast models for meter groups"),
    train_prophet: bool = Query(False, description="Also train Prophet models; slower and optional"),
) -> Dict[str, Any]:
    start = _parse_dt(PARTNER_START)
    end = _parse_dt(PARTNER_END)

    async with db.pool.acquire() as conn:
        meter_groups = await _partner_meter_groups(conn)

    results = []
    for group in meter_groups:
        machine_id = group["id"]
        item = {
            "machine_id": str(machine_id),
            "name": group["name"],
            "group": group["group_key"],
            "baseline": None,
            "arima": None,
            "prophet": None,
            "errors": [],
        }

        if train_baselines:
            try:
                async with db.pool.acquire() as conn:
                    baseline_drivers = await _partner_baseline_drivers(conn, group["group_key"])
                item["baseline"] = await baseline_service.train_baseline(
                    machine_id=machine_id,
                    start_date=start,
                    end_date=end,
                    drivers=baseline_drivers,
                    include_machine_status=False,
                )
            except Exception as exc:
                item["errors"].append(f"baseline: {exc}")

        if train_arima:
            try:
                item["arima"] = await forecast_service.train_arima(
                    machine_id=machine_id,
                    lookback_days=90,
                    auto_order=True,
                    start_time=end.replace(tzinfo=None) - timedelta(days=90),
                    end_time=end,
                )
            except Exception as exc:
                item["errors"].append(f"arima: {exc}")

        if train_prophet:
            try:
                item["prophet"] = await forecast_service.train_prophet(
                    machine_id=machine_id,
                    lookback_days=180,
                    use_regressors=False,
                    start_time=end.replace(tzinfo=None) - timedelta(days=180),
                    end_time=end,
                )
            except Exception as exc:
                item["errors"].append(f"prophet: {exc}")

        results.append(item)

    return {
        "display_name": PARTNER_DISPLAY_NAME,
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "label": _period_label(start, end),
        },
        "trained_assets": len(results),
        "baseline_drivers": (
            "per meter group: press_production_*, press_active_*, active_press_count, "
            "is_working_day, and is_saturday"
        ),
        "scope_note": "Training targets meter-group energy assets only; no per-press energy models are created.",
        "results": results,
    }


@router.get("/summary")
async def get_partner_press_summary(
    question_type: str = Query(
        "summary",
        description=(
            "summary, top_energy, total_energy, group_energy, compare_groups, "
            "group_production, press_production, press_energy, kpis, group_kpis, "
            "sec_explanation, anomalies, machines, seus, baseline_status, period, "
            "current_data, unknown_press"
        ),
    ),
    group: Optional[str] = Query(None, description="Optional group: bret, raster, dimeco"),
    press: Optional[str] = Query(None, description="Optional press name or alias"),
    start_time: Optional[str] = Query(None, description="Optional ISO start time"),
    end_time: Optional[str] = Query(None, description="Optional ISO end time"),
) -> Dict[str, Any]:
    start = _parse_dt(start_time or PARTNER_START)
    end = _parse_dt(end_time or PARTNER_END)
    selected_group = _group_key(group)
    selected_press = _normalize_press(press)

    async with db.pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("SET LOCAL jit = off")
            factory = await _partner_factory(conn)
            assets = await conn.fetch(
                """
                SELECT
                    m.id,
                    m.name,
                    m.metadata->>'group' AS group_key,
                    m.metadata->>'asset_level' AS asset_level
                FROM machines m
                JOIN factories f ON f.id = m.factory_id
                WHERE f.name = $1
                  AND m.metadata->>'source_dataset' = $2
                ORDER BY m.name
                """,
                PARTNER_FACTORY_NAME,
                PARTNER_SOURCE_DATASET,
            )

            meter_group_ids = [
                row["id"]
                for row in assets
                if row["asset_level"] == "meter_group"
            ]
            press_ids = [
                row["id"]
                for row in assets
                if row["asset_level"] == "press"
            ]
            all_partner_ids = meter_group_ids + press_ids

            energy_rows = await conn.fetch(
                """
                SELECT
                    m.metadata->>'group' AS group_key,
                    m.name AS asset_name,
                    SUM(er.energy_kwh) AS energy_kwh,
                    AVG(er.power_kw) AS avg_power_kw,
                    MAX(er.power_kw) AS peak_power_kw,
                    COUNT(*) AS readings
                FROM energy_readings er
                JOIN machines m ON m.id = er.machine_id
                WHERE er.machine_id = ANY($1::uuid[])
                  AND er.time >= $2
                  AND er.time < $3
                GROUP BY m.metadata->>'group', m.name
                ORDER BY energy_kwh DESC
                """,
                meter_group_ids,
                start,
                end,
            )
            production_group_rows = await conn.fetch(
                """
                SELECT
                    m.metadata->>'group' AS group_key,
                    m.name AS asset_name,
                    SUM(pd.production_count) AS production_units,
                    SUM(pd.production_count_good) AS good_units,
                    SUM(pd.production_count_bad) AS bad_units,
                    COUNT(*) AS rows
                FROM production_data pd
                JOIN machines m ON m.id = pd.machine_id
                WHERE pd.machine_id = ANY($1::uuid[])
                  AND pd.time >= $2
                  AND pd.time < $3
                GROUP BY m.metadata->>'group', m.name
                ORDER BY production_units DESC
                """,
                meter_group_ids,
                start,
                end,
            )
            production_press_rows = await conn.fetch(
                """
                SELECT
                    m.metadata->>'group' AS group_key,
                    m.name AS press_name,
                    SUM(pd.production_count) AS production_units
                FROM production_data pd
                JOIN machines m ON m.id = pd.machine_id
                WHERE pd.machine_id = ANY($1::uuid[])
                  AND pd.time >= $2
                  AND pd.time < $3
                GROUP BY m.metadata->>'group', m.name
                ORDER BY m.metadata->>'group', production_units DESC
                """,
                press_ids,
                start,
                end,
            )
            data_range = await conn.fetchrow(
                """
                WITH energy_range AS (
                    SELECT MIN(time) AS start_time, MAX(time) AS end_time, COUNT(*) AS row_count
                    FROM energy_readings
                    WHERE machine_id = ANY($1::uuid[])
                ),
                production_range AS (
                    SELECT MIN(time) AS start_time, MAX(time) AS end_time, COUNT(*) AS row_count
                    FROM production_data
                    WHERE machine_id = ANY($2::uuid[])
                )
                SELECT
                  energy_range.start_time AS energy_start,
                  energy_range.end_time AS energy_end,
                  energy_range.row_count AS energy_rows,
                  production_range.start_time AS production_start,
                  production_range.end_time AS production_end,
                  production_range.row_count AS production_rows
                FROM energy_range, production_range
                """,
                meter_group_ids,
                all_partner_ids,
            )
            anomaly_rows = await conn.fetch(
                """
                SELECT
                    COALESCE(m.metadata->>'group', 'unknown') AS group_key,
                    m.name AS asset_name,
                    a.severity,
                    COUNT(*) AS anomaly_count,
                    MAX(a.detected_at) AS latest_detected_at
                FROM anomalies a
                JOIN machines m ON m.id = a.machine_id
                WHERE a.machine_id = ANY($1::uuid[])
                  AND a.detected_at >= $2
                  AND a.detected_at < $3
                GROUP BY COALESCE(m.metadata->>'group', 'unknown'), m.name, a.severity
                ORDER BY anomaly_count DESC, latest_detected_at DESC
                """,
                all_partner_ids,
                start,
                end,
            )

    energy_by_group = [
        {
            "group": row["group_key"],
            "asset_name": row["asset_name"],
            "energy_kwh": _number(row["energy_kwh"]),
            "avg_power_kw": _number(row["avg_power_kw"]),
            "peak_power_kw": _number(row["peak_power_kw"]),
            "readings": int(row["readings"] or 0),
        }
        for row in energy_rows
    ]
    production_by_group = [
        {
            "group": row["group_key"],
            "asset_name": row["asset_name"],
            "production_units": int(row["production_units"] or 0),
            "good_units": int(row["good_units"] or 0),
            "bad_units": int(row["bad_units"] or 0),
            "rows": int(row["rows"] or 0),
        }
        for row in production_group_rows
    ]
    production_by_press = [
        {
            "group": row["group_key"],
            "press_name": row["press_name"],
            "production_units": int(row["production_units"] or 0),
        }
        for row in production_press_rows
    ]

    production_lookup = {item["group"]: item for item in production_by_group}
    kpis = []
    for item in energy_by_group:
        production = production_lookup.get(item["group"], {}).get("production_units", 0)
        sec = item["energy_kwh"] / production if production else None
        kpis.append({
            "group": item["group"],
            "asset_name": item["asset_name"],
            "energy_kwh": item["energy_kwh"],
            "production_units": production,
            "sec_kwh_per_unit": round(sec, 6) if sec is not None else None,
        })

    total_energy = round(sum(item["energy_kwh"] for item in energy_by_group), 2)
    total_production = sum(item["production_units"] for item in production_by_group)
    anomalies = [
        {
            "group": row["group_key"],
            "asset_name": row["asset_name"],
            "severity": row["severity"],
            "count": int(row["anomaly_count"] or 0),
            "latest_detected_at": (
                row["latest_detected_at"].isoformat()
                if row["latest_detected_at"]
                else None
            ),
        }
        for row in anomaly_rows
    ]
    anomaly_summary = {
        "total_count": sum(item["count"] for item in anomalies),
        "by_severity": {
            severity: sum(item["count"] for item in anomalies if item["severity"] == severity)
            for severity in sorted({item["severity"] for item in anomalies if item["severity"]})
        },
        "by_asset": anomalies,
    }
    response = _build_response(
        question_type=question_type,
        group=selected_group,
        press=selected_press,
        energy_by_group=energy_by_group,
        production_by_group=production_by_group,
        kpis=kpis,
        production_by_press=production_by_press,
        anomaly_summary=anomaly_summary,
        total_energy=total_energy,
        total_production=total_production,
        period=_period_label(start, end),
    )

    return {
        "display_name": PARTNER_DISPLAY_NAME,
        "factory": {
            "id": str(factory["id"]) if factory else None,
            "name": factory["name"] if factory else PARTNER_FACTORY_NAME,
        },
        "source_dataset": PARTNER_SOURCE_DATASET,
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "label": _period_label(start, end),
        },
        "scope_note": "Energy is group-level meter data only; press-level energy is not allocated.",
        "question_type": question_type,
        "selected_group": selected_group,
        "selected_press": selected_press,
        "total_energy_kwh": total_energy,
        "total_production_units": total_production,
        "energy_by_group": energy_by_group,
        "production_by_group": production_by_group,
        "production_by_press": production_by_press,
        "kpis": kpis,
        "anomalies": anomaly_summary,
        "data_range": {
            "energy_start": data_range["energy_start"].isoformat() if data_range and data_range["energy_start"] else None,
            "energy_end": data_range["energy_end"].isoformat() if data_range and data_range["energy_end"] else None,
            "energy_rows": int(data_range["energy_rows"] or 0) if data_range else 0,
            "production_start": data_range["production_start"].isoformat() if data_range and data_range["production_start"] else None,
            "production_end": data_range["production_end"].isoformat() if data_range and data_range["production_end"] else None,
            "production_rows": int(data_range["production_rows"] or 0) if data_range else 0,
        },
        "response": response,
    }


def _build_response(
    question_type: str,
    group: Optional[str],
    press: Optional[str],
    energy_by_group: list[dict],
    production_by_group: list[dict],
    kpis: list[dict],
    production_by_press: list[dict],
    anomaly_summary: dict,
    total_energy: float,
    total_production: int,
    period: str,
) -> str:
    question = (question_type or "summary").lower()
    group_energy = {item["group"]: item for item in energy_by_group}
    group_production = {item["group"]: item for item in production_by_group}
    press_production = {item["press_name"]: item for item in production_by_press}

    if question == "current_data":
        return (
            "The ASSA ABLOY partner press-shop package has historical data, not live data. "
            f"The configured pilot period is {period}, and the latest imported readings end on "
            "2026-05-31. I will not substitute simulator or today's demo data for this partner answer."
        )

    if question == "period":
        return (
            f"The configured ASSA ABLOY partner pilot period is {period}. "
            "Imported energy and production readings currently run from 2026-03-13 through "
            "2026-05-31. Questions without an explicit date use the partner pilot period, "
            "not today's simulator data."
        )

    if question == "machines":
        meter_groups = [item["asset_name"] for item in energy_by_group]
        presses = [item["press_name"] for item in production_by_press]
        return (
            f"The partner press-shop instance has {len(meter_groups)} energy meter groups "
            f"and {len(presses)} presses. Energy meter groups: {', '.join(meter_groups)}. "
            f"Presses: {', '.join(presses)}."
        )

    if question in {"seus", "baseline_status"}:
        seu_names = [
            "Bret Presses Electricity",
            "Dimeco Presses Electricity",
            "Raster Presses Electricity",
        ]
        base = (
            f"The partner press-shop SEUs are {', '.join(seu_names)}. "
            "These are group-level electricity uses tied to the Bret, Dimeco, and Raster "
            "meter groups; individual presses are production assets, not separate energy SEUs."
        )
        if question == "baseline_status":
            return (
                base
                + " The SEU registry currently marks 0 of these 3 partner SEUs as having "
                "trained EnPI baselines, so all 3 still need linked baseline status for OVOS."
            )
        return base

    if question == "unknown_press":
        return (
            "I could not match that press name to the imported ASSA ABLOY press-shop list. "
            "Known presses are Bret125-1, Bret160-1, Bret250-1, Bret250-2, Rast160-1, "
            "Rast125-1, Rast250-1, Rast250-2, Dimeco80-1, Dimeco80-2, Flexi-1, "
            "Schu80-1, and Rast125-2. Energy is only available at Bret, Raster, "
            "and Dimeco meter-group level."
        )

    if question == "total_energy":
        return (
            f"For {period}, the ASSA ABLOY partner press shop used {total_energy:,.2f} kWh "
            "across the three imported press-shop meter groups."
        )

    if question == "press_energy" and press:
        item = press_production.get(press)
        group_text = f" Its production belongs to the {GROUP_LABELS[item['group']]}." if item else ""
        return (
            f"No per-press energy is available for {press}. Energy is only metered at the "
            f"Bret, Raster, and Dimeco group level, so I will not allocate or invent "
            f"energy for an individual press.{group_text}"
        )

    if question == "press_production" and press:
        item = press_production.get(press)
        if not item:
            return f"No SQDC production data was found for press {press} in {period}."
        return (
            f"For {period}, press {press} produced {item['production_units']:,} units "
            f"in the {GROUP_LABELS[item['group']]}."
        )

    if question == "group_energy" and group:
        item = group_energy.get(group)
        if not item:
            return f"No energy data was found for the {group} press group in the partner period."
        return (
            f"For {period}, the {GROUP_LABELS[group]} used {item['energy_kwh']:,.2f} kWh. "
            "This is meter-group energy; no per-press allocation has been invented."
        )

    if question == "group_production" and group:
        item = group_production.get(group)
        if not item:
            return f"No production data was found for the {group} press group in the partner period."
        return (
            f"For {period}, {GROUP_LABELS[group]} produced {item['production_units']:,} units "
            "based on SQDC press production summed to the group."
        )

    if question == "group_kpis" and group:
        item = next((kpi for kpi in kpis if kpi["group"] == group), None)
        if not item:
            return f"No KPI data was found for the {group} press group in {period}."
        sec = item["sec_kwh_per_unit"]
        sec_text = f"{sec:.6f} kWh/unit" if sec is not None else "SEC unavailable"
        return (
            f"For {period}, {GROUP_LABELS[group]} used {item['energy_kwh']:,.2f} kWh, "
            f"produced {item['production_units']:,} units, and had SEC {sec_text}."
        )

    if question == "compare_groups":
        parts = [
            f"{GROUP_LABELS[item['group']]}: {item['energy_kwh']:,.2f} kWh"
            for item in energy_by_group
        ]
        return f"For {period}, energy by press-meter group was: " + "; ".join(parts) + "."

    if question == "anomalies":
        total = anomaly_summary.get("total_count", 0)
        if not total:
            return (
                f"No anomalies are recorded for the {PARTNER_DISPLAY_NAME} dataset in {period}. "
                "This answer is based on the imported partner meter groups and press assets only."
            )
        by_severity = anomaly_summary.get("by_severity") or {}
        severity_text = ", ".join(
            f"{count} {severity}" for severity, count in sorted(by_severity.items())
        )
        asset_parts = [
            f"{item['asset_name']} {item['count']} {item['severity']}"
            for item in anomaly_summary.get("by_asset", [])[:3]
        ]
        asset_text = "; ".join(asset_parts)
        return (
            f"For {period}, the {PARTNER_DISPLAY_NAME} dataset has {total} recorded anomalies"
            f" ({severity_text}). Top affected assets: {asset_text}. "
            "No simulator anomalies are included."
        )

    if question == "kpis":
        parts = []
        for item in kpis:
            sec = item["sec_kwh_per_unit"]
            sec_text = f"{sec:.6f} kWh/unit" if sec is not None else "SEC unavailable"
            parts.append(
                f"{GROUP_LABELS[item['group']]}: {item['energy_kwh']:,.2f} kWh, "
                f"{item['production_units']:,} units, {sec_text}"
            )
        return (
            f"Partner press-shop KPIs for {period}: total energy {total_energy:,.2f} kWh "
            f"and total production {total_production:,} units. " + "; ".join(parts) + "."
        )

    if question == "sec_explanation":
        parts = []
        for item in kpis:
            sec = item["sec_kwh_per_unit"]
            if sec is not None:
                parts.append(f"{GROUP_LABELS[item['group']]} {sec:.6f} kWh/unit")
        return (
            "SEC means specific energy consumption: energy used per produced unit. "
            "Lower SEC is better when product mix is comparable. "
            f"For {period}, partner press-shop SEC by meter group is: "
            + "; ".join(parts)
            + "."
        )

    ranked = energy_by_group[:3]
    if question in {"top_energy", "summary"}:
        parts = [
            f"{idx}. {item['asset_name']} {item['energy_kwh']:,.2f} kWh"
            for idx, item in enumerate(ranked, start=1)
        ]
        return (
            f"For the {PARTNER_DISPLAY_NAME} dataset ({period}), total group-meter energy was "
            f"{total_energy:,.2f} kWh. Top energy consumers: " + "; ".join(parts) + "."
        )

    return (
        f"For {period}, total partner press-shop group-meter energy was {total_energy:,.2f} kWh "
        f"and summed group production was {total_production:,} units."
    )

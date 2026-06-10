#!/usr/bin/env python3
"""
Import partner press-shop production and energy data into the EnMS schema.

The importer reads the original partner attachment zip directly. It does not
require pandas/openpyxl; XLSX files are parsed through the standard ZIP/XML
format. Applying the import uses psql, preferring the postgres Docker service
so the host does not need Python database dependencies.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


DEFAULT_PACKAGE = Path("/home/ubuntu/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip")
DEFAULT_FACTORY_NAME = "Partner Press Shop"
DEFAULT_FACTORY_ID = uuid.UUID("52f9e235-4ef2-5a1b-a302-5db5a06420fc")
DATASET_SOURCE = "partner_press_shop_2026_06_10"
NAMESPACE = uuid.UUID("0f720db0-7c42-5b1b-9b0b-93ba9e79e7c2")

XLSX_NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL_NS = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}

GROUP_PRESS_NAMES = {
    "bret": ["Bret125-1", "Bret160-1", "Bret250-1", "Bret250-2"],
    "raster": ["Rast160-1", "Rast125-1", "Rast250-1", "Rast250-2"],
    "dimeco": ["Dimeco80-1", "Dimeco80-2", "Flexi-1", "Schu80-1", "Rast125-2"],
}

GROUPS = {
    "bret": {
        "display": "Bret Presses",
        "zip_name": "Bret presses.zip",
        "meter_component": "PP BU STANTARE Bret",
        "rated_power_kw": Decimal("250"),
    },
    "raster": {
        "display": "Raster Presses",
        "zip_name": "Raster presses.zip",
        "meter_component": "PP BU RASTERE",
        "rated_power_kw": Decimal("250"),
    },
    "dimeco": {
        "display": "Dimeco Presses",
        "zip_name": "Dimeco.zip",
        "meter_component": "Prese Dimeco",
        "rated_power_kw": Decimal("250"),
    },
}

PRESS_TO_GROUP = {
    press: group for group, presses in GROUP_PRESS_NAMES.items() for press in presses
}


@dataclass(frozen=True)
class Machine:
    id: uuid.UUID
    name: str
    kind: str
    group_key: str | None
    is_meter_group: bool
    rated_power_kw: Decimal


@dataclass(frozen=True)
class EnergyRow:
    machine_id: uuid.UUID
    timestamp: datetime
    energy_kwh: Decimal
    power_kw: Decimal
    group_key: str
    source_file: str
    source_component: str
    resolution: str


@dataclass(frozen=True)
class ProductionRow:
    machine_id: uuid.UUID
    timestamp: datetime
    production_count: int
    source_kind: str
    group_key: str | None
    press_name: str | None
    source_rows: int
    source_column: str


@dataclass
class Dataset:
    machines: dict[str, Machine]
    energy_rows: list[EnergyRow]
    production_rows: list[ProductionRow]
    skipped_energy_files: list[dict[str, str]]
    warnings: list[str]


def excel_datetime(value: str | int | float | Decimal) -> datetime:
    return datetime(1899, 12, 30, tzinfo=timezone.utc) + timedelta(days=float(value))


def normalize_decimal(value: str | int | float | Decimal | None) -> Decimal:
    if value in (None, ""):
        return Decimal("0")
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError(f"Cannot parse decimal value: {value!r}") from exc


def machine_id(slug: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, f"{DATASET_SOURCE}:machine:{slug}")


def seu_id(slug: str) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, f"{DATASET_SOURCE}:seu:{slug}")


def column_number(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if not match:
        return 1
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - 64
    return value


def read_xlsx_rows(xlsx_bytes: bytes, sheet_index: int = 0) -> list[list[str | None]]:
    with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as workbook:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            for item in root.findall("a:si", XLSX_NS):
                shared_strings.append("".join(text.text or "" for text in item.findall(".//a:t", XLSX_NS)))

        wb_root = ET.fromstring(workbook.read("xl/workbook.xml"))
        rel_root = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
        rel_map = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rel_root.findall("rel:Relationship", REL_NS)
        }
        sheet = wb_root.findall("a:sheets/a:sheet", XLSX_NS)[sheet_index]
        rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target = rel_map[rel_id].lstrip("/")
        sheet_path = target if target.startswith("xl/") else f"xl/{target}"
        root = ET.fromstring(workbook.read(sheet_path))

        rows: list[list[str | None]] = []
        for row in root.findall(".//a:sheetData/a:row", XLSX_NS):
            values: list[str | None] = []
            last_col = 0
            for cell in row.findall("a:c", XLSX_NS):
                idx = column_number(cell.attrib.get("r", "A1"))
                while last_col + 1 < idx:
                    values.append(None)
                    last_col += 1

                node = cell.find("a:v", XLSX_NS)
                value = None if node is None else node.text
                if cell.attrib.get("t") == "s" and value is not None:
                    value = shared_strings[int(value)]
                values.append(value)
                last_col = idx
            rows.append(values)
        return rows


def machine_catalog() -> dict[str, Machine]:
    catalog: dict[str, Machine] = {}
    for group_key, cfg in GROUPS.items():
        name = f"{cfg['display']} Meter Group"
        catalog[f"group:{group_key}"] = Machine(
            id=machine_id(f"group:{group_key}"),
            name=name,
            kind="other",
            group_key=group_key,
            is_meter_group=True,
            rated_power_kw=cfg["rated_power_kw"],
        )
        for press in GROUP_PRESS_NAMES[group_key]:
            catalog[f"press:{press}"] = Machine(
                id=machine_id(f"press:{press}"),
                name=press,
                kind="other",
                group_key=group_key,
                is_meter_group=False,
                rated_power_kw=Decimal("0"),
            )
    return catalog


def parse_production(package: zipfile.ZipFile, catalog: dict[str, Machine]) -> tuple[list[ProductionRow], list[str]]:
    rows = read_xlsx_rows(package.read("SQDC.mai2025-mai2026.xlsx"))
    if not rows:
        raise ValueError("SQDC workbook is empty")

    header = rows[0]
    quantity_idx = 7  # Column H, named LIBRE1 in the source workbook.
    warnings: list[str] = []
    if len(header) <= quantity_idx or header[quantity_idx] != "LIBRE1":
        warnings.append(f"Expected SQDC column H to be LIBRE1, found {header[quantity_idx] if len(header) > quantity_idx else None!r}")

    daily_by_press: dict[tuple[str, date], dict[str, int]] = defaultdict(lambda: {"qty": 0, "rows": 0})
    unknown_presses: set[str] = set()
    for row in rows[1:]:
        if len(row) < 8:
            continue
        press = (row[1] or "").strip()
        raw_date = row[2]
        if not press or not raw_date:
            continue
        if press not in PRESS_TO_GROUP:
            unknown_presses.add(press)
            continue
        qty = int(normalize_decimal(row[quantity_idx] if len(row) > quantity_idx else None))
        prod_date = excel_datetime(raw_date).date()
        key = (press, prod_date)
        daily_by_press[key]["qty"] += qty
        daily_by_press[key]["rows"] += 1

    if unknown_presses:
        warnings.append(f"Skipped unknown SQDC press names: {', '.join(sorted(unknown_presses))}")

    production_rows: list[ProductionRow] = []
    daily_by_group: dict[tuple[str, date], dict[str, int | set[str]]] = defaultdict(
        lambda: {"qty": 0, "rows": 0, "presses": set()}
    )

    for (press, prod_date), stats in sorted(daily_by_press.items(), key=lambda item: (item[0][1], item[0][0])):
        group_key = PRESS_TO_GROUP[press]
        ts = datetime.combine(prod_date, time.min, tzinfo=timezone.utc)
        machine = catalog[f"press:{press}"]
        qty = int(stats["qty"])
        production_rows.append(
            ProductionRow(
                machine_id=machine.id,
                timestamp=ts,
                production_count=qty,
                source_kind="press_daily",
                group_key=group_key,
                press_name=press,
                source_rows=int(stats["rows"]),
                source_column="SQDC!H/LIBRE1",
            )
        )
        group_key_date = (group_key, prod_date)
        daily_by_group[group_key_date]["qty"] = int(daily_by_group[group_key_date]["qty"]) + qty
        daily_by_group[group_key_date]["rows"] = int(daily_by_group[group_key_date]["rows"]) + int(stats["rows"])
        presses = daily_by_group[group_key_date]["presses"]
        assert isinstance(presses, set)
        presses.add(press)

    for (group_key, prod_date), stats in sorted(daily_by_group.items(), key=lambda item: (item[0][1], item[0][0])):
        machine = catalog[f"group:{group_key}"]
        production_rows.append(
            ProductionRow(
                machine_id=machine.id,
                timestamp=datetime.combine(prod_date, time.min, tzinfo=timezone.utc),
                production_count=int(stats["qty"]),
                source_kind="group_daily_derived",
                group_key=group_key,
                press_name=None,
                source_rows=int(stats["rows"]),
                source_column="SUM(SQDC!H/LIBRE1 by group)",
            )
        )

    return production_rows, warnings


def parse_energy(
    package: zipfile.ZipFile,
    catalog: dict[str, Machine],
    include_bret_transformer: bool,
) -> tuple[list[EnergyRow], list[dict[str, str]]]:
    energy_rows: list[EnergyRow] = []
    skipped: list[dict[str, str]] = []

    for group_key, cfg in GROUPS.items():
        nested = zipfile.ZipFile(io.BytesIO(package.read(cfg["zip_name"])))
        group_machine = catalog[f"group:{group_key}"]
        for name in sorted(nested.namelist()):
            if not name.lower().endswith(".xlsx"):
                continue
            rows = read_xlsx_rows(nested.read(name))
            if len(rows) < 5:
                skipped.append({"file": name, "reason": "no Records data"})
                continue

            component = rows[1][1] if len(rows[1]) > 1 else ""
            series = rows[2][1] if len(rows[2]) > 1 else ""
            unit = rows[3][1] if len(rows[3]) > 1 else ""
            is_expected_meter = component == cfg["meter_component"]
            is_bret_transformer = group_key == "bret" and component == "Statia TRAFO-TRAFO 3"

            if not is_expected_meter and not (include_bret_transformer and is_bret_transformer):
                skipped.append({
                    "file": name,
                    "component": str(component),
                    "reason": "component is not the configured group meter",
                })
                continue
            if series != "Energy cons. T1":
                skipped.append({"file": name, "component": str(component), "reason": f"unsupported series {series!r}"})
                continue
            if unit != "[ kWh ]":
                skipped.append({"file": name, "component": str(component), "reason": f"unsupported unit {unit!r}"})
                continue

            resolution = "hourly" if "_hours_" in name else "daily"
            interval_hours = Decimal("1") if resolution == "hourly" else Decimal("24")
            for row in rows[4:]:
                if len(row) < 2 or row[0] in (None, "") or row[1] in (None, ""):
                    continue
                energy_kwh = normalize_decimal(row[1])
                timestamp = excel_datetime(row[0])
                energy_rows.append(
                    EnergyRow(
                        machine_id=group_machine.id,
                        timestamp=timestamp,
                        energy_kwh=energy_kwh,
                        power_kw=(energy_kwh / interval_hours).quantize(Decimal("0.001")),
                        group_key=group_key,
                        source_file=name,
                        source_component=str(component),
                        resolution=resolution,
                    )
                )

    return energy_rows, skipped


def load_dataset(package_path: Path, include_bret_transformer: bool = False) -> Dataset:
    catalog = machine_catalog()
    with zipfile.ZipFile(package_path) as package:
        required = {"SQDC.mai2025-mai2026.xlsx"} | {cfg["zip_name"] for cfg in GROUPS.values()}
        missing = required - set(package.namelist())
        if missing:
            raise FileNotFoundError(f"Partner package is missing: {', '.join(sorted(missing))}")
        production_rows, warnings = parse_production(package, catalog)
        energy_rows, skipped = parse_energy(package, catalog, include_bret_transformer)
    return Dataset(catalog, energy_rows, production_rows, skipped, warnings)


def sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, Decimal)):
        return str(value)
    if isinstance(value, uuid.UUID):
        return f"'{value}'::uuid"
    if isinstance(value, datetime):
        return f"'{value.isoformat()}'::timestamptz"
    text = str(value).replace("'", "''")
    return f"'{text}'"


def json_literal(value: dict[str, object]) -> str:
    return f"{sql_literal(json.dumps(value, sort_keys=True, separators=(',', ':')))}::jsonb"


def values_sql(rows: Iterable[Iterable[object]]) -> str:
    return ",\n".join("(" + ", ".join(sql_literal(value) for value in row) + ")" for row in rows)


def chunked(items: list[object], size: int) -> Iterable[list[object]]:
    for idx in range(0, len(items), size):
        yield items[idx: idx + size]


def build_sql(dataset: Dataset, factory_name: str, factory_id: uuid.UUID, refresh_aggregates: bool) -> str:
    lines: list[str] = [
        "\\set ON_ERROR_STOP on",
        "BEGIN;",
        "",
        "INSERT INTO factories (id, name, location, timezone, is_active, metadata)",
        "VALUES (",
        f"  {sql_literal(factory_id)},",
        f"  {sql_literal(factory_name)},",
        "  'Partner press shop',",
        "  'Europe/Bucharest',",
        "  TRUE,",
        f"  {json_literal({'source_dataset': DATASET_SOURCE, 'importer': 'scripts/import_partner_press_data.py'})}",
        ")",
        "ON CONFLICT (id) DO UPDATE SET",
        "  name = EXCLUDED.name,",
        "  location = EXCLUDED.location,",
        "  timezone = EXCLUDED.timezone,",
        "  is_active = TRUE,",
        "  metadata = factories.metadata || EXCLUDED.metadata,",
        "  updated_at = NOW();",
        "",
    ]

    machine_rows = []
    for machine in sorted(dataset.machines.values(), key=lambda item: item.name):
        metadata = {
            "source_dataset": DATASET_SOURCE,
            "asset_level": "meter_group" if machine.is_meter_group else "press",
            "group": machine.group_key,
            "energy_scope": "group_meter_only" if machine.is_meter_group else "no_direct_energy_meter",
        }
        machine_rows.append((
            machine.id,
            factory_id,
            machine.name,
            f"Partner press-shop {'meter group' if machine.is_meter_group else 'press'} imported from {DATASET_SOURCE}",
            machine.kind,
            "Partner",
            "Foreign partner source data",
            str(machine.id)[:18],
            machine.rated_power_kw,
            400,
            50,
            "Press shop",
            86400,
            f"factory/partner-press-shop/{machine.name.lower().replace(' ', '-').replace('/', '-')}",
            True,
            machine.is_meter_group,
            json.dumps(metadata, sort_keys=True, separators=(",", ":")),
        ))

    lines += [
        "INSERT INTO machines (",
        "  id, factory_id, name, description, type, manufacturer, model, serial_number,",
        "  rated_power_kw, rated_voltage_v, rated_frequency_hz, location_in_factory,",
        "  data_interval_seconds, mqtt_topic, is_active, is_critical, metadata",
        ") VALUES",
        values_sql(machine_rows),
        "ON CONFLICT (id) DO UPDATE SET",
        "  factory_id = EXCLUDED.factory_id,",
        "  name = EXCLUDED.name,",
        "  description = EXCLUDED.description,",
        "  type = EXCLUDED.type,",
        "  manufacturer = EXCLUDED.manufacturer,",
        "  model = EXCLUDED.model,",
        "  rated_power_kw = EXCLUDED.rated_power_kw,",
        "  location_in_factory = EXCLUDED.location_in_factory,",
        "  data_interval_seconds = EXCLUDED.data_interval_seconds,",
        "  mqtt_topic = EXCLUDED.mqtt_topic,",
        "  is_active = TRUE,",
        "  is_critical = EXCLUDED.is_critical,",
        "  metadata = machines.metadata || EXCLUDED.metadata,",
        "  updated_at = NOW();",
        "",
    ]

    # One SEU per meter group, because energy is available at group/meter level.
    lines += [
        "INSERT INTO seus (id, name, description, energy_source_id, machine_ids, baseline_year, baseline_start_date, baseline_end_date, is_active)",
        "SELECT v.id, v.name, v.description, es.id, ARRAY[v.machine_id]::uuid[], 2025, DATE '2025-05-01', DATE '2026-05-31', TRUE",
        "FROM (VALUES",
        values_sql([
            (
                seu_id(group_key),
                f"{cfg['display']} Electricity",
                f"Partner press-shop {cfg['display']} electricity meter group. Energy is metered at group level; press-level energy is not allocated.",
                dataset.machines[f"group:{group_key}"].id,
            )
            for group_key, cfg in GROUPS.items()
        ]),
        ") AS v(id, name, description, machine_id)",
        "JOIN energy_sources es ON es.name = 'electricity'",
        "ON CONFLICT (id) DO UPDATE SET",
        "  name = EXCLUDED.name,",
        "  description = EXCLUDED.description,",
        "  energy_source_id = EXCLUDED.energy_source_id,",
        "  machine_ids = EXCLUDED.machine_ids,",
        "  baseline_year = EXCLUDED.baseline_year,",
        "  baseline_start_date = EXCLUDED.baseline_start_date,",
        "  baseline_end_date = EXCLUDED.baseline_end_date,",
        "  is_active = TRUE,",
        "  updated_at = NOW();",
        "",
    ]

    for batch in chunked(dataset.energy_rows, 500):
        lines += [
            "INSERT INTO energy_readings (",
            "  time, machine_id, energy_type, power_kw, energy_kwh, voltage_v, power_factor,",
            "  is_estimated, quality_score, source, metadata",
            ") VALUES",
            values_sql([
                (
                    row.timestamp,
                    row.machine_id,
                    "electrical",
                    row.power_kw,
                    row.energy_kwh,
                    400,
                    Decimal("0.95"),
                    False,
                    Decimal("1.00"),
                    "partner_import",
                    json.dumps({
                        "source_dataset": DATASET_SOURCE,
                        "source_file": row.source_file,
                        "source_component": row.source_component,
                        "group": row.group_key,
                        "resolution": row.resolution,
                    }, sort_keys=True, separators=(",", ":")),
                )
                for row in batch
            ]),
            "ON CONFLICT (machine_id, time, energy_type) DO UPDATE SET",
            "  power_kw = EXCLUDED.power_kw,",
            "  energy_kwh = EXCLUDED.energy_kwh,",
            "  voltage_v = EXCLUDED.voltage_v,",
            "  power_factor = EXCLUDED.power_factor,",
            "  is_estimated = EXCLUDED.is_estimated,",
            "  quality_score = EXCLUDED.quality_score,",
            "  source = EXCLUDED.source,",
            "  metadata = energy_readings.metadata || EXCLUDED.metadata;",
            "",
        ]

    for batch in chunked(dataset.production_rows, 500):
        lines += [
            "INSERT INTO production_data (",
            "  time, machine_id, production_count, production_count_good, production_count_bad,",
            "  operating_mode, product_id, quality_score, metadata",
            ") VALUES",
            values_sql([
                (
                    row.timestamp,
                    row.machine_id,
                    row.production_count,
                    row.production_count,
                    0,
                    "running" if row.production_count > 0 else "idle",
                    "press-shop-production",
                    Decimal("100.00"),
                    json.dumps({
                        "source_dataset": DATASET_SOURCE,
                        "source_kind": row.source_kind,
                        "source_column": row.source_column,
                        "group": row.group_key,
                        "press_name": row.press_name,
                        "source_rows": row.source_rows,
                    }, sort_keys=True, separators=(",", ":")),
                )
                for row in batch
            ]),
            "ON CONFLICT (machine_id, time) DO UPDATE SET",
            "  production_count = EXCLUDED.production_count,",
            "  production_count_good = EXCLUDED.production_count_good,",
            "  production_count_bad = EXCLUDED.production_count_bad,",
            "  operating_mode = EXCLUDED.operating_mode,",
            "  product_id = EXCLUDED.product_id,",
            "  quality_score = EXCLUDED.quality_score,",
            "  metadata = production_data.metadata || EXCLUDED.metadata;",
            "",
        ]

    status_rows = []
    energy_totals: dict[uuid.UUID, Decimal] = defaultdict(Decimal)
    energy_latest: dict[uuid.UUID, datetime] = {}
    prod_totals: dict[uuid.UUID, int] = defaultdict(int)
    prod_latest: dict[uuid.UUID, datetime] = {}
    for row in dataset.energy_rows:
        energy_totals[row.machine_id] += row.energy_kwh
        energy_latest[row.machine_id] = max(energy_latest.get(row.machine_id, row.timestamp), row.timestamp)
    for row in dataset.production_rows:
        prod_totals[row.machine_id] += row.production_count
        prod_latest[row.machine_id] = max(prod_latest.get(row.machine_id, row.timestamp), row.timestamp)
    for machine in sorted(dataset.machines.values(), key=lambda item: item.name):
        status_rows.append((
            machine.id,
            False,
            "offline",
            0,
            energy_totals.get(machine.id, Decimal("0")).quantize(Decimal("0.001")),
            prod_totals.get(machine.id, 0),
            energy_latest.get(machine.id),
            prod_latest.get(machine.id),
            "normal",
            Decimal("100.00"),
            json.dumps({"source_dataset": DATASET_SOURCE, "last_imported_at": datetime.now(timezone.utc).isoformat()}, sort_keys=True, separators=(",", ":")),
        ))

    lines += [
        "INSERT INTO machine_status (",
        "  machine_id, is_running, current_mode, current_power_kw, energy_total_kwh,",
        "  production_total_units, last_reading_time, last_production_time, alert_level, health_score, metadata",
        ") VALUES",
        values_sql(status_rows),
        "ON CONFLICT (machine_id) DO UPDATE SET",
        "  is_running = EXCLUDED.is_running,",
        "  current_mode = EXCLUDED.current_mode,",
        "  current_power_kw = EXCLUDED.current_power_kw,",
        "  energy_total_kwh = EXCLUDED.energy_total_kwh,",
        "  production_total_units = EXCLUDED.production_total_units,",
        "  last_reading_time = EXCLUDED.last_reading_time,",
        "  last_production_time = EXCLUDED.last_production_time,",
        "  alert_level = EXCLUDED.alert_level,",
        "  health_score = EXCLUDED.health_score,",
        "  metadata = machine_status.metadata || EXCLUDED.metadata,",
        "  last_updated = NOW();",
        "",
    ]

    lines += [
        "COMMIT;",
        "",
    ]

    if refresh_aggregates:
        for view in [
            "energy_readings_1min",
            "energy_readings_15min",
            "energy_readings_1hour",
            "energy_readings_1day",
            "production_data_1min",
            "production_data_15min",
            "production_data_1hour",
            "production_data_1day",
        ]:
            lines.append(
                f"CALL refresh_continuous_aggregate('{view}', '2025-04-01T00:00:00+00'::timestamptz, '2026-06-01T00:00:00+00'::timestamptz);"
            )
        lines.append("")

    lines += [
        "SELECT",
        "  (SELECT COUNT(*) FROM machines WHERE metadata->>'source_dataset' = 'partner_press_shop_2026_06_10') AS partner_machines,",
        "  (SELECT COUNT(*) FROM energy_readings WHERE source = 'partner_import') AS partner_energy_rows,",
        "  (SELECT COUNT(*) FROM production_data WHERE metadata->>'source_dataset' = 'partner_press_shop_2026_06_10') AS partner_production_rows;",
    ]
    return "\n".join(lines)


def profile(dataset: Dataset) -> dict[str, object]:
    energy_by_group: dict[str, dict[str, object]] = {}
    for group_key in GROUPS:
        rows = [row for row in dataset.energy_rows if row.group_key == group_key]
        if rows:
            energy_by_group[group_key] = {
                "rows": len(rows),
                "total_kwh": float(sum((row.energy_kwh for row in rows), Decimal("0"))),
                "start": min(row.timestamp for row in rows).date().isoformat(),
                "end": max(row.timestamp for row in rows).date().isoformat(),
            }
        else:
            energy_by_group[group_key] = {"rows": 0, "total_kwh": 0.0, "start": None, "end": None}

    prod_by_machine: dict[str, dict[str, object]] = {}
    id_to_name = {machine.id: machine.name for machine in dataset.machines.values()}
    for row in dataset.production_rows:
        name = id_to_name[row.machine_id]
        stats = prod_by_machine.setdefault(name, {"rows": 0, "total_units": 0, "start": None, "end": None})
        stats["rows"] = int(stats["rows"]) + 1
        stats["total_units"] = int(stats["total_units"]) + row.production_count
        current_start = stats["start"]
        current_end = stats["end"]
        row_date = row.timestamp.date().isoformat()
        stats["start"] = row_date if current_start is None else min(str(current_start), row_date)
        stats["end"] = row_date if current_end is None else max(str(current_end), row_date)

    return {
        "dataset": DATASET_SOURCE,
        "machines": len(dataset.machines),
        "energy": energy_by_group,
        "production": prod_by_machine,
        "skipped_energy_files": dataset.skipped_energy_files,
        "warnings": dataset.warnings,
    }


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def run_psql(sql: str, env_path: Path, sql_output: Path | None) -> None:
    if sql_output:
        sql_output.write_text(sql, encoding="utf-8")

    env = read_env(env_path)
    user = env.get("POSTGRES_USER", os.environ.get("POSTGRES_USER", "raptorblingx"))
    db_name = env.get("POSTGRES_DB", os.environ.get("POSTGRES_DB", "enms_db"))

    with tempfile.NamedTemporaryFile("w", suffix=".sql", encoding="utf-8", delete=False) as handle:
        handle.write(sql)
        sql_path = Path(handle.name)

    try:
        docker_cmd = ["docker", "compose", "exec", "-T", "postgres", "psql", "-U", user, "-d", db_name]
        subprocess.run(docker_cmd, input=sql, text=True, check=True)
    except FileNotFoundError:
        host_cmd = ["psql", "-U", user, "-d", db_name, "-f", str(sql_path)]
        if env.get("POSTGRES_EXTERNAL_PORT"):
            host_cmd[1:1] = ["-p", env["POSTGRES_EXTERNAL_PORT"]]
        if env.get("POSTGRES_HOST"):
            host_cmd[1:1] = ["-h", env["POSTGRES_HOST"]]
        host_env = os.environ.copy()
        if env.get("POSTGRES_PASSWORD"):
            host_env["PGPASSWORD"] = env["POSTGRES_PASSWORD"]
        subprocess.run(host_cmd, env=host_env, check=True)
    finally:
        sql_path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile or import partner press-shop data.")
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE, help="Path to the partner attachment zip.")
    parser.add_argument("--factory-name", default=DEFAULT_FACTORY_NAME)
    parser.add_argument("--factory-id", type=uuid.UUID, default=DEFAULT_FACTORY_ID)
    parser.add_argument("--include-bret-transformer", action="store_true", help="Also import the separate Bret transformer hourly file.")
    parser.add_argument("--apply", action="store_true", help="Apply the import to the configured PostgreSQL database.")
    parser.add_argument("--no-refresh-aggregates", action="store_true", help="Skip continuous aggregate refresh calls.")
    parser.add_argument("--env-file", type=Path, default=Path(".env"), help="Environment file for DB credentials.")
    parser.add_argument("--write-sql", type=Path, help="Write generated SQL to this path.")
    parser.add_argument("--json", action="store_true", help="Print profile as JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dataset = load_dataset(args.package, include_bret_transformer=args.include_bret_transformer)
    summary = profile(dataset)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"Dataset: {summary['dataset']}")
        print(f"Machines to upsert: {summary['machines']}")
        print("Energy by group:")
        for group_key, stats in summary["energy"].items():
            print(f"  - {group_key}: {stats['rows']} rows, {stats['total_kwh']:.3f} kWh, {stats['start']} to {stats['end']}")
        print("Production rows by machine:")
        for name, stats in sorted(summary["production"].items()):
            print(f"  - {name}: {stats['rows']} rows, {stats['total_units']} units, {stats['start']} to {stats['end']}")
        if summary["skipped_energy_files"]:
            print("Skipped energy files:")
            for item in summary["skipped_energy_files"]:
                print(f"  - {item.get('file')}: {item.get('reason')} ({item.get('component', '')})")
        for warning in summary["warnings"]:
            print(f"WARNING: {warning}", file=sys.stderr)

    sql = build_sql(
        dataset=dataset,
        factory_name=args.factory_name,
        factory_id=args.factory_id,
        refresh_aggregates=not args.no_refresh_aggregates,
    )
    if args.write_sql and not args.apply:
        args.write_sql.write_text(sql, encoding="utf-8")
        print(f"Wrote SQL to {args.write_sql}")
    if args.apply:
        run_psql(sql, args.env_file, args.write_sql)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# ASSA ABLOY Data Verification

Verification date: **2026-06-15**

Source:

```text
data/raw/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip
```

## Package Integrity

- Outer ZIP CRC check passed.
- All three nested ZIP CRC checks passed.
- Outer package contains the SQDC workbook and three energy archives.
- Nested energy archives contain 42 XLSX files:
  - Bret: 15 files.
  - Dimeco: 13 files.
  - Raster: 14 files.
- Bret includes 14 group-meter workbooks plus one separate transformer
  workbook. No workbook is silently ignored by the default import.

## Imported Assets

The database contains 17 partner assets:

- 3 press-group energy meters.
- 13 production presses.
- 1 auxiliary Bret transformer reference meter.

The transformer is marked `upstream_reference_not_in_group_totals`. It is not
added to Bret energy, total press-shop energy, or SEC.

## Energy Reconciliation

Full source group-meter data:

| Group | Source rows | Source total |
|---|---:|---:|
| Bret | 426 | 42,818.125 kWh |
| Raster | 426 | 45,598.376 kWh |
| Dimeco | 383 | 59,661.969 kWh |
| **Total** | **1,235** | **148,078.470 kWh** |

Separate transformer reference:

| Meter | Rows | Period | Total |
|---|---:|---|---:|
| Bret Transformer Meter (TRAFO 3) | 743 | 2026-03-01 00:00 to 2026-03-31 23:00 | 263,999.155 kWh |

Default dashboard KPI period is 2025-05-01 through 2026-06-01:

| Group | KPI-period total |
|---|---:|
| Bret | 39,611.063 kWh |
| Raster | 41,981.813 kWh |
| Dimeco | 59,661.969 kWh |
| **Total** | **141,254.845 kWh** |

The API and OVOS display the half-up rounded total: **141,254.85 kWh**.

Imported energy rows in the database: **1,978**

- 1,235 group-meter rows.
- 743 transformer reference rows.

## SQDC Reconciliation

- Workbook XML rows including header: 9,628.
- Post-header rows: 9,627.
- Blank terminal row: 1.
- Valid source records: 9,626.
- Recognized press names: 13 of 13.
- Quantity column: `LIBRE1` (column H).
- Raw negative correction entries: 66.
- Negative daily net adjustments after aggregation: 13.
- Net source production: **27,625,665 units**.

Materialized database rows:

- Per-press daily rows: 5,148.
- Derived group daily rows: 1,188.
- Total production rows: **6,336**.

Derived group rows duplicate the same source production only to align
production with group-meter energy for SEC. They are not extra source output.

The source does not classify good units, bad units, or quality score. Those
database fields are null rather than invented as 100 percent good production.

## Production Totals

| Physical group | Net units |
|---|---:|
| Bret | 7,797,167 |
| Raster | 7,756,785 |
| Dimeco | 12,071,713 |
| **Total** | **27,625,665** |

Important mapping notes:

- `Rast125-2` belongs to the Dimeco physical group in the partner mapping.
- `Rast250-1` has zero `LIBRE1` production in the source.
- Individual presses have production data but no direct energy meter.

## Retention Defect Corrected

The original 90-day Timescale retention policies deleted historical raw rows,
which caused the dashboard to show only 228 energy readings and 1,216
production rows.

The importer now:

- Removes the 90-day policies for `energy_readings` and `production_data`.
- Applies five-year retention to both hypertables.
- Replaces this source dataset exactly on each import.
- Refreshes all relevant continuous aggregates.
- Clears stale partner anomaly records after an exact reimport.

Current policies were verified as five years.

## Dashboard And API Verification

Expected presentation values:

- Partner assets: 17.
- Baselines: 3 of 3 trained.
- Partner anomalies: 0.
- Energy readings: 1,978.
- Total KPI energy: 141.3K kWh.
- Production rows: 6,336.
- Data period: 396 days.
- Peak displayed group power: 12 kW after dashboard integer formatting.
- Cost is labeled as an estimate in EUR at EUR 0.15/kWh.
- Carbon is labeled as an estimate at 0.45 kg CO2/kWh.

Normal Isolation Forest candidates are no longer persisted or displayed as
anomalies. The previous eight `normal` records were removed.

## ML Verification

All three group-meter assets have active EnPI baselines and forecast rows:

| Group | Training samples | R-squared |
|---|---:|---:|
| Bret | 395 | 0.8487 |
| Raster | 395 | 0.8380 |
| Dimeco | 382 | 0.7392 |

## OVOS Verification

- OVOS health: healthy.
- Messagebus: connected.
- Dedicated `PartnerPress` Adapt intent registered.
- Optional local LLM absence is treated as a warning; verified partner queries
  do not depend on it.
- Invalid optional OCP/CommonQA pipeline stages were removed from the runtime
  pipeline configuration.
- Full final suite: **40/40 passed** on the rebuilt image.
- Final suite response time: approximately 0.2 to 0.7 seconds per normal query.

See [ASSA-ABLOY-OVOS-DEMO-QUERIES.md](ASSA-ABLOY-OVOS-DEMO-QUERIES.md).

## Reproduction

```bash
python3 scripts/import_partner_press_data.py --json

python3 scripts/import_partner_press_data.py \
  --package data/raw/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip \
  --apply

curl -sS \
  'http://localhost:8001/api/v1/partner-press/summary?question_type=data_inventory'

curl -sS -X POST http://localhost:5000/query \
  -H 'Content-Type: application/json' \
  -d '{"text":"How many readings and rows were imported for ASSA ABLOY?"}'
```

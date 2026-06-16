# Partner Press-Shop Data Ingestion

This is a local-lab ingestion path for the partner press-shop package received
on 2026-06-10. It must not be run against production.

## Scope

The partner data is represented honestly:

- Energy is imported for the three meter groups: Bret, Raster, and Dimeco.
- The separate Bret transformer workbook is retained as an auxiliary reference
  meter and is excluded from press-group energy totals and SEC calculations.
- Press-level energy is not invented.
- SQDC production is imported per press.
- Derived group production is also materialized for the three meter-group assets
  so existing EnMS SEC, dashboard, and OVOS ranking queries can work at the same
  group level as the available energy meters.

## Source Package

Default local-lab package path:

```bash
data/raw/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip
```

Expected contents:

```text
SQDC.mai2025-mai2026.xlsx
Bret presses.zip
Raster presses.zip
Dimeco.zip
```

Keep these raw files outside Git.

## Mapping

Meter groups:

```text
Bret   -> Bret Presses Meter Group
Raster -> Raster Presses Meter Group
Dimeco -> Dimeco Presses Meter Group
```

Press mapping:

```text
Bret:   Bret125-1, Bret160-1, Bret250-1, Bret250-2
Raster: Rast160-1, Rast125-1, Rast250-1, Rast250-2
Dimeco: Dimeco80-1, Dimeco80-2, Flexi-1, Schu80-1, Rast125-2
```

SQDC production quantity uses column H (`LIBRE1`) as stated in the partner
email. The importer aggregates duplicate SQDC rows to one daily row per press.

The Bret archive also contains a separate March 2026 hourly transformer file
for `Statia TRAFO-TRAFO 3`. The importer includes it by default as
`Bret Transformer Meter (TRAFO 3)`, with scope
`upstream_reference_not_in_group_totals`. To omit that reference series, pass
`--exclude-bret-transformer`.

## Local Simulator Bypass

Run the local lab stack with the partner override:

```bash
docker compose -f docker-compose.yml -f docker-compose.partner-press.yml up -d
```

The override keeps the simulator service present but prevents it from
auto-starting synthetic data generation:

```text
SIMULATOR_AUTO_START=false
SIMULATOR_ENABLE_ANOMALIES=false
```

The same override also sets the partner lab profile and OVOS bridge target for
analytics:

```text
PARTNER_PRESS_FACTORY_NAME=Partner Press Shop
PARTNER_PRESS_DISPLAY_NAME=ASSA ABLOY Partner Press Shop
PARTNER_PRESS_START=2025-05-01T00:00:00
PARTNER_PRESS_END=2026-06-01T00:00:00
PARTNER_PRESS_SOURCE_DATASET=partner_press_shop_2026_06_10
OVOS_BRIDGE_HOST=ovos-enms
OVOS_BRIDGE_PORT=5000
```

Do not use this override for production deployment.

## Dry Run

Profile the package without touching the database:

```bash
python3 scripts/import_partner_press_data.py \
  --package data/raw/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip
```

Machine-readable profile:

```bash
python3 scripts/import_partner_press_data.py \
  --package data/raw/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip \
  --json
```

## Apply Import

On the local lab with PostgreSQL running:

```bash
python3 scripts/import_partner_press_data.py \
  --package data/raw/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip \
  --apply
```

The import is idempotent. It uses deterministic UUIDs and `ON CONFLICT`
upserts for:

- `factories`
- `machines`
- `seus`
- `energy_readings`
- `production_data`
- `machine_status`

It refreshes Timescale continuous aggregates for the partner date range unless
`--no-refresh-aggregates` is passed.

## Expected Data Profile

Default full import:

```text
Partner machines: 17
Energy rows: 1,978
  Group-meter rows: 1,235
  Auxiliary transformer rows: 743
Production rows: 6,336
Energy period: 2025-04-01 through 2026-05-31
Production period: 2025-05-01 through 2026-05-31
```

Energy totals:

```text
Bret:   42,818.125 kWh
Raster: 45,598.376 kWh
Dimeco: 59,661.969 kWh
```

Auxiliary reference total, excluded from the totals above:

```text
Bret Transformer Meter (TRAFO 3): 263,999.155 kWh
2026-03-01 00:00 through 2026-03-31 23:00 source wall time
```

The dev pilot analytics profile uses `2025-05-01T00:00:00` through
`2026-06-01T00:00:00`, matching the partner May 2025 through May 2026 scope and
excluding April energy rows present in the Bret/Raster exports. In that
benchmark KPI period the group-meter energy totals are:

```text
Bret:   39,611.06 kWh
Raster: 41,981.81 kWh
Dimeco: 59,661.97 kWh
Total: 141,254.85 kWh
```

Derived group production totals:

```text
Bret Presses Meter Group:    7,797,167 units
Raster Presses Meter Group:  7,756,785 units
Dimeco Presses Meter Group: 12,071,713 units
```

The SQDC source contains net quantity corrections in `LIBRE1`. The importer
preserves the 13 negative daily net adjustments. The source does not contain
good/bad quality classifications, so `production_count_good`,
`production_count_bad`, and `quality_score` remain null.

`Rast125-2` is intentionally mapped to the Dimeco physical group in the
partner mapping, despite the `Rast` prefix.

## Validation Queries

Database checks:

```bash
docker compose exec postgres psql -U raptorblingx -d enms -c "
SELECT m.name, SUM(er.energy_kwh) AS kwh
FROM energy_readings er
JOIN machines m ON m.id = er.machine_id
WHERE er.source = 'partner_import'
GROUP BY m.name
ORDER BY kwh DESC;"
```

```bash
docker compose exec postgres psql -U raptorblingx -d enms -c "
SELECT m.name, SUM(pd.production_count) AS units
FROM production_data pd
JOIN machines m ON m.id = pd.machine_id
WHERE pd.metadata->>'source_dataset' = 'partner_press_shop_2026_06_10'
GROUP BY m.name
ORDER BY units DESC;"
```

OVOS/API ranking check:

```bash
curl "http://localhost:8001/api/v1/ovos/top-consumers?metric=energy&factory_name=Partner%20Press%20Shop&start_time=2025-05-01T00:00:00Z&end_time=2026-06-01T00:00:00Z&limit=3"
```

Partner profile API checks:

```bash
curl "http://localhost:8001/api/v1/partner-press/profile"
curl "http://localhost:8001/api/v1/partner-press/summary?question_type=kpis"
curl "http://localhost:8080/api/analytics/api/v1/partner-press/summary?question_type=top_energy"
```

OVOS runtime checks:

```bash
cd /home/ubuntu/ovos-llm
docker compose up -d
curl "http://localhost:5000/health"
curl "http://localhost:8080/api/ovos/voice/health"
```

OVOS voice checks:

```bash
curl -s -X POST "http://localhost:8001/api/v1/ovos/voice/query" \
  -H "Content-Type: application/json" \
  -d '{"text":"What are the top energy consumers in the ASSA ABLOY press shop?","include_audio":false}'
```

Direct bridge check, matching the OVOS skill development guide:

```bash
curl -s -X POST "http://localhost:5000/query" \
  -H "Content-Type: application/json" \
  -d '{"text":"Show KPIs for the partner press shop"}'
```

Useful partner questions:

```text
What are the top energy consumers in the ASSA ABLOY press shop?
How much energy did the Bret press group use?
Compare Bret, Raster, and Dimeco energy consumption.
What was the production quantity for Bret presses?
Show KPIs for the partner press shop.
What is the SEC for Bret group?
Production quantity for Raster160
How many parts did Dimeco80-1 produce?
Energy consumption of Bret125-1
How much energy did the press shop use in March 2026?
Latest energy for the partner press shop
```

Expected behavior:

- Press-shop energy answers use only the three meter-group assets.
- Press production answers use SQDC press-level production.
- Per-press energy questions should explicitly say that per-press energy is not
  available instead of allocating group energy to a press.
- `today`, `current`, `live`, or `latest` partner questions should explain that
  the package is historical and ends on `2026-05-31`.
- Unknown press names should list the known imported presses and keep energy at
  group level.

## Dev Service Health Notes

The partner pilot flow depends on PostgreSQL, analytics, nginx, Grafana, and the
separate `ovos-enms` runtime. On the current dev stack:

- `auth-service` may report unhealthy even while the public dev portal and
  partner analytics are reachable. Check it separately if login/admin flows are
  required.
- `query-service` is a placeholder service and can report unhealthy because its
  image lacks the `curl` binary used by the healthcheck. It is not part of the
  partner press-shop analytics or OVOS path.

Grafana:

- Select factory `Partner Press Shop`.
- Use the time range `2025-05-01 00:00` to `2026-06-01 00:00`.
- Energy dashboards should show the three meter-group assets.
- Production dashboards should show individual presses and the three derived
  meter-group production assets.

## Limitations

- Energy is daily for most meter files, not real-time interval data.
- The dataset ends on 2026-05-31, so default "today" views on 2026-06-10 will
  not show partner activity unless the dashboard/API time range is changed.
- The importer does not allocate group energy to individual presses.
- `Rast250-1` has zero production in SQDC column H for the imported period.

## Presentation Evidence

- [ASSA ABLOY data verification](ASSA-ABLOY-DATA-VERIFICATION.md)
- [ASSA ABLOY OVOS demo queries](ASSA-ABLOY-OVOS-DEMO-QUERIES.md)

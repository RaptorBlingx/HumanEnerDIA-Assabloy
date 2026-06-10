# ASSA ABLOY Partner Press Shop Pilot Operations

This dev-only pilot uses the imported partner press-shop package for the
`Partner Press Shop` factory. Production files remain private and are not stored
in Git.

## Scope

- Factory display name: `ASSA ABLOY Partner Press Shop`
- Data period: `2025-05-01` to `2026-06-01`
- Energy assets: `Bret Presses Meter Group`, `Raster Presses Meter Group`,
  `Dimeco Presses Meter Group`
- Production assets: individual presses from SQDC

Energy is only modeled at the three meter-group assets. The system must not
allocate or invent per-press energy.

## Dev URLs

- Portal: `http://10.33.10.103:8080/`
- Reports: `http://10.33.10.103:8080/reports.html`
- Analytics UI: `http://10.33.10.103:8080/api/analytics/ui/`
- Baseline UI: `http://10.33.10.103:8080/api/analytics/ui/baseline`
- Forecast UI: `http://10.33.10.103:8080/api/analytics/ui/forecast`
- Grafana: `http://10.33.10.103:3001/`

Mock pilot login:

- Username: `assaabloy`
- Password: `assaabloy`

## Partner Profile APIs

```bash
curl http://localhost:8080/api/analytics/api/v1/partner-press/profile
curl http://localhost:8080/api/analytics/api/v1/partner-press/summary?question_type=kpis
curl http://localhost:8080/api/analytics/api/v1/partner-press/ml-readiness
```

## ML Readiness and Training

The forecast table must exist before forecast predictions can be saved:

```bash
docker exec -i enms-postgres psql -U raptorblingx -d enms < database/init/12-forecast-predictions.sql
```

Train partner baselines and ARIMA forecasts:

```bash
curl -X POST \
  'http://localhost:8080/api/analytics/api/v1/partner-press/train-ml?train_baselines=true&train_arima=true&train_prophet=false'
```

Generate persisted short-horizon forecast rows:

```bash
for id in \
  2577243a-7fca-598a-92ef-62dd7399ca98 \
  8e130514-b24f-56dd-a1ab-792d680e53a8 \
  2b4a1841-d774-57ac-a42a-2b7fcae7bd0d
do
  curl -X POST http://localhost:8080/api/analytics/api/v1/forecast/predict \
    -H 'Content-Type: application/json' \
    -d "{\"machine_id\":\"$id\",\"horizon\":\"short\",\"periods\":16}"
done
```

The partner baseline models train successfully but are below the default R2
quality threshold because the package contains daily group-meter energy and
production, not richer drivers such as live status, environmental variables, or
shift-level process parameters.

Prophet medium/long forecasting is currently blocked by the container Prophet
backend error: `'Prophet' object has no attribute 'stan_backend'`. Use the
working ARIMA short-horizon forecast until the Prophet/CmdStan image dependency
is repaired.

## Reports

The V2 PDF report works with the partner factory:

```bash
curl -X POST http://localhost:8080/api/analytics/api/v1/reports/v2/generate \
  -H 'Content-Type: application/json' \
  -d '{"factory_id":"52f9e235-4ef2-5a1b-a302-5db5a06420fc","year":2026,"month":5}'
```

The report data fetcher uses aggregate `total_energy_kwh` values, not a power
proxy, so report totals align with imported meter data.

## Simulator Boundary

The partner override keeps simulator generation disabled. A no-data simulator
placeholder container may run so nginx can resolve its historical upstream; it
does not generate or import simulator readings.

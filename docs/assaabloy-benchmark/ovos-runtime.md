# OVOS Runtime For ASSA ABLOY Benchmark

The HumanEnerDIA repository contains the analytics proxy and browser widget for OVOS. The actual OVOS runtime and EnMS skill are maintained in the separate `ovos-llm` repository.

## Required OVOS Branch

Use the partner-capable OVOS branch:

```bash
git clone -b romania/stt-report-experiments https://github.com/RaptorBlingx/ovos-llm.git ../ovos-llm
```

If the repository already exists:

```bash
cd ../ovos-llm
git fetch --all
git switch romania/stt-report-experiments
git pull --ff-only
```

## Start Order

Start the HumanEnerDIA ASSA ABLOY lab stack first:

```bash
cd HumanEnerDIA-Assabloy
scripts/lab/bootstrap_assaabloy_lab.sh
```

Then start OVOS:

```bash
cd ../ovos-llm
ENMS_API_URL=http://enms-analytics:8001/api/v1 \
PARTNER_PRESS_PILOT_DEFAULT=true \
docker compose up -d --build
```

The OVOS compose file joins the existing `enms-network`, so it must be started after the HumanEnerDIA stack has created that Docker network.

## Health Checks

Direct OVOS REST bridge:

```bash
curl -fsS http://localhost:5000/health
```

HumanEnerDIA OVOS proxy:

```bash
curl -fsS http://localhost:8080/api/analytics/api/v1/ovos/voice/health
```

Strict platform + OVOS verification:

```bash
cd HumanEnerDIA-Assabloy
scripts/lab/verify_assaabloy_lab.sh --require-ovos
```

## Test Partner Query

```bash
curl -sS -X POST http://localhost:5000/query \
  -H 'Content-Type: application/json' \
  -d '{"text":"Show KPIs for the ASSA ABLOY partner press shop"}'
```

Expected response includes:

- `141,254.85 kWh`
- `27,625,665 units`
- Bret, Raster, and Dimeco SEC values

## Logs

```bash
docker exec ovos-enms tail -80 /var/log/ovos/skills.out.log
```

The expected structured partner intent is:

```text
partner_press_pilot
```

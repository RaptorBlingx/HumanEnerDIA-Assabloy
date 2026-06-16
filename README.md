# HumanEnerDIA ASSA ABLOY Lab

This repository is an isolated HumanEnerDIA lab package for the real ASSA ABLOY partner press-shop benchmark. It is intended for local Ubuntu deployment and A/B measurement of HumanEnerDIA without assistant support versus HumanEnerDIA with OVOS and chatbot support.

The live production server at `https://assaabloy.intel50001.com/` must not be used for this benchmark. Use this repository on a separate Ubuntu machine or local Ubuntu laptop.

## What This Repository Contains

- HumanEnerDIA platform services: portal, analytics, reports, Grafana, Rasa chatbot, PostgreSQL/TimescaleDB, Redis, MQTT, Node-RED.
- ASSA ABLOY partner press-shop ingestion and API routes.
- Partner-specific Docker Compose override: `docker-compose.partner-press.yml`.
- Chrome measurement extension: `pilot-measurement-extension/`.
- A/B benchmark protocol: `docs/assaabloy-benchmark/`.
- Lab bootstrap and verification scripts: `scripts/lab/`.

The raw partner attachment is private and is not committed to Git.

## Required Machine

- Ubuntu 22.04 or newer recommended.
- Docker Engine and Docker Compose v2.
- Python 3.
- At least 8 GB RAM recommended.
- Free ports: `8080`, `8443`, `5433`, `3001`, `1881`, `8001`, `8002`, `5005`, `5006`, `6380`.

Do not run this stack beside another HumanEnerDIA stack on the same Docker host unless ports and container names are isolated.

The lab compose file uses fixed container names such as `enms-mqtt`, `enms-postgres`, and `enms-nginx`. If another local EnMS/HumanEnerDIA stack is already present, stop or remove it before bootstrapping this lab.

## Install

Clone the new repository:

```bash
git clone git@github.com:RaptorBlingx/HumanEnerDIA-Assabloy.git
cd HumanEnerDIA-Assabloy
```

Prepare the environment:

```bash
cp .env.assaabloy.example .env
```

Place the private partner ZIP here:

```text
data/raw/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip
```

Alternative:

```bash
export ASSAABLOY_PACKAGE=/absolute/path/to/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip
```

Start the lab, import the data, train partner baselines, and verify the platform:

```bash
scripts/lab/bootstrap_assaabloy_lab.sh
```

If Docker reports a container-name conflict such as `/enms-mqtt is already in use`, remove the old local lab containers first:

```bash
docker rm -f enms-nginx enms-postgres enms-mqtt enms-redis enms-simulator enms-nodered enms-grafana enms-analytics enms-query-service enms-auth-service enms-rasa-actions enms-rasa enms-chatbot
```

Then rerun the bootstrap script. Use this only on the isolated local benchmark machine, not on a production or shared server.

## Open The Lab

- Portal: `http://localhost:8080/`
- Reports: `http://localhost:8080/reports.html`
- Analytics UI: `http://localhost:8080/api/analytics/ui/`
- Grafana: `http://localhost:8080/grafana`
- Analytics API docs: `http://localhost:8080/api/analytics/docs`

Partner pilot login:

```text
Username: assaabloy
Password: assaabloy
```

## Start OVOS For Condition B

The OVOS runtime is a separate repository. Start it after the HumanEnerDIA lab stack is running:

```bash
git clone -b romania/stt-report-experiments https://github.com/RaptorBlingx/ovos-llm.git ../ovos-llm
cd ../ovos-llm
ENMS_API_URL=http://enms-analytics:8001/api/v1 \
PARTNER_PRESS_PILOT_DEFAULT=true \
docker compose up -d --build
```

Verify strict platform + OVOS readiness:

```bash
cd ../HumanEnerDIA-Assabloy
scripts/lab/verify_assaabloy_lab.sh --require-ovos
```

More details: [docs/assaabloy-benchmark/ovos-runtime.md](docs/assaabloy-benchmark/ovos-runtime.md).

## Install Measurement Extension

1. Open Chrome.
2. Go to `chrome://extensions`.
3. Enable `Developer mode`.
4. Click `Load unpacked`.
5. Select:

```text
HumanEnerDIA-Assabloy/pilot-measurement-extension
```

The overlay appears on supported pages:

- `http://localhost/*`
- `http://127.0.0.1/*`
- `http://10.33.10.103/*`

The extension task list is ASSA ABLOY-specific.

## Run The A/B Benchmark

Use the fixed task set:

- [docs/assaabloy-benchmark/task-set.md](docs/assaabloy-benchmark/task-set.md)
- [docs/assaabloy-benchmark/manual-paths.md](docs/assaabloy-benchmark/manual-paths.md)
- [docs/assaabloy-benchmark/expected-answers.md](docs/assaabloy-benchmark/expected-answers.md)
- [docs/assaabloy-benchmark/measurement-protocol.md](docs/assaabloy-benchmark/measurement-protocol.md)

After exporting the raw CSV from the extension, summarize KPI results:

```bash
scripts/lab/summarize_ab_results.py evidence/measurements/raw-extension-export.csv
```

The script writes:

```text
evidence/measurements/assaabloy-kpi-summary.csv
```

## Verified Partner Facts

- Total group-meter energy: `141,254.85 kWh`.
- Total group production: `27,625,665 units`.
- Bret energy: `39,611.06 kWh`.
- Raster energy: `41,981.81 kWh`.
- Dimeco energy: `59,661.97 kWh`.
- Imported energy rows: `1,978`.
- Materialized production rows: `6,336`.
- Active partner baselines: `3 of 3`.
- Bret transformer reference: `263,999.16 kWh`, excluded from KPI totals.

## Stop The Lab

```bash
docker compose -f docker-compose.yml -f docker-compose.partner-press.yml down
```

To remove local database volumes:

```bash
docker compose -f docker-compose.yml -f docker-compose.partner-press.yml down -v
```

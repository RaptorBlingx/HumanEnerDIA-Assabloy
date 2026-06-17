# HumanEnerDIA ASSA ABLOY KPI Comparison Card Generator

Standalone evidence-card generator for the ASSA ABLOY real-partner HumanEnerDIA benchmark.

Use this app after collecting the A/B measurements. Enter the measured values from the pilot measurement extension, calculate the KPI reductions, and export PNG comparison cards for reporting or presentation material.

## What It Generates

- One comparison card per ASSA ABLOY benchmark task: `O1` to `O4`, `T1` to `T4`
- Operational subtotal card for the `30%` effort-reduction KPI
- Technical subtotal card for the `25%` intervention / effort-reduction KPI
- Final KPI summary card with DIA module coverage: Monitoring, Analyses, Documentation
- Copyable overlay / voiceover text for each card
- Downloadable JSON backup of entered values

## Inputs

For each task, enter:

- Condition A time in seconds
- Condition B time in seconds
- Condition A clicks and screens
- Condition B clicks and screens

Default flags follow the ASSA ABLOY benchmark design:

- Condition A: `Expert help = 0`, `Manual reasoning = 1`, `Success = 1`
- Condition B: `Expert help = 0`, `Manual reasoning = 0`, `Success = 1`

You can change the flags if a recorded clip is different.

## Calculation Logic

Per task:

- `time reduction = (A time - B time) / A time`
- `click reduction = (A clicks - B clicks) / A clicks`
- `screen reduction = (A screens - B screens) / A screens`
- `interaction reduction = average(click reduction, screen reduction)`
- `measured effort reduction = average(time reduction, interaction reduction)`

Subtotal cards average the measured effort reductions for the relevant task group.

## Run On Ubuntu

Prerequisites:

- Docker Engine with the Docker Compose plugin
- Git, if you want to clone from the repository

Run only this app from a cloned repository:

```bash
cd ~/HumanEnerDIA-Assabloy/pilot-measurement
docker compose up -d --build
```

Open:

```text
http://localhost:8095
```

Stop it:

```bash
cd ~/HumanEnerDIA-Assabloy/pilot-measurement
docker compose down
```

Use another port if `8095` is busy:

```bash
PILOT_MEASUREMENT_PORT=8096 docker compose up -d --build
```

Check that the container is reachable:

```bash
curl http://localhost:8095/health
```

## Run On Windows 11

Prerequisites:

- Docker Desktop
- Git, if you want to clone from the repository

```powershell
cd HumanEnerDIA-Assabloy\pilot-measurement
docker compose up -d --build
```

## Sparse Clone Option

If you want only this mini project instead of the whole working tree:

```powershell
git clone --filter=blob:none --sparse git@github.com:RaptorBlingx/HumanEnerDIA-Assabloy.git HumanEnerDIA-Assabloy-tools
cd HumanEnerDIA-Assabloy-tools
git sparse-checkout set pilot-measurement docs/assaabloy-benchmark
cd pilot-measurement
docker compose up -d --build
```

## Evidence Card Workflow

1. Open `http://localhost:8095`.
2. Select the task, for example `O1`.
3. Enter the measured A/B time, clicks, and screens from the recorded clips.
4. Keep the default Expert / Manual reasoning / Success flags unless the clip evidence says otherwise.
5. Click `Save Values`.
6. Click `Export PNG Card`.
7. Insert the exported card into the benchmark evidence material.
8. Repeat for all tasks.
9. Export the `Operational`, `Technical`, and `Final KPI` cards for the end of the video.

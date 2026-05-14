# HumanEnerDIA Pilot Measurement

Standalone manual measurement app for the simulated WASABI / HumanEnerDIA pilot videos.

For the official recording, prefer the Chrome extension in `pilot-measurement-extension/` because it can automatically count clicks and browser screen changes inside HumanEnerDIA and Grafana. This Docker app is useful as a fallback control panel, but it cannot automatically observe clicks outside its own page.

It runs by itself and does not start the full HumanEnerDIA stack. Use it when the official task flow moves through Grafana, reports, browser tabs, or any page where the in-platform recorder is not available.

## What It Measures

- Task completion time
- Click count
- Screen/dashboard/page count
- Expert help flag
- Manual reasoning flag
- Success flag
- Raw trial rows
- Per-task A/B KPI summary

Important limitation: because this is a Dockerized browser app, it cannot automatically observe clicks in other Windows applications or other browser tabs. Use the `+Click` and `+Screen` controls while you perform the task. This keeps the measurement consistent without needing OS-level monitoring software.

## Run On Windows 11

Prerequisites:

- Docker Desktop
- Git, if you want to clone from the repository

Run only this app from a cloned repository:

```powershell
cd HumanEnerDIA\pilot-measurement
docker compose up -d --build
```

Open:

```text
http://localhost:8095
```

Stop it:

```powershell
cd HumanEnerDIA\pilot-measurement
docker compose down
```

Use another port if `8095` is busy:

```powershell
$env:PILOT_MEASUREMENT_PORT = "8096"
docker compose up -d --build
```

## Sparse Clone Option

If you want only this mini project instead of the whole working tree:

```powershell
git clone --filter=blob:none --sparse git@github.com:RaptorBlingx/HumanEnerDIA.git HumanEnerDIA-pilot-tools
cd HumanEnerDIA-pilot-tools
git sparse-checkout set pilot-measurement docs/simulated-pilot
cd pilot-measurement
docker compose up -d --build
```

## Recording Workflow

1. Open `http://localhost:8095`.
2. Put the measurement app beside HumanEnerDIA/Grafana, or on a second screen.
3. Start the screen recorder.
4. Select `Condition A` or `Condition B`.
5. Select the task.
6. Click `Start Task` immediately before the first action.
7. Click `+Click` for each task click performed outside the measurement app.
8. Click `+Screen` for each meaningful page, dashboard, tab, report, or result-screen change.
9. Set `Expert`, `Manual reasoning`, and `Success` before stopping if the default is not correct.
10. Click `Answer Found` when the required answer is visible, or when OVOS voice playback finishes in Condition B.
11. Repeat for all tasks.
12. Export `Raw CSV` for evidence and `KPI Summary CSV` for the comparison table.

## Recommended Defaults

Condition A:

- `Manual reasoning`: checked
- `Expert`: unchecked
- `Success`: checked if the answer is visible
- Start timer before manual navigation
- Stop timer when the answer is visibly found

Condition B:

- `Manual reasoning`: unchecked unless you manually inspect dashboards after the assistant answer
- `Expert`: unchecked
- `Success`: checked if the answer/download is correct
- Start timer when you begin saying `Jarvis`
- Stop timer when the spoken answer finishes, or when the chatbot answer is visible

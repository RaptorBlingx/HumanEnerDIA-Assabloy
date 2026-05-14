# Standalone Pilot Measurement App

Use the standalone app when you want the measurement tool to run outside HumanEnerDIA, for example on a Windows 11 laptop beside Grafana, reports, OVOS, or the chatbot.

Project path:

```text
pilot-measurement/
```

## What It Solves

- It runs without the full HumanEnerDIA Docker stack.
- It gives one separate measurement control screen for both Condition A and Condition B.
- It records the same official task IDs: `O1`, `O2`, `O3`, `O4`, `T1`, `T2`, `T3`, `T4`.
- It exports raw evidence rows and a per-task KPI summary CSV.

Important limitation: the app is Dockerized and browser-based, so it cannot automatically see clicks inside other browser tabs, Grafana, OVOS, or Windows applications. Use `+Click` and `+Screen` manually while recording. This is still objective if the same rule is applied to Condition A and Condition B.

## Install And Run On Windows 11

Install prerequisites:

- Docker Desktop
- Git

Run only the mini app from the repository:

```powershell
cd HumanEnerDIA\pilot-measurement
docker compose up -d --build
```

Open:

```text
http://localhost:8095
```

Stop:

```powershell
docker compose down
```

Use a different port if needed:

```powershell
$env:PILOT_MEASUREMENT_PORT = "8096"
docker compose up -d --build
```

## Sparse Clone Option

To clone only the mini app and simulated-pilot docs:

```powershell
git clone --filter=blob:none --sparse git@github.com:RaptorBlingx/HumanEnerDIA.git HumanEnerDIA-pilot-tools
cd HumanEnerDIA-pilot-tools
git sparse-checkout set pilot-measurement docs/simulated-pilot
cd pilot-measurement
docker compose up -d --build
```

## How To Use During Recording

1. Open `http://localhost:8095`.
2. Put it beside the HumanEnerDIA/Grafana browser, or on a second monitor.
3. Start the screen recorder.
4. Select the condition and task.
5. Click `Start Task` immediately before the first task action.
6. Click `+Click` for each click performed in HumanEnerDIA, Grafana, OVOS, chatbot, or reports.
7. Click `+Screen` for each meaningful page, dashboard, result, or report screen change.
8. Set `Expert`, `Manual reasoning`, and `Success` before saving the task if the defaults are not correct.
9. Click `Answer Found` when the required result is visible. For OVOS voice tasks, click it when the spoken answer finishes.
10. Export `Raw CSV` and `KPI Summary CSV` after the run.

## Condition Defaults

Condition A:

- `Manual reasoning`: checked.
- `Expert`: unchecked unless a human expert is genuinely required.
- `Success`: checked only when the answer is visibly found.
- Start when manual navigation begins.
- Stop when the target answer is visible.

Condition B:

- `Manual reasoning`: unchecked unless you still need manual dashboard/API reasoning after assistant support.
- `Expert`: unchecked unless a human expert is genuinely required.
- `Success`: checked only when the assistant result is correct.
- Start when you begin saying `Jarvis` or submit the chatbot prompt.
- Stop when OVOS voice playback finishes, the chatbot answer appears, or the report download starts.


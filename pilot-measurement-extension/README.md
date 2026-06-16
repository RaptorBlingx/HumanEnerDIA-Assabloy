# HumanEnerDIA ASSA ABLOY Measurement Extension

This Chrome extension records browser-based task measurements for the ASSA ABLOY A/B benchmark.

It records:

- elapsed task time
- click count
- screen count
- task ID, trial, condition, persona, and module
- expert-help flag
- manual-reasoning flag
- success flag

## Supported Pages

- `http://localhost/*`
- `http://127.0.0.1/*`
- `http://10.33.10.103/*`

For the local ASSA ABLOY lab, use `http://localhost:8080/`.

## Install

1. Open Chrome.
2. Go to `chrome://extensions`.
3. Enable `Developer mode`.
4. Click `Load unpacked`.
5. Select this folder:

```text
HumanEnerDIA-Assabloy/pilot-measurement-extension
```

After pulling repository updates, reload the extension from `chrome://extensions` and refresh all open HumanEnerDIA tabs.

## Benchmark Workflow

1. Open `http://localhost:8080/`.
2. Select the benchmark task in the overlay.
3. Select the condition:
   - `A - Manual` for HumanEnerDIA without OVOS/chatbot.
   - `B - Assistant` for HumanEnerDIA with OVOS/chatbot.
4. Set the trial number.
5. Use default flags unless the task result requires a correction:
   - Condition A: `Manual` checked.
   - Condition B: `Manual` unchecked when the assistant gives the answer directly.
   - `Expert` unchecked unless human expert help was required.
   - `Success` checked only when the answer matches `docs/assaabloy-benchmark/expected-answers.md`.
6. Click `Start Task` immediately before the first manual action in Condition A.
7. For single-prompt OVOS tasks in Condition B, keep `Auto` checked.
8. For chatbot tasks, the timer starts automatically when typing begins in the chat input.
9. For multi-prompt Condition B tasks, uncheck `Auto`, perform all prompts, then click `Answer Found` manually after the final response.
10. Export `Copy Raw` after the run and save it under `evidence/measurements/`.

## Screen Counting

The extension automatically counts URL/history/hash navigation. Grafana redirects such as `/grafana/d/...` to `/grafana/d/...?orgId=...&refresh=...` are normalized so they count as one screen.

Use `+Screen` only when a meaningful screen changes without URL navigation.

## Reset Controls

- `Reset Current`: clears the active timer/counters without deleting saved records.
- `Delete Last Try`: removes the latest saved task record.
- `Reset All`: clears all saved records and current counters.
- `Reset Overlay Position`: available in the extension popup if the overlay is moved off screen.

## Keyboard Shortcuts

- `Alt+Shift+S`: start selected task.
- `Alt+Shift+A`: answer found / stop task.
- `Alt+Shift+X`: add one screen.

Chrome shortcuts can be changed at:

```text
chrome://extensions/shortcuts
```

## Export

Use:

- `Copy Raw`: raw task records.
- `Copy KPI`: per-task A/B median summary.
- `JSON`: raw record backup.

Then run:

```bash
scripts/lab/summarize_ab_results.py evidence/measurements/raw-extension-export.csv
```

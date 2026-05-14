# HumanEnerDIA Pilot Measurement Chrome Extension

This is the preferred measurement tool for the simulated pilot recordings. It is a local Chrome extension that automatically counts clicks and browser screen changes across HumanEnerDIA, Grafana, reports, OVOS, and chatbot pages.

## Why This Instead Of The Docker App

The Docker app cannot observe browser clicks outside its own page. A Chrome extension can run inside the HumanEnerDIA and Grafana browser tabs, so it can automatically count:

- task time
- clicks in the page
- URL/history/hash navigation as screen changes
- the selected task, trial, condition, expert flag, manual reasoning flag, and success flag
- HumanEnerDIA assistant timing events for single-prompt OVOS/chatbot tasks

Limitations:

- It measures browser activity only.
- It cannot see clicks in non-browser desktop applications.
- Some UI changes that do not change URL or history may still need the `+Screen` correction button.

For this pilot, the extension is the best option because the official A/B flow is browser-based.

## Install On Windows 11

1. Clone or update the repository.
2. Open Chrome.
3. Go to:

```text
chrome://extensions
```

4. Enable `Developer mode`.
5. Click `Load unpacked`.
6. Select this folder:

```text
HumanEnerDIA\pilot-measurement-extension
```

7. Open HumanEnerDIA:

```text
http://10.33.10.103:8080/index.html
```

8. Confirm the `Pilot Measurement` overlay appears on the page.

## Supported Pages

The extension is enabled on:

- `http://10.33.10.103/*`
- `http://localhost/*`
- `http://127.0.0.1/*`

This includes HumanEnerDIA and Grafana at `http://10.33.10.103:8080/...`.

## Recording Workflow

1. Start the screen recorder.
2. Select `Condition A` or `Condition B`.
3. Select the task and trial.
4. Set flags:
   - Condition A: `Manual reasoning` should normally be checked.
   - Condition B: `Manual reasoning` should normally be unchecked.
   - `Auto` should stay checked for single-prompt assistant tasks.
   - `Auto` should be unchecked for multi-prompt assistant tasks.
   - `Expert` should stay unchecked unless you genuinely need human expert help.
   - `Success` should stay checked only if the result is correct.
5. Click `Start Task` immediately before the first task action.
6. Perform the task normally in HumanEnerDIA, Grafana, OVOS, or chatbot.
7. Clicks are counted automatically.
8. URL/history/hash changes are counted automatically as screens.
9. Use `+Screen` only when a meaningful visual screen changes without a URL change.
10. Click `Answer Found` when the target answer is visible. For single-prompt assistant tasks, the extension can stop automatically when the HumanEnerDIA assistant completion event fires. For multi-prompt tasks, keep `Auto` unchecked and stop manually after the final response.
11. Repeat for all tasks.
12. Export `Raw CSV` and `KPI Summary CSV`.

## Keyboard Shortcuts

- `Alt+Shift+S`: start selected task
- `Alt+Shift+A`: answer found / stop task
- `Alt+Shift+X`: add one screen

Chrome may require you to confirm or change shortcuts at:

```text
chrome://extensions/shortcuts
```

## Export

Use the overlay or extension popup:

- `Copy Raw CSV`: evidence rows for every recorded trial
- `Copy KPI CSV`: per-task A/B median summary
- `Download JSON`: backup of the raw records

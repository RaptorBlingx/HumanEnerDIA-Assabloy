# Browser Extension Pilot Measurement

Use the Chrome extension for the official simulated-pilot recordings when automatic browser click and screen counting is required.

Project path:

```text
pilot-measurement-extension/
```

## Why This Is The Preferred Tool

The official A/B scenario is browser-based: HumanEnerDIA, Grafana, reports, OVOS, and the chatbot are all used through Chrome. A Chrome extension can inject the recorder into those pages and count browser activity automatically.

What it counts automatically:

- task time
- clicks inside HumanEnerDIA/Grafana/browser pages
- screen changes caused by full page navigation
- screen changes caused by SPA history navigation
- screen changes caused by hash changes
- HumanEnerDIA assistant timing events for single-prompt OVOS/chatbot tasks
- Grafana dashboard redirects are normalized so a quick `/grafana/d/...` to `/grafana/d/...?orgId=...&refresh=...` redirect counts as one screen

## Where Data Is Saved

When you click `Answer Found`, the extension saves the trial into Chrome extension local storage under key:

```text
humanenerdia_pilot_extension_state_v1
```

The saved rows are inside the `records` array in that local extension state. This data is local to the Chrome profile and the installed extension. It is not saved to HumanEnerDIA, Docker, PostgreSQL, Grafana, or Git.

Use `Copy Raw`, `Copy KPI`, or `JSON` export before clicking `Reset All`, clearing Chrome extension storage, removing the extension, or switching Chrome profiles.

What still needs manual correction:

- a meaningful visual screen change that does not change URL/history/hash
- any click performed outside Chrome

For the official experiment, this is better than a desktop app because it is easier to install, has lower security risk, and directly measures the browser workflow we are demonstrating.

## Install On Windows 11

1. Open Chrome.
2. Go to:

```text
chrome://extensions
```

3. Enable `Developer mode`.
4. Click `Load unpacked`.
5. Select:

```text
HumanEnerDIA\pilot-measurement-extension
```

6. Open:

```text
http://10.33.10.103:8080/index.html
```

7. Confirm the `Pilot Measurement` overlay appears in the bottom-right of the page.

After `git pull`, go back to `chrome://extensions` and click reload on `HumanEnerDIA Pilot Measurement` so Chrome loads the updated extension files.

## Official Recording Use

1. Start the screen recorder.
2. Select the condition, task, and trial in the overlay.
3. Click `Start Task` immediately before the first task action.
4. Perform the task normally.
5. Let the extension count clicks automatically.
6. Let the extension count URL/history/hash screen changes automatically.
7. Use `+Screen` only when the screen visibly changes but the URL does not.
8. Keep `Auto` checked for single-prompt assistant tasks so the timer can stop when the assistant completion event fires.
9. Uncheck `Auto` for multi-prompt assistant tasks, then click `Answer Found` after the final response.
10. Click `Answer Found` manually for Condition A when the required answer is visible.
11. Export `Copy Raw` and `Copy KPI` at the end.

The overlay is movable. Drag the `Pilot Measurement` header to another part of the page if it covers important content.

Use `Reset Current` if the current timer/counters are wrong before saving. Use `Delete Last Try` if the last saved trial is wrong. Use `Reset All` if you want to clear the whole run and start over.

## Keyboard Shortcuts

- `Alt+Shift+S`: start task
- `Alt+Shift+A`: answer found
- `Alt+Shift+X`: add one screen

If Chrome does not activate them automatically, configure them at:

```text
chrome://extensions/shortcuts
```

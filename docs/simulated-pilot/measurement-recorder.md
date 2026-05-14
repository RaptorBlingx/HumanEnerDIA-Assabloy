# Pilot Measurement Recorder

The browser extension is now the preferred recorder for the official simulated pilot because it can automatically count clicks and browser screen changes across HumanEnerDIA and Grafana. See [browser-extension-pilot-measurement.md](/home/ubuntu/enms/docs/simulated-pilot/browser-extension-pilot-measurement.md).

The old in-app recorder has been disabled in the HumanEnerDIA pages to avoid duplicate recorder overlays.

If you want a separate manual measurement page outside HumanEnerDIA, use the standalone Dockerized app in `pilot-measurement/`. See [standalone-pilot-measurement.md](/home/ubuntu/enms/docs/simulated-pilot/standalone-pilot-measurement.md).

## Enable The Official Extension
Install and enable the Chrome extension from:

```text
pilot-measurement-extension/
```

Then open:

```text
http://10.33.10.103:8080/index.html
```

The extension data is stored in Chrome extension local storage under key `humanenerdia_pilot_extension_state_v1`. It is local to the Chrome profile and extension install. It is not saved in HumanEnerDIA, Docker, PostgreSQL, or the Git repo. Use `Copy Raw`, `Copy KPI`, or `JSON` export before clearing the extension data.

## Pilot Mode Toggle
For Condition A:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'manual');
location.href = '/index.html';
```

For Condition B:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'assistant');
location.href = '/index.html';
```

To disable it:

```js
localStorage.removeItem('humanenerdia_pilot_mode');
location.reload();
```

## Condition A - Manual Path
- Select the task in the extension overlay.
- Click `Start Task`.
- Navigate manually through the required pages.
- Click `Answer Found` when the required answer is visibly identified on screen.
- The extension automatically tracks elapsed time, browser clicks, and URL/history/hash screen transitions.
- Use `+Screen` only when a meaningful visual screen change does not change the URL/history/hash.

## Condition B - Assistant Path
- Set the extension condition to `B - Assistant`.
- Select the matching task.
- For OVOS, the recorder starts automatically when `Jarvis` is detected or when the OVOS prompt is submitted.
- For the chatbot, the recorder starts automatically when the prompt is submitted.
- Keep `Auto-stop` checked for single-prompt OVOS tasks. The recorder stops automatically when voice playback finishes.
- Keep `Auto-stop` checked for single-prompt chatbot tasks. The recorder stops automatically when the answer appears.
- Uncheck `Auto-stop` for multi-prompt tasks. The recorder starts on the first assistant prompt and keeps running until you click `Answer Found` after the final spoken or visible answer is complete.
- Uncheck `Auto-stop` for the report download task so the measured task includes both the voice response and the download starting.

## Pilot Voice Playback
- Assistant pilot mode uses browser speech synthesis for OVOS playback timing.
- Default pilot speech rate is `1.00`.
- Spoken equipment labels are normalized, so `Compressor-1` is spoken as `Compressor one`.
- You can override the speech rate before recording with `localStorage.setItem('humanenerdia_pilot_tts_rate', '1.10')` only if rehearsal proves normal speed unsuitable.

## Checkbox Rules
- `Expert`: check only if a human/domain expert would be needed to complete the task.
- `Manual reasoning`: check when the user must manually hunt through dashboards/pages or inspect raw data after starting the task.
- `Success`: check only if the task result is correct and visible.
- `Auto-stop`: assistant-only timing control; leave checked unless the task needs multiple assistant answers or the report download must be observed.

## Evidence Export
- Click `Copy Raw` and `Copy KPI` after the run.
- Paste the copied rows into the KPI measurement sheet.
- Keep the same task order in both conditions.

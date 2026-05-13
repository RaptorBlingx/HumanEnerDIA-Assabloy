# Pilot Measurement Recorder

The in-app recorder replaces the external timer and manual click counter for the simulated pilot videos.

## Enable It
For Condition A:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'manual');
location.reload();
```

For Condition B:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'assistant');
location.reload();
```

To disable it:

```js
localStorage.removeItem('humanenerdia_pilot_mode');
location.reload();
```

## Condition A - Manual Path
- Select the task in the recorder.
- Click `Start Task`.
- Navigate manually through the required pages.
- Click `Answer Found` when the required answer is visibly identified on screen.
- The recorder automatically tracks elapsed time, clicks, and page/screen transitions.
- Use `+Click` or `+Screen` only when the task moves into a page that cannot be instrumented, such as Grafana.
- For Grafana tasks, click `Open Control Window` before navigating to Grafana and keep the small control window visible while recording.

## Condition B - Assistant Path
- Set the recorder condition to `B - Assistant`.
- Select the matching task.
- For OVOS, the recorder starts automatically when `Jarvis` is detected or when the OVOS prompt is submitted.
- For the chatbot, the recorder starts automatically when the prompt is submitted.
- The recorder stops automatically when the assistant answer appears.

## Evidence Export
- Click `Copy CSV` after the run.
- Paste the copied rows into the KPI measurement sheet.
- Keep the same task order in both conditions.

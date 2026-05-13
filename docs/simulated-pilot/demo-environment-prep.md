# Demo Environment Preparation

This is the internal setup guide for rehearsal and recording.

## 1. Identity Alignment
- Use the simulated pilot profile in [factory-profile.md](factory-profile.md) for all spoken and written references.
- Before recording, align visible labels where possible so the screen story fits the Romanian pilot narrative.
- Avoid verbal references to legacy demo identities from older US- and Germany-oriented sample environments.

## 2. Condition Toggle
The repo now supports a simple pilot-mode toggle for recording:

- `manual` mode hides assistant widgets for `Condition A`
- default mode keeps assistants available for `Condition B`
- `manual`, `assistant`, and `pilot` modes enable the in-app measurement recorder described in [measurement-recorder.md](measurement-recorder.md)

### Manual Mode
Run this once in the browser console before recording `Video A`:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'manual');
localStorage.removeItem('humanenerdia_pilot_measurement_state');
location.href = '/index.html';
```

### Assistant Mode
Run this before recording `Video B`:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'assistant');
localStorage.removeItem('humanenerdia_pilot_measurement_state');
location.href = '/index.html';
```

### Restore Normal Mode
Run this after recording:

```js
localStorage.removeItem('humanenerdia_pilot_mode');
location.reload();
```

### Single-Page Alternative
If needed, append `?pilot_mode=manual` to a page URL for a one-page manual-mode check.

## 3. Pages Used In The Benchmark
- Main dashboard: `/index.html`
- Analytics dashboard: `/api/analytics/ui/`
- Baseline: `/api/analytics/ui/baseline`
- Anomaly view: `/api/analytics/ui/anomaly`
- KPI view: `/api/analytics/ui/kpi`
- Forecast view: `/api/analytics/ui/forecast`
- Opportunities view: `/api/analytics/ui/opportunities`
- EnPI report view: `/api/analytics/ui/enpi-report`
- Reports: `/reports.html`
- Learning: `/energy-management-learning.html`
- ISO 50001 support: `/iso50001.html`
- Pilot procedures: `/pilot-procedures.html`
- Grafana folder: `/grafana/dashboards/f/f1a99949-9056-4103-96b1-69fa65dec378/`

## 4. Manual Reference For Documentation Tasks
- Use [pilot-policy-and-procedure-reference.md](pilot-policy-and-procedure-reference.md) as the source content behind `/pilot-procedures.html`.
- For `Condition A`, use `/pilot-procedures.html` as the browser-openable reference page before recording.
- For `Condition B`, mirror the same content into the chatbot knowledge base so the comparison stays fair.

## 5. Assistant Validation Before Rehearsal
- OVOS health must be working.
- Chatbot must answer:
  - `What is ISO 50001?`
  - `What is an energy baseline?`
  - `What should we do when an anomaly appears?`
  - `What is the procedure for responding to an efficiency issue?`
- OVOS must answer:
  - `Give me a factory overview`
  - `Show top 3 energy consumers`
  - `What's the status of Compressor-1?`
  - `Show me recent anomalies`
  - `Analyze performance of Compressor-1`
  - `Expected energy for Compressor-1 baseline`
  - `Energy forecast for Compressor-1`
  - `What are the energy saving opportunities?`
  - `Show energy performance indicators report`
  - `download report of Apr 2026`

## 6. Recording Defaults
- Use the same browser, zoom level, and screen resolution in both videos.
- Use the same user account in both videos.
- Keep the timer style identical across both videos.
- Keep the page order identical across both videos.
- Record `Condition A` first, then `Condition B`.

## 7. Report And Period Defaults
- EnPI task: `2026-Q1`
- Monthly report task: `April 2026`
- Machine-specific operational task: `Compressor-1`
- Technical anomaly task: keep one unresolved `critical` anomaly on `Compressor-2`

## 8. Final Gate Before Recording
- Manual mode hides assistants cleanly.
- Assistant mode restores both widgets cleanly.
- All pages open without dead ends.
- The controlled `Compressor-2` anomaly is visible before rehearsal starts.
- The same task wording is visible in both conditions.

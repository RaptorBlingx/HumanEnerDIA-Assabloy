# Video Script A - Manual Condition

Condition:
- HumanEnerDIA without OVOS
- HumanEnerDIA without chatbot

Personas:
- `Operational user`: facility / production manager
- `Technical user`: energy / maintenance / automation engineer

Official timing rule:
- Preferred workflow: record one short clip per task, then edit it beside the matching `Condition B` clip.
- If recording a full Condition A run instead, keep the same task order and later split the footage by task.
- Use the Chrome extension `Pilot Measurement` overlay for each task timer.
- Click `Start Task` immediately before the first manual action for the task.
- Click `Answer Found` immediately when the required answer is visibly found.
- Do not include any after-task explanation, narration, or note-taking in the task time.

Manual evidence rules:
- Use factory `Simulated Romanian Pilot Factory` everywhere.
- Use `Compressor-1` for machine-specific manual tasks.
- Live monitoring values move during recording. Match the same KPI, panel, or ranking, not the exact decimal if the value refreshes.
- Prefer HumanEnerDIA pages and Grafana panels over raw JSON.
- Do not improvise extra assistant-style questions during Condition A.

## Pre-Recording Setup
1. Open `http://10.33.10.103:8080/index.html`.
2. If a login page appears, log in before the official recording. Do not include login time in the KPI measurement.
3. Confirm the Chrome extension `HumanEnerDIA Pilot Measurement` is installed and enabled.
4. Open browser DevTools console only to set manual mode for hiding assistant widgets, then run:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'manual');
location.href = '/index.html';
```

5. Confirm the extension `Pilot Measurement` overlay is visible.
6. Confirm OVOS and chatbot are not used in this video.
7. Drag the extension overlay away from important dashboard content if needed.
8. Use `Reset Current`, `Delete Last Try`, or `Reset All` if rehearsal data must be corrected before the official run.
9. Set the browser zoom and window size you will also use for Condition B.
10. Open the screen recorder, but do not start the task clip yet.

## Clip Recording Rule
- For task-based editing, start recording a few seconds before selecting the task in the extension.
- Stop recording a few seconds after clicking `Answer Found`.
- Name the clip using the pattern `O1-A-manual.mp4`, `O2-A-manual.mp4`, and so on.
- Keep the extension overlay visible at the beginning and end of the clip so the task ID, condition, timer, clicks, screens, and flags are visible.
- Do not include login, browser setup, or window arrangement in the measured task clip.

## Recorder Checkbox Rules
- `Expert`: leave unchecked unless the task cannot be completed without asking a human expert or leaving HumanEnerDIA. Expected result for the official rehearsal is unchecked.
- `Manual reasoning`: keep checked for Condition A because the user is manually hunting across dashboards/pages and interpreting the result.
- `Success`: keep checked only if the required answer is found on screen. Uncheck it if the page is broken, the data is missing, or the task cannot be completed.
- `Auto-stop`: not relevant for Condition A. Leave it checked.

## Grafana Counting Rules
The Chrome extension runs on Grafana pages and counts browser clicks automatically.

- Before entering Grafana, select the task in the extension overlay and click `Start Task`.
- The extension automatically counts page clicks.
- The extension automatically counts URL/history/hash screen changes.
- Use `+Screen` only when the visible dashboard state changes but the URL does not.
- Grafana dashboard redirects from `/grafana/d/...` to `/grafana/d/...?orgId=...&refresh=...` are normalized and should count as one screen.
- When the answer is visible in Grafana, click `Answer Found` in the extension overlay.

## Grafana Reference Links
- Folder: `http://10.33.10.103:8080/grafana/dashboards/f/f1a99949-9056-4103-96b1-69fa65dec378/`
- Factory Overview: `http://10.33.10.103:8080/grafana/d/sota-factory-overview/factory-overview?orgId=1&var-factory=Simulated%20Romanian%20Pilot%20Factory&from=now/d&to=now`
- Machine Health for `Compressor-1`: `http://10.33.10.103:8080/grafana/d/sota-machine-health/machine-health?orgId=1&var-machine_id=c0000000-0000-0000-0000-000000000001&from=now/d&to=now`
- Operational Efficiency: `http://10.33.10.103:8080/grafana/d/sota-operational-efficiency/operational-efficiency?orgId=1&from=now/d&to=now`
- Anomaly Detection: `http://10.33.10.103:8080/grafana/d/sota_anomaly_detection/anomaly-detection?orgId=1&from=now-7d&to=now`
- Predictive Analytics: `http://10.33.10.103:8080/grafana/d/sota_predictive_analytics/predictive-analytics?orgId=1&from=now-7d&to=now%2B1d`
- ISO 50001 EnPI: `http://10.33.10.103:8080/grafana/d/sota-iso50001-enpi/iso-50001-enpi?orgId=1&from=2026-01-01T00:00:00.000Z&to=2026-03-31T23:59:59.000Z`

## Start A Manual Task Clip
1. Start the screen recorder for the current task clip.
2. Show this title on screen for the first manual clip, or use the shorter task label for later clips:

> Simulated pilot benchmark - Condition A  
> HumanEnerDIA without OVOS and without chatbot

3. For the first manual clip only, say:

> This benchmark uses the simulated Romanian pilot factory profile. In Condition A, users complete the same tasks manually through HumanEnerDIA portal pages, Grafana dashboards, analytics views, and reports without assistant support.

4. For later manual clips, use the task-specific label from [video-editing-guide.md](video-editing-guide.md).

## O1 - Factory Overview And Top Consumers
Persona: `Operational user`

Task prompt:

> Get a factory overview and identify the top 3 energy consumers.

Steps:
1. In the recorder, set `Condition` to `A - Manual`.
2. Select `O1 - Factory overview and top consumers`.
3. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
4. Click `Start Task`.
5. In the main browser, open `/index.html`.
6. Click the Grafana button or open the `Factory Overview` Grafana link directly.
7. Let the extension count the Grafana navigation click and screen change automatically.
8. If the folder view appears without a URL/screen count change, click `+Screen` once.
9. If the folder view opens first, open `Factory Overview`.
10. Let the extension count the dashboard click and dashboard screen change automatically.
11. If the dashboard visually changes without a URL/screen count change, click `+Screen` once.
12. Confirm the time range is `Today` because the assistant answer uses today/current factory state.
13. Use panels `Energy Today`, `Current Power`, `Cost Today`, `Active Anomalies`, `Machine Status & Health`, and `Energy by Machine (Today)`.
14. If you need the active or running machine count more clearly, open `Operational Efficiency` and use panel `Machine Status Overview`.
15. Expected answer to capture: the factory today/current summary is visible, and top consumers include `Compressor-2`, `Injection-Molding-1`, and `Compressor-1`.
16. Click `Answer Found` in the extension overlay as soon as those items are visible.
17. Manual proof source: Grafana `Factory Overview`, optionally `Operational Efficiency`.
18. Do not keep the task timer running while explaining the result.

## O2 - Machine Status And Today's Energy
Persona: `Operational user`

Task prompt:

> Check the status and today's energy of Compressor-1.

Steps:
1. Select `O2 - Compressor-1 status and today energy`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open the `Machine Health for Compressor-1` Grafana link directly, or open the Grafana folder if it is not already open.
5. Let the extension count Grafana navigation clicks and URL/screen changes automatically.
6. If needed, open `Machine Health` and set the machine variable to `Compressor-1`.
7. Let the extension count the dashboard click and URL/screen change automatically. Use `+Screen` only if the dashboard visibly changes without a URL/screen count change.
8. Confirm the time range is `Today`.
9. Use panels `Energy Today`, `Current Power`, and `Anomaly Details`.
10. If you need the explicit running or stopped status, open `Operational Efficiency` and use panel `Machine Status Overview`.
11. Expected answer to capture: `Compressor-1` is running, current power is visible, today's energy is visible in kWh, and anomaly status is visible. The exact kWh value may move because the simulator is live.
12. Click `Answer Found` in the extension overlay as soon as the status and energy value are visible.
13. Manual proof source: Grafana `Machine Health`, optionally `Operational Efficiency`.

## O3 - ISO 50001 And Baseline Understanding
Persona: `Operational user`

Task prompt:

> Understand what ISO 50001 is and what an energy baseline means.

Steps:
1. Select `O3 - ISO 50001 and energy baseline`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open `/energy-management-learning.html`.
5. Find the `What ISO 50001 Means` section.
6. Find the `What An Energy Baseline Means` section on the same page.
7. Open `/api/analytics/ui/baseline` only if you want supporting product context after the learning page definitions are already visible.
8. Expected answer to capture: ISO 50001 is the Energy Management System standard, and an energy baseline is the reference used to compare current performance against normal expected performance.
9. Click `Answer Found` when both concept definitions have been found.
10. Manual proof source: `/energy-management-learning.html`, optionally `/api/analytics/ui/baseline`.

## O4 - Policy / Procedure Guidance
Persona: `Operational user`

Task prompt:

> Find the policy and procedure guidance for responding to an anomaly or efficiency issue.

Steps:
1. Select `O4 - Anomaly or efficiency procedure`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open `/pilot-procedures.html`.
5. Find the anomaly response guidance section.
6. Find the efficiency issue response guidance section.
7. Open `/api/analytics/ui/anomaly` only if you want to show the operational anomaly context.
8. Expected answer to capture: review affected machine/time/severity, compare against baseline or expected performance, check status and production context, decide monitor/escalate, and record the action/reporting result.
9. Click `Answer Found` when the response guidance is visible.
10. Manual proof source: `/pilot-procedures.html`, optionally `/api/analytics/ui/anomaly`.

## T1 - Review Anomalies
Persona: `Technical user`

Task prompt:

> Review anomalies and identify the issue requiring attention.

Steps:
1. Select `T1 - Review anomalies`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open `/api/analytics/ui/anomaly`.
5. Review the current or recent anomaly list first.
6. If you want supporting Grafana evidence, open `Anomaly Detection` with time range `Last 7 days`.
7. Use Grafana panels `Unresolved Anomalies`, `Critical Anomalies`, and `Top Machines by Anomaly Count` if you need a clearer visual.
8. Filter by severity or inspect the visible list if needed.
9. Expected answer to capture: the issue needing attention is the unresolved high-severity or critical anomaly affecting `Compressor-2`, or the highest-severity visible anomaly in the current list at recording time.
10. Click `Answer Found` when the issue is clearly identified on screen.
11. Manual proof source: `/api/analytics/ui/anomaly`, optionally Grafana `Anomaly Detection`.

## T2 - Baseline, Forecast, And Recommendations
Persona: `Technical user`

Task prompt:

> Analyze Compressor-1 against baseline, check forecast context, and retrieve recommendations.

Steps:
1. Select `T2 - Baseline analysis and recommendations`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open Grafana `Machine Health` for `Compressor-1`.
5. Confirm the time range is `Today`.
6. Find panels `Actual vs Baseline Power` and `Baseline Variance (24h)`.
7. Open `/api/analytics/ui/forecast`.
8. In `Generate Forecast`, select `Compressor-1`.
9. Select `Short (1-4 hours)` because this is the trained forecast model available in the demo environment.
10. Click `Generate Forecast`.
11. Wait until the forecast result and chart are visible.
12. Open `/api/analytics/ui/opportunities`.
13. Keep the factory as `Simulated Romanian Pilot Factory`.
14. Keep period as `Month`.
15. Click `Load` if the page did not already load recommendations.
16. Identify the top savings recommendations.
17. If needed, open Grafana `Predictive Analytics` for supporting forecast evidence and use panels `Power Forecast vs Actual (24-Hour)` and `Recent 24-Hour Forecasts (Historical)`.
18. Expected answer to capture: baseline evidence for `Compressor-1`, forecast evidence, and top recommendations such as time-based setback scheduling and the highest-ranked opportunities for `Injection-Molding-1`, `Compressor-1`, and `Hydraulic-Pump-1`.
19. Click `Answer Found` only after the baseline result, forecast result, and recommendations have been found.
20. Manual proof source: Grafana `Machine Health`, `/api/analytics/ui/forecast`, `/api/analytics/ui/opportunities`, optionally Grafana `Predictive Analytics`.

## T3 - KPI And EnPI Status
Persona: `Technical user`

Task prompt:

> Retrieve factory KPI and EnPI status for 2026-Q1.

Steps:
1. Select `T3 - KPI and EnPI status`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open `/api/analytics/ui/kpi`.
5. Review the factory KPI dashboard.
6. Open `/api/analytics/ui/enpi-report`.
7. Confirm the factory is `11111111-1111-1111-1111-111111111111` if the page shows the raw factory selector, or confirm the visible factory is the simulated Romanian pilot factory.
8. Confirm the period is `2026-Q1`.
9. Find the `2026-Q1` EnPI report/status.
10. If you want supporting trend evidence, open Grafana `ISO 50001 EnPI`.
11. Expected answer to capture: status is `on track`, actual energy is above baseline by about `4.60%`, and the performance gap is about `11,809.3 kWh`.
12. Click `Answer Found` when the EnPI status and deviation are visible.
13. Manual proof source: `/api/analytics/ui/enpi-report`, optionally Grafana `ISO 50001 EnPI`.

## T4 - Generate Monthly Report
Persona: `Technical user`

Task prompt:

> Generate the April 2026 monthly report and summarize the result.

Steps:
1. Select `T4 - April 2026 report`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open `/reports.html`.
5. Select the simulated Romanian pilot factory if the page asks for a factory.
6. Select `April 2026`.
7. Click the report generation/download action.
8. Wait until the page confirms the April 2026 report is generated or the browser starts downloading the report.
9. Expected answer to capture: April 2026 monthly report generated/downloaded successfully.
10. Click `Answer Found` when the generation/download result is visible.
11. Manual proof source: `/reports.html`.

## End A Manual Task Clip
1. After clicking `Answer Found`, keep the extension overlay visible for a few seconds.
2. Stop the screen recorder for that task clip.
3. After all manual and assistant task clips are recorded, open the extension `Pilot Measurement` overlay or popup.
4. Click `Copy Raw` and `Copy KPI` and keep the copied data for the KPI table.

Optional closing line for a full manual-condition source video:

> Condition A complete. Same tasks, manual navigation only.

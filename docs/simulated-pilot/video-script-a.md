# Video Script A - Manual Condition

Condition:
- HumanEnerDIA without OVOS
- HumanEnerDIA without chatbot

Personas:
- `Operational user`: facility / production manager
- `Technical user`: energy / maintenance / automation engineer

Official timing rule:
- Start one continuous screen recording for the whole Condition A video.
- Use the in-app Pilot Measurement recorder for each task timer.
- Click `Start Task` immediately before the first manual action for the task.
- Click `Answer Found` immediately when the required answer is visibly found.
- Do not include any after-task explanation, narration, or note-taking in the task time.

## Pre-Recording Setup
1. Open `http://10.33.10.103:8080/index.html`.
2. If a login page appears, log in before the official recording. Do not include login time in the KPI measurement.
3. Open browser DevTools console.
4. Run:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'manual');
localStorage.removeItem('humanenerdia_pilot_measurement_state');
location.href = '/index.html';
```

5. Confirm the `Pilot Measurement` panel is visible.
6. Confirm OVOS and chatbot are not used in this video.
7. Click `Open Control Window` in the Pilot Measurement panel.
8. Keep the control window visible beside the main browser. This is required for Grafana because Grafana does not run the HumanEnerDIA recorder script.
9. Set the browser zoom and window size you will also use for Condition B.
10. Open the screen recorder, but do not start recording yet.

## Recorder Checkbox Rules
- `Expert`: leave unchecked unless the task cannot be completed without asking a human expert or leaving HumanEnerDIA. Expected result for the official rehearsal is unchecked.
- `Manual reasoning`: keep checked for Condition A because the user is manually hunting across dashboards/pages and interpreting the result.
- `Success`: keep checked only if the required answer is found on screen. Uncheck it if the page is broken, the data is missing, or the task cannot be completed.
- `Auto-stop`: not relevant for Condition A. Leave it checked.

## Grafana Counting Rules
Grafana pages do not contain the Pilot Measurement overlay, so use the separate control window.

- Before entering Grafana, select the task in the control window and click `Start Task`.
- For every click you perform inside Grafana, click `+Click` once in the control window.
- For every meaningful screen/dashboard change inside Grafana, click `+Screen` once in the control window.
- Do not count clicks on the Pilot Measurement control window itself.
- When the answer is visible in Grafana, click `Answer Found` in the control window.

## Start The Video Recording
1. Start the screen recorder.
2. Show this title on screen or say it clearly:

> Simulated pilot benchmark - Condition A  
> HumanEnerDIA without OVOS and without chatbot

3. Say:

> This benchmark uses the simulated Romanian pilot factory profile. In Condition A, users complete the same tasks manually through HumanEnerDIA portal pages, Grafana dashboards, analytics views, and reports without assistant support.

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
6. Click the Grafana button or open `/grafana/dashboards/f/f1a99949-9056-4103-96b1-69fa65dec378/`.
7. In the control window, click `+Click` for the Grafana navigation action.
8. In the control window, click `+Screen` when the Grafana dashboard folder appears.
9. Open `Factory Overview`, `Executive Summary`, or the dashboard that shows factory-level consumption.
10. In the control window, click `+Click` for opening the dashboard.
11. In the control window, click `+Screen` when the dashboard opens.
12. Identify the factory overview and the top consumers on screen.
13. Expected answer to capture: top consumers should include `Compressor-2`, `Injection-Molding-1`, and `Compressor-1`.
14. Click `Answer Found` in the control window as soon as the top consumers are visible.
15. Do not keep the task timer running while explaining the result.

## O2 - Machine Status And Today's Energy
Persona: `Operational user`

Task prompt:

> Check the status and today's energy of Compressor-1.

Steps:
1. Select `O2 - Compressor-1 status and today energy`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open the Grafana folder `/grafana/dashboards/f/f1a99949-9056-4103-96b1-69fa65dec378/` if it is not already open.
5. Use `+Click` and `+Screen` in the control window for the Grafana navigation.
6. Open `Machine Health` or the dashboard that shows `Compressor-1`.
7. Use `+Click` for the dashboard click and `+Screen` when the dashboard view changes.
8. Find `Compressor-1` status and today's energy consumption.
9. Expected answer to capture: `Compressor-1` is running and today's energy is visible in kWh. The exact kWh value may move because the simulator is live.
10. Click `Answer Found` in the control window as soon as the status and energy value are visible.

## O3 - ISO 50001 And Baseline Understanding
Persona: `Operational user`

Task prompt:

> Understand what ISO 50001 is and what an energy baseline means.

Steps:
1. Select `O3 - ISO 50001 and energy baseline`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open `/energy-management-learning.html`.
5. Find the learning section that explains ISO 50001.
6. Open `/api/analytics/ui/baseline`.
7. Find the baseline analysis/training view and the baseline concept context.
8. Expected answer to capture: ISO 50001 is the Energy Management System standard, and an energy baseline is the reference used to compare current performance against normal expected performance.
9. Click `Answer Found` when both concepts have been found.

## O4 - Policy / Procedure Guidance
Persona: `Operational user`

Task prompt:

> Find the policy and procedure guidance for responding to an anomaly or efficiency issue.

Steps:
1. Select `O4 - Anomaly or efficiency procedure`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open `/pilot-procedures.html`.
5. Find the anomaly response guidance.
6. Find the efficiency issue response guidance.
7. Open `/api/analytics/ui/anomaly` only if you want to show the operational anomaly context.
8. Expected answer to capture: review affected machine/time/severity, compare against baseline or expected performance, check status and production context, decide monitor/escalate, and record the action/reporting result.
9. Click `Answer Found` when the response guidance is visible.

## T1 - Review Anomalies
Persona: `Technical user`

Task prompt:

> Review anomalies and identify the issue requiring attention.

Steps:
1. Select `T1 - Review anomalies`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open `/api/analytics/ui/anomaly`.
5. Review the current/recent anomaly list.
6. Filter by severity or inspect the visible list if needed.
7. Expected answer to capture: the issue needing attention is the unresolved high-severity/critical anomaly affecting `Compressor-2` or the highest-severity visible anomaly in the current list.
8. Click `Answer Found` when the issue is clearly identified on screen.

## T2 - Baseline, Forecast, Predict, And Recommendations
Persona: `Technical user`

Task prompt:

> Analyze Compressor-1 against baseline, check forecast/prediction context, and retrieve recommendations.

Steps:
1. Select `T2 - Baseline analysis and recommendations`.
2. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
3. Click `Start Task`.
4. Open `/api/analytics/ui/baseline`.
5. Select or locate `Compressor-1` if the page requires a machine selection.
6. Identify the baseline model/deviation context.
7. Open `/api/analytics/ui/forecast`.
8. In `Generate Forecast`, select `Compressor-1`.
9. Select `Short (1-4 hours)` unless another value is already selected.
10. Click `Generate Forecast`.
11. Wait until the forecast result and chart are visible.
12. Open `/api/analytics/ui/opportunities`.
13. Keep the factory as `Simulated Romanian Pilot Factory`.
14. Keep period as `Month`.
15. Click `Load` if the page did not already load recommendations.
16. Identify the top savings recommendations.
17. Expected answer to capture: baseline/forecast evidence for `Compressor-1` plus top recommendations such as time-based setback scheduling and other prioritized savings opportunities.
18. Click `Answer Found` only after the baseline/forecast result and recommendations have been found.

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
7. Find the `2026-Q1` EnPI report/status.
8. Expected answer to capture: status is `on track`, actual energy is above baseline by about `2.22%`, and the performance gap is about `5,838.6 kWh`.
9. Click `Answer Found` when the EnPI status and deviation are visible.

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

## End The Video Recording
1. Show this closing statement on screen or say it clearly:

> Condition A complete. Same tasks, manual navigation only.

2. Open the Pilot Measurement panel or control window.
3. Click `Copy CSV` and keep the copied data for the KPI table.
4. Stop the screen recorder.

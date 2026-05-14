# Frozen Task Set

This file defines the exact task list for both recordings. Do not improvise tasks during rehearsal or recording.

## Recording Order
1. Operational user tasks `O1` to `O4`
2. Technical user tasks `T1` to `T4`

## Operational User Tasks

| ID | Module | Task | Condition A - Manual Path | Condition B - Assistant Support |
| --- | --- | --- | --- | --- |
| O1 | Monitoring | Get a factory overview and identify the top 3 energy consumers. | Open Grafana `Factory Overview` and use `Energy Today`, `Current Power`, `Cost Today`, `Active Anomalies`, and `Energy by Machine (Today)`. | OVOS prompts: `Give me a factory overview` and `Show top 3 energy consumers`. |
| O2 | Monitoring | Check the status and today's energy of `Compressor-1`. | Open Grafana `Machine Health` for `Compressor-1`; use `Operational Efficiency` / `Machine Status Overview` only if the explicit running status is needed. | OVOS prompt: `What's the status of Compressor-1?` |
| O3 | Documentation | Understand what ISO 50001 is and what an energy baseline means. | Open `/energy-management-learning.html`, then open `/api/analytics/ui/baseline` to connect the concept to the product. | Rasa prompts: `What is ISO 50001?` and `What is an energy baseline?` |
| O4 | Documentation | Find the policy / procedure guidance for responding to an anomaly or efficiency issue. | Open `/pilot-procedures.html` together with `/api/analytics/ui/anomaly` for context. | Rasa prompts: `What should we do when an anomaly appears?` and `What is the procedure for responding to an efficiency issue?` |

## Technical User Tasks

| ID | Module | Task | Condition A - Manual Path | Condition B - Assistant Support |
| --- | --- | --- | --- | --- |
| T1 | Monitoring | Review anomalies and identify the issue requiring attention. | Open `/api/analytics/ui/anomaly` and identify the recent unresolved critical anomaly on `Compressor-2`. | OVOS prompt: `Show me recent anomalies` |
| T2 | Analyses | Analyze `Compressor-1` against baseline, forecast context, and recommendations. | Cross-check Grafana `Machine Health`, `/api/analytics/ui/forecast`, and `/api/analytics/ui/opportunities` to summarize baseline, forecast, and likely actions. | OVOS prompts: `Analyze performance of Compressor-1`, `Energy forecast for Compressor-1`, and `What are the energy saving opportunities?` |
| T3 | Analyses | Retrieve factory KPI and EnPI status for `2026-Q1`. | Open `/api/analytics/ui/kpi`, then open `/api/analytics/ui/enpi-report` to read the current EnPI status. | OVOS prompt: `Show energy performance indicators report` |
| T4 | Analyses / Documentation | Generate the `April 2026` monthly report and summarize the result. | Open `/reports.html`, choose the frozen factory and `April 2026`, generate the report, then summarize the visible outcome. | OVOS prompt: `download report of Apr 2026`, then summarize the generated PDF download confirmation. |

## Timing And Capture Rules
- Use the same task order in both videos.
- Start the in-app recorder when the first task action begins. In Condition B, OVOS/chatbot prompts start the recorder automatically.
- Stop the in-app recorder when the required answer is visible in Condition A and chatbot tasks.
- For single-prompt OVOS tasks, `Auto-stop` stops after voice playback finishes.
- For multi-prompt assistant tasks, disable `Auto-stop` and click `Answer Found` after the final spoken or visible answer is complete.
- Record click / screen count, need for expert help, need for manual dashboard hunting / manual API-style reasoning, and task success / failure for every task.

## Frozen Factory / Period Inputs
- Machine-specific tasks use `Compressor-1`.
- EnPI task uses `2026-Q1`.
- Monthly report task uses `April 2026`.
- Anomaly task uses the seeded unresolved critical anomaly on `Compressor-2`.

## Safe Assistant Prompt Set
Only use the prompts below in the official recording unless rehearsal proves an equivalent prompt is more stable:
- `Give me a factory overview`
- `Show top 3 energy consumers`
- `What's the status of Compressor-1?`
- `Show me recent anomalies`
- `Analyze performance of Compressor-1`
- `Energy forecast for Compressor-1`
- `What are the energy saving opportunities?`
- `Show energy performance indicators report`
- `download report of Apr 2026`
- `What is ISO 50001?`
- `What is an energy baseline?`
- `What should we do when an anomaly appears?`
- `What is the procedure for responding to an efficiency issue?`

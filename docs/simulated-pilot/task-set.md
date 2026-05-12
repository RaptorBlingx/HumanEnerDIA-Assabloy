# Frozen Task Set

This file defines the exact task list for both recordings. Do not improvise tasks during rehearsal or recording.

## Recording Order
1. Operational user tasks `O1` to `O4`
2. Technical user tasks `T1` to `T4`

## Operational User Tasks

| ID | Module | Task | Condition A - Manual Path | Condition B - Assistant Support |
| --- | --- | --- | --- | --- |
| O1 | Monitoring | Get a factory overview and identify the top 3 energy consumers. | Open `/index.html` for the main dashboard, then open `/grafana/` and use the `SOTA Executive Summary` or `SOTA Operational Efficiency` dashboard to identify the largest consumers. | OVOS prompts: `Give me a factory overview` and `Show top 3 energy consumers`. |
| O2 | Monitoring | Check the status and today's energy of `Compressor-1`. | Open `/grafana/` and use `SOTA Machine Health` or the real-time dashboard with a machine filter for `Compressor-1`. | OVOS prompt: `What's the status of Compressor-1?` |
| O3 | Documentation | Understand what ISO 50001 is and what an energy baseline means. | Open `/iso50001.html`, then open `/api/analytics/ui/baseline` to connect the concept to the product. | Rasa prompts: `What is ISO 50001?` and `What is an energy baseline?` |
| O4 | Documentation | Find the policy / procedure guidance for responding to an anomaly or efficiency issue. | Use the staged manual reference based on [pilot-policy-and-procedure-reference.md](/home/ubuntu/enms/docs/simulated-pilot/pilot-policy-and-procedure-reference.md) together with `/api/analytics/ui/anomaly` for context. | Rasa prompts: `What should we do when an anomaly appears?` and `What is the procedure for responding to an efficiency issue?` |

## Technical User Tasks

| ID | Module | Task | Condition A - Manual Path | Condition B - Assistant Support |
| --- | --- | --- | --- | --- |
| T1 | Monitoring | Review anomalies and identify the issue requiring attention. | Open `/api/analytics/ui/anomaly` and filter the current / recent anomaly list. | OVOS prompt: `Show me recent anomalies` |
| T2 | Analyses | Analyze `Compressor-1` against baseline and retrieve recommendations. | Cross-check `/api/analytics/ui/baseline`, `/api/analytics/ui/model-performance`, and relevant dashboard/report context to summarize the deviation and likely actions. | OVOS prompts: `Analyze performance of Compressor-1` and `What are the energy saving opportunities?` |
| T3 | Analyses | Retrieve factory KPI and EnPI status for `2025-Q4`. | Open `/api/analytics/ui/kpi`, then open `/grafana/` and use the `SOTA ISO 50001 EnPI` dashboard to read the current status. | OVOS prompt: `Show energy performance indicators report` |
| T4 | Analyses / Documentation | Generate the `December 2025` monthly report and summarize the result. | Open `/reports.html`, choose the frozen factory and `December 2025`, generate the report, then summarize the visible outcome. | Rasa prompt: `How do I generate a report?`, then use `/reports.html` for the same report generation flow and summarize the result. |

## Timing And Capture Rules
- Use the same task order in both videos.
- Start the timer when the task prompt appears on screen.
- Stop the timer when the user has spoken or displayed the final answer.
- Record click / screen count, need for expert help, need for manual dashboard hunting / manual API-style reasoning, and task success / failure for every task.

## Frozen Factory / Period Inputs
- Machine-specific tasks use `Compressor-1`.
- EnPI task uses `2025-Q4`.
- Monthly report task uses `December 2025`.

## Safe Assistant Prompt Set
Only use the prompts below in the official recording unless rehearsal proves an equivalent prompt is more stable:
- `Give me a factory overview`
- `Show top 3 energy consumers`
- `What's the status of Compressor-1?`
- `Show me recent anomalies`
- `Analyze performance of Compressor-1`
- `What are the energy saving opportunities?`
- `Show energy performance indicators report`
- `What is ISO 50001?`
- `What is an energy baseline?`
- `What should we do when an anomaly appears?`
- `What is the procedure for responding to an efficiency issue?`
- `How do I generate a report?`

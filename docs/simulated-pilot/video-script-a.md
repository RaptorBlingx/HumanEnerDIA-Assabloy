# Video Script A - Manual Condition

Condition:
- HumanEnerDIA without OVOS
- HumanEnerDIA without chatbot

Use:
- `Operational user`: facility / production manager
- `Technical user`: energy / maintenance / automation engineer

## Opening
Display on screen:

> Simulated pilot benchmark - Condition A  
> HumanEnerDIA without OVOS and without chatbot

Voice-over:

> This benchmark uses a simulated Romanian pilot factory profile aligned with the HumanEnerDIA pilot-factory scope. In Condition A, the same platform is used without OVOS and without the chatbot, so users rely on manual portal, dashboard, and reporting navigation.

## Task Order

### O1 - Factory Overview And Top Consumers
- Show prompt on screen: `Get a factory overview and identify the top 3 energy consumers.`
- Start timer.
- Navigate to `/index.html`.
- Open `/grafana/dashboards/f/f1a99949-9056-4103-96b1-69fa65dec378/`.
- Use `Executive Summary` or `Operational Efficiency`.
- Read the overview and identify the top 3 consumers.
- Stop timer when the answer is spoken or shown.

### O2 - Machine Status And Today's Energy
- Show prompt on screen: `Check the status and today's energy of Compressor-1.`
- Start timer.
- Open `/grafana/dashboards/f/f1a99949-9056-4103-96b1-69fa65dec378/`.
- Use `Machine Health` or real-time dashboard views with `Compressor-1`.
- Read the current status and today's energy result.
- Stop timer.

### O3 - ISO 50001 And Baseline Understanding
- Show prompt on screen: `Understand what ISO 50001 is and what an energy baseline means.`
- Start timer.
- Open `/energy-management-learning.html`.
- Open `/api/analytics/ui/baseline`.
- Summarize both concepts in user language.
- Stop timer.

### O4 - Policy / Procedure Guidance
- Show prompt on screen: `Find the policy and procedure guidance for responding to an anomaly or efficiency issue.`
- Start timer.
- Open `/pilot-procedures.html`.
- Open `/api/analytics/ui/anomaly` for operational context.
- Summarize the expected response steps.
- Stop timer.

### T1 - Review Anomalies
- Show prompt on screen: `Review anomalies and identify the issue requiring attention.`
- Start timer.
- Open `/api/analytics/ui/anomaly`.
- Filter or inspect current / recent anomalies.
- Identify the unresolved `critical` `Compressor-2` spike as the issue that needs attention.
- Stop timer.

### T2 - Baseline Analysis And Recommendations
- Show prompt on screen: `Analyze Compressor-1 against baseline and retrieve recommendations.`
- Start timer.
- Open `/api/analytics/ui/baseline`.
- Cross-check `/api/analytics/ui/model-performance`.
- Open `/api/analytics/api/v1/performance/opportunities?factory_id=11111111-1111-1111-1111-111111111111&period=month`.
- Summarize the baseline deviation for `Compressor-1` and the broader top savings recommendations.
- Stop timer.

### T3 - KPI And EnPI Status
- Show prompt on screen: `Retrieve factory KPI and EnPI status for 2026-Q1.`
- Start timer.
- Open `/api/analytics/ui/kpi`.
- Open `/api/analytics/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2026-Q1&baseline_year=2026`.
- Read the EnPI status for `2026-Q1` and summarize the deviation.
- Stop timer.

### T4 - Generate Monthly Report
- Show prompt on screen: `Generate the April 2026 monthly report and summarize the result.`
- Start timer.
- Open `/reports.html`.
- Select the frozen factory and `April 2026`.
- Generate the report.
- Summarize what was generated or shown on screen.
- Stop timer.

## Closing
Display on screen:

> Condition A complete  
> Same tasks, manual navigation only

Voice-over:

> Condition A shows the baseline user journey without the digital assistants. The next recording repeats the same tasks with OVOS and chatbot support enabled.

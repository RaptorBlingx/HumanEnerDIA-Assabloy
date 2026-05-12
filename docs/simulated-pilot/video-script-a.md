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
- Open `/grafana/`.
- Use `SOTA Executive Summary` or `SOTA Operational Efficiency`.
- Read the overview and identify the top 3 consumers.
- Stop timer when the answer is spoken or shown.

### O2 - Machine Status And Today's Energy
- Show prompt on screen: `Check the status and today's energy of Compressor-1.`
- Start timer.
- Open `/grafana/`.
- Use `SOTA Machine Health` or real-time dashboard views with `Compressor-1`.
- Read the current status and today's energy result.
- Stop timer.

### O3 - ISO 50001 And Baseline Understanding
- Show prompt on screen: `Understand what ISO 50001 is and what an energy baseline means.`
- Start timer.
- Open `/iso50001.html`.
- Open `/api/analytics/ui/baseline`.
- Summarize both concepts in user language.
- Stop timer.

### O4 - Policy / Procedure Guidance
- Show prompt on screen: `Find the policy and procedure guidance for responding to an anomaly or efficiency issue.`
- Start timer.
- Open the staged manual reference based on [pilot-policy-and-procedure-reference.md](/home/ubuntu/enms/docs/simulated-pilot/pilot-policy-and-procedure-reference.md).
- Open `/api/analytics/ui/anomaly` for operational context.
- Summarize the expected response steps.
- Stop timer.

### T1 - Review Anomalies
- Show prompt on screen: `Review anomalies and identify the issue requiring attention.`
- Start timer.
- Open `/api/analytics/ui/anomaly`.
- Filter or inspect current / recent anomalies.
- Identify the issue that needs attention.
- Stop timer.

### T2 - Baseline Analysis And Recommendations
- Show prompt on screen: `Analyze Compressor-1 against baseline and retrieve recommendations.`
- Start timer.
- Open `/api/analytics/ui/baseline`.
- Cross-check `/api/analytics/ui/model-performance`.
- Use relevant dashboard or report context if needed.
- Summarize the baseline deviation and likely recommendations.
- Stop timer.

### T3 - KPI And EnPI Status
- Show prompt on screen: `Retrieve factory KPI and EnPI status for 2025-Q4.`
- Start timer.
- Open `/api/analytics/ui/kpi`.
- Open `/grafana/`.
- Use `SOTA ISO 50001 EnPI`.
- Read the KPI / EnPI status for `2025-Q4`.
- Stop timer.

### T4 - Generate Monthly Report
- Show prompt on screen: `Generate the December 2025 monthly report and summarize the result.`
- Start timer.
- Open `/reports.html`.
- Select the frozen factory and `December 2025`.
- Generate the report.
- Summarize what was generated or shown on screen.
- Stop timer.

## Closing
Display on screen:

> Condition A complete  
> Same tasks, manual navigation only

Voice-over:

> Condition A shows the baseline user journey without the digital assistants. The next recording repeats the same tasks with OVOS and chatbot support enabled.

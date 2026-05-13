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

Measurement setup:
- Enable manual mode with `localStorage.setItem('humanenerdia_pilot_mode', 'manual'); location.reload();`.
- Use the in-app pilot recorder instead of an external timer.
- For each task, click `Start Task` before manual navigation and click `Answer Found` when the required answer is visibly identified.
- Do not include optional narration after `Answer Found` in the task time.
- For Grafana tasks, open the recorder `Control Window` first so the timer remains visible while the main window is on Grafana.

## Task Order

### O1 - Factory Overview And Top Consumers
- Show prompt on screen: `Get a factory overview and identify the top 3 energy consumers.`
- Select `O1` in the recorder and click `Start Task`.
- Navigate to `/index.html`.
- Open `/grafana/dashboards/f/f1a99949-9056-4103-96b1-69fa65dec378/`.
- Use `Executive Summary` or `Operational Efficiency`.
- Identify the top 3 consumers on screen.
- Click `Answer Found`.

### O2 - Machine Status And Today's Energy
- Show prompt on screen: `Check the status and today's energy of Compressor-1.`
- Select `O2` in the recorder and click `Start Task`.
- Open `/grafana/dashboards/f/f1a99949-9056-4103-96b1-69fa65dec378/`.
- Use `Machine Health` or real-time dashboard views with `Compressor-1`.
- Identify the current status and today's energy result on screen.
- Click `Answer Found`.

### O3 - ISO 50001 And Baseline Understanding
- Show prompt on screen: `Understand what ISO 50001 is and what an energy baseline means.`
- Select `O3` in the recorder and click `Start Task`.
- Open `/energy-management-learning.html`.
- Open `/api/analytics/ui/baseline`.
- Identify the ISO 50001 and baseline explanation on screen.
- Click `Answer Found`.

### O4 - Policy / Procedure Guidance
- Show prompt on screen: `Find the policy and procedure guidance for responding to an anomaly or efficiency issue.`
- Select `O4` in the recorder and click `Start Task`.
- Open `/pilot-procedures.html`.
- Open `/api/analytics/ui/anomaly` for operational context.
- Identify the expected response steps on screen.
- Click `Answer Found`.

### T1 - Review Anomalies
- Show prompt on screen: `Review anomalies and identify the issue requiring attention.`
- Select `T1` in the recorder and click `Start Task`.
- Open `/api/analytics/ui/anomaly`.
- Filter or inspect current / recent anomalies.
- Identify the unresolved `critical` `Compressor-2` spike as the issue that needs attention.
- Click `Answer Found`.

### T2 - Baseline Analysis And Recommendations
- Show prompt on screen: `Analyze Compressor-1 against baseline and retrieve recommendations.`
- Select `T2` in the recorder and click `Start Task`.
- Open `/api/analytics/ui/baseline`.
- Cross-check `/api/analytics/ui/model-performance`.
- Open `/api/analytics/ui/opportunities`.
- Identify the relevant baseline context and top savings recommendations on screen.
- Click `Answer Found`.

### T3 - KPI And EnPI Status
- Show prompt on screen: `Retrieve factory KPI and EnPI status for 2026-Q1.`
- Select `T3` in the recorder and click `Start Task`.
- Open `/api/analytics/ui/kpi`.
- Open `/api/analytics/ui/enpi-report`.
- Identify the EnPI status and deviation for `2026-Q1` on screen.
- Click `Answer Found`.

### T4 - Generate Monthly Report
- Show prompt on screen: `Generate the April 2026 monthly report and summarize the result.`
- Select `T4` in the recorder and click `Start Task`.
- Open `/reports.html`.
- Select the frozen factory and `April 2026`.
- Generate the report.
- Confirm the April 2026 report generation result on screen.
- Click `Answer Found`.

## Closing
Display on screen:

> Condition A complete  
> Same tasks, manual navigation only

Voice-over:

> Condition A shows the baseline user journey without the digital assistants. The next recording repeats the same tasks with OVOS and chatbot support enabled.

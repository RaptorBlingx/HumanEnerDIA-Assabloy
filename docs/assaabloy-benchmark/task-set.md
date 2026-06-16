# ASSA ABLOY Benchmark Task Set

Use this fixed task set for both conditions. Do not change tasks between Condition A and Condition B.

## Personas

- Operational user: facility or production manager.
- Technical user: energy, maintenance, or automation engineer.

## Conditions

- Condition A: HumanEnerDIA without OVOS and without chatbot assistance.
- Condition B: HumanEnerDIA with OVOS and chatbot assistance.

## Operational-User Tasks

### O1 - Partner KPI Overview

- Module: Monitoring
- Task: retrieve the ASSA ABLOY press-shop KPI overview: total energy, total production, and group SEC values.
- Condition A path: use HumanEnerDIA partner KPI/dashboard views and reports.
- Condition B prompt: `Show KPIs for the ASSA ABLOY partner press shop`
- Stop criterion: total energy `141,254.85 kWh`, total production `27,625,665 units`, and Bret/Raster/Dimeco SEC values are visible.
- Default flags: Expert Help `0`, Manual Reasoning A `1`, Manual Reasoning B `0`, Success `1`.

### O2 - Energy Group Comparison

- Module: Monitoring
- Task: compare Bret, Raster, and Dimeco group energy consumption for the partner KPI period.
- Condition A path: use HumanEnerDIA partner energy charts or partner summary evidence.
- Condition B prompt: `Compare Bret, Raster, and Dimeco energy consumption`
- Stop criterion: Dimeco `59,661.97 kWh`, Raster `41,981.81 kWh`, and Bret `39,611.06 kWh` are visible.
- Default flags: Expert Help `0`, Manual Reasoning A `1`, Manual Reasoning B `0`, Success `1`.

### O3 - Production And SEC Meaning

- Module: Analyses / Documentation
- Task: understand production-normalized performance using SEC and partner production totals.
- Condition A path: use the KPI view and ISO/EnPI documentation.
- Condition B prompt: `Explain SEC for the partner press shop`
- Optional chatbot support: `What is SEC?`
- Stop criterion: SEC is defined as kWh per produced unit and Bret/Raster/Dimeco SEC values are visible.
- Default flags: Expert Help `0`, Manual Reasoning A `1`, Manual Reasoning B `0`, Success `1`.

### O4 - Baseline Concept And Active Baselines

- Module: Documentation / Analyses
- Task: understand the energy-baseline concept and confirm which partner meter groups have active EnPI baselines.
- Condition A path: use the baseline UI and ISO 50001 documentation.
- Condition B chatbot prompt: `What is an energy baseline?`
- Condition B OVOS prompt: `Which partner meter groups have baselines?`
- Stop criterion: baseline concept is visible and active EnPI baselines for `3 of 3` partner meter groups are visible.
- Default flags: Expert Help `0`, Manual Reasoning A `1`, Manual Reasoning B `0`, Success `1`.

## Technical-User Tasks

### T1 - Data Inventory Verification

- Module: Documentation
- Task: verify imported ASSA ABLOY energy and production row counts.
- Condition A path: use the partner data verification document and partner profile/API evidence.
- Condition B prompt: `How many readings and rows were imported for ASSA ABLOY?`
- Stop criterion: `1,978` energy readings and `6,336` materialized production rows are visible.
- Default flags: Expert Help `0`, Manual Reasoning A `1`, Manual Reasoning B `0`, Success `1`.

### T2 - Meter Boundary And Per-Press Guardrail

- Module: Documentation / Analyses
- Task: confirm the Bret transformer reference-meter boundary and verify that per-press energy is not invented.
- Condition A path: use the partner ingestion/verification documentation and partner summary evidence.
- Condition B prompts: `What does the Bret transformer reference meter show?` then `Energy consumption of Bret125-1`
- Stop criterion: transformer shows `743` rows and `263,999.16 kWh` excluded from KPIs, and Bret125-1 per-press energy is refused.
- Default flags: Expert Help `0`, Manual Reasoning A `1`, Manual Reasoning B `0`, Success `1`.

### T3 - SEU And Baseline Readiness

- Module: Analyses
- Task: identify partner SEUs and confirm baseline readiness for the three partner meter groups.
- Condition A path: use baseline/model-performance views and partner ML readiness evidence.
- Condition B prompts: `What are the significant energy uses in the partner press shop?` then `Which partner meter groups have baselines?`
- Stop criterion: Bret, Dimeco, and Raster Presses Electricity are listed and active baselines are shown for `3 of 3` meter groups.
- Default flags: Expert Help `0`, Manual Reasoning A `1`, Manual Reasoning B `0`, Success `1`.

### T4 - Monthly Reporting

- Module: Analyses / Documentation
- Task: generate or retrieve a monthly reporting result for the partner press shop.
- Condition A path: use `/reports.html` with `ASSA ABLOY Partner Press Shop` and `May 2026`.
- Condition B prompt: `download the ASSA ABLOY partner press shop report for May 2026`
- Stop criterion: the May 2026 monthly energy report is generated/downloaded or the report-ready response is visible.
- Default flags: Expert Help `0`, Manual Reasoning A `1`, Manual Reasoning B `0`, Success `1`.

## Notes

May 2026 is used for T4 because it is the last complete month inside the configured KPI period ending `2026-06-01`.

For multi-prompt Condition B tasks, disable the extension `Auto` checkbox before starting the task and click `Answer Found` manually after the final response.

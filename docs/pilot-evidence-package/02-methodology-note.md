# Methodology Note

## Purpose
This benchmark demonstrates HumanEnerDIA through a simulated pilot factory. The simulation uses a representative Romanian manufacturing profile aligned with the HumanEnerDIA pilot-factory scope and proposal context.

## Design
- Two conditions were compared:
  - `Condition A`: HumanEnerDIA without OVOS and without chatbot
  - `Condition B`: HumanEnerDIA with OVOS and chatbot support
- Two personas were used:
  - operational user: facility / production manager
  - technical user: energy / maintenance / automation engineer
- The same fixed task set was used in both conditions.

## Measured Outputs
For each task, the benchmark records:
- task completion time
- click / screen count
- need for expert help
- need for manual dashboard or API-style analysis
- task success / failure

## KPI Interpretation
- Operational-user effort reduction is assessed from the A/B task results and compared against the proposal target of `30%`.
- Technical-user intervention reduction is assessed from the A/B task results and compared against the proposal target of `25%`.
- The benchmark also demonstrates the three required DIA modules:
  - Monitoring
  - Analyses
  - Documentation

## Final Measured Results
- Operational-user effort reduction: `61.7%` against the `30%` target.
- Technical-user intervention / effort reduction: `55.1%` against the `25%` target.
- DIA module evidence: `3/3` modules demonstrated - Monitoring, Analyses, and Documentation.
- Final status: all KPI targets met in the simulated pilot benchmark.

One technical task, `T2 - Baseline analysis and recommendations`, took longer in Condition B because the assistant-supported path executed heavier analysis. The task still exceeded the technical KPI target because it substantially reduced clicks and screen transitions while preserving task success.

## Scope Of The Claim
The benchmark shows measurable improvement in user interaction, task completion, and access to energy-management information within a simulated pilot scenario. It does not claim a completed live Romanian factory deployment.

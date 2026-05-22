# HumanEnerDIA Simulated Pilot Evidence Package

## Purpose

This folder contains the finalized evidence package for the HumanEnerDIA simulated pilot benchmark prepared for the WASABI project KPI demonstration.

The package supports the final edited A/B benchmark video and documents the methodology, simulated factory profile, fixed task set, measured KPI results, and exported comparison cards.

## Final KPI Outcome

| KPI Area | Proposal Target | Measured Result | Status |
| --- | ---: | ---: | --- |
| Operational-user effort reduction | 30% | 61.7% | Target met |
| Technical-user intervention / effort reduction | 25% | 55.1% | Target met |
| DIA module demonstration | 3 modules | 3/3 modules | Target met |

The demonstrated DIA modules are Monitoring, Analyses, and Documentation.

## Package Contents

| File / Folder | Purpose |
| --- | --- |
| [01-final-results-summary.md](01-final-results-summary.md) | Executive summary of the final measured KPI results. |
| [02-methodology-note.md](02-methodology-note.md) | Methodology, scope, assumptions, and claim boundary. |
| [03-simulated-factory-profile.md](03-simulated-factory-profile.md) | Frozen simulated Romanian pilot-factory profile. |
| [04-task-set-and-measurement-rules.md](04-task-set-and-measurement-rules.md) | Fixed A/B task set, personas, prompts, and timing rules. |
| [05-final-kpi-results.csv](05-final-kpi-results.csv) | Final measured KPI values used for the cards and final conclusion. |
| [kpi-cards](kpi-cards) | Exported PNG comparison cards for each task, subtotals, and final KPI summary. |
| [06-measurement-protocol.md](06-measurement-protocol.md) | Reviewer-facing description of how the A/B measurements were collected. |
| [video](video) | Place the final edited benchmark video here before sending the package. |

## Claim Boundary

This evidence package describes a simulated pilot benchmark. It does not claim that a live Romanian factory deployment was completed. The benchmark uses a representative Romanian manufacturing profile and compares the same tasks under two conditions:

- `Condition A`: HumanEnerDIA without OVOS and without chatbot
- `Condition B`: HumanEnerDIA with OVOS and chatbot support

## Recommended Handover Set

When sending the final package, include:

- this full `pilot-evidence-package` folder
- the final edited benchmark video in the `video` folder
- any raw A/B clips or measurement exports if the reviewer requests audit-level evidence

## Recommended Closing Statement

The simulated A/B pilot shows that adding OVOS and chatbot support to HumanEnerDIA reduced operational-user effort by `61.7%`, reduced technical-user effort / intervention need by `55.1%`, and demonstrated the required DIA modules: Monitoring, Analyses, and Documentation. These results exceed the committed KPI thresholds in the proposal within the simulated pilot scope.

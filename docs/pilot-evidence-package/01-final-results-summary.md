# Simulated Pilot Final Results Summary

## Final Conclusion

The simulated HumanEnerDIA A/B pilot evidence supports the proposal KPI targets.

- Operational-user effort reduction target: `30%`
- Measured operational-user effort reduction: `61.7%`
- Technical-user intervention / effort reduction target: `25%`
- Measured technical-user effort reduction: `55.1%`
- DIA modules demonstrated: `3/3` - Monitoring, Analyses, Documentation
- Final KPI status: all KPI targets met in the simulated pilot benchmark

## Evidence Basis

The final video uses the same task set under two conditions:

- `Condition A`: HumanEnerDIA without OVOS and without chatbot
- `Condition B`: HumanEnerDIA with OVOS and chatbot support

Each task was measured using:

- task completion time
- clicks
- screen transitions
- expert-help flag
- manual-reasoning flag
- success flag

The exported KPI cards are stored in [kpi-cards](kpi-cards).

## Task-Level Results

| Task | Persona | Module | A Time | B Time | Measured Effort Reduction | Status |
| --- | --- | --- | ---: | ---: | ---: | --- |
| O1 | Operational | Monitoring | 84s | 53s | 63.5% | Target met |
| O2 | Operational | Monitoring | 41s | 18s | 69.7% | Target met |
| O3 | Operational | Documentation | 32s | 14s | 53.1% | Target met |
| O4 | Operational | Documentation | 31s | 9s | 60.5% | Target met |
| T1 | Technical | Monitoring | 62s | 10s | 79.4% | Target met |
| T2 | Technical | Analyses | 76s | 83s | 40.4% | Target met |
| T3 | Technical | Analyses | 43s | 40s | 45.2% | Target met |
| T4 | Technical | Analyses / Documentation | 31s | 18s | 55.3% | Target met |

## Subtotal Results

| KPI Area | A Total Time | B Total Time | Time Reduction | Interaction Reduction | Measured Effort Reduction | Target | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Operational user | 188s | 94s | 55.1% | 68.3% | 61.7% | 30% | Target met |
| Technical user | 212s | 151s | 30.9% | 79.3% | 55.1% | 25% | Target met |

## Interpretation Notes

- The benchmark is a simulated pilot, not a completed live Romanian factory deployment.
- `T2 - Baseline analysis and recommendations` took longer in Condition B because the assistant-supported path executed heavier analysis. The task still exceeded the technical KPI target because it substantially reduced clicks and screen transitions while preserving task success.
- The result interpretation is based on the measured A/B task evidence, the exported KPI cards, and the methodology documented in this evidence package.

## Final Evidence Statement

The simulated A/B pilot shows that adding OVOS and chatbot support to HumanEnerDIA reduced operational-user effort by `61.7%`, reduced technical-user effort / intervention need by `55.1%`, and demonstrated the required DIA modules: Monitoring, Analyses, and Documentation. These results exceed the committed KPI thresholds in the proposal within the simulated pilot scope.

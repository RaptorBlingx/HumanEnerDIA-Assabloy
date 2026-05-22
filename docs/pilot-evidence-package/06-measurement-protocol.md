# Measurement Protocol

## Benchmark Design

The benchmark used an A/B comparison design with the same personas, tasks, and success criteria in both conditions.

| Condition | Description |
| --- | --- |
| Condition A | HumanEnerDIA without OVOS and without chatbot support. |
| Condition B | HumanEnerDIA with OVOS and chatbot support. |

## Personas

| Persona | Role Represented |
| --- | --- |
| Operational user | Facility / production manager |
| Technical user | Energy / maintenance / automation engineer |

## Measured Fields

Each task was measured using the following fields:

| Field | Meaning |
| --- | --- |
| Task completion time | Time from the first task action to the point where the required result was visible or the assistant response was complete. |
| Click count | Number of task-relevant browser interactions. |
| Screen count | Number of meaningful page, dashboard, report, or result-screen transitions. |
| Expert help | Whether external expert assistance was needed to complete the task. |
| Manual reasoning | Whether the user had to manually inspect dashboards, reports, or API-style outputs to derive the answer. |
| Success | Whether the required task result was obtained. |

## KPI Calculation

Per task:

```text
time reduction = (Condition A time - Condition B time) / Condition A time
click reduction = (Condition A clicks - Condition B clicks) / Condition A clicks
screen reduction = (Condition A screens - Condition B screens) / Condition A screens
interaction reduction = average(click reduction, screen reduction)
measured effort reduction = average(time reduction, interaction reduction)
```

For the operational and technical subtotals, the measured effort reduction was averaged across the relevant task group.

## Interpretation

The operational-user KPI is considered met when the measured operational effort reduction is at least `30%`.

The technical-user KPI is considered met when the measured technical intervention / effort reduction is at least `25%`.

The DIA module KPI is considered met when the benchmark demonstrates Monitoring, Analyses, and Documentation.

## Final Measured Results

| KPI Area | Target | Measured Result | Status |
| --- | ---: | ---: | --- |
| Operational-user effort reduction | 30% | 61.7% | Target met |
| Technical-user intervention / effort reduction | 25% | 55.1% | Target met |
| DIA module coverage | 3 modules | 3/3 modules | Target met |

## Scope

The measurements support a simulated pilot benchmark. They should not be presented as evidence of a completed live factory deployment.

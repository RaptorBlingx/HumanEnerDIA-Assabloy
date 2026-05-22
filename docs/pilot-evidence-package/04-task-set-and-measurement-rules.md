# Benchmark Task Set And Measurement Rules

## Purpose

This document defines the fixed benchmark tasks used to compare HumanEnerDIA performance under two conditions:

| Condition | Description |
| --- | --- |
| Condition A | Manual HumanEnerDIA usage without OVOS and without chatbot support |
| Condition B | HumanEnerDIA usage with OVOS and chatbot support |

The same task objectives, personas, success criteria, and measurement fields were used in both conditions.

## Operational User Tasks

| ID | DIA Module | Task Objective | Condition A Evidence Path | Condition B Evidence Path |
| --- | --- | --- | --- | --- |
| O1 | Monitoring | Obtain a factory overview and identify the top three energy consumers. | Manual review of factory overview and energy-consumption dashboard evidence. | Assistant-supported retrieval of the factory overview and top energy consumers. |
| O2 | Monitoring | Check the operational status and daily energy use of Compressor-1. | Manual review of machine-health and operational-status dashboard evidence. | Assistant-supported retrieval of Compressor-1 status and energy-use information. |
| O3 | Documentation | Understand ISO 50001 and the meaning of an energy baseline. | Manual review of energy-management learning and baseline documentation evidence. | Chatbot-supported retrieval of ISO 50001 and energy-baseline explanations. |
| O4 | Documentation | Identify the policy / procedure guidance for anomaly or efficiency response. | Manual review of procedure and anomaly-context documentation evidence. | Chatbot-supported retrieval of anomaly-response and efficiency-response procedure guidance. |

## Technical User Tasks

| ID | DIA Module | Task Objective | Condition A Evidence Path | Condition B Evidence Path |
| --- | --- | --- | --- | --- |
| T1 | Monitoring | Review anomalies and identify the issue requiring attention. | Manual review of anomaly evidence and unresolved critical alert context. | Assistant-supported retrieval of recent anomaly information. |
| T2 | Analyses | Analyze Compressor-1 against baseline, forecast context, and recommendations. | Manual cross-check of machine-health, forecast, baseline, and opportunity evidence. | Assistant-supported analysis of performance, forecast context, and saving opportunities. |
| T3 | Analyses | Retrieve factory KPI and EnPI status for 2026-Q1. | Manual review of factory KPI / EnPI dashboard evidence. | Assistant-supported retrieval of energy performance indicator status. |
| T4 | Analyses / Documentation | Generate and summarize the April 2026 monthly report. | Manual report generation and summary from report evidence. | Assistant-supported April 2026 report generation and confirmation. |

## Measurement Fields

Each task was measured using the same fields in both conditions:

| Field | Description |
| --- | --- |
| Task completion time | Time required to reach the required task result. |
| Click count | Number of task-relevant browser interactions. |
| Screen count | Number of meaningful page, dashboard, report, or result-screen transitions. |
| Expert help | Whether external expert assistance was required. |
| Manual reasoning | Whether the user had to manually inspect dashboards, reports, or API-style outputs to derive the answer. |
| Success | Whether the required task result was obtained. |

## Success Criteria

| Task Group | Success Criteria |
| --- | --- |
| Operational tasks | The operational user obtains the required operational, documentation, or procedure answer. |
| Technical tasks | The technical user obtains the required monitoring, analysis, KPI, or report answer. |
| DIA coverage | Monitoring, Analyses, and Documentation are all represented in the task evidence. |

## KPI Mapping

| Proposal KPI | Benchmark Evidence |
| --- | --- |
| 30% reduction in operational-user energy-management effort | Operational task subtotal across O1-O4 |
| 25% reduction in technical-user intervention / effort | Technical task subtotal across T1-T4 |
| Integration of DIA modules including monitoring, analyses, and documentation | Task coverage across Monitoring, Analyses, and Documentation |

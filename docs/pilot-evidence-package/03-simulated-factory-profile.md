# Simulated Pilot Factory Profile

## Purpose
This document defines the simulated pilot factory profile used consistently in the KPI sheet, recording, video, and final evidence package.

## Reference Name
`HumanEnerDIA Simulated Pilot - Romanian Automotive Plastics Components Facility`

## Display Name Used In The Benchmark
`Simulated Romanian Pilot Factory`

## Pilot Summary

| Field | Frozen Value |
| --- | --- |
| Country | Romania |
| City / Industrial Area | Pitesti, Arges County |
| Industrial profile | Automotive supplier producing plastic and electro-mechanical interior components |
| Employees | 420 |
| Closed facility area | 18,000 m2 |
| Annual electricity use | 1,200 MWh |
| Production operations | 6 |
| Digital monitoring | Yes |
| Digital meters | 12 |
| SCADA / dashboards | Yes |
| Digital maturity | Medium |
| Energy-management readiness | Dedicated energy / maintenance coordination role in place |

## Why This Profile Fits The Existing System
- It matches the pilot-factory call and application criteria already present in the portal.
- It fits the current simulated equipment mix in the repo:
  - `Compressor-1`
  - `HVAC-Main`
  - `Conveyor-A`
  - `Hydraulic-Pump-1`
  - `Injection-Molding-1`
  - `Boiler-1`
- It supports the three required DIA proof areas:
  - Monitoring
  - Analyses
  - Documentation

## Equipment Narrative For The Demo
- `Injection-Molding-1` represents the main plastics production cell.
- `Compressor-1` supports pneumatic tools and automation.
- `HVAC-Main` represents environmental control for stable process conditions.
- `Conveyor-A` represents part flow between work areas.
- `Hydraulic-Pump-1` represents press-side utility support.
- `Boiler-1` represents thermal-process and facility-support loads.

## Frozen Personas
- `Operational user`: facility / production manager
- `Technical user`: energy / maintenance / automation engineer

## Frozen Conditions
- `Condition A`: HumanEnerDIA without OVOS and without chatbot
- `Condition B`: HumanEnerDIA with OVOS and chatbot enabled

## Frozen Reporting Periods
- Daily operational tasks: use current simulated day during rehearsal and recording.
- EnPI / compliance summary task: use `2026-Q1`.
- Monthly report generation task: use `April 2026`.
- Anomaly review task: keep one unresolved `critical` `Compressor-2` spike available for the technical-user flow.

## Disclosure Line For Video And Methodology
Use this exact language at the start of the benchmark and demo:

> This is a simulated pilot based on a representative Romanian manufacturing profile aligned with the HumanEnerDIA pilot-factory scope. The original field-trial host factory withdrew, so the KPI demonstration is being performed through a realistic A/B simulation on the existing HumanEnerDIA platform.

## Consistency Rules
- Use the same factory profile wording in both conditions and all task clips.
- Do not mix in older sample-factory identities from previous demo environments.
- Use `Compressor-1` as the default machine for machine-specific benchmark tasks unless rehearsal proves another machine is more stable.
- Keep the controlled anomaly scenario stable so `T1` always resolves to the recent `Compressor-2` alert.

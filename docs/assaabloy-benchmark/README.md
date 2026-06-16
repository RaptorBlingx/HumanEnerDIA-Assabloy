# ASSA ABLOY A/B Benchmark Package

This folder defines the real-partner ASSA ABLOY benchmark used to compare:

- Condition A: HumanEnerDIA without OVOS and without chatbot assistance.
- Condition B: HumanEnerDIA with OVOS and chatbot assistance.

The benchmark uses the imported ASSA ABLOY partner press-shop dataset, not the previous simulated Romanian factory scenario.

## Evidence Scope

- Factory: ASSA ABLOY Partner Press Shop
- Data source: private partner attachment received on 2026-06-10
- Git policy: raw partner files are not committed
- KPI period: 2025-05-01 through 2026-06-01
- Energy scope: Bret, Raster, and Dimeco press-shop meter groups
- Production scope: SQDC production rows for the imported presses
- Boundary rule: no per-press energy is allocated or invented
- Reference meter: Bret Transformer Meter (TRAFO 3) is retained as an upstream reference and excluded from KPI totals

## Benchmark Files

- [task-set.md](task-set.md): fixed A/B tasks, personas, modules, and stop criteria.
- [manual-paths.md](manual-paths.md): Condition A manual navigation paths.
- [expected-answers.md](expected-answers.md): expected real-data facts and assistant responses.
- [measurement-protocol.md](measurement-protocol.md): measurement rules, KPI formulas, and export process.
- [ovos-runtime.md](ovos-runtime.md): separate OVOS runtime setup for Condition B.

## Committed KPI Targets

- 30% reduction in operational-user energy-management effort.
- 25% reduction in technical-user intervention need.
- DIA coverage across Monitoring, Analyses, and Documentation modules.

## Measurement Tool

Use the Chrome extension in `pilot-measurement-extension/`. It records elapsed time, clicks, screen changes, success, expert-help flag, and manual-reasoning flag across the browser-based HumanEnerDIA flow.

The extension task list is already aligned with the ASSA ABLOY task set in this folder.

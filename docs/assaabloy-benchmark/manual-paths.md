# Condition A Manual Paths

Use these paths for Condition A. They keep the manual condition inside HumanEnerDIA without OVOS or chatbot support.

## Common Entry Points

- Portal: `http://localhost:8080/`
- Analytics UI: `http://localhost:8080/api/analytics/ui/`
- KPI Dashboard: `http://localhost:8080/api/analytics/ui/kpi`
- Baseline UI: `http://localhost:8080/api/analytics/ui/baseline`
- Model Performance: `http://localhost:8080/api/analytics/ui/model-performance`
- Reports: `http://localhost:8080/reports.html`
- Grafana: `http://localhost:8080/grafana`

## O1 - Partner KPI Overview

1. Open `http://localhost:8080/api/analytics/ui/kpi`.
2. Use KPI Scope `ASSA ABLOY Partner Press Shop` or the default partner factory scope.
3. Use Time Period `Partner Dataset Period`.
4. Click `Load Data` if data is not already loaded.
5. Stop when the cards/table show total energy `141,254.85 kWh`, total production `27,625,665 units`, and group SEC values.

## O2 - Energy Group Comparison

1. Open `http://localhost:8080/api/analytics/ui/kpi`.
2. Keep the partner factory scope and partner period.
3. Review the energy-by-meter-group chart/table.
4. Stop when Dimeco, Raster, and Bret group-energy values are identified.

## O3 - Production And SEC Meaning

1. Open `http://localhost:8080/api/analytics/ui/kpi`.
2. Review the production and SEC chart/table for partner groups.
3. Open `http://localhost:8080/energy-management-learning.html` only if the SEC or EnPI concept must be explained manually.
4. Stop when SEC is understood and group SEC values are identified.

## O4 - Baseline Concept And Active Baselines

1. Open `http://localhost:8080/api/analytics/ui/baseline`.
2. Review the partner meter-group baseline context.
3. Open `http://localhost:8080/api/analytics/ui/model-performance`.
4. Stop when active baselines for Bret, Raster, and Dimeco meter groups are identified.

## T1 - Data Inventory Verification

1. Open [../ASSA-ABLOY-DATA-VERIFICATION.md](../ASSA-ABLOY-DATA-VERIFICATION.md).
2. Review the Imported Assets, Energy Reconciliation, and SQDC Reconciliation sections.
3. Optionally open the profile API in the browser: `http://localhost:8080/api/analytics/api/v1/partner-press/summary?question_type=data_inventory`.
4. Stop when `1,978` energy rows and `6,336` materialized production rows are identified.

## T2 - Meter Boundary And Per-Press Guardrail

1. Open [../partner-press-data-ingestion.md](../partner-press-data-ingestion.md).
2. Review the Source Package, Mapping, and Expected Data Profile sections.
3. Optionally open `http://localhost:8080/api/analytics/api/v1/partner-press/summary?question_type=reference_meter`.
4. Optionally open `http://localhost:8080/api/analytics/api/v1/partner-press/summary?question_type=press_energy&press=Bret125-1`.
5. Stop when the transformer boundary and no-per-press-energy rule are identified.

## T3 - SEU And Baseline Readiness

1. Open `http://localhost:8080/api/analytics/ui/model-performance`.
2. Review partner model status for Bret, Raster, and Dimeco meter groups.
3. Open `http://localhost:8080/api/analytics/api/v1/partner-press/ml-readiness` only if the UI does not show the required baseline detail.
4. Stop when the three partner SEUs and `3 of 3` active baselines are identified.

## T4 - Monthly Reporting

1. Open `http://localhost:8080/reports.html`.
2. Select `ASSA ABLOY Partner Press Shop`.
3. Select year `2026`.
4. Select month `May`.
5. Generate the monthly energy report.
6. Stop when the report is generated or the download is ready.

## Measurement Note

Opening raw JSON endpoints is acceptable for technical Condition A tasks only when the equivalent HumanEnerDIA UI does not expose the exact verification fact. Keep this consistent across trials and record screen/click counts normally.

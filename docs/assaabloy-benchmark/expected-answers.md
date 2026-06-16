# ASSA ABLOY Expected Answers

These are the expected facts for the real-partner dataset. They should be used to judge task success in the A/B benchmark.

## Core Dataset Facts

- KPI period: `2025-05-01` through `2026-06-01`.
- Energy rows: `1,978` total.
- Press-group meter rows: `1,235`.
- Bret transformer reference rows: `743`.
- Materialized production rows: `6,336`.
- Per-press SQDC rows: `5,148`.
- Derived group production rows: `1,188`.
- Total press-shop group-meter energy: `141,254.85 kWh`.
- Total group production: `27,625,665 units`.

## Energy By Meter Group

- Bret Presses Meter Group: `39,611.06 kWh`.
- Raster Presses Meter Group: `41,981.81 kWh`.
- Dimeco Presses Meter Group: `59,661.97 kWh`.

## Production By Group

- Bret Presses Meter Group: `7,797,167 units`.
- Raster Presses Meter Group: `7,756,785 units`.
- Dimeco Presses Meter Group: `12,071,713 units`.

## SEC Values

- Bret Presses Meter Group: `0.005080 kWh/unit`.
- Raster Presses Meter Group: `0.005412 kWh/unit`.
- Dimeco Presses Meter Group: `0.004942 kWh/unit`.

SEC means specific energy consumption: energy used per produced unit. Lower SEC is better when product mix is comparable.

## Transformer Boundary

- Reference meter: `Bret Transformer Meter (TRAFO 3)`.
- Reference rows: `743` hourly readings.
- Reference energy: `263,999.16 kWh`.
- Boundary: this meter is retained as an upstream reference and excluded from Bret press-group energy, total press-shop energy, and SEC.

## Baseline And SEU Readiness

- Partner SEUs:
  - Bret Presses Electricity
  - Dimeco Presses Electricity
  - Raster Presses Electricity
- Active EnPI baselines: `3 of 3` partner meter groups.
- Modeling boundary: ML baselines and forecasts target group-meter energy assets only; presses have production data only.

## Per-Press Energy Guardrail

For individual presses such as `Bret125-1` and `Rast125-2`, the correct answer is that no per-press energy is available. Energy is only metered at Bret, Raster, and Dimeco group level, so HumanEnerDIA/OVOS must not allocate or invent energy for an individual press.

## Recommended Assistant Prompts

- `Show KPIs for the ASSA ABLOY partner press shop`
- `Compare Bret, Raster, and Dimeco energy consumption`
- `Explain SEC for the partner press shop`
- `What is an energy baseline?`
- `Which partner meter groups have baselines?`
- `How many readings and rows were imported for ASSA ABLOY?`
- `What does the Bret transformer reference meter show?`
- `Energy consumption of Bret125-1`
- `What are the significant energy uses in the partner press shop?`
- `download the ASSA ABLOY partner press shop report for May 2026`

## Voice-Optimized Expected OVOS Responses

The Condition B OVOS responses are intentionally concise so the benchmark measures assisted task completion rather than long text-to-speech playback.

- `Show KPIs for the ASSA ABLOY partner press shop`
  Expected: total energy `141,254.85 kWh`, production `27,625,665 units`, and SEC values for Dimeco `0.004942`, Raster `0.005412`, and Bret `0.005080 kWh/unit`.
- `Compare Bret, Raster, and Dimeco energy consumption`
  Expected: Dimeco `59,661.97 kWh`, Raster `41,981.81 kWh`, and Bret `39,611.06 kWh`.
- `Explain SEC for the partner press shop`
  Expected: SEC is `kWh per produced unit`, with Dimeco `0.004942`, Raster `0.005412`, and Bret `0.005080 kWh/unit`.
- `Which partner meter groups have baselines?`
  Expected: `3 of 3` active baselines for the Bret, Dimeco, and Raster meter groups.
- `How many readings and rows were imported for ASSA ABLOY?`
  Expected: `1,978` energy readings and `6,336` production rows, including `1,235` group-meter, `743` transformer, and `5,148` per-press SQDC rows.
- `What does the Bret transformer reference meter show?`
  Expected: `743` readings and `263,999.16 kWh`, marked as reference-only and excluded from KPIs and SEC.
- `Energy consumption of Bret125-1`
  Expected: no direct per-press energy meter; energy is only available for Bret, Raster, and Dimeco groups.
- `What are the significant energy uses in the partner press shop?`
  Expected: Bret Presses Electricity, Dimeco Presses Electricity, and Raster Presses Electricity.
- `download the ASSA ABLOY partner press shop report for May 2026`
  Expected in the browser widget: May 2026 monthly report-ready/download response.

## Prompts To Avoid

- Avoid old simulated-factory prompts such as `Compressor-1`, `Boiler-1`, `Injection-Molding-1`, or generic anomaly tasks.
- Avoid `show energy performance indicator report` for this benchmark because that phrase is reserved for the previous simulated EnPI fallback path.
- Avoid report prompts that omit `ASSA ABLOY` or `partner press shop`; the report resolver needs the partner context to select the correct factory.

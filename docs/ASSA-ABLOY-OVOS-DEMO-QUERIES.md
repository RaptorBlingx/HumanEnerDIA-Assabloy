# ASSA ABLOY OVOS Demo Queries

Official benchmark prompts should be tested against the running OVOS REST bridge:

```text
POST http://localhost:5000/query
```

The recommended benchmark subset below uses voice-optimized responses: enough
information to complete the task, without unnecessary text-to-speech playback.

## Recommended Demo Sequence

1. `Show KPIs for the ASSA ABLOY partner press shop`
   - Energy 141,254.85 kWh, production 27,625,665 units, and SEC for all three groups.
2. `What are the top energy consumers in the partner press shop?`
   - Dimeco first, Raster second, Bret third.
3. `Compare Bret, Raster, and Dimeco energy consumption`
   - Dimeco 59,661.97 kWh, Raster 41,981.81 kWh, Bret 39,611.06 kWh.
4. `What does the Bret transformer reference meter show?`
   - 743 readings and 263,999.16 kWh, reference-only and excluded from KPIs.
5. `How many readings and rows were imported for ASSA ABLOY?`
   - 1,978 energy readings, 6,336 production rows, plus the key row splits.
6. `Energy consumption of Bret125-1`
   - Correctly refuses to invent per-press energy.

## Overview And Energy

7. `Give me an overview of the partner press shop`
   - Returns the partner-only energy ranking and total.
8. `What was the total energy use for the ASSA ABLOY press shop?`
   - 141,254.85 kWh for the configured KPI period.
9. `How much energy did the Bret press group use?`
   - 39,611.06 kWh.
10. `How much energy did the Raster press group use?`
    - 41,981.81 kWh.
11. `How much energy did the Dimeco press group use?`
    - 59,661.97 kWh.
12. `What are the top energy consumers?`
    - Uses the ASSA ABLOY pilot by default and returns the three meter groups.

## Production

13. `What was the production quantity for Bret presses?`
    - 7,797,167 units.
14. `What was the production quantity for Raster presses?`
    - 7,756,785 units.
15. `What was the production quantity for Dimeco presses?`
    - 12,071,713 units.
16. `How many units did Bret125-1 produce?`
    - 3,373,086 units.
17. `How many units did Bret160-1 produce?`
    - 1,019,033 units.
18. `How many units did Bret250-2 produce?`
    - 1,649,618 units.
19. `How many units did Dimeco80-1 produce?`
    - 3,687,138 units.
20. `How many units did Flexi-1 produce?`
    - 1,032,901 units.
21. `How many units did Rast125-2 produce?`
    - 2,342,966 units in the Dimeco physical group.
22. `Production quantity for Raster160`
    - Resolves the spoken alias to Rast160-1: 3,174,686 units.
23. `How many units did Rast250-1 produce?`
    - Correctly reports zero units from the SQDC source.

## KPIs And ISO 50001

24. `Show the KPIs for the Bret press group`
    - 39,611.06 kWh, 7,797,167 units, SEC 0.005080 kWh/unit.
25. `What is the SEC for the Raster press group?`
    - 0.005412 kWh/unit.
26. `Show the Dimeco performance indicators`
    - SEC 0.004942 kWh/unit.
27. `Explain SEC for the partner press shop`
    - Defines SEC as kWh per produced unit and lists all group values.
28. `What are the significant energy uses in the partner press shop?`
    - Bret, Dimeco, and Raster Presses Electricity.
29. `Which partner meter groups have baselines?`
    - Active EnPI baselines for 3 of 3 partner meter groups.

## Data Scope And Integrity

30. `What machines and meters are in the ASSA ABLOY press shop?`
    - 3 group meters, 13 presses, and 1 transformer reference meter.
31. `What data period is available for the partner press shop?`
    - Energy 2025-04-01 through 2026-05-31; production 2025-05-01
      through 2026-05-31.
32. `What is the latest live energy for the partner press shop?`
    - Clearly states that the package is historical, not live.
33. `Are there any anomalies in the ASSA ABLOY press shop?`
    - No partner anomalies are currently recorded.
34. `Are there any current alerts?`
    - No partner anomalies are currently recorded.
35. `Production for unknown press`
    - Gives a controlled unknown-press response and lists known presses.

## Monthly Questions

36. `How much energy did the ASSA ABLOY press shop use in March 2026?`
    - 13,482.15 kWh across the three group meters.
37. `How much energy did Bret use in March 2026?`
    - 3,535.31 kWh.
38. `How much energy did the press shop use in April 2025?`
    - 6,823.63 kWh; Dimeco has no April source rows.

## Guardrail Questions

39. `Energy consumption of Rast125-2`
    - Refuses per-press energy allocation; production remains available.
40. `How much energy did Boiler-1 use?`
    - Rejects the simulator asset as outside the ASSA ABLOY dataset.

## Operator Check

```bash
curl -sS -X POST http://localhost:5000/query \
  -H 'Content-Type: application/json' \
  -d '{"text":"Show KPIs for the ASSA ABLOY partner press shop"}'

docker exec ovos-enms sh -lc \
  "tail -n 80 /var/log/ovos/skills.out.log"
```

Expected structured intent for partner answers:

```text
partner_press_pilot
```

Expected out-of-scope intent:

```text
partner_press_out_of_scope_asset
```

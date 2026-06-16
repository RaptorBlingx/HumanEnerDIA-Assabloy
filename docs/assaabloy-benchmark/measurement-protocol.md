# ASSA ABLOY Measurement Protocol

## Measurement Principle

The benchmark compares the same fixed task set in two conditions:

- Condition A: manual HumanEnerDIA use without OVOS and without chatbot.
- Condition B: HumanEnerDIA with OVOS and chatbot support.

The measurement unit is a user task. Each task should be run once for a rehearsal and then one or more official trials. If multiple official trials are recorded, use the median value per condition.

## Recorded Metrics

For every task, record:

- elapsed task time in seconds
- click count
- screen count
- expert-help flag
- manual-reasoning flag
- success flag

The Chrome extension records elapsed time, clicks, and screen changes automatically across supported browser pages. The user sets the task, condition, trial, success, expert-help, manual-reasoning, and auto-stop flags.

## Start And Stop Rules

- Condition A starts when the first manual action toward the task begins.
- Condition A stops when the expected answer is visible and can be copied into the benchmark result.
- Condition B starts when the assistant query begins.
- For OVOS widget tasks, the extension can start from the assistant event and stop when the response-complete event fires.
- For chatbot tasks, the timer starts automatically when typing begins in the chat input.
- For multi-prompt tasks, disable `Auto` in the extension and click `Answer Found` manually after the final response is visible.

## Default Flags

- Expert Help: `0` unless a human expert must explain where to find or interpret the answer.
- Manual Reasoning in Condition A: `1`.
- Manual Reasoning in Condition B: `0` when the assistant directly provides the answer.
- Success: `1` only when the answer matches [expected-answers.md](expected-answers.md).

## KPI Calculation

Per-task time reduction:

```text
(A_time - B_time) / A_time * 100
```

Per-task click reduction:

```text
(A_clicks - B_clicks) / A_clicks * 100
```

Per-task screen reduction:

```text
(A_screens - B_screens) / A_screens * 100
```

Per-task measured effort reduction is the average of the available time, click, and screen reductions.

Operational-user effort KPI:

```text
average measured effort reduction across O1, O2, O3, O4
target >= 30%
```

Technical-user intervention KPI:

```text
average measured effort reduction across T1, T2, T3, T4
target >= 25%
```

The manual-reasoning and expert-help flags are retained as supporting evidence for reduced intervention need.

## Export And Summarize

After the official A/B trials:

1. Use the extension `Copy Raw` or popup export.
2. Save the raw CSV under `evidence/measurements/`.
3. Run:

```bash
scripts/lab/summarize_ab_results.py evidence/measurements/raw-extension-export.csv
```

The script writes:

```text
evidence/measurements/assaabloy-kpi-summary.csv
```

The summary prints whether the 30% operational and 25% technical targets were met.
Overall KPI percentages are calculated from tasks that have both Condition A and Condition B records. Incomplete task rows remain visible in the CSV and must be completed before using the result as final benchmark evidence.
The summary script marks a KPI target as met only when all four tasks for that persona are complete.

## DIA Module Coverage

The task set covers:

- Monitoring: O1, O2
- Analyses: O3, O4, T3, T4
- Documentation: O3, O4, T1, T2, T4

This satisfies the required DIA module evidence across Monitoring, Analyses, and Documentation.

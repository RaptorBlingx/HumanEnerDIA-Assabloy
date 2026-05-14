# Video Editing Guide

For the full record-and-edit workflow, use [video-production-playbook.md](video-production-playbook.md). This file remains the focused editing reference.

Use this guide after recording short task clips. The recommended final video is one edited benchmark video organized by task: show `Condition A` first, then `Condition B`, then a short comparison card for that same task.

## Editing Goal
The video should make the KPI argument easy to follow:

- The same task is attempted manually in `Condition A`.
- The same task is repeated with OVOS/chatbot support in `Condition B`.
- The viewer sees the effort difference immediately after each A/B pair.
- The final section consolidates the task results into the proposal KPI story.

## Recommended Final Video Structure
1. Opening title and disclosure.
2. Methodology slide.
3. Eight task rounds:
   - `A` manual clip
   - `B` assistant clip
   - task comparison card
4. Operational-user subtotal.
5. Technical-user subtotal.
6. Final KPI summary.
7. Closing evidence-pack slide.

## Opening Title
On-screen text:

```text
HumanEnerDIA Simulated Pilot Benchmark
Romanian manufacturing profile
A/B comparison: manual workflow vs OVOS + chatbot support
```

Voiceover:

```text
This is a simulated pilot based on a representative Romanian manufacturing profile aligned with the HumanEnerDIA pilot-factory scope. The original field-trial host factory withdrew, so the KPI demonstration is being performed through a realistic A/B simulation on the existing HumanEnerDIA platform.
```

## Methodology Slide
On-screen text:

```text
Methodology
Same factory profile
Same personas
Same task set
Same browser and screen setup
Measured with the Pilot Measurement Chrome extension
Metrics: time, clicks, screens, expert help, manual reasoning, success
```

Voiceover:

```text
The benchmark compares the same tasks under two conditions. Condition A uses HumanEnerDIA without OVOS and without the chatbot. Condition B repeats the same tasks with OVOS and chatbot support. The Pilot Measurement Chrome extension records task time, click count, screen count, expert-help need, manual-reasoning need, and success.
```

## Task Round Order
Use this exact order:

| Round | Persona | Module | Task |
| --- | --- | --- | --- |
| `O1` | Operational user | Monitoring | Factory overview and top 3 energy consumers |
| `O2` | Operational user | Monitoring | `Compressor-1` status and today's energy |
| `O3` | Operational user | Documentation | ISO 50001 and energy baseline understanding |
| `O4` | Operational user | Documentation | Anomaly and efficiency response procedure |
| `T1` | Technical user | Monitoring | Recent anomalies and issue requiring attention |
| `T2` | Technical user | Analyses | Baseline, forecast, and recommendations |
| `T3` | Technical user | Analyses | KPI and EnPI status for `2026-Q1` |
| `T4` | Technical user | Analyses / Documentation | April 2026 monthly report |

## Clip Naming
Use simple filenames so editing and KPI lookup stay aligned:

```text
O1-A-manual.mp4
O1-B-assistant.mp4
O2-A-manual.mp4
O2-B-assistant.mp4
...
T4-A-manual.mp4
T4-B-assistant.mp4
```

If you record multiple takes, add a suffix:

```text
O1-A-manual-take2.mp4
```

Only use the official take in the final edit and in the KPI sheet.

## Per-Task Segment Template
Each task round should follow this pattern.

### Task Title Card
On-screen text:

```text
Task O1 - Factory overview and top 3 energy consumers
Persona: Operational user
Module: Monitoring
```

Voiceover:

```text
This round compares the manual workflow with the assistant-supported workflow for the same task.
```

### Condition A Clip Label
On-screen text:

```text
Condition A - Manual workflow
No OVOS
No chatbot
```

Voiceover:

```text
In Condition A, the user completes the task by manually navigating HumanEnerDIA, Grafana, analytics views, or reports.
```

### Condition B Clip Label
On-screen text:

```text
Condition B - Assistant-supported workflow
OVOS and chatbot enabled
```

Voiceover:

```text
In Condition B, the same task is completed using OVOS or the chatbot, depending on the task type.
```

### Task Comparison Card
Show this immediately after the `B` clip for the same task.

On-screen table:

```text
Task O1 comparison
A time: [A seconds]
B time: [B seconds]
Time reduction: [percent]
A clicks/screens: [A clicks] / [A screens]
B clicks/screens: [B clicks] / [B screens]
Expert help: A [0/1] | B [0/1]
Manual reasoning: A [0/1] | B [0/1]
Success: A [0/1] | B [0/1]
```

Voiceover:

```text
For this task, the assistant-supported workflow reduced completion time and interaction effort while preserving task success.
```

If a task does not show a strong time reduction but still reduces manual reasoning or expert-help need, use:

```text
For this task, the main improvement is reduced manual dashboard hunting and direct access to the required information.
```

## Per-Task Overlay Text
Use these exact task labels in the video.

| Task | Condition A label | Condition B label |
| --- | --- | --- |
| `O1` | `Manual: Grafana factory overview and top consumers` | `Assistant: OVOS factory overview and top consumers` |
| `O2` | `Manual: Grafana machine status and energy` | `Assistant: OVOS machine status and energy` |
| `O3` | `Manual: learning page and baseline context` | `Assistant: chatbot standards explanation` |
| `O4` | `Manual: pilot procedure reference` | `Assistant: chatbot procedure guidance` |
| `T1` | `Manual: anomaly page / Grafana anomaly review` | `Assistant: OVOS recent anomalies` |
| `T2` | `Manual: baseline, forecast, and opportunities pages` | `Assistant: OVOS analysis, forecast, and opportunities` |
| `T3` | `Manual: KPI and EnPI report pages` | `Assistant: OVOS EnPI status` |
| `T4` | `Manual: reports page and April 2026 report generation` | `Assistant: OVOS April 2026 report download` |

## What To Keep Visible
- Keep the Chrome extension overlay visible during timed task execution when it does not hide important evidence.
- If the overlay covers a dashboard panel, drag it away before starting the task timer.
- Keep the timer and task ID visible at the start and end of each task clip.
- Keep the final answer/evidence visible before clicking `Answer Found`.
- For OVOS tasks, keep the OVOS text response visible and keep the voice playback audible.
- For chatbot tasks, keep the prompt and final chatbot answer visible.

## What To Cut Out
Cut these from the final edited video:

- login time
- browser setup
- extension reloads
- failed rehearsal takes
- typing mistakes before the official task starts
- time spent arranging windows before `Start Task`
- waiting after `Answer Found`

Do not cut inside the measured task window unless the cut is clearly marked. The timed task segment should remain honest and understandable.

If you speed up any task footage, label it:

```text
Playback speed changed for viewing only. KPI timing comes from the measurement extension.
```

Best practice: do not speed up the timed task footage unless the final video becomes too long.

## Comparison Timing
Show a short comparison card after every A/B task pair. This helps reviewers understand the improvement immediately.

Also show a final consolidated comparison at the end. The final table is where the KPI thresholds are evaluated.

Do not wait until the end only. If the viewer sees eight tasks without intermediate comparisons, the KPI story becomes harder to follow.

## Operational-User Subtotal
Show this after `O4`.

On-screen text:

```text
Operational-user subtotal
Tasks: O1-O4
Target KPI: 30% reduction in operational energy-management effort
Measured from task time, clicks/screens, manual reasoning, and success
```

Voiceover:

```text
The operational-user tasks show whether OVOS and the chatbot reduce the effort needed to understand monitoring results, standards, procedures, and documentation.
```

## Technical-User Subtotal
Show this after `T4`.

On-screen text:

```text
Technical-user subtotal
Tasks: T1-T4
Target KPI: 25% reduction in technical intervention need
Measured from task time, clicks/screens, expert-help need, manual reasoning, and success
```

Voiceover:

```text
The technical-user tasks show whether assistant support reduces the effort required to monitor, analyse, and report energy-efficiency information.
```

## Final KPI Summary
Use the completed KPI sheet and extension exports.

On-screen text:

```text
Final KPI summary
Operational-user effort reduction: [percent] target >= 30%
Technical-user intervention reduction: [percent] target >= 25%
DIA modules demonstrated: Monitoring, Analyses, Documentation
```

Voiceover:

```text
The A/B benchmark shows the measured impact of assistant support on the same task set. The results are calculated from recorded task completion time, clicks, screen count, expert-help need, manual-reasoning need, and task success.
```

## Final Evidence Slide
On-screen text:

```text
Evidence package
Final edited benchmark video
Raw A/B task clips
Pilot Measurement extension export
KPI comparison sheet
Methodology note
Simulated factory profile
```

Voiceover:

```text
The evidence package keeps the simulated-pilot claim separate from a real factory deployment claim and links the measured A/B results to the proposal KPIs.
```

## Editing Rules For Objectivity
- Use the same task wording for `A` and `B`.
- Use the same browser zoom and screen resolution for all clips.
- Do not include setup time before `Start Task`.
- Do not include explanation time after `Answer Found`.
- Do not hide failed task outcomes. If a task fails, mark `Success = 0` and explain it in the KPI notes.
- Do not manually change extension results in the video. If a measurement is wrong, redo the task or use `Delete Last Try` before exporting.
- Keep the simulated-pilot disclosure in the opening and final methodology package.

## Recommended Final Length
- Opening and methodology: `45-60 seconds`
- Each A/B task round: `60-120 seconds`, depending on task complexity
- Per-task comparison card: `8-12 seconds`
- Operational subtotal: `10-15 seconds`
- Technical subtotal: `10-15 seconds`
- Final KPI summary and evidence slide: `30-45 seconds`

Target final edited video length: `12-18 minutes`.

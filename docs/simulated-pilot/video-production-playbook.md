# Video Production Playbook

Use this as the single operational guide for recording and editing the simulated pilot benchmark video. It combines the manual script, assistant script, and editing guide into one step-by-step workflow.

Source references:
- [video-script-a.md](video-script-a.md)
- [video-script-b.md](video-script-b.md)
- [video-editing-guide.md](video-editing-guide.md)
- [browser-extension-pilot-measurement.md](browser-extension-pilot-measurement.md)

## Final Output

Create one final edited benchmark video, not two separate final videos.

There are two different timelines:

- Recording timeline: this is how you capture the raw evidence clips.
- Editing timeline: this is how you arrange those clips into the final video.

Do not mix these two steps. During recording, your job is only to capture clean evidence clips with the Pilot Measurement extension visible. During editing, your job is to add title cards, labels, voiceover, comparison cards, and the final KPI summary.

The final video order is:

1. Opening title and simulated-pilot disclosure.
2. Methodology slide.
3. `O1` task round: title card, `A` manual clip, `B` assistant clip, comparison card.
4. `O2` task round: title card, `A` manual clip, `B` assistant clip, comparison card.
5. `O3` task round: title card, `A` manual clip, `B` assistant clip, comparison card.
6. `O4` task round: title card, `A` manual clip, `B` assistant clip, comparison card.
7. Operational-user subtotal.
8. `T1` task round: title card, `A` manual clip, `B` assistant clip, comparison card.
9. `T2` task round: title card, `A` manual clip, `B` assistant clip, comparison card.
10. `T3` task round: title card, `A` manual clip, `B` assistant clip, comparison card.
11. `T4` task round: title card, `A` manual clip, `B` assistant clip, comparison card.
12. Technical-user subtotal.
13. Final KPI summary.
14. Evidence package slide.

Do not wait until the end to show all comparisons. Show a short comparison card after every A/B task pair, then show the consolidated KPI summary at the end.

## End-To-End Timeline

Follow this order from start to finish.

### Phase 1 - Prepare Once

Do this before recording any official clip:

1. Open Chrome.
2. Reload the `HumanEnerDIA Pilot Measurement` extension at `chrome://extensions`.
3. Open `http://10.33.10.103:8080/index.html`.
4. Log in if needed.
5. Confirm the Pilot Measurement overlay appears.
6. Confirm the extension can count a sample click and screen change.
7. Confirm the screen recorder captures the browser screen.
8. Confirm audio capture works for microphone and browser audio.
9. Create a folder for raw clips.
10. Create a folder for final edited video assets.

Do not record the opening title, methodology slide, task labels, or comparison cards yet. Those are editing assets, not raw evidence clips.

### Phase 2 - Record Raw Evidence Clips

Recommended recording order:

1. Set `manual` mode once.
2. Record all `Condition A` clips: `O1-A`, `O2-A`, `O3-A`, `O4-A`, `T1-A`, `T2-A`, `T3-A`, `T4-A`.
3. Set `assistant` mode once.
4. Record all `Condition B` clips: `O1-B`, `O2-B`, `O3-B`, `O4-B`, `T1-B`, `T2-B`, `T3-B`, `T4-B`.

This is the cleanest workflow because it avoids switching between manual and assistant modes after every task.

Allowed alternative:

```text
O1-A, O1-B, O2-A, O2-B, ... T4-A, T4-B
```

Use the alternative only if you strongly prefer checking each A/B pair immediately. The final edited video is the same either way.

For each raw clip:

1. Start the screen recorder.
2. Set the extension condition and task.
3. Start the task timer.
4. Perform the task.
5. Stop the task timer with `Answer Found` or assistant auto-stop.
6. Keep the extension overlay visible for a few seconds.
7. Stop the screen recorder.
8. Rename the clip immediately using the official clip name.

Important: do not add title cards, labels, subtitles, or voiceover during raw recording. If you need to speak during Condition A, keep it outside the measured task window. OVOS speech in Condition B is different because it is part of the measured assistant interaction.

### Phase 3 - Export Measurements

Do this after all raw clips are recorded:

1. Open the Pilot Measurement extension overlay or popup.
2. Click `Copy Raw`.
3. Save the raw rows with the evidence package.
4. Click `Copy KPI`.
5. Paste the KPI rows into the KPI sheet.
6. Verify every task has an `A` row and a `B` row.
7. Verify time, clicks, screens, expert help, manual reasoning, and success.
8. Calculate the reduction percentages.

Do not build comparison cards before this phase. The comparison cards need the final measured values.

### Phase 4 - Build The Edited Video Timeline

Now open your video editor and build the final timeline in this order:

1. Add the opening title card.
2. Add the opening disclosure voiceover.
3. Add the methodology slide.
4. Add the methodology voiceover.
5. Add the `O1` title card.
6. Add the `Condition A` label.
7. Insert `O1-A-manual.mp4`.
8. Add the `Condition B` label.
9. Insert `O1-B-assistant.mp4`.
10. Add the `O1` comparison card using measured values.
11. Repeat the same pattern for `O2`, `O3`, and `O4`.
12. Add the operational-user subtotal card.
13. Repeat the same pattern for `T1`, `T2`, `T3`, and `T4`.
14. Add the technical-user subtotal card.
15. Add the final KPI summary card.
16. Add the evidence package slide.
17. Export the final edited video.

This is when you add the text labels and voiceovers. The raw clips should remain evidence clips; the editing timeline explains them.

## Example Timeline For One Full Round

Use this example for `O1`. Every other task follows the same logic.

Recording stage:

1. Set manual mode.
2. Start screen recorder.
3. In the extension, select `A - Manual` and `O1 - Factory overview and top consumers`.
4. Click `Start Task`.
5. Complete the manual Grafana lookup.
6. Click `Answer Found`.
7. Stop screen recorder.
8. Save the raw clip as `O1-A-manual.mp4`.
9. Later, set assistant mode.
10. Start screen recorder.
11. In the extension, select `B - Assistant` and `O1 - Factory overview and top consumers`.
12. Ask the two OVOS prompts.
13. Click `Answer Found` after the second voice answer finishes.
14. Stop screen recorder.
15. Save the raw clip as `O1-B-assistant.mp4`.

Measurement stage:

1. Export `Copy Raw` and `Copy KPI`.
2. Read the measured `O1-A` and `O1-B` values.
3. Calculate the `O1` time reduction and confirm clicks/screens, expert help, manual reasoning, and success.

Editing stage:

1. Add title card: `Task O1 - Factory overview and top 3 energy consumers`.
2. Add voiceover: `This round compares the manual workflow with the assistant-supported workflow for the same task.`
3. Add label card or lower-third: `Condition A - Manual workflow`.
4. Insert `O1-A-manual.mp4`.
5. Add label card or lower-third: `Condition B - Assistant-supported workflow`.
6. Insert `O1-B-assistant.mp4`.
7. Add `O1` comparison card with the measured A/B values.
8. Add comparison voiceover explaining the improvement.

The evaluator should see this sequence in the final video:

```text
O1 title -> A label -> O1-A clip -> B label -> O1-B clip -> O1 comparison
```

## What Goes Where

Use this table to decide what belongs in raw recording versus editing.

| Item | Add During Raw Recording? | Add During Editing? |
| --- | --- | --- |
| Pilot Measurement extension overlay | Yes | Already visible inside raw clip |
| Manual task navigation | Yes | Insert raw clip only |
| OVOS prompt and voice playback | Yes | Insert raw clip with audio |
| Chatbot prompt and answer | Yes | Insert raw clip only |
| Opening title | No | Yes |
| Methodology slide | No | Yes |
| Task title card | No | Yes |
| `Condition A` / `Condition B` labels | No | Yes |
| Lower-third task label | No | Yes |
| Explanatory voiceover | No, except first clip intro if wanted outside timing | Yes |
| Per-task comparison card | No | Yes, after KPI values are available |
| Operational / technical subtotal | No | Yes |
| Final KPI summary | No | Yes |
| Evidence package slide | No | Yes |

## Simple Mental Model

Use this rule:

```text
Recording = evidence.
Editing = explanation.
```

If something proves what happened on screen, record it. If something explains the evidence to the evaluator, add it later in the edit.

## Global Recording Rules

- Record short clips per task, not one long final video.
- Recommended recording order is all `Condition A` clips first, then all `Condition B` clips. The final edited video still shows each task as `A` followed by `B`.
- If you prefer pair-by-pair recording, you may record `O1-A`, then `O1-B`, then move to `O2-A`, but do not edit until all clips and KPI values are ready.
- Keep the task wording identical in both conditions.
- Keep the same browser, zoom, screen resolution, and user account for all clips.
- Keep the Pilot Measurement extension visible at the start and end of every measured clip.
- Drag the extension overlay away from important evidence before starting the task timer.
- Do not include login, browser setup, window arrangement, extension reloads, or failed takes in the measured task time.
- Do not add narration inside the measured task window for Condition A. Add explanatory voiceover later in the edit.
- For Condition B OVOS clips, keep the real assistant voice playback audible because it is part of the official measured time.
- If a take is wrong, use `Delete Last Try` if already saved, or `Reset Current` if not saved, then record the task again.
- If using three trials for the KPI sheet, use the same number of trials for `A` and `B`. Do not use a best-of result for only one condition.

## Clip Names

Use these exact names for the official clips:

```text
O1-A-manual.mp4
O1-B-assistant.mp4
O2-A-manual.mp4
O2-B-assistant.mp4
O3-A-manual.mp4
O3-B-assistant.mp4
O4-A-manual.mp4
O4-B-assistant.mp4
T1-A-manual.mp4
T1-B-assistant.mp4
T2-A-manual.mp4
T2-B-assistant.mp4
T3-A-manual.mp4
T3-B-assistant.mp4
T4-A-manual.mp4
T4-B-assistant.mp4
```

For a failed or extra take, add a suffix such as:

```text
O1-A-manual-take2.mp4
```

Only use the official take in the final edit. Keep extra takes outside the evidence package unless they are needed for audit notes.

## Detailed Setup Before Recording

1. Open Chrome.
2. Reload the Chrome extension at `chrome://extensions` if you recently pulled code changes.
3. Open `http://10.33.10.103:8080/index.html`.
4. Log in before recording if login appears.
5. Confirm the `Pilot Measurement` overlay appears.
6. Confirm Grafana, analytics pages, reports, OVOS, and chatbot are reachable.
7. Confirm the browser zoom and screen resolution are fixed.
8. Confirm audio recording captures the microphone and browser audio clearly.
9. Confirm the extension can count a sample click and screen change.
10. Confirm `Copy Raw` and `Copy KPI` work in the extension.

## Manual Mode Setup

Use this before recording `Condition A` clips:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'manual');
location.href = '/index.html';
```

Confirm OVOS and chatbot are hidden or not used.

## Assistant Mode Setup

Use this before recording `Condition B` clips:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'assistant');
location.href = '/index.html';
```

Confirm OVOS and chatbot are visible.

For OVOS, use the wake word `Jarvis` if stable. If wake word recognition is unreliable, use typed OVOS prompts consistently for all OVOS tasks.

## Extension Checkbox Rules

For `Condition A`:

- `Condition`: `A - Manual`
- `Expert`: unchecked unless the task cannot be completed without a human expert
- `Manual reasoning`: checked
- `Success`: checked only if the required answer is found on screen
- `Auto-stop`: can stay checked, but it is not used for manual tasks

For `Condition B`:

- `Condition`: `B - Assistant`
- `Expert`: unchecked unless the assistant answer is not enough and a human expert would be needed
- `Manual reasoning`: unchecked unless you still need manual dashboard/API reasoning after the assistant response
- `Success`: checked only if the assistant answer is correct and completes the task
- `Auto-stop`: checked for single-prompt assistant tasks, unchecked for multi-prompt tasks and the report download task

## Editing Asset - Opening Title

Add this at the start of the edited video.

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

## Editing Asset - Methodology Slide

Add this immediately after the opening title.

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

## Editing Asset - Standard Task Round Pattern

Use this pattern for every task:

1. Add the task title card.
2. Add the `Condition A` label.
3. Insert the `Condition A` measured clip.
4. Add the `Condition B` label.
5. Insert the `Condition B` measured clip.
6. Add the task comparison card.

Task title card template:

```text
Task [ID] - [task name]
Persona: [Operational user or Technical user]
Module: [Monitoring, Analyses, Documentation]
```

Task title voiceover:

```text
This round compares the manual workflow with the assistant-supported workflow for the same task.
```

Condition A label:

```text
Condition A - Manual workflow
No OVOS
No chatbot
```

Condition A voiceover:

```text
In Condition A, the user completes the task by manually navigating HumanEnerDIA, Grafana, analytics views, or reports.
```

Condition B label:

```text
Condition B - Assistant-supported workflow
OVOS and chatbot enabled
```

Condition B voiceover:

```text
In Condition B, the same task is completed using OVOS or the chatbot, depending on the task type.
```

Task comparison card template:

```text
Task [ID] comparison
A time: [A seconds]
B time: [B seconds]
Time reduction: [percent]
A clicks/screens: [A clicks] / [A screens]
B clicks/screens: [B clicks] / [B screens]
Expert help: A [0/1] | B [0/1]
Manual reasoning: A [0/1] | B [0/1]
Success: A [0/1] | B [0/1]
```

Standard comparison voiceover:

```text
For this task, the assistant-supported workflow reduced completion time and interaction effort while preserving task success.
```

Use this alternative voiceover if the time reduction is small but the assistant still reduces manual search or interpretation effort:

```text
For this task, the main improvement is reduced manual dashboard hunting and direct access to the required information.
```

## Recording a Condition A Manual Clip

Use this flow for every `A` clip:

1. Start the screen recorder a few seconds before the task.
2. In the extension, set `Condition` to `A - Manual`.
3. Select the correct task ID.
4. Confirm `Expert` unchecked.
5. Confirm `Manual reasoning` checked.
6. Confirm `Success` checked.
7. Confirm the overlay is not hiding the target page or panel.
8. Click `Start Task` immediately before the first manual action.
9. Perform only the task actions.
10. Let the extension count clicks and screen changes automatically.
11. Use `+Screen` only if the visible screen changes but the URL/history/hash does not.
12. Click `Answer Found` as soon as the required answer is visibly found.
13. Keep the overlay and answer visible for a few seconds.
14. Stop the screen recorder.
15. Name the clip with the correct `A` filename.

## Recording a Condition B Assistant Clip

Use this flow for every `B` clip:

1. Start the screen recorder a few seconds before the task.
2. In the extension, set `Condition` to `B - Assistant`.
3. Select the same task ID as the matching `A` clip.
4. Confirm `Expert` unchecked.
5. Confirm `Manual reasoning` unchecked.
6. Confirm `Success` checked.
7. Set `Auto-stop` based on the task instructions below.
8. Confirm the overlay, OVOS, or chatbot does not hide the final answer.
9. Start the assistant task using the official prompt.
10. For OVOS tasks, wait until the text answer is visible and voice playback finishes.
11. For chatbot tasks, wait until the answer is visible.
12. For multi-prompt tasks, click `Answer Found` after the final answer is complete.
13. Keep the overlay and final answer visible for a few seconds.
14. Stop the screen recorder.
15. Name the clip with the correct `B` filename.

If auto-start does not trigger in a rehearsal, click `Start Task` immediately before the prompt and note this in the KPI notes. Do not change the rule during the official run unless the same fallback is used consistently.

## O1 Round - Factory Overview And Top Consumers

Title card:

```text
Task O1 - Factory overview and top 3 energy consumers
Persona: Operational user
Module: Monitoring
```

### O1 A Clip

Clip name: `O1-A-manual.mp4`

Lower-third label:

```text
Manual: Grafana factory overview and top consumers
```

Task prompt:

```text
Get a factory overview and identify the top 3 energy consumers.
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `A - Manual`.
3. Select `O1 - Factory overview and top consumers`.
4. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
5. Click `Start Task`.
6. Open `/index.html`.
7. Click the Grafana button or open the `Factory Overview` Grafana dashboard directly.
8. If the Grafana folder appears first, open `Factory Overview`.
9. Confirm the time range is `Today`.
10. Use panels `Energy Today`, `Current Power`, `Cost Today`, `Active Anomalies`, `Machine Status & Health`, and `Energy by Machine (Today)`.
11. If running/active machine count is needed, open `Operational Efficiency` and use `Machine Status Overview`.
12. Confirm the top consumers include `Compressor-2`, `Injection-Molding-1`, and `Compressor-1`.
13. Click `Answer Found` as soon as the factory overview and top consumers are visible.
14. Stop the screen recorder.

### O1 B Clip

Clip name: `O1-B-assistant.mp4`

Lower-third label:

```text
Assistant: OVOS factory overview and top consumers
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `B - Assistant`.
3. Select `O1 - Factory overview and top consumers`.
4. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
5. Uncheck `Auto-stop` because this task uses two OVOS prompts.
6. Say `Jarvis`, then ask `Give me a factory overview`.
7. Wait until the OVOS answer is visible and voice playback finishes.
8. Say `Jarvis`, then ask `Show top 3 energy consumers`.
9. Wait until the top-consumers answer is visible and voice playback finishes.
10. Confirm the answer includes `Compressor-2`, `Injection-Molding-1`, and `Compressor-1`.
11. Click `Answer Found`.
12. Stop the screen recorder.
13. Re-check `Auto-stop` before the next single-prompt task.

### O1 Comparison Card

Show the measured A/B values from the extension.

Voiceover:

```text
This task shows the monitoring effort difference. Manually, the user must locate the Grafana overview and inspect the relevant panels. With OVOS, the user receives the overview and top consumers directly.
```

## O2 Round - Compressor-1 Status And Today's Energy

Title card:

```text
Task O2 - Compressor-1 status and today's energy
Persona: Operational user
Module: Monitoring
```

### O2 A Clip

Clip name: `O2-A-manual.mp4`

Lower-third label:

```text
Manual: Grafana machine status and energy
```

Task prompt:

```text
Check the status and today's energy of Compressor-1.
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `A - Manual`.
3. Select `O2 - Compressor-1 status and today energy`.
4. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
5. Click `Start Task`.
6. Open the Grafana `Machine Health` dashboard for `Compressor-1`.
7. Confirm the time range is `Today`.
8. Use panels `Energy Today`, `Current Power`, and `Anomaly Details`.
9. If explicit running/stopped status is needed, open `Operational Efficiency` and use `Machine Status Overview`.
10. Confirm `Compressor-1` status and today's kWh are visible.
11. Click `Answer Found`.
12. Stop the screen recorder.

### O2 B Clip

Clip name: `O2-B-assistant.mp4`

Lower-third label:

```text
Assistant: OVOS machine status and energy
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `B - Assistant`.
3. Select `O2 - Compressor-1 status and today energy`.
4. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
5. Confirm `Auto-stop` checked.
6. Say `Jarvis`, then ask `What's the status of Compressor-1?`
7. Wait for the recorder to stop automatically after voice playback finishes.
8. Confirm the answer includes status, current power, and today's energy.
9. Stop the screen recorder.

### O2 Comparison Card

Voiceover:

```text
This task compares manual machine-dashboard lookup against a direct machine-status query through OVOS.
```

## O3 Round - ISO 50001 And Energy Baseline

Title card:

```text
Task O3 - ISO 50001 and energy baseline understanding
Persona: Operational user
Module: Documentation
```

### O3 A Clip

Clip name: `O3-A-manual.mp4`

Lower-third label:

```text
Manual: learning page and baseline context
```

Task prompt:

```text
Understand what ISO 50001 is and what an energy baseline means.
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `A - Manual`.
3. Select `O3 - ISO 50001 and energy baseline`.
4. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
5. Click `Start Task`.
6. Open `/energy-management-learning.html`.
7. Find `What ISO 50001 Means`.
8. Find `What An Energy Baseline Means`.
9. Open `/api/analytics/ui/baseline` only if you want supporting product context after the definitions are already visible.
10. Click `Answer Found` when both definitions have been found.
11. Stop the screen recorder.

### O3 B Clip

Clip name: `O3-B-assistant.mp4`

Lower-third label:

```text
Assistant: chatbot standards explanation
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `B - Assistant`.
3. Select `O3 - ISO 50001 and energy baseline`.
4. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
5. Uncheck `Auto-stop` because this task uses two chatbot prompts.
6. Open the chatbot.
7. Send `What is ISO 50001?`
8. Wait until the answer is visible.
9. Send `What is an energy baseline?`
10. Wait until the answer is visible.
11. Click `Answer Found`.
12. Stop the screen recorder.
13. Re-check `Auto-stop` if the next task is single-prompt.

### O3 Comparison Card

Voiceover:

```text
This task shows documentation access. Manually, the user searches the learning material. With the chatbot, the user receives the required standards and baseline explanation directly.
```

## O4 Round - Anomaly And Efficiency Response Procedure

Title card:

```text
Task O4 - Anomaly and efficiency response procedure
Persona: Operational user
Module: Documentation
```

### O4 A Clip

Clip name: `O4-A-manual.mp4`

Lower-third label:

```text
Manual: pilot procedure reference
```

Task prompt:

```text
Find the policy and procedure guidance for responding to an anomaly or efficiency issue.
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `A - Manual`.
3. Select `O4 - Anomaly or efficiency procedure`.
4. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
5. Click `Start Task`.
6. Open `/pilot-procedures.html`.
7. Find the anomaly response guidance section.
8. Find the efficiency issue response guidance section.
9. Open `/api/analytics/ui/anomaly` only if you want to show operational anomaly context.
10. Confirm the guidance includes review affected machine/time/severity, compare against baseline, check status and production context, decide monitor/escalate, and record the action.
11. Click `Answer Found`.
12. Stop the screen recorder.

### O4 B Clip

Clip name: `O4-B-assistant.mp4`

Lower-third label:

```text
Assistant: chatbot procedure guidance
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `B - Assistant`.
3. Select `O4 - Anomaly or efficiency procedure`.
4. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
5. Uncheck `Auto-stop` because this task uses two chatbot prompts.
6. Open the chatbot.
7. Send `What should we do when an anomaly appears?`
8. Wait until the answer is visible.
9. Send `What is the procedure for responding to an efficiency issue?`
10. Wait until the answer is visible.
11. Click `Answer Found`.
12. Stop the screen recorder.
13. Re-check `Auto-stop` before the next single-prompt task.

### O4 Comparison Card

Voiceover:

```text
This task compares manual procedure lookup against direct chatbot guidance for anomaly and efficiency response.
```

## Operational-User Subtotal

Place this after the `O4` comparison card.

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

## T1 Round - Recent Anomalies

Title card:

```text
Task T1 - Recent anomalies and issue requiring attention
Persona: Technical user
Module: Monitoring
```

### T1 A Clip

Clip name: `T1-A-manual.mp4`

Lower-third label:

```text
Manual: anomaly page / Grafana anomaly review
```

Task prompt:

```text
Review anomalies and identify the issue requiring attention.
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `A - Manual`.
3. Select `T1 - Review anomalies`.
4. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
5. Click `Start Task`.
6. Open `/api/analytics/ui/anomaly`.
7. Review the current or recent anomaly list.
8. If supporting Grafana evidence is needed, open `Anomaly Detection` with time range `Last 7 days`.
9. Use panels `Unresolved Anomalies`, `Critical Anomalies`, and `Top Machines by Anomaly Count` if needed.
10. Identify the unresolved high-severity or critical anomaly affecting `Compressor-2`, or the highest-severity visible anomaly at recording time.
11. Click `Answer Found`.
12. Stop the screen recorder.

### T1 B Clip

Clip name: `T1-B-assistant.mp4`

Lower-third label:

```text
Assistant: OVOS recent anomalies
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `B - Assistant`.
3. Select `T1 - Review anomalies`.
4. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
5. Confirm `Auto-stop` checked.
6. Say `Jarvis`, then ask `Show me recent anomalies`.
7. Wait for the recorder to stop automatically after voice playback finishes.
8. Confirm the assistant identifies recent anomalies and affected machines, including `Boiler-1` and `Compressor-2` when those are active.
9. Stop the screen recorder.

### T1 Comparison Card

Voiceover:

```text
This task compares manual anomaly review against a direct assistant summary of recent issues requiring attention.
```

## T2 Round - Baseline, Forecast, And Recommendations

Title card:

```text
Task T2 - Baseline, forecast, and recommendations
Persona: Technical user
Module: Analyses
```

### T2 A Clip

Clip name: `T2-A-manual.mp4`

Lower-third label:

```text
Manual: baseline, forecast, and opportunities pages
```

Task prompt:

```text
Analyze Compressor-1 against baseline, check forecast context, and retrieve recommendations.
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `A - Manual`.
3. Select `T2 - Baseline analysis and recommendations`.
4. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
5. Click `Start Task`.
6. Open Grafana `Machine Health` for `Compressor-1`.
7. Confirm the time range is `Today`.
8. Find `Actual vs Baseline Power` and `Baseline Variance (24h)`.
9. Open `/api/analytics/ui/forecast`.
10. Select `Compressor-1`.
11. Select `Short (1-4 hours)`.
12. Click `Generate Forecast`.
13. Wait until the forecast result and chart are visible.
14. Open `/api/analytics/ui/opportunities`.
15. Keep factory as `Simulated Romanian Pilot Factory`.
16. Keep period as `Month`.
17. Click `Load` if recommendations are not already loaded.
18. Identify the top savings recommendations.
19. If needed, open Grafana `Predictive Analytics` and use `Power Forecast vs Actual (24-Hour)` and `Recent 24-Hour Forecasts (Historical)`.
20. Click `Answer Found` only after baseline evidence, forecast evidence, and recommendations are all visible.
21. Stop the screen recorder.

### T2 B Clip

Clip name: `T2-B-assistant.mp4`

Lower-third label:

```text
Assistant: OVOS analysis, forecast, and opportunities
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `B - Assistant`.
3. Select `T2 - Baseline analysis and recommendations`.
4. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
5. Uncheck `Auto-stop` because this task uses three OVOS prompts.
6. Say `Jarvis`, then ask `Analyze performance of Compressor-1`.
7. Wait until the performance/baseline answer is visible and voice playback finishes.
8. Say `Jarvis`, then ask `Energy forecast for Compressor-1`.
9. Wait until the forecast answer is visible and voice playback finishes.
10. Say `Jarvis`, then ask `What are the energy saving opportunities?`
11. Wait until the recommendations answer is visible and voice playback finishes.
12. Click `Answer Found`.
13. Stop the screen recorder.
14. Re-check `Auto-stop` before the next single-prompt task.

### T2 Comparison Card

Voiceover:

```text
This task demonstrates the Analyses module. Manually, the technical user must connect baseline, forecast, and recommendations across multiple views. With OVOS, the same analysis is requested in plain language.
```

## T3 Round - KPI And EnPI Status

Title card:

```text
Task T3 - KPI and EnPI status for 2026-Q1
Persona: Technical user
Module: Analyses
```

### T3 A Clip

Clip name: `T3-A-manual.mp4`

Lower-third label:

```text
Manual: KPI and EnPI report pages
```

Task prompt:

```text
Retrieve factory KPI and EnPI status for 2026-Q1.
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `A - Manual`.
3. Select `T3 - KPI and EnPI status`.
4. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
5. Click `Start Task`.
6. Open `/api/analytics/ui/kpi`.
7. In `KPI Scope`, select `Factory - Simulated Romanian Pilot Factory`.
8. Confirm `Time Period` is `2026-Q1 Pilot Period`.
9. Review the factory KPI / EnPI cards.
10. Confirm the same values that OVOS reports are visible: status is `requires attention`, `6` SEUs were analyzed, actual energy is about `268,426.2 kWh`, baseline is about `250,637.2 kWh`, deviation is `7.10%` above baseline, and the performance gap is about `17,789.0 kWh`.
11. Open `/api/analytics/ui/enpi-report` only if supporting details or the SEU breakdown are needed.
12. If supporting trend evidence is needed, open Grafana `ISO 50001 EnPI`.
13. Click `Answer Found`.
14. Stop the screen recorder.

### T3 B Clip

Clip name: `T3-B-assistant.mp4`

Lower-third label:

```text
Assistant: OVOS EnPI status
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `B - Assistant`.
3. Select `T3 - KPI and EnPI status`.
4. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
5. Confirm `Auto-stop` checked.
6. Say `Jarvis`, then ask `Show energy performance indicators report`.
7. Wait for the recorder to stop automatically after voice playback finishes.
8. Confirm the answer says `2026-Q1` ISO 50001 EnPI status is `requires attention`, `6` SEUs were analyzed, actual energy is about `268,426.2 kWh`, baseline is about `250,637.2 kWh`, deviation is `7.10%` above baseline, and the performance gap is about `17,789.0 kWh`.
9. Stop the screen recorder.

### T3 Comparison Card

Voiceover:

```text
This task compares manual KPI and EnPI report lookup against direct assistant reporting for the ISO 50001 performance indicator status.
```

## T4 Round - April 2026 Monthly Report

Title card:

```text
Task T4 - April 2026 monthly report
Persona: Technical user
Module: Analyses / Documentation
```

### T4 A Clip

Clip name: `T4-A-manual.mp4`

Lower-third label:

```text
Manual: reports page and April 2026 report generation
```

Task prompt:

```text
Generate the April 2026 monthly report and summarize the result.
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `A - Manual`.
3. Select `T4 - April 2026 report`.
4. Confirm `Expert` unchecked, `Manual reasoning` checked, `Success` checked.
5. Click `Start Task`.
6. Open `/reports.html`.
7. Select the simulated Romanian pilot factory if the page asks for a factory.
8. Select `April 2026`.
9. Click the report generation/download action.
10. Wait until the page confirms the April 2026 report is generated or the browser starts downloading the report.
11. Click `Answer Found`.
12. Stop the screen recorder.

### T4 B Clip

Clip name: `T4-B-assistant.mp4`

Lower-third label:

```text
Assistant: OVOS April 2026 report download
```

Record the clip:

1. Start the screen recorder.
2. Set extension condition to `B - Assistant`.
3. Select `T4 - April 2026 report`.
4. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
5. Uncheck `Auto-stop` because success requires both the voice response and report download start.
6. Say `Jarvis`, then ask `download report of Apr 2026`.
7. Wait for this answer:

```text
Your monthly energy report for April 2026 is ready. The download should start automatically in your browser.
```

8. Wait until the browser download starts or the OVOS widget shows the download message.
9. Wait until voice playback finishes.
10. Click `Answer Found`.
11. Stop the screen recorder.
12. Re-check `Auto-stop` after saving the task record if you continue testing.

### T4 Comparison Card

Voiceover:

```text
This task compares manual report generation against assistant-triggered report retrieval for the April 2026 monthly reporting workflow.
```

## Technical-User Subtotal

Place this after the `T4` comparison card.

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

## Evidence Package Slide

Place this as the final slide.

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

## After Recording All Clips

1. Open the Pilot Measurement extension overlay or popup.
2. Click `Copy Raw`.
3. Save the raw rows with the evidence package.
4. Click `Copy KPI`.
5. Paste the KPI rows into [kpi-measurement-sheet.csv](kpi-measurement-sheet.csv) or the spreadsheet used for reporting.
6. Fill or verify time, clicks, screens, expert help, manual reasoning, and success for each task.
7. Calculate the A/B reduction percentages.
8. Use the final values in the per-task comparison cards and final KPI summary.

## Editing Checklist

- Opening title and simulated-pilot disclosure are present.
- Methodology slide explains A/B design and extension measurement.
- Every task round shows `A` before `B`.
- Every task round uses the same task wording for both conditions.
- The extension overlay is visible at the start and end of each measured clip.
- OVOS voice playback remains audible in assistant clips.
- Chatbot prompts and answers remain visible in chatbot clips.
- A comparison card appears immediately after every `B` clip.
- Operational-user subtotal appears after `O4`.
- Technical-user subtotal appears after `T4`.
- Final KPI summary includes the `30%` and `25%` targets.
- Final evidence slide lists raw clips, extension export, KPI sheet, methodology note, and simulated factory profile.

## Objectivity Rules

- Do not cut inside a measured task window unless the cut is explicitly labeled.
- Do not speed up timed footage unless the video label says playback speed changed only for viewing and KPI timing comes from the extension.
- Do not hide failed task outcomes. If a task fails, set `Success = 0` and explain it in the KPI notes.
- Do not manually improve or rewrite extension results. If the measurement is wrong, redo the task.
- Do not claim a real Romanian factory deployment. State that this is a realistic simulated pilot.

## Recommended Final Length

- Opening and methodology: `45-60 seconds`
- Each A/B task round: `60-120 seconds`
- Per-task comparison card: `8-12 seconds`
- Operational subtotal: `10-15 seconds`
- Technical subtotal: `10-15 seconds`
- Final KPI summary and evidence slide: `30-45 seconds`

Target final edited video length: `12-18 minutes`.

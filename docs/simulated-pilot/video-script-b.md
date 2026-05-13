# Video Script B - Assistant Condition

Condition:
- HumanEnerDIA with OVOS
- HumanEnerDIA with chatbot

Personas:
- `Operational user`: facility / production manager
- `Technical user`: energy / maintenance / automation engineer

Official timing rule:
- Start one continuous screen recording for the whole Condition B video.
- Use the in-app Pilot Measurement recorder for each task timer.
- For OVOS voice tasks, the task timer starts when the wake word event starts the assistant flow. In practice, this is when you say `Jarvis` if wake word is enabled.
- If you type into OVOS instead of using the wake word, the task timer starts when you send the prompt.
- For chatbot tasks, the timer starts when you send the chatbot message.
- The official measurement stops when the answer is visible, not when text-to-speech playback finishes. This avoids measuring browser audio/TTS variability instead of decision-support speed.
- For multi-prompt tasks, disable `Auto-stop`, ask all prompts for the task, then click `Answer Found` after the final useful answer.

## Pre-Recording Setup
1. Open `http://10.33.10.103:8080/index.html`.
2. If a login page appears, log in before the official recording. Do not include login time in the KPI measurement.
3. Open browser DevTools console.
4. Run:

```js
localStorage.setItem('humanenerdia_pilot_mode', 'assistant');
localStorage.removeItem('humanenerdia_pilot_measurement_state');
location.href = '/index.html';
```

5. Confirm the `Pilot Measurement` panel is visible.
6. Confirm OVOS is visible and connected.
7. Confirm the chatbot is visible.
8. If you will use voice, enable the `Jarvis` wake word before the official recording and allow microphone permission.
9. If wake word recognition is unreliable during rehearsal, use typed OVOS prompts consistently for the whole video. Do not mix voice and typing randomly.
10. Set the same browser zoom and window size used for Condition A.
11. Open the screen recorder, but do not start recording yet.

## Recorder Checkbox Rules
- `Expert`: leave unchecked unless the assistant answer is not enough and a human/domain expert would be needed. Expected result for the official rehearsal is unchecked.
- `Manual reasoning`: leave unchecked when the assistant provides the answer directly. Check it only if you must manually open dashboards, inspect raw API output, or reason through pages after the assistant response.
- `Success`: keep checked only if the assistant answer is correct and completes the task. Uncheck it if the assistant gives the wrong answer, times out, or misses the required task result.
- `Auto-stop`: keep checked for single-prompt tasks. Turn it off for multi-prompt tasks and for the report download task.

## How To Use Auto-Stop
- Single-prompt task: `Auto-stop` checked. Select task, ask the prompt, and the recorder stops automatically when the assistant answer appears.
- Multi-prompt task: `Auto-stop` unchecked. Select task, ask all prompts, then click `Answer Found` manually after the final answer appears.
- Report download task: `Auto-stop` unchecked. Stop manually only after the assistant response appears and the PDF download has started or the download message is visible.

## Start The Video Recording
1. Start the screen recorder.
2. Show this title on screen or say it clearly:

> Simulated pilot benchmark - Condition B  
> HumanEnerDIA with OVOS and chatbot support

3. Say:

> This benchmark repeats the same simulated Romanian pilot tasks with assistant support. OVOS supports monitoring, analysis, prediction, forecasting, and reporting. The chatbot supports standards, documentation, and procedure guidance.

## O1 - Factory Overview And Top Consumers
Persona: `Operational user`

Task prompt:

> Get a factory overview and identify the top 3 energy consumers.

Steps:
1. In the recorder, set `Condition` to `B - Assistant`.
2. Select `O1 - Factory overview and top consumers`.
3. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
4. Uncheck `Auto-stop` because this task uses two OVOS prompts.
5. Say `Jarvis`, then ask: `Give me a factory overview`.
6. Wait until the OVOS answer is visible.
7. Say `Jarvis`, then ask: `Show top 3 energy consumers`.
8. Wait until the top-consumers answer is visible.
9. Expected answer to capture: top consumers include `Compressor-2`, `Injection-Molding-1`, and `Compressor-1`.
10. Click `Answer Found` immediately after the second answer appears.
11. Re-check `Auto-stop` before the next single-prompt task.

Typed fallback:
- If you do not use wake word, type each OVOS prompt and click send. The timer starts when the first prompt is sent.

## O2 - Machine Status And Today's Energy
Persona: `Operational user`

Task prompt:

> Check the status and today's energy of Compressor-1.

Steps:
1. Select `O2 - Compressor-1 status and today energy`.
2. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
3. Confirm `Auto-stop` checked.
4. Say `Jarvis`, then ask: `What's the status of Compressor-1?`
5. The recorder should start automatically and stop automatically when the answer appears.
6. Expected answer to capture: `Compressor-1` is running, current power is shown in kW, and today's energy is shown in kWh. The exact live value may move.

## O3 - ISO 50001 And Baseline Understanding
Persona: `Operational user`

Task prompt:

> Understand what ISO 50001 is and what an energy baseline means.

Steps:
1. Select `O3 - ISO 50001 and energy baseline`.
2. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
3. Uncheck `Auto-stop` because this task uses two chatbot prompts.
4. Open the chatbot.
5. Send chatbot prompt: `What is ISO 50001?`
6. Wait until the chatbot answer is visible.
7. Send chatbot prompt: `What is an energy baseline?`
8. Wait until the chatbot answer is visible.
9. Expected answer to capture: ISO 50001 is the EnMS standard, and the energy baseline is the historical reference for comparing current performance against expected performance.
10. Click `Answer Found` immediately after the second chatbot answer appears.
11. Re-check `Auto-stop` if the next task is single-prompt.

## O4 - Policy / Procedure Guidance
Persona: `Operational user`

Task prompt:

> Find the policy and procedure guidance for responding to an anomaly or efficiency issue.

Steps:
1. Select `O4 - Anomaly or efficiency procedure`.
2. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
3. Uncheck `Auto-stop` because this task uses two chatbot prompts.
4. Open the chatbot.
5. Send chatbot prompt: `What should we do when an anomaly appears?`
6. Wait until the chatbot answer is visible.
7. Send chatbot prompt: `What is the procedure for responding to an efficiency issue?`
8. Wait until the chatbot answer is visible.
9. Expected answer to capture: review the affected machine/time/severity, compare against baseline/expected performance, check status and production context, decide monitor/escalate, and record the action in the reporting workflow.
10. Click `Answer Found` immediately after the second chatbot answer appears.
11. Re-check `Auto-stop` before the next single-prompt task.

## T1 - Review Anomalies
Persona: `Technical user`

Task prompt:

> Review anomalies and identify the issue requiring attention.

Steps:
1. Select `T1 - Review anomalies`.
2. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
3. Confirm `Auto-stop` checked.
4. Say `Jarvis`, then ask: `Show me recent anomalies`.
5. The recorder should start automatically and stop automatically when the answer appears.
6. Expected answer to capture: the assistant identifies recent anomalies and affected machines, including `Boiler-1` and `Compressor-2` when those are the active recent anomalies.

## T2 - Baseline, Forecast, Predict, And Recommendations
Persona: `Technical user`

Task prompt:

> Analyze Compressor-1 against baseline, check forecast/prediction context, and retrieve recommendations.

Decision:
- Forecast and Predict should be part of the Analysis evidence, but not a new KPI task. This keeps the A/B comparison stable while showing that the Analysis module covers baseline, forecast, prediction, and recommendations.

Steps:
1. Select `T2 - Baseline analysis and recommendations`.
2. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
3. Uncheck `Auto-stop` because this task uses multiple OVOS prompts.
4. Say `Jarvis`, then ask: `Analyze performance of Compressor-1`.
5. Wait until the performance/baseline answer is visible.
6. Say `Jarvis`, then ask: `Expected energy for Compressor-1 baseline`.
7. Wait until the baseline prediction answer is visible.
8. Say `Jarvis`, then ask: `Energy forecast for Compressor-1`.
9. Wait until the forecast answer is visible.
10. Say `Jarvis`, then ask: `What are the energy saving opportunities?`
11. Wait until the recommendations answer is visible.
12. Expected answer to capture: performance/baseline status for `Compressor-1`, expected baseline energy, tomorrow forecast, and prioritized savings recommendations.
13. Click `Answer Found` immediately after the recommendations answer appears.
14. Re-check `Auto-stop` before the next single-prompt task.

Typed fallback:
- If using typed OVOS prompts, send the four prompts in the same order. The timer starts when the first prompt is sent and stops when you click `Answer Found`.

## T3 - KPI And EnPI Status
Persona: `Technical user`

Task prompt:

> Retrieve factory KPI and EnPI status for 2026-Q1.

Steps:
1. Select `T3 - KPI and EnPI status`.
2. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
3. Confirm `Auto-stop` checked.
4. Say `Jarvis`, then ask: `Show energy performance indicators report`.
5. The recorder should start automatically and stop automatically when the answer appears.
6. Expected answer to capture: `2026-Q1` ISO 50001 EnPI status is `on track`, actual energy is about `2.22%` above baseline, and the performance gap is about `5,838.6 kWh`.

## T4 - Generate Monthly Report
Persona: `Technical user`

Task prompt:

> Generate the April 2026 monthly report and summarize the result.

Steps:
1. Select `T4 - April 2026 report`.
2. Confirm `Expert` unchecked, `Manual reasoning` unchecked, `Success` checked.
3. Uncheck `Auto-stop` because success requires the report download to start, not only the assistant text answer.
4. Say `Jarvis`, then ask: `download report of Apr 2026`.
5. Wait for the assistant answer:

> Your monthly energy report for April 2026 is ready. The download should start automatically in your browser.

6. Wait until the browser download starts or the OVOS widget shows the download message.
7. Expected answer to capture: April 2026 monthly report generated and download started.
8. Click `Answer Found` immediately after the download start is visible.
9. Re-check `Auto-stop` after saving the task record if you continue testing.

## End The Video Recording
1. Show this closing statement on screen or say it clearly:

> Condition B complete. Same tasks, assistant-supported workflow.

2. Open the Pilot Measurement panel.
3. Click `Copy CSV` and keep the copied data for the KPI comparison table.
4. Stop the screen recorder.

## Verified Assistant Prompts
These are the official prompts to use in the recording. Do not improvise alternatives during the official run.

- `Give me a factory overview`
- `Show top 3 energy consumers`
- `What's the status of Compressor-1?`
- `What is ISO 50001?`
- `What is an energy baseline?`
- `What should we do when an anomaly appears?`
- `What is the procedure for responding to an efficiency issue?`
- `Show me recent anomalies`
- `Analyze performance of Compressor-1`
- `Expected energy for Compressor-1 baseline`
- `Energy forecast for Compressor-1`
- `What are the energy saving opportunities?`
- `Show energy performance indicators report`
- `download report of Apr 2026`

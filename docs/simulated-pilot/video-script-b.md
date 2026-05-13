# Video Script B - Assistant Condition

Condition:
- HumanEnerDIA with OVOS
- HumanEnerDIA with chatbot

Use:
- `Operational user`: facility / production manager
- `Technical user`: energy / maintenance / automation engineer

## Opening
Display on screen:

> Simulated pilot benchmark - Condition B  
> HumanEnerDIA with OVOS and chatbot support

Voice-over:

> This benchmark repeats the same simulated pilot tasks with OVOS for monitoring and analysis support and the chatbot for standards, documentation, and procedural guidance.

Measurement setup:
- Enable assistant mode with `localStorage.setItem('humanenerdia_pilot_mode', 'assistant'); location.reload();`.
- Use the in-app pilot recorder instead of an external timer.
- Select the matching task before each prompt.
- OVOS and chatbot prompts start the timer automatically; the timer stops when the assistant answer appears.

## Task Order

### O1 - Factory Overview And Top Consumers
- Show prompt on screen: `Get a factory overview and identify the top 3 energy consumers.`
- Select `O1` in the recorder.
- OVOS prompt 1: `Give me a factory overview`
- OVOS prompt 2: `Show top 3 energy consumers`
- The recorder starts automatically on the assistant prompt and stops when the answer appears.

### O2 - Machine Status And Today's Energy
- Show prompt on screen: `Check the status and today's energy of Compressor-1.`
- Select `O2` in the recorder.
- OVOS prompt: `What's the status of Compressor-1?`
- The recorder starts automatically on the assistant prompt and stops when the answer appears.

### O3 - ISO 50001 And Baseline Understanding
- Show prompt on screen: `Understand what ISO 50001 is and what an energy baseline means.`
- Select `O3` in the recorder.
- Chatbot prompt 1: `What is ISO 50001?`
- Chatbot prompt 2: `What is an energy baseline?`
- The recorder starts automatically on the chatbot prompt and stops when the answer appears.

### O4 - Policy / Procedure Guidance
- Show prompt on screen: `Find the policy and procedure guidance for responding to an anomaly or efficiency issue.`
- Select `O4` in the recorder.
- Chatbot prompt 1: `What should we do when an anomaly appears?`
- Chatbot prompt 2: `What is the procedure for responding to an efficiency issue?`
- The recorder starts automatically on the chatbot prompt and stops when the answer appears.

### T1 - Review Anomalies
- Show prompt on screen: `Review anomalies and identify the issue requiring attention.`
- Select `T1` in the recorder.
- OVOS prompt: `Show me recent anomalies`
- The recorder starts automatically on the assistant prompt and stops when the answer appears.

### T2 - Baseline Analysis And Recommendations
- Show prompt on screen: `Analyze Compressor-1 against baseline and retrieve recommendations.`
- Select `T2` in the recorder.
- OVOS prompt 1: `Analyze performance of Compressor-1`
- OVOS prompt 2: `What are the energy saving opportunities?`
- The recorder starts automatically on the assistant prompt and stops when the answer appears.

### T3 - KPI And EnPI Status
- Show prompt on screen: `Retrieve factory KPI and EnPI status for 2026-Q1.`
- Select `T3` in the recorder.
- OVOS prompt: `Show energy performance indicators report`
- The recorder starts automatically on the assistant prompt and stops when the answer appears.

### T4 - Generate Monthly Report
- Show prompt on screen: `Generate the April 2026 monthly report and summarize the result.`
- Select `T4` in the recorder.
- OVOS prompt: `download report of Apr 2026`
- The recorder starts automatically on the assistant prompt and stops when the answer appears.

## Closing
Display on screen:

> Condition B complete  
> Same tasks, assistant-supported workflow

Voice-over:

> Condition B shows the same HumanEnerDIA tasks with OVOS and chatbot support. The KPI comparison table will compare the two recordings using time, click or screen count, need for expert help, need for manual dashboard hunting or manual API-style reasoning, and task success or failure.

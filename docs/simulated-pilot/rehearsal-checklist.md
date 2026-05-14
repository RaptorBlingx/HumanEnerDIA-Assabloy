# Rehearsal Checklist

Use this checklist before freezing the recording scripts.

## Environment
- [ ] The simulated Romanian pilot story is consistent with [factory-profile.md](factory-profile.md).
- [ ] The browser login works on all required pages.
- [ ] Manual mode hides assistant widgets cleanly.
- [ ] Assistant mode restores the widgets cleanly.
- [ ] Grafana loads without broken dashboards.
- [ ] Reports page generates the selected monthly report.

## Manual Reference
- [ ] `/pilot-procedures.html` is accessible for `Condition A`.
- [ ] The same content is available through the chatbot for `Condition B`.

## OVOS Prompt Stability
- [ ] `Give me a factory overview`
- [ ] `Show top 3 energy consumers`
- [ ] `What's the status of Compressor-1?`
- [ ] `Show me recent anomalies`
- [ ] `Analyze performance of Compressor-1`
- [ ] `What are the energy saving opportunities?`
- [ ] `Show energy performance indicators report`
- [ ] `download report of Apr 2026`

## Chatbot Prompt Stability
- [ ] `What is ISO 50001?`
- [ ] `What is an energy baseline?`
- [ ] `What should we do when an anomaly appears?`
- [ ] `What is the procedure for responding to an efficiency issue?`

## Script Fit
- [ ] The same task wording is used in both conditions.
- [ ] The same task order is used in both conditions.
- [ ] The same machine and reporting periods are used in both conditions.
- [ ] The recent `Compressor-2` anomaly is present for both the manual and assistant anomaly tasks.
- [ ] Each task can be completed in a measurable way.
- [ ] The assistant-supported flow is clearly faster or simpler than the manual flow.

## Recording Setup
- [ ] Pilot Measurement extension overlay is visible and readable.
- [ ] Extension click, screen, and task-time counters update during a sample manual task.
- [ ] Extension auto-start/auto-stop works during a sample assistant task.
- [ ] Screen resolution and zoom are fixed.
- [ ] Audio capture is clear enough for spoken prompts and summaries.
- [ ] No debug windows, terminals, or unrelated tabs are visible.

## Go / No-Go
- [ ] All required tasks are complete in rehearsal.
- [ ] No broken paths remain.
- [ ] Final prompts are frozen for recording.

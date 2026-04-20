import subprocess
import time
import requests
import json
import re

queries = [
    "compare this week to last week",
    "forecast energy for tomorrow",
    "what is the powre of comprsor one",
    "is boilar one onlne",
    "which machines are using most electricity",
    "which machines are wasting electricity"
]

def get_log():
    try:
        res = subprocess.run(["docker", "exec", "ovos-enms", "tail", "-n", "100", "/var/log/ovos/skills.log"], capture_output=True, text=True)
        return res.stdout
    except Exception as e:
        return str(e)

print(f"{'Query':<45} | {'Latency':<7} | {'Response Text':<30} | {'Route Notes'}")
print("-" * 120)

for q in queries:
    start_time = time.time()
    try:
        response = requests.post("http://localhost:5000/query", json={"query": q}, timeout=60)
        latency = time.time() - start_time
        data = response.json()
        resp_text = data.get("response", "N/A")
    except Exception as e:
        latency = time.time() - start_time
        resp_text = f"Error: {str(e)}"
        data = {}

    time.sleep(2)  # Wait for logs to flush
    logs = get_log()
    
    notes = []
    if "fallback_medium match" in logs: notes.append("fallback_medium")
    if "trying_llm_tier" in logs: notes.append("llm_tier")
    if "clarification_needed" in logs: notes.append("clarification")
    
    intent_match = re.search(r"IntentMatch.*?'intent_type': '(.+?)'", logs)
    if intent_match:
        notes.append(f"Intent: {intent_match.group(1)}")
    elif "Parsing utterance" in logs:
        if not notes: notes.append("Parsing detected")

    print(f"{q:<45} | {latency:<7.2f} | {str(resp_text)[:30]:<30} | {', '.join(notes)}")

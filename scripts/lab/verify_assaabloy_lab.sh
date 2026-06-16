#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REQUIRE_OVOS=false

if [[ "${1:-}" == "--require-ovos" ]]; then
  REQUIRE_OVOS=true
fi

cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

BASE="http://localhost:${NGINX_HTTP_PORT:-8080}/api/analytics/api/v1"

python3 - "$BASE" "$REQUIRE_OVOS" <<'PY'
import json
import sys
import urllib.error
import urllib.request

base = sys.argv[1].rstrip("/")
require_ovos = sys.argv[2].lower() == "true"


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def get_json(path):
    url = f"{base}{path}"
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(path, payload):
    url = f"{base}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def approx(actual, expected, tolerance=0.02):
    return abs(float(actual) - float(expected)) <= tolerance


print("Checking partner KPI summary...")
kpis = get_json("/partner-press/summary?question_type=kpis")
if not approx(kpis["total_energy_kwh"], 141254.85):
    fail(f"total_energy_kwh expected 141254.85, got {kpis['total_energy_kwh']}")
if int(kpis["total_production_units"]) != 27625665:
    fail(f"total_production_units expected 27625665, got {kpis['total_production_units']}")

energy = {item["group"]: item["energy_kwh"] for item in kpis["energy_by_group"]}
expected_energy = {"bret": 39611.063, "raster": 41981.813, "dimeco": 59661.969}
for group, expected in expected_energy.items():
    if not approx(energy[group], expected, 0.02):
        fail(f"{group} energy expected {expected}, got {energy[group]}")

print("Checking data inventory...")
inventory = get_json("/partner-press/summary?question_type=data_inventory")
data_range = inventory["data_range"]
expected_rows = {
    "energy_rows": 1978,
    "group_energy_rows": 1235,
    "auxiliary_energy_rows": 743,
    "production_rows": 6336,
    "press_production_rows": 5148,
    "group_production_rows": 1188,
}
for key, expected in expected_rows.items():
    if int(data_range[key]) != expected:
        fail(f"{key} expected {expected}, got {data_range[key]}")

print("Checking transformer boundary...")
reference = get_json("/partner-press/summary?question_type=reference_meter")
aux = reference["auxiliary_energy"][0]
if int(aux["readings"]) != 743:
    fail(f"transformer readings expected 743, got {aux['readings']}")
if not approx(aux["energy_kwh"], 263999.155, 0.02):
    fail(f"transformer kWh expected 263999.155, got {aux['energy_kwh']}")
if "excluded" not in reference["response"].lower():
    fail("reference meter response does not state exclusion from KPI totals")

print("Checking ML baseline readiness...")
readiness = get_json("/partner-press/ml-readiness")
trained = sum(1 for item in readiness["meter_groups"] if item.get("baseline_trained"))
if trained != 3:
    fail(f"active baselines expected 3 of 3, got {trained}")

print("Checking chatbot endpoint...")
try:
    with urllib.request.urlopen("http://localhost:5006/health", timeout=10) as response:
        if response.status >= 400:
            fail(f"chatbot health returned {response.status}")
except Exception as exc:
    fail(f"chatbot health check failed: {exc}")

print("Checking OVOS proxy health...")
try:
    health = get_json("/ovos/voice/health")
    connected = bool(health.get("ovos_connected"))
    if require_ovos and not connected:
        fail(f"OVOS bridge is not connected: {health}")
    if connected:
        response = post_json(
            "/ovos/voice/query",
            {
                "text": "Show KPIs for the ASSA ABLOY partner press shop",
                "include_audio": False,
            },
        )
        text = response.get("response") or ""
        if "141,254.85" not in text and "141254.85" not in text:
            fail(f"OVOS KPI response missing expected total: {text}")
    else:
        print("WARN: OVOS bridge is not connected. Run with --require-ovos after starting OVOS.")
except urllib.error.URLError as exc:
    if require_ovos:
        fail(f"OVOS proxy check failed: {exc}")
    print(f"WARN: OVOS proxy check skipped: {exc}")

print("ASSA ABLOY lab verification passed.")
PY

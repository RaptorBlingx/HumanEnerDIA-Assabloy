#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEFAULT_PACKAGE="$ROOT/data/raw/Attachments_umut.ogur@aartimuhendislik.com_2026-06-10_08-03-41.zip"
PACKAGE="${ASSAABLOY_PACKAGE:-${1:-$DEFAULT_PACKAGE}}"
COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.partner-press.yml)
LAB_CONTAINERS=(
  enms-nginx
  enms-postgres
  enms-mqtt
  enms-redis
  enms-simulator
  enms-nodered
  enms-grafana
  enms-analytics
  enms-query-service
  enms-auth-service
  enms-rasa-actions
  enms-rasa
  enms-chatbot
)

die() {
  echo "ERROR: $*" >&2
  exit 1
}

wait_for_http() {
  local url="$1"
  local name="$2"
  local attempts="${3:-60}"
  for _ in $(seq 1 "$attempts"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "$name is ready: $url"
      return 0
    fi
    sleep 2
  done
  die "$name did not become ready: $url"
}

wait_for_postgres() {
  for _ in $(seq 1 60); do
    if docker exec enms-postgres pg_isready -U "${POSTGRES_USER:-raptorblingx}" -d "${POSTGRES_DB:-enms}" >/dev/null 2>&1; then
      echo "PostgreSQL is ready."
      return 0
    fi
    sleep 2
  done
  die "PostgreSQL did not become ready."
}

ensure_energy_baseline_schema() {
  local has_energy_source_id

  has_energy_source_id="$(docker exec enms-postgres psql \
    -U "${POSTGRES_USER:-raptorblingx}" \
    -d "${POSTGRES_DB:-enms}" \
    -tAc "SELECT EXISTS (
      SELECT 1
      FROM information_schema.columns
      WHERE table_schema = 'public'
        AND table_name = 'energy_baselines'
        AND column_name = 'energy_source_id'
    );" | tr -d '[:space:]')"

  if [[ "$has_energy_source_id" == "t" ]]; then
    return 0
  fi

  if [[ ! -f database/init/14-fix-multi-energy-baselines.sql ]]; then
    die "energy_baselines.energy_source_id is missing and database/init/14-fix-multi-energy-baselines.sql was not found."
  fi

  echo "Applying multi-energy baseline schema migration..."
  docker exec -i enms-postgres psql \
    -U "${POSTGRES_USER:-raptorblingx}" \
    -d "${POSTGRES_DB:-enms}" \
    < database/init/14-fix-multi-energy-baselines.sql >/dev/null
}

preflight_container_conflicts() {
  local conflicts=()
  local name
  for name in "${LAB_CONTAINERS[@]}"; do
    if docker ps -a --format '{{.Names}}' | grep -Fxq "$name"; then
      conflicts+=("$name")
    fi
  done

  if [[ ${#conflicts[@]} -eq 0 ]]; then
    return 0
  fi

  if [[ "${ASSAABLOY_LAB_REPLACE_EXISTING:-false}" == "true" ]]; then
    echo "Removing existing HumanEnerDIA containers because ASSAABLOY_LAB_REPLACE_EXISTING=true:"
    printf '  %s\n' "${conflicts[@]}"
    docker rm -f "${conflicts[@]}" >/dev/null
    return 0
  fi

  cat >&2 <<EOF
ERROR: Existing HumanEnerDIA/EnMS containers are already using the fixed lab names:
$(printf '  - %s\n' "${conflicts[@]}")

This ASSA ABLOY lab stack uses the same container names as the full HumanEnerDIA stack.
Stop or remove the existing stack before running this bootstrap.

If the existing stack is disposable on this Ubuntu machine, run:

  docker rm -f ${conflicts[*]}

Then rerun:

  scripts/lab/bootstrap_assaabloy_lab.sh

If you want the bootstrap script to remove the conflicting containers itself, run:

  ASSAABLOY_LAB_REPLACE_EXISTING=true scripts/lab/bootstrap_assaabloy_lab.sh

Do not use the replace option on a production or shared server.
EOF
  exit 1
}

cd "$ROOT"

command -v docker >/dev/null 2>&1 || die "Docker is not installed or not on PATH."
docker compose version >/dev/null 2>&1 || die "Docker Compose v2 is required."
command -v curl >/dev/null 2>&1 || die "curl is required."
command -v python3 >/dev/null 2>&1 || die "python3 is required."

if [[ ! -f .env ]]; then
  cp .env.assaabloy.example .env
  echo "Created .env from .env.assaabloy.example."
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

if [[ ! -f "$PACKAGE" ]]; then
  cat >&2 <<EOF
ERROR: Raw partner package was not found.

Expected:
  $PACKAGE

Place the private ASSA ABLOY source package at that path, or run:
  ASSAABLOY_PACKAGE=/absolute/path/to/package.zip $0

The raw package is intentionally ignored by Git.
EOF
  exit 1
fi

preflight_container_conflicts

echo "Starting HumanEnerDIA ASSA ABLOY lab stack..."
"${COMPOSE[@]}" up -d --build

wait_for_postgres
wait_for_http "http://localhost:${ANALYTICS_PORT:-8001}/api/v1/health" "Analytics service"
wait_for_http "http://localhost:${NGINX_HTTP_PORT:-8080}/health" "Nginx gateway"

echo "Importing ASSA ABLOY partner press-shop data..."
python3 scripts/import_partner_press_data.py --package "$PACKAGE" --apply

if [[ -f database/init/12-forecast-predictions.sql ]]; then
  echo "Ensuring forecast prediction table exists..."
  docker exec -i enms-postgres psql \
    -U "${POSTGRES_USER:-raptorblingx}" \
    -d "${POSTGRES_DB:-enms}" \
    < database/init/12-forecast-predictions.sql >/dev/null
fi

ensure_energy_baseline_schema

echo "Training partner baselines and short-horizon forecast models..."
curl -fsS -X POST \
  "http://localhost:${NGINX_HTTP_PORT:-8080}/api/analytics/api/v1/partner-press/train-ml?train_baselines=true&train_arima=true&train_prophet=false" \
  >/tmp/assaabloy_train_ml.json
echo "Training response saved to /tmp/assaabloy_train_ml.json"

echo "Running platform verification..."
scripts/lab/verify_assaabloy_lab.sh

cat <<EOF

ASSA ABLOY lab stack is ready.

Open:
  Portal:       http://localhost:${NGINX_HTTP_PORT:-8080}/
  Reports:      http://localhost:${NGINX_HTTP_PORT:-8080}/reports.html
  Analytics UI: http://localhost:${NGINX_HTTP_PORT:-8080}/api/analytics/ui/
  Grafana:      http://localhost:${NGINX_HTTP_PORT:-8080}/grafana

Login:
  Username: assaabloy
  Password: assaabloy

For Condition B voice tasks, start the separate OVOS runtime after this stack is up.
See docs/assaabloy-benchmark/ovos-runtime.md.
EOF

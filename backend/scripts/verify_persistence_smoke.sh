#!/usr/bin/env bash
# Smoke checks against a running API (NFR-002 / SC-001 helper).
# Usage: BASE_URL=http://127.0.0.1:8000 ./backend/scripts/verify_persistence_smoke.sh
# After this script succeeds, restart the backend process and run the GET lines again manually.

set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "POST create student..."
create=$(curl -sS -X POST "${BASE_URL}/api/v1/students" \
  -H "Content-Type: application/json" \
  -d '{"name":"烟测","gender":"male"}')
echo "$create" | head -c 400
echo

sid=$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['data']['id'])" "$create")

echo "GET list..."
curl -sS "${BASE_URL}/api/v1/students" | head -c 400
echo

echo "GET edit-form for id=${sid}..."
curl -sS "${BASE_URL}/api/v1/students/${sid}/edit-form" | head -c 400
echo

echo "OK. Restart the backend, then re-run:"
echo "  curl -sS ${BASE_URL}/api/v1/students"
echo "  curl -sS ${BASE_URL}/api/v1/students/${sid}/edit-form"

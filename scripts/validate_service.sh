#!/usr/bin/env bash
set -euo pipefail

echo "=== ValidateService: checking app health ==="

APP_PORT=5000
MAX_RETRIES=10
RETRY_INTERVAL=5
HEALTH_URL="http://localhost:${APP_PORT}/health"

echo "Health URL   : ${HEALTH_URL}"
echo "Max retries  : ${MAX_RETRIES}"

for i in $(seq 1 "${MAX_RETRIES}"); do
  echo "Attempt ${i}/${MAX_RETRIES}..."
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_URL}" || echo "000")

  if [ "${HTTP_CODE}" -eq 200 ]; then
    echo "Health check passed (HTTP ${HTTP_CODE})."
    echo "=== ValidateService complete ==="
    exit 0
  fi

  echo "Health check returned HTTP ${HTTP_CODE}. Retrying in ${RETRY_INTERVAL}s..."
  sleep "${RETRY_INTERVAL}"
done

echo "ERROR: Health check failed after ${MAX_RETRIES} attempts."
echo "=== Container logs ==="
docker logs qrcode-app --tail 50 || true
exit 1
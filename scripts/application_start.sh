#!/usr/bin/env bash
set -euo pipefail

echo "=== ApplicationStart: starting QR Code app container ==="

CONTAINER_NAME="qrcode-app"
APP_PORT=5000
ENV_FILE="/opt/qrcode/.env"

# Load env file written by after_install.sh
if [ -f "${ENV_FILE}" ]; then
  source "${ENV_FILE}"
else
  echo "ERROR: ${ENV_FILE} not found. Run AfterInstall first."
  exit 1
fi

echo "Image        : ${ECR_REPO_URI}:latest"
echo "Container    : ${CONTAINER_NAME}"
echo "Port         : ${APP_PORT}"

docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  -p "${APP_PORT}:${APP_PORT}" \
  -e APP_PORT="${APP_PORT}" \
  -e APP_HOST="0.0.0.0" \
  "${ECR_REPO_URI}:latest"

echo "Container started."
echo "=== ApplicationStart complete ==="
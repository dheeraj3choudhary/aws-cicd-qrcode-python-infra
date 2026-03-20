#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="qrcode-app"

echo "=== BeforeInstall: stopping and removing existing container ==="

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Stopping container: ${CONTAINER_NAME}"
  docker stop "${CONTAINER_NAME}" || true
  echo "Removing container: ${CONTAINER_NAME}"
  docker rm "${CONTAINER_NAME}" || true
  echo "Container removed."
else
  echo "No existing container found. Skipping."
fi

echo "=== BeforeInstall complete ==="
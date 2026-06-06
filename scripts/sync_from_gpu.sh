#!/usr/bin/env bash
set -euo pipefail

ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"
SOURCE="${1:-}"

echo "[voice-lab] Sync from GPU placeholder"
echo "Root: ${ROOT}"

if [ -n "${SOURCE}" ]; then
  echo "Source: ${SOURCE}"
else
  echo "Source: not provided"
fi

echo
echo "Fase 1 no sincroniza archivos."
echo "En MVP futuro este script traera .pth, .index, configs y logs desde el GPU Droplet temporal."

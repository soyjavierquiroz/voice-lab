#!/usr/bin/env bash
set -euo pipefail

ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"
TARGET="${1:-}"

echo "[voice-lab] Sync to GPU placeholder"
echo "Root: ${ROOT}"

if [ -n "${TARGET}" ]; then
  echo "Target: ${TARGET}"
else
  echo "Target: not provided"
fi

echo
echo "Fase 1 no sincroniza archivos."
echo "En MVP futuro este script podra usar rsync/scp para enviar datasets limpios a un GPU Droplet temporal."

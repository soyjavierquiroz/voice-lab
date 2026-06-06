#!/usr/bin/env bash
set -euo pipefail

ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"
MAX_BATCH_JOBS="${MAX_BATCH_JOBS:-1}"

echo "[voice-lab] Low-priority batch placeholder"
echo "Root: ${ROOT}"
echo "Max batch jobs: ${MAX_BATCH_JOBS}"
echo
echo "Fase 1 no procesa cola real."
echo "En MVP futuro este flujo usara herramientas como nice, ionice, flock o systemd-run"
echo "para evitar competir con los stacks existentes del servidor."

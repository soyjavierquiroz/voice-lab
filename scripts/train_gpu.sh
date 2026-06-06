#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME="${1:-${DEFAULT_MODEL_NAME:-mi_voz}}"
ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"

echo "[voice-lab] GPU training placeholder"
echo "Model: ${MODEL_NAME}"
echo "Root: ${ROOT}"
echo
echo "Fase 1 no entrena modelos."
echo "En MVP futuro este script ejecutara entrenamiento RVC/Applio en un GPU Droplet temporal."

#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME="${1:-${DEFAULT_MODEL_NAME:-mi_voz}}"
ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"

echo "[voice-lab] Prepare dataset placeholder"
echo "Model: ${MODEL_NAME}"
echo "Dataset raw: ${ROOT}/datasets/${MODEL_NAME}/raw"
echo "Dataset clean: ${ROOT}/datasets/${MODEL_NAME}/clean"
echo
echo "Fase 1 no limpia ni convierte audios."
echo "En MVP futuro este script normalizara audios autorizados y generara metadata."

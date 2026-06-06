#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <input_audio> [model_name]" >&2
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  usage
  exit 2
fi

INPUT_AUDIO="$1"
MODEL_NAME="${2:-${DEFAULT_MODEL_NAME:-mi_voz}}"
ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"

if [ ! -f "${INPUT_AUDIO}" ]; then
  echo "[voice-lab] Input file not found: ${INPUT_AUDIO}" >&2
  exit 1
fi

echo "[voice-lab] Single inference placeholder"
echo "Input: ${INPUT_AUDIO}"
echo "Model: ${MODEL_NAME}"
echo "Root: ${ROOT}"
echo
echo "Fase 1 no ejecuta inferencia real."
echo "MVP 1 implementara normalizacion WAV, llamada a RVC/Applio y exportacion WAV/MP3."

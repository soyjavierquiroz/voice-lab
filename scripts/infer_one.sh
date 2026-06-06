#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <input_audio> <model_name>" >&2
}

if [ "$#" -ne 2 ]; then
  usage
  exit 2
fi

INPUT_AUDIO="$1"
MODEL_NAME="$2"
ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"
PYTHON_BIN="python3"

if [ ! -f "${INPUT_AUDIO}" ]; then
  echo "[voice-lab] Input file not found: ${INPUT_AUDIO}" >&2
  exit 1
fi

INPUT_AUDIO="$(cd "$(dirname "${INPUT_AUDIO}")" && pwd)/$(basename "${INPUT_AUDIO}")"

if [ -z "${MODEL_NAME}" ]; then
  echo "[voice-lab] Model name is required." >&2
  exit 1
fi

if [ -f "${ROOT}/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "${ROOT}/.venv/bin/activate"
  PYTHON_BIN="python"
fi

mkdir -p "${ROOT}/processing" "${ROOT}/output/wav" "${ROOT}/output/mp3" "${ROOT}/logs/jobs"

BASENAME="$(basename "${INPUT_AUDIO}")"
STEM="${BASENAME%.*}"
PROCESSING_WAV="${ROOT}/processing/${STEM}.clean.wav"
OUTPUT_WAV="${ROOT}/output/wav/${STEM}.clean.wav"
OUTPUT_MP3="${ROOT}/output/mp3/${STEM}.clean.mp3"
LOG_FILE="${ROOT}/logs/jobs/${STEM}.log"

{
  echo "[voice-lab] Fase 1B audio pipeline"
  echo "Started: $(date -Is)"
  echo "Input: ${INPUT_AUDIO}"
  echo "Model: ${MODEL_NAME}"
  echo "Root: ${ROOT}"
  echo
  echo "NOTE: NO hubo conversion RVC real. output/wav es copia placeholder del WAV limpio hasta integrar RVC."
  echo
  echo "[1/3] Normalize to clean WAV"
  (cd "${ROOT}" && "${PYTHON_BIN}" -m app.cli normalize --input "${INPUT_AUDIO}" --output "${PROCESSING_WAV}")
  echo
  echo "[2/3] Copy placeholder WAV output"
  cp "${PROCESSING_WAV}" "${OUTPUT_WAV}"
  echo "${OUTPUT_WAV}"
  echo
  echo "[3/3] Export MP3"
  (cd "${ROOT}" && "${PYTHON_BIN}" -m app.cli export-mp3 --input-wav "${PROCESSING_WAV}" --output-mp3 "${OUTPUT_MP3}")
  echo
  echo "Finished: $(date -Is)"
} 2>&1 | tee "${LOG_FILE}"

echo
echo "[voice-lab] Done"
echo "WAV limpio: ${PROCESSING_WAV}"
echo "WAV placeholder: ${OUTPUT_WAV}"
echo "MP3: ${OUTPUT_MP3}"
echo "Log: ${LOG_FILE}"

#!/usr/bin/env bash
set -euo pipefail

ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"
DATASET="${DEFAULT_MODEL_NAME:-mi_voz}"
OVERWRITE_ARG=""
PYTHON_BIN="${PYTHON_BIN:-python}"

if [ "${1:-}" = "--overwrite" ]; then
  OVERWRITE_ARG="--overwrite"
elif [ -n "${1:-}" ]; then
  DATASET="$1"
fi

if [ "${2:-}" = "--overwrite" ]; then
  OVERWRITE_ARG="--overwrite"
elif [ -n "${2:-}" ]; then
  echo "Usage: $0 [dataset] [--overwrite]" >&2
  exit 2
fi

LOG_DIR="${ROOT}/datasets/${DATASET}/logs"
LOG_FILE="${LOG_DIR}/prepare_dataset.log"

mkdir -p "${LOG_DIR}"

if [ -d "${ROOT}/.venv" ]; then
  # shellcheck disable=SC1091
  source "${ROOT}/.venv/bin/activate"
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

cd "${ROOT}"

{
  echo "[voice-lab] prepare_dataset.sh"
  echo "Dataset: ${DATASET}"
  echo "Sample rate: ${DEFAULT_SAMPLE_RATE:-40000}"
  echo "Overwrite: ${OVERWRITE_ARG:-no}"
  echo
} >> "${LOG_FILE}"

"${PYTHON_BIN}" -m app.dataset_cli prepare \
  --dataset "${DATASET}" \
  --sample-rate "${DEFAULT_SAMPLE_RATE:-40000}" \
  ${OVERWRITE_ARG}

echo
"${PYTHON_BIN}" -m app.dataset_cli report --dataset "${DATASET}"

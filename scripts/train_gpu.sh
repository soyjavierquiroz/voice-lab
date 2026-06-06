#!/usr/bin/env bash
set -euo pipefail

cd /opt/voice-lab

if [ -f ".env" ]; then
  # shellcheck disable=SC1091
  set -a
  source ".env"
  set +a
fi

DATASET_NAME="${DEFAULT_DATASET_NAME:-mi_voz}"
MODEL_NAME="${DEFAULT_MODEL_NAME:-mi_voz}"
ROOT="/opt/voice-lab"

usage() {
  echo "Usage: ./scripts/train_gpu.sh --dataset <dataset_name> --model <model_name>"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dataset)
      if [ "${2:-}" = "" ]; then
        echo "ERROR --dataset requires a value" >&2
        exit 2
      fi
      DATASET_NAME="$2"
      shift
      ;;
    --model)
      if [ "${2:-}" = "" ]; then
        echo "ERROR --model requires a value" >&2
        exit 2
      fi
      MODEL_NAME="$2"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

CLEAN_DIR="${ROOT}/datasets/${DATASET_NAME}/clean"
MODEL_DIR="${ROOT}/models/${MODEL_NAME}"
NOW_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

echo "[voice-lab] GPU training placeholder"
echo "Root: ${ROOT}"
echo "Dataset: ${DATASET_NAME}"
echo "Model: ${MODEL_NAME}"
echo

if [ ! -d "${CLEAN_DIR}" ]; then
  echo "ERROR missing clean dataset directory: ${CLEAN_DIR}" >&2
  echo "Prepare a real dataset first, for example: ./scripts/prepare_dataset.sh ${DATASET_NAME}" >&2
  exit 1
fi

if ! find "${CLEAN_DIR}" -maxdepth 1 -type f -name '*.wav' -print -quit | grep -q .; then
  echo "ERROR no clean WAV files found in ${CLEAN_DIR}" >&2
  echo "Prepare a real dataset first: add authorized audio to datasets/${DATASET_NAME}/raw/ and run ./scripts/prepare_dataset.sh ${DATASET_NAME}" >&2
  exit 1
fi

mkdir -p "${MODEL_DIR}/logs"

cat > "${MODEL_DIR}/train_notes.md" <<EOF
# ${MODEL_NAME} training notes

Status: placeholder, no entrenado todavia.

- Dataset usado: ${DATASET_NAME}
- Fecha UTC: ${NOW_UTC}
- Uso autorizado: requerido para todo audio de origen y modelo resultante.
- Estado actual: este script solo valida el dataset y prepara notas/config placeholder.

Outputs esperados futuros:

- model.pth
- model.index
- config.json
- logs/

No se creo ningun .pth ni .index falso. No se ejecuto entrenamiento RVC/Applio.
EOF

cat > "${MODEL_DIR}/config.example.json" <<EOF
{
  "model_name": "${MODEL_NAME}",
  "dataset_name": "${DATASET_NAME}",
  "sample_rate": 40000,
  "pitch_extractor": "placeholder",
  "index_rate": 0.0,
  "notes": "Placeholder informativo; no es una config real de RVC/Applio."
}
EOF

echo "OK clean WAV files found in ${CLEAN_DIR}"
echo "OK wrote ${MODEL_DIR}/train_notes.md"
echo "OK wrote ${MODEL_DIR}/config.example.json"
echo "No training was executed."

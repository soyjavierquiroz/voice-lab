#!/usr/bin/env bash
set -euo pipefail

cd /opt/voice-lab

if [ -f ".env" ]; then
  # shellcheck disable=SC1091
  set -a
  source ".env"
  set +a
fi

MODE="dry-run"
MODEL_NAME="${DEFAULT_MODEL_NAME:-mi_voz}"

usage() {
  echo "Usage: ./scripts/sync_from_gpu.sh --model <model_name> [--dry-run|--yes]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --model)
      if [ "${2:-}" = "" ]; then
        echo "ERROR --model requires a value" >&2
        exit 2
      fi
      MODEL_NAME="$2"
      shift
      ;;
    --dry-run)
      MODE="dry-run"
      ;;
    --yes)
      MODE="yes"
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

ROOT="/opt/voice-lab"
GPU_HOST="${GPU_HOST:-}"
GPU_USER="${GPU_USER:-root}"
GPU_PORT="${GPU_PORT:-22}"
GPU_SSH_KEY="${GPU_SSH_KEY:-}"
GPU_PROJECT_PATH="${GPU_PROJECT_PATH:-/opt/voice-lab}"
RSYNC_DELETE="${RSYNC_DELETE:-false}"

LOCAL_DIR="${ROOT}/models/${MODEL_NAME}/"
SOURCE="${GPU_USER}@${GPU_HOST}:${GPU_PROJECT_PATH}/models/${MODEL_NAME}/"
SSH_CMD=(ssh -p "${GPU_PORT}")
RSYNC_CMD=(rsync -az --human-readable --itemize-changes)

if [ "${MODE}" = "dry-run" ]; then
  RSYNC_CMD+=(--dry-run)
fi

if [ -n "${GPU_SSH_KEY}" ]; then
  SSH_CMD+=(-i "${GPU_SSH_KEY}")
fi

if [ "${RSYNC_DELETE}" = "true" ]; then
  if [ "${MODE}" = "yes" ]; then
    echo "WARNING RSYNC_DELETE=true; remote deletions in models/${MODEL_NAME}/ will delete matching local files."
    RSYNC_CMD+=(--delete)
  else
    echo "INFO RSYNC_DELETE=true; --delete would be added only with --yes."
  fi
fi

RSYNC_CMD+=(
  --exclude='__pycache__/'
  --exclude='*.tmp'
  --exclude='*.temp'
  --exclude='*.cache'
  --exclude='.cache/'
  --exclude='tmp/'
  -e "${SSH_CMD[*]}"
)

echo "[voice-lab] Sync from GPU"
echo "Mode: ${MODE}"
echo "Model: ${MODEL_NAME}"
echo "Source: ${GPU_USER}@${GPU_HOST:-<missing>}:${GPU_PROJECT_PATH}/models/${MODEL_NAME}/"
echo "Destination: ${LOCAL_DIR}"
echo "Scope: models/${MODEL_NAME}/ only"
echo

mkdir -p "${LOCAL_DIR}"

if [ -z "${GPU_HOST}" ]; then
  if [ "${MODE}" = "yes" ]; then
    echo "REAL SYNC BLOCKED: GPU_HOST is not configured."
    echo "Set GPU_HOST in .env before running with --yes."
    exit 1
  fi
  echo "DRY-RUN BLOCKED: GPU_HOST is not configured."
  echo "Set GPU_HOST in .env before running a real sync."
  exit 0
fi

echo "Command summary: rsync ${MODE} over ssh port ${GPU_PORT} from ${SOURCE}"
if [ "${MODE}" = "dry-run" ]; then
  echo "No files will be changed."
else
  echo "Real sync confirmed with --yes."
fi

"${RSYNC_CMD[@]}" "${SOURCE}" "${LOCAL_DIR}"

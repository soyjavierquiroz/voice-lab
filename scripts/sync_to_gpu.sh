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

usage() {
  echo "Usage: ./scripts/sync_to_gpu.sh [--dry-run|--yes]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
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

DEST="${GPU_USER}@${GPU_HOST}:${GPU_PROJECT_PATH}/"
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
    RSYNC_CMD+=(--delete)
  else
    echo "INFO RSYNC_DELETE=true; --delete would be added only with --yes."
  fi
fi

RSYNC_CMD+=(
  --exclude='.git/'
  --exclude='.venv/'
  --exclude='__pycache__/'
  --exclude='input/pending/*'
  --exclude='input/manual/*'
  --exclude='processing/*'
  --exclude='output/*'
  --exclude='queue/*'
  --exclude='logs/*.log'
  --exclude='logs/jobs/*.log'
  --exclude='tmp/*'
  --include='app/***'
  --include='scripts/***'
  --include='requirements-*.txt'
  --include='README.md'
  --include='.env.example'
  --include='docs/***'
  --include='datasets/***'
  --include='models/***'
  --exclude='*'
  -e "${SSH_CMD[*]}"
)

echo "[voice-lab] Sync to GPU"
echo "Mode: ${MODE}"
echo "Root: ${ROOT}"
echo "Destination: ${GPU_USER}@${GPU_HOST:-<missing>}:${GPU_PROJECT_PATH}/"
echo "Includes: app/, scripts/, requirements-*.txt, README.md, .env.example, docs/, datasets/, models/"
echo "Excludes: .git/, .venv/, __pycache__/, pending/manual inputs, processing, output, queue, logs/*.log, logs/jobs/*.log, tmp"
echo

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

echo "Command summary: rsync ${MODE} over ssh port ${GPU_PORT} to ${DEST}"
if [ "${MODE}" = "dry-run" ]; then
  echo "No files will be changed."
else
  echo "Real sync confirmed with --yes."
fi

"${RSYNC_CMD[@]}" ./ "${DEST}"

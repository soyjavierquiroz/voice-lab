#!/usr/bin/env bash
set -euo pipefail

ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"
LOCK_FILE="${VOICE_LAB_BATCH_LOCK:-/tmp/voice-lab-run-batch.lock}"
LOG_FILE="${ROOT}/logs/batch.log"

mkdir -p "$(dirname "${LOG_FILE}")"
exec >>"${LOG_FILE}" 2>&1

echo
echo "[voice-lab] Batch low-priority run"
echo "Started: $(date -Is)"
echo "Root: ${ROOT}"
echo "Lock: ${LOCK_FILE}"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "Another batch run is already active. Exiting."
  exit 0
fi

cd "${ROOT}"

PYTHON_BIN="python3"
if [ -f "${ROOT}/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "${ROOT}/.venv/bin/activate"
  PYTHON_BIN="python"
fi

run_lowprio() {
  if command -v ionice >/dev/null 2>&1; then
    ionice -c3 nice -n 19 "$@"
  else
    nice -n 19 "$@"
  fi
}

run_lowprio "${PYTHON_BIN}" -m app.queue_cli enqueue-pending
run_lowprio "${PYTHON_BIN}" -m app.queue_cli process-all --limit 1

echo "Finished: $(date -Is)"

# Cron futuro:
# 0 2 * * * /opt/voice-lab/scripts/run_batch_limited.sh >> /opt/voice-lab/logs/cron.log 2>&1

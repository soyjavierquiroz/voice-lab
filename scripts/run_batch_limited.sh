#!/usr/bin/env bash
set -euo pipefail

ROOT="/opt/voice-lab"
RUNNER="${ROOT}/scripts/run_batch_lowprio.sh"
LOG_FILE="${ROOT}/logs/batch_limited.log"

load_env_file() {
  local env_file="$1"
  local line key value

  [ -f "${env_file}" ] || return 0

  while IFS= read -r line || [ -n "${line}" ]; do
    line="${line%$'\r'}"
    [[ "${line}" =~ ^[[:space:]]*$ ]] && continue
    [[ "${line}" =~ ^[[:space:]]*# ]] && continue
    [[ "${line}" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]] || continue

    key="${BASH_REMATCH[1]}"
    value="${BASH_REMATCH[2]}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"

    if [[ "${value}" == \"*\" && "${value}" == *\" ]]; then
      value="${value:1:${#value}-2}"
    elif [[ "${value}" == \'*\' && "${value}" == *\' ]]; then
      value="${value:1:${#value}-2}"
    fi

    export "${key}=${value}"
  done <"${env_file}"
}

cd "${ROOT}"
mkdir -p "$(dirname "${LOG_FILE}")"
exec > >(tee -a "${LOG_FILE}") 2>&1

load_env_file "${ROOT}/.env"

CPU_QUOTA="${CPU_QUOTA:-60%}"
MEMORY_MAX="${MEMORY_MAX:-5G}"
UNIT_NAME="voice-lab-batch-$(date +%Y%m%d%H%M%S)"

echo
echo "[voice-lab] Batch limited run"
echo "Started: $(date -Is)"
echo "Root: ${ROOT}"
echo "Unit: ${UNIT_NAME}"
echo "Unit type: transient systemd service"
echo "CPUQuota: ${CPU_QUOTA}"
echo "MemoryMax: ${MEMORY_MAX}"

if ! command -v systemd-run >/dev/null 2>&1; then
  echo "FAIL systemd-run: not found"
  exit 1
fi

if [ ! -x "${RUNNER}" ]; then
  echo "FAIL runner: ${RUNNER} is missing or not executable"
  exit 1
fi

set +e
systemd-run \
  --wait \
  --collect \
  --unit="${UNIT_NAME}" \
  -p "CPUQuota=${CPU_QUOTA}" \
  -p "MemoryMax=${MEMORY_MAX}" \
  -p "Nice=19" \
  -p "IOSchedulingClass=idle" \
  "${RUNNER}"
status=$?
set -e

if [ "${status}" -ne 0 ]; then
  echo "FAIL systemd-run exited with status ${status}."
  echo "No fallback was run. Check whether this host supports transient service units with CPUQuota, MemoryMax, Nice and IOSchedulingClass."
  exit "${status}"
fi

echo "Finished: $(date -Is)"

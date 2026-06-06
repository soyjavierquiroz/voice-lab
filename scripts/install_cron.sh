#!/usr/bin/env bash
set -euo pipefail

ROOT="/opt/voice-lab"
CRON_COMMAND="/opt/voice-lab/scripts/run_batch_limited.sh >> /opt/voice-lab/logs/cron.log 2>&1"
MODE="dry-run"

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

usage() {
  echo "Usage: ./scripts/install_cron.sh [--dry-run|--yes]"
}

case "${1:---dry-run}" in
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
    usage
    exit 2
    ;;
esac

cd "${ROOT}"
load_env_file "${ROOT}/.env"
BATCH_CRON_SCHEDULE="${BATCH_CRON_SCHEDULE:-0 2 * * *}"
CRON_LINE="${BATCH_CRON_SCHEDULE} ${CRON_COMMAND}"

echo "[voice-lab] Install cron"
echo "Mode: ${MODE}"
echo "Proposed line:"
echo "${CRON_LINE}"
echo

if ! command -v crontab >/dev/null 2>&1; then
  echo "FAIL crontab: not found"
  exit 1
fi

current_crontab="$(crontab -l 2>/dev/null || true)"
final_crontab="${current_crontab}"
cron_line_exists=false

while IFS= read -r line || [ -n "${line}" ]; do
  trimmed_line="${line#"${line%%[![:space:]]*}"}"
  [[ "${trimmed_line}" == \#* ]] && continue

  if [[ "${line}" == *"${CRON_COMMAND}"* ]]; then
    cron_line_exists=true
    break
  fi
done <<<"${current_crontab}"

if [ "${cron_line_exists}" = "true" ]; then
  echo "Cron line already exists. No duplicate will be added."
elif [ -n "${current_crontab}" ]; then
  final_crontab="${current_crontab}"$'\n'"${CRON_LINE}"
else
  final_crontab="${CRON_LINE}"
fi

echo "Final crontab:"
echo "-----BEGIN CRONTAB-----"
printf '%s\n' "${final_crontab}"
echo "-----END CRONTAB-----"

if [ "${MODE}" = "yes" ]; then
  printf '%s\n' "${final_crontab}" | crontab -
  echo "Installed cron line."
else
  echo "Dry-run only. Re-run with --yes to install."
fi

#!/usr/bin/env bash
set -euo pipefail

CRON_COMMAND="/opt/voice-lab/scripts/run_batch_limited.sh >> /opt/voice-lab/logs/cron.log 2>&1"
MODE="dry-run"

usage() {
  echo "Usage: ./scripts/remove_cron.sh [--dry-run|--yes]"
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

echo "[voice-lab] Remove cron"
echo "Mode: ${MODE}"
echo "Target command:"
echo "${CRON_COMMAND}"
echo

if ! command -v crontab >/dev/null 2>&1; then
  echo "FAIL crontab: not found"
  exit 1
fi

current_crontab="$(crontab -l 2>/dev/null || true)"
final_lines=()

if [ -n "${current_crontab}" ]; then
  while IFS= read -r line || [ -n "${line}" ]; do
    trimmed_line="${line#"${line%%[![:space:]]*}"}"
    if [[ "${trimmed_line}" != \#* && "${line}" == *"${CRON_COMMAND}"* ]]; then
      continue
    fi
    final_lines+=("${line}")
  done <<<"${current_crontab}"

  final_crontab="$(printf '%s\n' "${final_lines[@]}")"
else
  final_crontab=""
fi

echo "Resulting crontab:"
echo "-----BEGIN CRONTAB-----"
if [ -n "${final_crontab}" ]; then
  printf '%s\n' "${final_crontab}"
fi
echo "-----END CRONTAB-----"

if [ "${MODE}" = "yes" ]; then
  if [ -n "${final_crontab}" ]; then
    printf '%s\n' "${final_crontab}" | crontab -
  else
    crontab -r 2>/dev/null || true
  fi
  echo "Removed voice-lab cron line if it existed."
else
  echo "Dry-run only. Re-run with --yes to remove."
fi

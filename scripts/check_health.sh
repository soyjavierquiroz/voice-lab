#!/usr/bin/env bash
set -euo pipefail

ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"
FAILURES=0
WARNINGS=0

check_cmd() {
  local name="$1"
  local required="${2:-required}"
  if command -v "${name}" >/dev/null 2>&1; then
    echo "OK   ${name}: $(command -v "${name}")"
  elif [ "${required}" = "required" ]; then
    echo "FAIL ${name}: not found"
    FAILURES=$((FAILURES + 1))
  else
    echo "WARN ${name}: not found"
    WARNINGS=$((WARNINGS + 1))
  fi
}

check_dir() {
  local path="$1"
  if [ -d "${path}" ]; then
    echo "OK   dir: ${path}"
  else
    echo "FAIL dir: ${path}"
    FAILURES=$((FAILURES + 1))
  fi
}

check_file() {
  local path="$1"
  if [ -f "${path}" ]; then
    echo "OK   file: ${path}"
  else
    echo "FAIL file: ${path}"
    FAILURES=$((FAILURES + 1))
  fi
}

echo "[voice-lab] Health check"
echo "Root: ${ROOT}"
echo

check_cmd python3
check_cmd git
check_cmd ffmpeg
check_cmd ffprobe

echo
check_file "${ROOT}/app/cli.py"

echo
check_dir "${ROOT}/app"
check_dir "${ROOT}/scripts"
check_dir "${ROOT}/input/pending"
check_dir "${ROOT}/input/manual"
check_dir "${ROOT}/queue/jobs"
check_dir "${ROOT}/queue/done"
check_dir "${ROOT}/queue/failed"
check_dir "${ROOT}/processing"
check_dir "${ROOT}/output/wav"
check_dir "${ROOT}/output/mp3"
check_dir "${ROOT}/datasets/mi_voz/raw"
check_dir "${ROOT}/datasets/mi_voz/clean"
check_dir "${ROOT}/datasets/mi_voz/metadata"
check_dir "${ROOT}/datasets/mi_voz/logs"
check_dir "${ROOT}/models/mi_voz/logs"
check_dir "${ROOT}/logs/jobs"
check_dir "${ROOT}/tmp"

echo
if [ "${FAILURES}" -gt 0 ]; then
  echo "FAIL Health check complete: ${FAILURES} failure(s), ${WARNINGS} warning(s)."
  echo "No packages were installed and no services were modified."
  exit 1
fi

echo "OK   Health check complete: ${WARNINGS} warning(s)."
echo "No packages were installed and no services were modified."

#!/usr/bin/env bash
set -euo pipefail

ROOT="${VOICE_LAB_ROOT:-/opt/voice-lab}"

check_cmd() {
  local name="$1"
  if command -v "${name}" >/dev/null 2>&1; then
    echo "OK   ${name}: $(command -v "${name}")"
  else
    echo "WARN ${name}: not found"
  fi
}

check_dir() {
  local path="$1"
  if [ -d "${path}" ]; then
    echo "OK   dir: ${path}"
  else
    echo "MISS dir: ${path}"
  fi
}

echo "[voice-lab] Health check"
echo "Root: ${ROOT}"
echo

check_cmd python3
check_cmd git
check_cmd ffmpeg

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
echo "Health check complete. No packages were installed and no services were modified."

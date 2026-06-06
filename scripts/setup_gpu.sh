#!/usr/bin/env bash
set -euo pipefail

cd /opt/voice-lab

ROOT="/opt/voice-lab"

echo "[voice-lab] GPU setup checklist"
echo "Root: ${ROOT}"
echo

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "OK nvidia-smi found:"
  nvidia-smi
else
  echo "WARN nvidia-smi not found."
  echo "This script is intended for a future GPU Droplet. No GPU setup was performed."
fi

echo
echo "Future checklist, not executed yet:"
echo "1. Verify nvidia-smi and CUDA driver/runtime compatibility."
echo "2. Verify python version."
echo "3. Create .venv-gpu or another isolated GPU environment."
echo "4. Install PyTorch CUDA matching the available CUDA version."
echo "5. Install Applio/RVC dependencies."
echo
echo "No apt, pip, external downloads, Docker or Swarm changes were performed."

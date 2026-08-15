#!/usr/bin/env bash
# ==============================================================================
# Persistent Background Distillation Pipeline Runner
# Designed to run indefinitely on Linux VPS even when local PC disconnects / powers off
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${SCRIPT_DIR}"
export PYTHONPATH="${SCRIPT_DIR}"

# Ensure virtualenv is loaded
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

MODEL_FILE="${SCRIPT_DIR}/models/qwen2.5-7b-instruct-q4_k_m.gguf"
MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

echo "================================================================="
echo "  Starting Background Pipeline Service at $(date)"
echo "================================================================="

mkdir -p models logs

# 1. Download Model if not present
if [ ! -f "${MODEL_FILE}" ] || [ $(wc -c < "${MODEL_FILE}") -lt 1000000000 ]; then
    echo "[1/2] Downloading Qwen2.5-7B-Instruct Q4_K_M model weights..."
    curl -L -C - -o "${MODEL_FILE}" "${MODEL_URL}"
else
    echo "[1/2] Model weights already present ($(ls -lh "${MODEL_FILE}" | awk '{print $5}'))."
fi

# 2. Run Pipeline in Python unbuffered mode
echo "[2/2] Launching Distillation Pipeline (1,000 samples per format, batches of 20, 5 CPU threads)..."
python3 -u run_pipeline.py \
  --model-path "${MODEL_FILE}" \
  --output-file "${SCRIPT_DIR}/distillation_dataset.jsonl" \
  --samples-per-schema 1000 \
  --batch-size 20 \
  --threads 5 \
  --ctx-size 4096 \
  --include-seeds \
  --resume

echo "================================================================="
echo "  Pipeline Finished Successfully at $(date)"
echo "================================================================="

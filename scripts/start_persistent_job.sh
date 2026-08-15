#!/usr/bin/env bash
# ==============================================================================
# Persistent Background Distillation Pipeline Runner
# Designed to run indefinitely on Linux VPS even when local PC disconnects / powers off
# ==============================================================================

set -euo pipefail
cd /root/africa-deep

# Ensure virtualenv is loaded
source venv/bin/activate

LOG_FILE="/root/africa-deep/pipeline.log"
PID_FILE="/root/africa-deep/pipeline.pid"
MODEL_FILE="/root/africa-deep/models/qwen2.5-7b-instruct-q4_k_m.gguf"
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
  --output-file /root/africa-deep/distillation_dataset.jsonl \
  --samples-per-schema 1000 \
  --batch-size 20 \
  --threads 5 \
  --ctx-size 4096 \
  --include-seeds \
  --resume

echo "================================================================="
echo "  Pipeline Finished Successfully at $(date)"
echo "================================================================="

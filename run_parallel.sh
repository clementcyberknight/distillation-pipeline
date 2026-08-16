#!/usr/bin/env bash
# ==============================================================================
# Parallel Distillation Pipeline for NVIDIA RTX 4090 (24GB VRAM / 24 Physical Cores)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

mkdir -p logs data_splits

FINAL_OUTPUT="distillation_dataset.jsonl"
FINAL_QUARANTINE="logs/rejected_samples.jsonl"

echo "=========================================================="
echo " Starting Parallel Distillation Pipeline on RTX 4090"
echo " Cores: 24 (6 threads/worker) | VRAM: 24GB (4 workers)"
echo "=========================================================="


# Worker 1: 3 Schemas
python3 run_pipeline.py \
  --schemas GENERATIVE_CHART DOCUMENT_OUTPUT CONVERSATIONAL_CHAT \
  --output-file data_splits/dataset_w1.jsonl \
  --quarantine-file data_splits/quarantine_w1.jsonl \
  --device gpu \
  --threads 6 \
  --batch-size 50 \
  --no-resume \
  > logs/worker_1.log 2>&1 &
P1=$!

# Worker 2: 3 Schemas
python3 run_pipeline.py \
  --schemas DEEP_RESEARCH SHIFT_SCHEDULE PRODUCTIVITY_CHART \
  --output-file data_splits/dataset_w2.jsonl \
  --quarantine-file data_splits/quarantine_w2.jsonl \
  --device gpu \
  --threads 6 \
  --batch-size 50 \
  --no-resume \
  > logs/worker_2.log 2>&1 &
P2=$!

# Worker 3: 2 Schemas
python3 run_pipeline.py \
  --schemas RED_FLAG_ALERT AUTO_TASK \
  --output-file data_splits/dataset_w3.jsonl \
  --quarantine-file data_splits/quarantine_w3.jsonl \
  --device gpu \
  --threads 6 \
  --batch-size 50 \
  --no-resume \
  > logs/worker_3.log 2>&1 &
P3=$!

# Worker 4: 2 Schemas
python3 run_pipeline.py \
  --schemas TOOL_CALL ACTION_CONFIRMATION \
  --output-file data_splits/dataset_w4.jsonl \
  --quarantine-file data_splits/quarantine_w4.jsonl \
  --device gpu \
  --threads 6 \
  --batch-size 50 \
  --no-resume \
  > logs/worker_4.log 2>&1 &
P4=$!

echo "Worker 1 (PID $P1): GENERATIVE_CHART, DOCUMENT_OUTPUT, CONVERSATIONAL_CHAT"
echo "Worker 2 (PID $P2): DEEP_RESEARCH, SHIFT_SCHEDULE, PRODUCTIVITY_CHART"
echo "Worker 3 (PID $P3): RED_FLAG_ALERT, AUTO_TASK"
echo "Worker 4 (PID $P4): TOOL_CALL, ACTION_CONFIRMATION"
echo "=========================================================="
echo "Monitoring: 'watch -n 1 nvidia-smi' | Logs: 'tail -f logs/worker_*.log'"
echo "Waiting for workers to finish..."

# Wait for all processes to complete
wait $P1 $P2 $P3 $P4

echo "=========================================================="
echo "All workers finished! Merging split datasets..."

# Atomic merge
cat data_splits/dataset_w1.jsonl \
    data_splits/dataset_w2.jsonl \
    data_splits/dataset_w3.jsonl \
    data_splits/dataset_w4.jsonl > "${FINAL_OUTPUT}"

cat data_splits/quarantine_w1.jsonl \
    data_splits/quarantine_w2.jsonl \
    data_splits/quarantine_w3.jsonl \
    data_splits/quarantine_w4.jsonl > "${FINAL_QUARANTINE}" 2>/dev/null || true

TOTAL_LINES=$(wc -l < "${FINAL_OUTPUT}")
echo "✓ Merge complete! Total generated training pairs: ${TOTAL_LINES}"
echo "✓ Saved to: ${FINAL_OUTPUT}"
echo "=========================================================="

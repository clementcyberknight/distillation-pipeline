#!/bin/bash
# run_parallel.sh
# Parallel execution script for the Synthetic Data Distillation Engine on RunPod (RTX 4090).
# Splits the 10 schema formats across 4 concurrent python processes to fully saturate
# the 24GB VRAM and 48 CPU threads.

echo "=========================================================="
echo "Starting Parallel Distillation Pipeline on RTX 4090"
echo "=========================================================="

# Define schema batches for 4 workers
WORKER_1_SCHEMAS="GENERATIVE_CHART DOCUMENT_OUTPUT CONVERSATIONAL_CHAT"
WORKER_2_SCHEMAS="DEEP_RESEARCH SHIFT_SCHEDULE PRODUCTIVITY_CHART"
WORKER_3_SCHEMAS="RED_FLAG_ALERT AUTO_TASK"
WORKER_4_SCHEMAS="TOOL_CALL ACTION_CONFIRMATION"

# Ensure log directory exists
mkdir -p logs

echo "Launching Worker 1: $WORKER_1_SCHEMAS"
python3 run_pipeline.py --schemas $WORKER_1_SCHEMAS > logs/worker_1.log 2>&1 &
P1=$!

echo "Launching Worker 2: $WORKER_2_SCHEMAS"
python3 run_pipeline.py --schemas $WORKER_2_SCHEMAS > logs/worker_2.log 2>&1 &
P2=$!

echo "Launching Worker 3: $WORKER_3_SCHEMAS"
python3 run_pipeline.py --schemas $WORKER_3_SCHEMAS > logs/worker_3.log 2>&1 &
P3=$!

echo "Launching Worker 4: $WORKER_4_SCHEMAS"
python3 run_pipeline.py --schemas $WORKER_4_SCHEMAS > logs/worker_4.log 2>&1 &
P4=$!

echo "All workers launched successfully!"
echo "Worker PIDs: $P1 $P2 $P3 $P4"
echo "=========================================================="
echo "To monitor GPU usage, open another terminal and run: watch -n 1 nvidia-smi"
echo "To view progress, run: tail -f logs/worker_*.log"
echo "Waiting for all workers to finish..."

wait $P1 $P2 $P3 $P4

echo "=========================================================="
echo "All workers completed!"
echo "Combined dataset is in distillation_dataset.jsonl"

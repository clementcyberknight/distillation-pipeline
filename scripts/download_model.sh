#!/usr/bin/env bash
# ==============================================================================
# Model Downloader for Linux VPS (6 vCPU, 12 GB RAM)
# Downloads Qwen2.5-7B-Instruct-GGUF (Q4_K_M quantization ~4.68 GB)
# ==============================================================================

set -euo pipefail

MODEL_DIR="models"
MODEL_FILENAME="qwen2.5-7b-instruct-q4_k_m.gguf"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILENAME}"
HF_REPO="bartowski/Qwen2.5-7B-Instruct-GGUF"
DIRECT_URL="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

mkdir -p "${MODEL_DIR}"

echo "========================================================"
echo "  Downloading Teacher Model: ${MODEL_FILENAME}"
echo "  Target Destination: ${MODEL_PATH}"
echo "========================================================"

if [ -f "${MODEL_PATH}" ]; then
    echo "✓ Model file already exists at ${MODEL_PATH}."
    ls -lh "${MODEL_PATH}"
    exit 0
fi

# 1. Try downloading via huggingface-cli if available
if command -v huggingface-cli &> /dev/null; then
    echo "[1/3] Using huggingface-cli..."
    huggingface-cli download "${HF_REPO}" "Qwen2.5-7B-Instruct-Q4_K_M.gguf" --local-dir "${MODEL_DIR}" --local-dir-use-symlinks False
    mv "${MODEL_DIR}/Qwen2.5-7B-Instruct-Q4_K_M.gguf" "${MODEL_PATH}" || true

# 2. Try aria2c for multi-connection accelerated download
elif command -v aria2c &> /dev/null; then
    echo "[2/3] Using aria2c for fast multi-threaded download..."
    aria2c -x 4 -s 4 -o "${MODEL_FILENAME}" -d "${MODEL_DIR}" "${DIRECT_URL}"

# 3. Fallback to curl / wget
elif command -v curl &> /dev/null; then
    echo "[3/3] Using curl with progress bar..."
    curl -L -C - -o "${MODEL_PATH}" "${DIRECT_URL}"

elif command -v wget &> /dev/null; then
    echo "[3/3] Using wget..."
    wget -c -O "${MODEL_PATH}" "${DIRECT_URL}"

else
    echo "ERROR: Neither huggingface-cli, aria2c, curl, nor wget is installed."
    echo "Please install curl: sudo apt-get update && sudo apt-get install -y curl"
    exit 1
fi

echo "========================================================"
echo "✓ Download Complete!"
ls -lh "${MODEL_PATH}"
echo "========================================================"

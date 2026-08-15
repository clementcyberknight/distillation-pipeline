#!/usr/bin/env python3
"""Python-native model downloader for the Qwen2.5-7B-Instruct GGUF weights."""

import os
import sys
from pathlib import Path

MODEL_DIR = Path("models")
MODEL_FILENAME = "qwen2.5-7b-instruct-q4_k_m.gguf"
TARGET_PATH = MODEL_DIR / MODEL_FILENAME
REPO_ID = "bartowski/Qwen2.5-7B-Instruct-GGUF"
FILENAME_IN_REPO = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"


def download():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if TARGET_PATH.exists() and TARGET_PATH.stat().st_size > 1_000_000_000:
        print(f"✓ Model already exists at {TARGET_PATH} ({TARGET_PATH.stat().st_size / (1024**3):.2f} GB)")
        return

    print(f"Downloading {FILENAME_IN_REPO} from Hugging Face ({REPO_ID})...")
    try:
        from huggingface_hub import hf_hub_download
        downloaded = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME_IN_REPO,
            local_dir=str(MODEL_DIR),
            local_dir_use_symlinks=False,
        )
        # Rename to standardized filename if needed
        if os.path.exists(downloaded) and downloaded != str(TARGET_PATH):
            os.replace(downloaded, str(TARGET_PATH))
        print(f"✓ Successfully downloaded model to {TARGET_PATH}")
    except ImportError:
        print("huggingface_hub is not installed. Installing or running curl...")
        import urllib.request
        url = f"https://huggingface.co/{REPO_ID}/resolve/main/{FILENAME_IN_REPO}"
        print(f"Downloading from: {url}")
        urllib.request.urlretrieve(url, str(TARGET_PATH))
        print(f"✓ Downloaded model to {TARGET_PATH}")


if __name__ == "__main__":
    download()

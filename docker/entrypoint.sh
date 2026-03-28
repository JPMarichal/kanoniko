#!/bin/bash
set -e

# Download embedding model on first run using huggingface-cli
# (avoids the httpx client-closed bug in huggingface_hub)
MODEL_NAME="${ALEJANDRIA_EMBEDDING_MODEL:-sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2}"
echo "Ensuring embedding model is cached: $MODEL_NAME"
huggingface-cli download "$MODEL_NAME" --quiet 2>/dev/null || {
    echo "huggingface-cli download failed, trying with requests backend..."
    HF_HUB_ENABLE_HTTPX=0 python -c "
from huggingface_hub import snapshot_download
snapshot_download('$MODEL_NAME')
print('Model downloaded.')
" || echo "WARNING: Could not pre-download model. Will retry at first query."
}

# Start the API server
exec uvicorn alejandria.main:app --host 0.0.0.0 --port 4300

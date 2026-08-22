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

# SSH tunnel key: the source is on a Windows filesystem mounted read-only,
# which breaks Unix permissions (SSH refuses 0777). Copy to /tmp with 600.
if [ -f /root/.ssh/tunnel_key ]; then
    cp /root/.ssh/tunnel_key /tmp/tunnel_key
    chmod 600 /tmp/tunnel_key
    export ALEJANDRIA_SSH_TUNNEL_PRIVATE_KEY_PATH=/tmp/tunnel_key
    echo "SSH tunnel key fixed at $ALEJANDRIA_SSH_TUNNEL_PRIVATE_KEY_PATH"
fi

# Start the API server
exec uvicorn alejandria.main:app --host 0.0.0.0 --port 4300

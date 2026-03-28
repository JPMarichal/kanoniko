FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Inject corporate/custom CA certificates (for environments behind SSL-inspecting proxies)
COPY docker/ca-certificates.crt /usr/local/share/ca-certificates/corporate.crt
RUN update-ca-certificates
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Python deps — install in two layers for caching
COPY pyproject.toml ./

# Core deps
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.30.0" \
    "pydantic>=2.0" \
    "pydantic-settings>=2.0" \
    "beautifulsoup4>=4.12.0" \
    "markdown-it-py>=3.0.0" \
    "aiofiles>=23.0"

# Semantic deps (separate layer — heavier, changes less often)
RUN pip install --no-cache-dir \
    "sentence-transformers>=3.0" \
    "qdrant-client>=1.12"

# Graph deps
RUN pip install --no-cache-dir \
    "neo4j>=5.0"

# MCP + CLI deps
RUN pip install --no-cache-dir \
    "click>=8.1" \
    "mcp>=1.0"

# Chat (RAG) deps
RUN pip install --no-cache-dir \
    "anthropic>=0.40" \
    "openai>=1.50" \
    "google-genai>=1.0"

# NER deps (spaCy + language models for entity auto-discovery)
RUN pip install --no-cache-dir "spacy>=3.7"
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download es_core_news_sm

# Copy source and install package
COPY src/ ./src/
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
RUN pip install --no-cache-dir -e .

# Create data directories
RUN mkdir -p /app/data/sqlite

EXPOSE 4300

ENV ALEJANDRIA_HOST=0.0.0.0
ENV ALEJANDRIA_PORT=4300
ENV ALEJANDRIA_CORPUS_PATH=/app/corpus
ENV ALEJANDRIA_SQLITE_DB_PATH=/app/data/sqlite/alejandria.db
ENV ALEJANDRIA_EMBEDDING_DEVICE=cpu
ENV ALEJANDRIA_QDRANT_HOST=qdrant
ENV ALEJANDRIA_QDRANT_PORT=6333
ENV ALEJANDRIA_NEO4J_URI=bolt://neo4j:7687
ENV ALEJANDRIA_NEO4J_USER=neo4j
ENV ALEJANDRIA_NEO4J_PASSWORD=alejandria

CMD ["/app/entrypoint.sh"]

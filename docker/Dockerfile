FROM python:3.11-slim AS base

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY pyproject.toml ./
RUN pip install --no-cache-dir . 2>/dev/null || true
# Install core deps explicitly for the build stage
RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    "uvicorn[standard]>=0.30.0" \
    pydantic>=2.0 \
    pydantic-settings>=2.0 \
    beautifulsoup4>=4.12.0 \
    markdown-it-py>=3.0.0 \
    aiofiles>=24.0

# Copy source
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir -e .

# Create data directories
RUN mkdir -p /app/data/sqlite

EXPOSE 4300

ENV ALEJANDRIA_HOST=0.0.0.0
ENV ALEJANDRIA_PORT=4300
ENV ALEJANDRIA_CORPUS_PATH=/app/corpus
ENV ALEJANDRIA_SQLITE_DB_PATH=/app/data/sqlite/alejandria.db

CMD ["uvicorn", "alejandria.main:app", "--host", "0.0.0.0", "--port", "4300"]

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Alejandría"
    app_version: str = "0.1.0"

    # Corpus
    corpus_path: Path = Path("/app/corpus")

    # SQLite FTS
    sqlite_db_path: Path = Path("/app/data/sqlite/alejandria.db")

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "alejandria"

    # Neo4j
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "alejandria"

    # Embeddings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_device: str = "cuda"
    embedding_dim: int = 384

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Indexing
    index_interval_seconds: int = 300
    supported_extensions: list[str] = [".md", ".txt", ".html", ".json"]

    # LLM (for RAG chat)
    llm_provider: str = "anthropic"  # "anthropic", "gemini", or "openai"
    llm_model: str = "claude-haiku-4-5-20251001"
    llm_api_key: str = ""
    llm_base_url: str | None = None  # For OpenAI-compatible endpoints
    llm_max_tokens: int = 2048
    llm_max_tokens_fast: int = 1024   # Shorter output for simple questions (FAST tier)
    llm_temperature: float = 0.3

    # Per-provider API keys (preferred over llm_api_key/llm_alt_api_key)
    llm_anthropic_api_key: str = ""
    llm_gemini_api_key: str = ""
    llm_openai_api_key: str = ""
    llm_deepseek_api_key: str = ""

    # Alternative LLM (legacy — kept for /chat/compare backward compat)
    llm_alt_provider: str = ""  # e.g., "gemini"
    llm_alt_model: str = ""  # e.g., "gemini-2.5-flash"
    llm_alt_api_key: str = ""

    # Tiered model selection
    llm_answer_tier: str = "auto"   # "auto", "fast", "balanced", "quality", or a model ID
    llm_internal_tier: str = "fast"  # Tier for internal calls (expansion, reranking)

    # Entity Profiles
    profile_max_passages: int = 10  # Max key passages per entity profile
    profile_llm_tier: str = "fast"  # LLM tier for profile generation (Phase 2)

    # RAG
    rag_context_chunks: int = 8   # Max chunks in final context (was 12; 8 saves ~30% input tokens)
    rag_context_chunks_quality: int = 12  # More context for complex questions (QUALITY tier)
    rag_search_limit: int = 25  # Candidates per search mode before RRF

    # Server
    host: str = "0.0.0.0"
    port: int = 4300

    model_config = {"env_prefix": "ALEJANDRIA_", "env_file": ".env"}


settings = Settings()

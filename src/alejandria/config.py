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

    # Server
    host: str = "0.0.0.0"
    port: int = 4300

    model_config = {"env_prefix": "ALEJANDRIA_", "env_file": ".env"}


settings = Settings()

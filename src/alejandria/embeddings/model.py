"""Embedding model wrapper using sentence-transformers. Singleton pattern."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

logger = logging.getLogger(__name__)

_model = None


def get_model():
    """Get or initialize the sentence-transformers model (singleton)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        from alejandria.config import settings

        logger.info(
            "Loading embedding model %s on device=%s",
            settings.embedding_model,
            settings.embedding_device,
        )
        # Use local_files_only to avoid huggingface_hub's httpx client which
        # conflicts with uvicorn's event loop. The model must be pre-downloaded
        # by the entrypoint script.
        try:
            _model = SentenceTransformer(
                settings.embedding_model,
                device=settings.embedding_device,
                local_files_only=True,
            )
        except Exception:
            logger.warning("Model not cached locally, attempting download...")
            os.environ["HF_HUB_ENABLE_HTTPX"] = "0"
            os.environ["TRANSFORMERS_OFFLINE"] = "0"
            _model = SentenceTransformer(
                settings.embedding_model,
                device=settings.embedding_device,
            )
        logger.info("Embedding model loaded. Dimension: %d", _model.get_sentence_embedding_dimension())
    return _model


def encode(texts: list[str], batch_size: int = 64) -> NDArray[np.float32]:
    """Encode a list of texts into embedding vectors.

    Returns:
        numpy array of shape (len(texts), embedding_dim)
    """
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=len(texts) > 100,
        normalize_embeddings=True,
    )
    return embeddings


def encode_single(text: str) -> NDArray[np.float32]:
    """Encode a single text into an embedding vector."""
    return encode([text])[0]

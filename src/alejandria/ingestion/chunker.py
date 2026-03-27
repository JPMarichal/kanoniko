"""Text chunker that splits documents into overlapping chunks respecting sentence boundaries."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    index: int
    start_char: int
    end_char: int


_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n\n+")


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[Chunk]:
    """Split text into overlapping chunks.

    Strategy:
    1. Split into sentences/paragraphs.
    2. Accumulate sentences into chunks of approximately `chunk_size` words.
    3. Overlap by `chunk_overlap` words from the end of the previous chunk.
    """
    if not text.strip():
        return []

    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks: list[Chunk] = []
    current_words: list[str] = []
    current_start = 0
    char_pos = 0
    chunk_start_char = 0

    for sentence in sentences:
        words = sentence.split()
        if not words:
            char_pos += len(sentence)
            continue

        if current_words and len(current_words) + len(words) > chunk_size:
            chunk_text_str = " ".join(current_words)
            chunks.append(Chunk(
                text=chunk_text_str,
                index=len(chunks),
                start_char=chunk_start_char,
                end_char=chunk_start_char + len(chunk_text_str),
            ))

            # Overlap: keep last chunk_overlap words
            if chunk_overlap > 0 and len(current_words) > chunk_overlap:
                overlap_words = current_words[-chunk_overlap:]
                current_words = overlap_words
            else:
                current_words = []
            chunk_start_char = char_pos

        if not current_words:
            chunk_start_char = char_pos

        current_words.extend(words)
        char_pos += len(sentence)

    # Final chunk
    if current_words:
        chunk_text_str = " ".join(current_words)
        chunks.append(Chunk(
            text=chunk_text_str,
            index=len(chunks),
            start_char=chunk_start_char,
            end_char=chunk_start_char + len(chunk_text_str),
        ))

    return chunks


def _split_sentences(text: str) -> list[str]:
    """Split text by sentence boundaries or paragraph breaks."""
    parts = _SENTENCE_RE.split(text)
    return [p.strip() for p in parts if p.strip()]

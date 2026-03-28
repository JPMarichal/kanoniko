"""Text chunker that splits documents into overlapping chunks respecting sentence boundaries.

For scripture files, uses verse-aware chunking that groups consecutive verses
into chunks of a target word size, preserving verse boundaries.
"""

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
_VERSE_LINE_RE = re.compile(r"^(\d{1,3})\s+(.*)", re.MULTILINE)


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


def chunk_scripture(
    text: str,
    target_words: int = 150,
    max_words: int = 300,
) -> list[Chunk]:
    """Split verse-numbered scripture text into verse-group chunks.

    Groups consecutive verses until the word count approaches *target_words*,
    never exceeding *max_words*.  Each chunk preserves verse numbers in the
    text (e.g., "18 Now the birth of Jesus Christ...  19 Then Joseph...").

    Falls back to :func:`chunk_text` if no verses are detected.
    """
    verses = _parse_verse_lines(text)
    if not verses:
        return chunk_text(text, chunk_size=target_words * 2, chunk_overlap=30)

    chunks: list[Chunk] = []
    current_verses: list[tuple[int, str]] = []
    current_words = 0
    char_pos = 0

    for vnum, vtext in verses:
        vword_count = len(vtext.split())

        # If adding this verse would exceed max_words, flush first
        if current_verses and (current_words + vword_count) > max_words:
            chunks.append(_build_verse_chunk(current_verses, len(chunks), char_pos))
            char_pos += len(chunks[-1].text) + 1  # +1 for newline
            current_verses = []
            current_words = 0

        current_verses.append((vnum, vtext))
        current_words += vword_count

        # If we've reached target and the next verse would push us over, flush
        if current_words >= target_words:
            chunks.append(_build_verse_chunk(current_verses, len(chunks), char_pos))
            char_pos += len(chunks[-1].text) + 1
            current_verses = []
            current_words = 0

    # Remaining verses
    if current_verses:
        chunks.append(_build_verse_chunk(current_verses, len(chunks), char_pos))

    return chunks


def _parse_verse_lines(text: str) -> list[tuple[int, str]]:
    """Parse numbered verse lines from scripture text.

    Returns list of (verse_number, verse_text) tuples.
    Handles multi-line verses (continuation lines without a number prefix).
    """
    verses: list[tuple[int, str]] = []
    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            continue
        m = _VERSE_LINE_RE.match(line)
        if m:
            verses.append((int(m.group(1)), m.group(2)))
        elif verses:
            # Continuation of previous verse
            num, body = verses[-1]
            verses[-1] = (num, body + " " + line.strip())
    return verses


def _build_verse_chunk(
    verses: list[tuple[int, str]],
    index: int,
    start_char: int,
) -> Chunk:
    """Build a Chunk from a group of verses, preserving verse numbers."""
    text = " ".join(f"{vnum} {vtext}" for vnum, vtext in verses)
    return Chunk(
        text=text,
        index=index,
        start_char=start_char,
        end_char=start_char + len(text),
    )

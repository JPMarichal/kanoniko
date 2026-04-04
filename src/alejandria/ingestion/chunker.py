"""Text chunker that splits documents into overlapping chunks respecting sentence boundaries.

For scripture files, uses verse-aware chunking that groups consecutive verses
into chunks of a target word size, preserving verse boundaries.

For handbook files, uses section-aware chunking that splits on markdown
section headings (## N.M, ### N.M.P, etc.) and preserves section references.
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
    reference: str | None = None


_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n\n+")
_VERSE_LINE_RE = re.compile(r"^(\d{1,3})\s+(.*)", re.MULTILINE)

# Matches handbook section headings like "## 8.1 Purpose", "### 8.1.1 Purpose",
# "#### 8.2.1.1 Gospel Learning", or bare "8.1 Purpose" at start of line.
_HANDBOOK_HEADING_RE = re.compile(
    r"^(?:#{2,4}\s+)?(\d+(?:\.\d+)+)\s+(.+)",
    re.MULTILINE,
)


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


# ---------------------------------------------------------------------------
# Handbook chunker
# ---------------------------------------------------------------------------


def chunk_handbook(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[Chunk]:
    """Split handbook markdown into section-aware chunks.

    Strategy:
    1. Split the document at section headings (``## N.M``, ``### N.M.P``,
       ``#### N.M.P.Q``, or bare ``N.M Title`` at start of line).
    2. Each section becomes one chunk.  If the section exceeds *chunk_size*
       words it is further split at paragraph boundaries.
    3. Sections shorter than *chunk_size* words are merged with subsequent
       sections until the limit is reached.
    4. Every chunk carries the originating section number in its
       ``reference`` field (e.g. ``"8.1.2"``).

    Falls back to :func:`chunk_text` if no section headings are detected.
    """
    sections = _split_handbook_sections(text)
    if not sections:
        return chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks: list[Chunk] = []
    pending_text: str = ""
    pending_ref: str = ""
    pending_start: int = 0

    for section_ref, section_text, start_char in sections:
        word_count = len(section_text.split())

        # If pending + this section would exceed chunk_size, flush pending first
        if pending_text:
            combined_words = len(pending_text.split()) + word_count
            if combined_words > chunk_size:
                chunks.extend(
                    _emit_handbook_chunks(
                        pending_text, pending_ref, pending_start,
                        len(chunks), chunk_size, chunk_overlap,
                    )
                )
                pending_text = ""
                pending_ref = ""

        # Start new pending or merge into it
        if not pending_text:
            pending_text = section_text
            pending_ref = section_ref
            pending_start = start_char
        else:
            pending_text += "\n\n" + section_text
            # Keep the first section ref for the merged chunk

    # Flush remaining
    if pending_text:
        chunks.extend(
            _emit_handbook_chunks(
                pending_text, pending_ref, pending_start,
                len(chunks), chunk_size, chunk_overlap,
            )
        )

    # Re-index to ensure sequential indices
    for i, c in enumerate(chunks):
        c.index = i

    return chunks


def _split_handbook_sections(text: str) -> list[tuple[str, str, int]]:
    """Split text into sections delimited by handbook headings.

    Returns list of ``(section_ref, section_text, start_char)`` tuples.
    *section_text* includes the heading line itself as the first line.
    """
    matches = list(_HANDBOOK_HEADING_RE.finditer(text))
    if not matches:
        return []

    sections: list[tuple[str, str, int]] = []

    # Content before the first heading (preamble) — skip or attach to first section
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        section_ref = m.group(1)  # e.g. "8.1.2"
        if section_text:
            sections.append((section_ref, section_text, start))

    return sections


def _emit_handbook_chunks(
    text: str,
    reference: str,
    start_char: int,
    base_index: int,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    """Emit one or more chunks from a handbook section.

    If the text fits within *chunk_size* words, a single chunk is returned.
    Otherwise the text is split at paragraph boundaries, preserving the
    section heading as the first line of every sub-chunk.
    """
    words = text.split()
    if len(words) <= chunk_size:
        return [Chunk(
            text=text,
            index=base_index,
            start_char=start_char,
            end_char=start_char + len(text),
            reference=reference,
        )]

    # Extract heading (first line) to prepend to every sub-chunk
    first_newline = text.find("\n")
    if first_newline == -1:
        # Single very long line — fall back to word-level splitting
        heading = ""
        body = text
    else:
        heading = text[:first_newline].strip()
        body = text[first_newline:].strip()

    paragraphs = re.split(r"\n\n+", body)
    chunks: list[Chunk] = []
    current_parts: list[str] = []
    current_words = len(heading.split()) if heading else 0
    offset = start_char

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        pwords = len(para.split())

        if current_parts and current_words + pwords > chunk_size:
            # Flush
            chunk_body = "\n\n".join(current_parts)
            chunk_text_str = f"{heading}\n\n{chunk_body}" if heading else chunk_body
            chunks.append(Chunk(
                text=chunk_text_str,
                index=base_index + len(chunks),
                start_char=offset,
                end_char=offset + len(chunk_text_str),
                reference=reference,
            ))
            # Overlap: keep last chunk_overlap words from current parts
            if chunk_overlap > 0:
                overlap_text = " ".join(chunk_body.split()[-chunk_overlap:])
                current_parts = [overlap_text]
                current_words = len(heading.split()) + chunk_overlap
            else:
                current_parts = []
                current_words = len(heading.split()) if heading else 0
            offset += len(chunk_text_str) + 2  # approximate

        current_parts.append(para)
        current_words += pwords

    # Final sub-chunk
    if current_parts:
        chunk_body = "\n\n".join(current_parts)
        chunk_text_str = f"{heading}\n\n{chunk_body}" if heading else chunk_body
        chunks.append(Chunk(
            text=chunk_text_str,
            index=base_index + len(chunks),
            start_char=offset,
            end_char=offset + len(chunk_text_str),
            reference=reference,
        ))

    return chunks

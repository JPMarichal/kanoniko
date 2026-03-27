"""Tests for text chunker."""

from alejandria.ingestion.chunker import chunk_text


def test_empty_text() -> None:
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_short_text() -> None:
    chunks = chunk_text("Hello world. This is a test.", chunk_size=100)
    assert len(chunks) == 1
    assert "Hello world" in chunks[0].text


def test_chunking_produces_overlap() -> None:
    # Build a text that exceeds chunk_size words
    sentences = [f"Sentence number {i} with some extra words to fill space." for i in range(50)]
    text = " ".join(sentences)

    chunks = chunk_text(text, chunk_size=30, chunk_overlap=5)
    assert len(chunks) > 1

    # Verify chunks have sequential indices
    for i, chunk in enumerate(chunks):
        assert chunk.index == i


def test_chunk_indices_are_sequential() -> None:
    text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
    chunks = chunk_text(text, chunk_size=5, chunk_overlap=1)
    for i, chunk in enumerate(chunks):
        assert chunk.index == i

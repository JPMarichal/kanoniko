"""Shared test fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from alejandria.ingestion.registry import DocumentRegistry
from alejandria.search.textual import TextualSearch


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def registry(tmp_db: Path) -> DocumentRegistry:
    return DocumentRegistry(tmp_db)


@pytest.fixture
def textual_search(tmp_db: Path) -> TextualSearch:
    return TextualSearch(tmp_db)


@pytest.fixture
def sample_corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir()

    # Create sample files
    scriptures = corpus / "scriptures"
    scriptures.mkdir()
    (scriptures / "sample.txt").write_text(
        "And it came to pass that Nephi did go forth into the wilderness. "
        "He traveled many days in the desert. "
        "And he prayed unto the Lord for guidance.",
        encoding="utf-8",
    )

    (scriptures / "sample.md").write_text(
        "# The Book of Alma\n\n"
        "Now it came to pass that the sons of Mosiah journeyed into the land of Nephi. "
        "They went forth to preach the word of God.",
        encoding="utf-8",
    )

    conference = corpus / "general-conference"
    conference.mkdir()
    (conference / "talk.html").write_text(
        "<html><body><h1>Faith and Hope</h1>"
        "<p>Brothers and sisters, today I want to speak about faith.</p>"
        "<p>Faith is the substance of things hoped for.</p>"
        "</body></html>",
        encoding="utf-8",
    )

    (conference / "talk.json").write_text(
        '{"title": "On Charity", "speaker": "Elder Smith", '
        '"body": "Charity is the pure love of Christ. It endureth forever."}',
        encoding="utf-8",
    )

    return corpus

"""Tests for the ingestion pipeline."""

from pathlib import Path
from unittest.mock import patch

from alejandria.ingestion.pipeline import IngestionPipeline
from alejandria.ingestion.sqlite_registry import SqliteDocumentRegistry as DocumentRegistry
from alejandria.search.textual import TextualSearch


def test_ingest_new_files(sample_corpus: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    registry = DocumentRegistry(db_path)
    textual = TextualSearch(db_path)

    pipeline = IngestionPipeline(registry, textual)

    with patch("alejandria.ingestion.pipeline.settings") as mock_settings:
        mock_settings.corpus_path = sample_corpus
        mock_settings.supported_extensions = [".md", ".txt", ".html", ".json"]
        mock_settings.chunk_size = 500
        mock_settings.chunk_overlap = 50

        stats = pipeline.run()

    assert stats.new_files == 4
    assert stats.errors == 0
    assert stats.total_chunks > 0
    assert registry.count() == 4
    assert textual.count_chunks() > 0


def test_incremental_skip_unchanged(sample_corpus: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    registry = DocumentRegistry(db_path)
    textual = TextualSearch(db_path)

    pipeline = IngestionPipeline(registry, textual)

    with patch("alejandria.ingestion.pipeline.settings") as mock_settings:
        mock_settings.corpus_path = sample_corpus
        mock_settings.supported_extensions = [".md", ".txt", ".html", ".json"]
        mock_settings.chunk_size = 500
        mock_settings.chunk_overlap = 50

        # First run
        stats1 = pipeline.run()
        assert stats1.new_files == 4

        # Second run — nothing changed
        stats2 = pipeline.run()
        assert stats2.new_files == 0
        assert stats2.updated_files == 0


def test_detect_modified_file(sample_corpus: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    registry = DocumentRegistry(db_path)
    textual = TextualSearch(db_path)

    pipeline = IngestionPipeline(registry, textual)

    with patch("alejandria.ingestion.pipeline.settings") as mock_settings:
        mock_settings.corpus_path = sample_corpus
        mock_settings.supported_extensions = [".md", ".txt", ".html", ".json"]
        mock_settings.chunk_size = 500
        mock_settings.chunk_overlap = 50

        pipeline.run()

        # Modify a file
        (sample_corpus / "scriptures" / "sample.txt").write_text(
            "New content that is different from before.", encoding="utf-8"
        )

        stats = pipeline.run()
        assert stats.updated_files == 1


def test_detect_deleted_file(sample_corpus: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    registry = DocumentRegistry(db_path)
    textual = TextualSearch(db_path)

    pipeline = IngestionPipeline(registry, textual)

    with patch("alejandria.ingestion.pipeline.settings") as mock_settings:
        mock_settings.corpus_path = sample_corpus
        mock_settings.supported_extensions = [".md", ".txt", ".html", ".json"]
        mock_settings.chunk_size = 500
        mock_settings.chunk_overlap = 50

        pipeline.run()

        # Delete a file
        (sample_corpus / "scriptures" / "sample.txt").unlink()

        stats = pipeline.run()
        assert stats.deleted_files == 1
        assert registry.count() == 3

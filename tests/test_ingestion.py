"""Tests for the ingestion pipeline.

These tests pin the SQLite-backed legacy drivers explicitly. They are
retired alongside SQLite in §3.4 of docs/ingestion-workflow.md; integration
tests against Postgres live in tests/storage/ and tests/knowledge/.
"""

from pathlib import Path
from unittest.mock import patch

from alejandria.ingestion.pipeline import IngestionPipeline
from alejandria.ingestion.sqlite_registry import SqliteDocumentRegistry
from alejandria.storage.legacy_chunk_writer import LegacyChunkWriter


def _make_pipeline(db_path: Path) -> tuple[SqliteDocumentRegistry, LegacyChunkWriter, IngestionPipeline]:
    registry = SqliteDocumentRegistry(db_path)
    chunk_writer = LegacyChunkWriter()
    pipeline = IngestionPipeline(registry, chunk_writer)
    return registry, chunk_writer, pipeline


def _patched_settings(mock_settings, sample_corpus: Path, db_path: Path) -> None:
    mock_settings.corpus_path = sample_corpus
    mock_settings.supported_extensions = [".md", ".txt", ".html", ".json"]
    mock_settings.chunk_size = 500
    mock_settings.chunk_overlap = 50
    mock_settings.sqlite_db_path = db_path


def test_ingest_new_files(sample_corpus: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    registry, chunk_writer, pipeline = _make_pipeline(db_path)

    with patch("alejandria.ingestion.pipeline.settings") as mock_settings:
        _patched_settings(mock_settings, sample_corpus, db_path)
        stats = pipeline.run()

    assert stats.new_files == 4
    assert stats.errors == 0
    assert stats.total_chunks > 0
    assert registry.count() == 4
    assert chunk_writer.count_chunks() > 0


def test_incremental_skip_unchanged(sample_corpus: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    _, _, pipeline = _make_pipeline(db_path)

    with patch("alejandria.ingestion.pipeline.settings") as mock_settings:
        _patched_settings(mock_settings, sample_corpus, db_path)

        stats1 = pipeline.run()
        assert stats1.new_files == 4

        stats2 = pipeline.run()
        assert stats2.new_files == 0
        assert stats2.updated_files == 0


def test_detect_modified_file(sample_corpus: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    _, _, pipeline = _make_pipeline(db_path)

    with patch("alejandria.ingestion.pipeline.settings") as mock_settings:
        _patched_settings(mock_settings, sample_corpus, db_path)

        pipeline.run()

        (sample_corpus / "scriptures" / "sample.txt").write_text(
            "New content that is different from before.", encoding="utf-8"
        )

        stats = pipeline.run()
        assert stats.updated_files == 1


def test_detect_deleted_file(sample_corpus: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    registry, _, pipeline = _make_pipeline(db_path)

    with patch("alejandria.ingestion.pipeline.settings") as mock_settings:
        _patched_settings(mock_settings, sample_corpus, db_path)

        pipeline.run()

        (sample_corpus / "scriptures" / "sample.txt").unlink()

        stats = pipeline.run()
        assert stats.deleted_files == 1
        assert registry.count() == 3

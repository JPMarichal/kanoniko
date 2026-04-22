"""Dataclass smoke tests: shape + round-trip + defaults."""
from __future__ import annotations

from alejandria.backlogs.models import (
    DiscoveryEntry,
    DownloadEntry,
    IndexingEntry,
    ResearchEntry,
)


def test_discovery_entry_minimal() -> None:
    e = DiscoveryEntry(slug="a-book", title="A Book")
    d = e.to_dict()
    assert d == {
        "slug": "a-book",
        "title": "A Book",
        "source": "",
        "language": "",
        "category": "",
        "target_path": "",
        "status": "propuesto",
        "notes": "",
    }


def test_research_entry_defaults() -> None:
    e = ResearchEntry(slug="x")
    assert e.status == "pendiente"
    assert e.completed_at is None


def test_download_entry_roundtrip() -> None:
    e = DownloadEntry(
        slug="x", source_url="https://example.com/x.html",
        skill="manual", raw_path="data/raw/x.html",
        sha256="a" * 64, status="descargado",
    )
    d = e.to_dict()
    assert d["status"] == "descargado"
    assert d["sha256"] == "a" * 64


def test_indexing_entry_paths_default_list() -> None:
    e = IndexingEntry(slug="x")
    assert e.paths == []
    # Each instance gets its own list (field(default_factory=...))
    e2 = IndexingEntry(slug="y")
    e.paths.append("en/test/a.txt")
    assert e2.paths == []

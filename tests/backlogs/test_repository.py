"""JsonBacklog repository tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from alejandria.backlogs.repository import JsonBacklog
from alejandria.backlogs.validate import BACKLOG_NAMES


@pytest.fixture
def isolated_root(tmp_path: Path) -> Path:
    """Temp root with schemas copied from the real tree + empty JSON files."""
    root = tmp_path / "backlogs"
    root.mkdir()
    (root / "schemas").mkdir()

    real_schemas = Path(__file__).resolve().parents[2] / "backlogs" / "schemas"
    for schema in real_schemas.glob("*.schema.json"):
        (root / "schemas" / schema.name).write_text(
            schema.read_text(encoding="utf-8"), encoding="utf-8"
        )
    for name in BACKLOG_NAMES:
        (root / f"{name}.json").write_text("[]", encoding="utf-8")
    return root


def test_unknown_backlog_name_raises(isolated_root: Path) -> None:
    with pytest.raises(ValueError, match="unknown backlog"):
        JsonBacklog("bogus", root=isolated_root)


def test_empty_backlog_len_zero(isolated_root: Path) -> None:
    bl = JsonBacklog("discovery", root=isolated_root)
    assert len(bl) == 0
    assert bl.entries() == []
    assert "anything" not in bl


def test_upsert_insert_then_update(isolated_root: Path) -> None:
    bl = JsonBacklog("discovery", root=isolated_root)
    bl.upsert({"slug": "a", "title": "Alpha"})
    assert len(bl) == 1
    assert bl.get("a") == {"slug": "a", "title": "Alpha"}

    bl.upsert({"slug": "a", "title": "Alpha v2"})
    assert len(bl) == 1   # same slug updates in place
    assert bl.get("a")["title"] == "Alpha v2"


def test_upsert_without_slug_raises(isolated_root: Path) -> None:
    bl = JsonBacklog("discovery", root=isolated_root)
    with pytest.raises(ValueError, match="slug"):
        bl.upsert({"title": "no slug"})


def test_remove_reindexes(isolated_root: Path) -> None:
    bl = JsonBacklog("discovery", root=isolated_root)
    bl.upsert({"slug": "a", "title": "A"})
    bl.upsert({"slug": "b", "title": "B"})
    bl.upsert({"slug": "c", "title": "C"})
    assert bl.remove("b") is True
    assert [e["slug"] for e in bl.entries()] == ["a", "c"]
    assert bl.get("b") is None
    assert bl.get("c") == {"slug": "c", "title": "C"}


def test_remove_missing_slug_returns_false(isolated_root: Path) -> None:
    bl = JsonBacklog("discovery", root=isolated_root)
    assert bl.remove("nonexistent") is False


def test_save_atomic_and_roundtrip(isolated_root: Path) -> None:
    bl = JsonBacklog("downloads", root=isolated_root)
    bl.upsert({
        "slug": "x", "source_url": "https://example.com/x",
        "skill": "manual", "raw_path": "data/raw/x",
        "sha256": "a" * 64, "status": "descargado", "error": "",
    })
    bl.save()

    # Re-load from disk: state survives.
    bl2 = JsonBacklog("downloads", root=isolated_root)
    assert bl2.get("x")["sha256"] == "a" * 64

    # File on disk is valid JSON with an array root.
    raw = json.loads((isolated_root / "downloads.json").read_text(encoding="utf-8"))
    assert isinstance(raw, list)
    assert len(raw) == 1


def test_entries_returns_copy_not_reference(isolated_root: Path) -> None:
    bl = JsonBacklog("discovery", root=isolated_root)
    bl.upsert({"slug": "a", "title": "A"})
    lst = bl.entries()
    lst[0]["title"] = "mutated"
    # Internal state unchanged
    assert bl.get("a")["title"] == "A"


def test_validate_catches_invalid_in_memory(isolated_root: Path) -> None:
    bl = JsonBacklog("discovery", root=isolated_root)
    bl.upsert({"slug": "BAD_SLUG", "title": "T"})
    errors = bl.validate()
    assert errors, "expected pattern error on slug"


def test_save_preserves_insertion_order(isolated_root: Path) -> None:
    bl = JsonBacklog("discovery", root=isolated_root)
    for s in ["c", "a", "b"]:
        bl.upsert({"slug": s, "title": s.upper()})
    bl.save()
    raw = json.loads((isolated_root / "discovery.json").read_text(encoding="utf-8"))
    assert [e["slug"] for e in raw] == ["c", "a", "b"]

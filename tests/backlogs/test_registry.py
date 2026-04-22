"""BacklogRegistry cross-query tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from alejandria.backlogs.registry import BacklogRegistry
from alejandria.backlogs.validate import BACKLOG_NAMES


@pytest.fixture
def registry(tmp_path: Path) -> BacklogRegistry:
    root = tmp_path / "backlogs"
    root.mkdir()
    (root / "schemas").mkdir()
    real = Path(__file__).resolve().parents[2] / "backlogs" / "schemas"
    for s in real.glob("*.schema.json"):
        (root / "schemas" / s.name).write_text(s.read_text(encoding="utf-8"), encoding="utf-8")
    for n in BACKLOG_NAMES:
        (root / f"{n}.json").write_text("[]", encoding="utf-8")
    return BacklogRegistry(root=root)


def test_state_empty_for_unknown_slug(registry: BacklogRegistry) -> None:
    st = registry.state("nonexistent")
    assert st.slug == "nonexistent"
    assert st.discovery is None and st.research is None
    assert st.present_in() == []
    assert not st.is_researched()
    assert not st.is_downloaded()
    assert not st.is_indexed()


def test_state_combines_all_four_backlogs(registry: BacklogRegistry) -> None:
    registry.discovery.upsert({"slug": "x", "title": "X"})
    registry.research.upsert({"slug": "x", "status": "completa"})
    registry.downloads.upsert({"slug": "x", "status": "descargado"})
    registry.indexing.upsert({"slug": "x", "status": "indexado"})

    st = registry.state("x")
    assert st.is_researched()
    assert st.is_downloaded()
    assert st.is_indexed()
    assert set(st.present_in()) == {"discovery", "research", "downloads", "indexing"}


def test_all_slugs_union(registry: BacklogRegistry) -> None:
    registry.discovery.upsert({"slug": "a", "title": "A"})
    registry.research.upsert({"slug": "b"})
    registry.downloads.upsert({"slug": "c"})
    assert registry.all_slugs() == {"a", "b", "c"}


def test_slugs_by_state_researched_not_indexed(registry: BacklogRegistry) -> None:
    # Slug 'x': researched + indexed → NOT returned
    registry.research.upsert({"slug": "x", "status": "completa"})
    registry.indexing.upsert({"slug": "x", "status": "indexado"})
    # Slug 'y': researched but not yet indexed → returned
    registry.research.upsert({"slug": "y", "status": "completa"})
    registry.indexing.upsert({"slug": "y", "status": "pendiente"})
    # Slug 'z': not researched → NOT returned
    registry.research.upsert({"slug": "z", "status": "pendiente"})

    result = registry.slugs_by_state(researched=True, indexed=False)
    assert result == ["y"]


def test_save_all_persists_each_backlog(registry: BacklogRegistry, tmp_path: Path) -> None:
    registry.discovery.upsert({"slug": "a", "title": "A"})
    registry.indexing.upsert({"slug": "a", "status": "pendiente"})
    registry.save_all()

    # Re-open from disk
    registry2 = BacklogRegistry(root=registry.discovery._root)
    assert registry2.discovery.get("a")["title"] == "A"
    assert registry2.indexing.get("a")["status"] == "pendiente"


def test_validate_all_aggregates_errors(registry: BacklogRegistry) -> None:
    # Inject garbage directly (bypass upsert's slug guard):
    registry.discovery._wc.entries.append({"slug": "BAD_SLUG"})
    registry.discovery._wc.reindex()
    registry.downloads._wc.entries.append({"slug": "y", "sha256": "not-hex"})
    registry.downloads._wc.reindex()

    errors = registry.validate_all()
    assert len(errors) >= 2
    names = {e.backlog for e in errors}
    assert "discovery" in names
    assert "downloads" in names

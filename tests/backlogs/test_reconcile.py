"""Reconcile engine tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from alejandria.backlogs.reconcile import (
    CorpusFileCheck,
    DownloadCacheCheck,
    Environment,
    OrphanCorpusCheck,
    PostgresStateCheck,
    Reconciler,
    ReconcileFinding,
    ReviewFileCheck,
    _sha256_of_paths,
)
from alejandria.backlogs.registry import BacklogRegistry
from alejandria.backlogs.validate import BACKLOG_NAMES


# --------------------------------------------------------------------------- #
# Fixture: an isolated "repo" with empty backlogs + an empty corpus
# --------------------------------------------------------------------------- #

@pytest.fixture
def env(tmp_path: Path) -> Environment:
    # backlogs/
    bl_root = tmp_path / "backlogs"
    bl_root.mkdir()
    (bl_root / "schemas").mkdir()
    real_schemas = Path(__file__).resolve().parents[2] / "backlogs" / "schemas"
    for s in real_schemas.glob("*.schema.json"):
        (bl_root / "schemas" / s.name).write_text(
            s.read_text(encoding="utf-8"), encoding="utf-8"
        )
    for n in BACKLOG_NAMES:
        (bl_root / f"{n}.json").write_text("[]", encoding="utf-8")

    # corpus/, data/raw/, prods/reseñas/
    (tmp_path / "corpus").mkdir()
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "prods" / "reseñas").mkdir(parents=True)

    return Environment(
        registry=BacklogRegistry(root=bl_root),
        corpus_root=tmp_path / "corpus",
        downloads_root=tmp_path / "data" / "raw",
        reviews_root=tmp_path / "prods" / "reseñas",
    )


# --------------------------------------------------------------------------- #
# ReviewFileCheck
# --------------------------------------------------------------------------- #

def test_review_file_promotes_pending_to_completa(env: Environment) -> None:
    env.registry.research.upsert({"slug": "x", "status": "pendiente"})
    review_dir = env.reviews_root / "x"
    review_dir.mkdir()
    (review_dir / "reseña.md").write_text("# review", encoding="utf-8")

    findings = ReviewFileCheck().run(env)
    assert len(findings) == 1
    assert findings[0].kind == "update"
    assert findings[0].backlog == "research"
    assert findings[0].slug == "x"
    assert findings[0].patch["status"] == "completa"
    assert "completed_at" in findings[0].patch


def test_review_file_flags_missing_when_status_completa(env: Environment) -> None:
    env.registry.research.upsert({"slug": "x", "status": "completa"})
    # no reseña.md on disk
    findings = ReviewFileCheck().run(env)
    assert any(f.kind == "info" and "missing" in f.reason for f in findings)


def test_review_file_detects_orphan_reseña(env: Environment) -> None:
    # reseña exists but no slug registered in research.json
    (env.reviews_root / "ghost").mkdir()
    (env.reviews_root / "ghost" / "reseña.md").write_text("x", encoding="utf-8")

    findings = ReviewFileCheck().run(env)
    orphans = [f for f in findings if f.kind == "orphan"]
    assert len(orphans) == 1
    assert orphans[0].slug == "ghost"


# --------------------------------------------------------------------------- #
# DownloadCacheCheck
# --------------------------------------------------------------------------- #

def test_download_cache_detects_downloaded_file(env: Environment, tmp_path: Path) -> None:
    raw = env.downloads_root / "abc.html"
    raw.write_bytes(b"hello world")
    env.registry.downloads.upsert({
        "slug": "abc", "raw_path": str(raw), "status": "pendiente",
    })

    findings = DownloadCacheCheck().run(env)
    assert len(findings) == 1
    assert findings[0].patch["status"] == "descargado"
    # SHA256 of "hello world"
    import hashlib
    expected = hashlib.sha256(b"hello world").hexdigest()
    assert findings[0].patch["sha256"] == expected


def test_download_cache_flags_missing_file(env: Environment) -> None:
    env.registry.downloads.upsert({
        "slug": "abc",
        "raw_path": str(env.downloads_root / "nonexistent.html"),
        "status": "descargado",
    })
    findings = DownloadCacheCheck().run(env)
    assert any(f.kind == "info" and "missing" in f.reason for f in findings)


# --------------------------------------------------------------------------- #
# CorpusFileCheck
# --------------------------------------------------------------------------- #

def test_corpus_file_marks_stale_when_sha_drifts(env: Environment) -> None:
    corpus_file = env.corpus_root / "en" / "test" / "doc.txt"
    corpus_file.parent.mkdir(parents=True)
    corpus_file.write_text("first content", encoding="utf-8")

    # Compute the aggregate SHA at the time of "last index"
    first_sha = _sha256_of_paths([corpus_file])
    env.registry.indexing.upsert({
        "slug": "x",
        "paths": ["en/test/doc.txt"],
        "last_sha": first_sha,
        "status": "indexado",
    })

    # No drift → no update
    assert CorpusFileCheck().run(env) == []

    # Drift: modify file → SHA changes
    corpus_file.write_text("second content", encoding="utf-8")
    findings = CorpusFileCheck().run(env)
    assert len(findings) == 1
    assert findings[0].patch == {"status": "stale"}


def test_corpus_file_ignores_empty_paths(env: Environment) -> None:
    env.registry.indexing.upsert({"slug": "x", "paths": [], "status": "indexado"})
    assert CorpusFileCheck().run(env) == []


# --------------------------------------------------------------------------- #
# PostgresStateCheck — no-op when no client
# --------------------------------------------------------------------------- #

def test_postgres_check_noop_without_client(env: Environment) -> None:
    env.registry.indexing.upsert({
        "slug": "x", "paths": ["en/a.txt"], "status": "indexado",
    })
    assert PostgresStateCheck().run(env) == []


def test_postgres_check_flags_missing_path() -> None:
    # Build env by hand with a fake Postgres registry
    from types import SimpleNamespace

    class FakeRec:
        def __init__(self, fp): self.file_path = fp

    pg = SimpleNamespace(all_records=lambda: [FakeRec("en/b.txt")])
    # Minimal env
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    (tmp / "backlogs" / "schemas").mkdir(parents=True)
    real_schemas = Path(__file__).resolve().parents[2] / "backlogs" / "schemas"
    for s in real_schemas.glob("*.schema.json"):
        (tmp / "backlogs" / "schemas" / s.name).write_text(
            s.read_text(encoding="utf-8"), encoding="utf-8"
        )
    for n in BACKLOG_NAMES:
        (tmp / "backlogs" / f"{n}.json").write_text("[]", encoding="utf-8")

    env = Environment(
        registry=BacklogRegistry(root=tmp / "backlogs"),
        corpus_root=tmp / "corpus",
        downloads_root=tmp / "data" / "raw",
        reviews_root=tmp / "prods" / "reseñas",
        postgres_document_registry=pg,
    )
    env.registry.indexing.upsert({
        "slug": "x",
        "paths": ["en/a.txt"],  # not in FakeRec set
        "status": "indexado",
    })

    findings = PostgresStateCheck().run(env)
    assert len(findings) == 1
    assert findings[0].patch["status"] == "stale"


# --------------------------------------------------------------------------- #
# OrphanCorpusCheck
# --------------------------------------------------------------------------- #

def test_orphan_corpus_flags_untracked_file(env: Environment) -> None:
    tracked = env.corpus_root / "en" / "tracked.txt"
    tracked.parent.mkdir(parents=True)
    tracked.write_text("t", encoding="utf-8")
    orphan = env.corpus_root / "en" / "orphan.txt"
    orphan.write_text("o", encoding="utf-8")

    env.registry.indexing.upsert({
        "slug": "tracked-slug", "paths": ["en/tracked.txt"], "status": "indexado",
    })
    findings = OrphanCorpusCheck().run(env)
    rels = [f.reason for f in findings if f.kind == "orphan"]
    assert any("en/orphan.txt" in r for r in rels)
    assert not any("en/tracked.txt" in r for r in rels)


def test_orphan_corpus_respects_directory_coverage(env: Environment) -> None:
    # Declare a directory path: everything under it is covered.
    (env.corpus_root / "en" / "series").mkdir(parents=True)
    (env.corpus_root / "en" / "series" / "1.txt").write_text("x", encoding="utf-8")
    (env.corpus_root / "en" / "series" / "2.txt").write_text("y", encoding="utf-8")
    env.registry.indexing.upsert({
        "slug": "series", "paths": ["en/series/"], "status": "indexado",
    })
    findings = OrphanCorpusCheck().run(env)
    assert not any(f.kind == "orphan" for f in findings)


# --------------------------------------------------------------------------- #
# Reconciler orchestrator + apply
# --------------------------------------------------------------------------- #

def test_reconciler_applies_only_updates(env: Environment) -> None:
    # Seed one update-worthy and one orphan
    env.registry.research.upsert({"slug": "x", "status": "pendiente"})
    review = env.reviews_root / "x" / "reseña.md"
    review.parent.mkdir(parents=True)
    review.write_text("#", encoding="utf-8")

    (env.reviews_root / "ghost").mkdir()
    (env.reviews_root / "ghost" / "reseña.md").write_text("#", encoding="utf-8")

    rec = Reconciler(checks=[ReviewFileCheck()])
    findings = rec.scan(env)
    kinds = {f.kind for f in findings}
    assert kinds == {"update", "orphan"}

    applied = rec.apply(env, findings)
    assert len(applied) == 1
    # 'x' now completa; 'ghost' NOT created
    assert env.registry.research.get("x")["status"] == "completa"
    assert env.registry.research.get("ghost") is None


def test_reconciler_scan_is_read_only(env: Environment) -> None:
    env.registry.research.upsert({"slug": "x", "status": "pendiente"})
    review = env.reviews_root / "x" / "reseña.md"
    review.parent.mkdir(parents=True)
    review.write_text("#", encoding="utf-8")

    rec = Reconciler(checks=[ReviewFileCheck()])
    rec.scan(env)
    # Scan without apply: status untouched.
    assert env.registry.research.get("x")["status"] == "pendiente"


# --------------------------------------------------------------------------- #
# ReconcileFinding.describe
# --------------------------------------------------------------------------- #

def test_finding_describe_formatting() -> None:
    f = ReconcileFinding(
        kind="update", backlog="research", slug="x",
        patch={"status": "completa"}, reason="reseña found",
    )
    s = f.describe()
    assert s.startswith("[update]")
    assert "research/x" in s
    assert "reseña found" in s

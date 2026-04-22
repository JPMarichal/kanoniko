"""Schema + uniqueness validation tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from alejandria.backlogs.validate import (
    BACKLOG_NAMES,
    validate_all,
    validate_backlog,
)


@pytest.fixture
def isolated_backlogs(tmp_path: Path) -> Path:
    """A temp backlogs root with empty JSON files and the real schemas symlinked."""
    root = tmp_path / "backlogs"
    root.mkdir()
    (root / "schemas").mkdir()

    # Copy the real schemas — they're the contract under test.
    real_schemas = Path(__file__).resolve().parents[2] / "backlogs" / "schemas"
    for schema in real_schemas.glob("*.schema.json"):
        (root / "schemas" / schema.name).write_text(
            schema.read_text(encoding="utf-8"), encoding="utf-8"
        )

    for name in BACKLOG_NAMES:
        (root / f"{name}.json").write_text("[]", encoding="utf-8")

    return root


def _write(root: Path, name: str, data: list[dict]) -> None:
    (root / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Shipped empty backlogs validate.
# --------------------------------------------------------------------------- #

def test_shipped_empty_backlogs_pass() -> None:
    errors = validate_all()  # uses the real DEFAULT_BACKLOGS_ROOT
    assert errors == []


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #

def test_discovery_valid_entry(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "discovery", [
        {"slug": "abc-123", "title": "T"},
    ])
    assert validate_backlog("discovery", root=isolated_backlogs) == []


def test_discovery_rejects_bad_slug(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "discovery", [
        {"slug": "ABC_NO", "title": "T"},
    ])
    errs = validate_backlog("discovery", root=isolated_backlogs)
    # jsonschema's message for failed pattern: "... does not match '<regex>'"
    assert any("does not match" in e.message for e in errs)


def test_discovery_rejects_missing_title(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "discovery", [{"slug": "ok"}])
    errs = validate_backlog("discovery", root=isolated_backlogs)
    assert any("title" in e.message.lower() for e in errs)


def test_discovery_rejects_additional_properties(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "discovery", [
        {"slug": "ok", "title": "T", "made_up_field": 1},
    ])
    errs = validate_backlog("discovery", root=isolated_backlogs)
    assert any("additional" in e.message.lower() or "unexpected" in e.message.lower()
               for e in errs)


def test_discovery_rejects_invalid_status(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "discovery", [
        {"slug": "ok", "title": "T", "status": "nonsense"},
    ])
    errs = validate_backlog("discovery", root=isolated_backlogs)
    assert any("nonsense" in e.message or "enum" in e.message.lower() for e in errs)


# --------------------------------------------------------------------------- #
# Duplicate-slug detection (schema alone can't express this)
# --------------------------------------------------------------------------- #

def test_duplicate_slug_detected(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "discovery", [
        {"slug": "dup", "title": "first"},
        {"slug": "dup", "title": "second"},
    ])
    errs = validate_backlog("discovery", root=isolated_backlogs)
    assert any("duplicate slug" in e.message for e in errs)


# --------------------------------------------------------------------------- #
# Downloads — sha256 format guard
# --------------------------------------------------------------------------- #

def test_download_bad_sha_rejected(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "downloads", [
        {"slug": "x", "sha256": "not-a-hash"},
    ])
    errs = validate_backlog("downloads", root=isolated_backlogs)
    assert errs, "expected pattern error on sha256"


def test_download_empty_sha_accepted(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "downloads", [
        {"slug": "x", "sha256": ""},
    ])
    assert validate_backlog("downloads", root=isolated_backlogs) == []


# --------------------------------------------------------------------------- #
# Indexing — paths array shape
# --------------------------------------------------------------------------- #

def test_indexing_paths_must_be_strings(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "indexing", [
        {"slug": "x", "paths": [1, 2, 3]},
    ])
    errs = validate_backlog("indexing", root=isolated_backlogs)
    assert errs, "expected type error on paths items"


# --------------------------------------------------------------------------- #
# ValidationError formatting
# --------------------------------------------------------------------------- #

def test_error_format_includes_index_and_path(isolated_backlogs: Path) -> None:
    _write(isolated_backlogs, "discovery", [
        {"slug": "ok", "title": "T"},
        {"slug": "bad-slug!"},  # fails pattern + missing title
    ])
    errs = validate_backlog("discovery", root=isolated_backlogs)
    assert errs
    # First error should reference index 1
    assert any(e.index == 1 for e in errs)
    # Each formatted error has a readable shape
    for e in errs:
        formatted = e.format()
        assert "[discovery" in formatted

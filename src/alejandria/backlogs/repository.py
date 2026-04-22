"""Backlog storage Protocol + JSON-file implementation.

Repository pattern: one :class:`JsonBacklog` instance per backlog file.
Consumers depend on the :class:`Backlog` Protocol, not on the JSON
implementation — if we ever want to back a backlog with Postgres or SQLite,
we add a ``PostgresBacklog`` / ``SqliteBacklog`` class without touching
the reconciler or the CLI.

Concurrency: atomic write via temp file + rename (``os.replace``), which is
atomic on both POSIX and Windows. No locking — the backlogs are edited
from a single session (user CLI + pre-commit hook, never two at once in
practice). If multi-writer becomes a need, wrap in a filelock.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Protocol, runtime_checkable

from alejandria.backlogs.validate import (
    BACKLOG_NAMES,
    DEFAULT_BACKLOGS_ROOT,
    load_backlog,
    validate_backlog,
)


@runtime_checkable
class Backlog(Protocol):
    """Minimal store interface.

    The shape of entries is backlog-specific (schema-validated); callers
    pass and receive ``dict[str, Any]`` payloads.
    """

    name: str

    def entries(self) -> list[dict[str, Any]]: ...
    def get(self, slug: str) -> dict[str, Any] | None: ...
    def upsert(self, entry: dict[str, Any]) -> None: ...
    def remove(self, slug: str) -> bool: ...
    def save(self) -> None: ...
    def validate(self) -> list: ...  # list[ValidationError]


@dataclass
class _WorkingCopy:
    """In-memory mirror of the JSON file, mutated by upsert/remove
    until :meth:`save` materialises it back to disk."""

    entries: list[dict[str, Any]]
    _slug_index: dict[str, int]

    @classmethod
    def from_entries(cls, entries: list[dict[str, Any]]) -> "_WorkingCopy":
        idx = {}
        for i, e in enumerate(entries):
            slug = e.get("slug")
            if isinstance(slug, str):
                idx[slug] = i
        return cls(entries=list(entries), _slug_index=idx)

    def reindex(self) -> None:
        self._slug_index = {
            e["slug"]: i for i, e in enumerate(self.entries)
            if isinstance(e.get("slug"), str)
        }


class JsonBacklog:
    """JSON-file-backed :class:`Backlog` implementation.

    Loads the file eagerly on construction, mutates in memory, and only
    writes back to disk on :meth:`save`. This keeps the pre-commit hook
    and reconciler transactional: the JSON on disk is either the
    pre-operation state or the post-save state, never a partial.
    """

    def __init__(
        self,
        name: str,
        root: Path = DEFAULT_BACKLOGS_ROOT,
    ) -> None:
        if name not in BACKLOG_NAMES:
            raise ValueError(
                f"unknown backlog {name!r}; expected one of {BACKLOG_NAMES}"
            )
        self.name = name
        self._root = Path(root)
        self._path = self._root / f"{name}.json"
        raw = load_backlog(name, root=self._root)
        self._wc = _WorkingCopy.from_entries(raw)

    # ----- Protocol implementation ----------------------------------- #

    def entries(self) -> list[dict[str, Any]]:
        """Return a shallow copy so callers can't mutate internal state."""
        return [dict(e) for e in self._wc.entries]

    def get(self, slug: str) -> dict[str, Any] | None:
        i = self._wc._slug_index.get(slug)
        if i is None:
            return None
        return dict(self._wc.entries[i])

    def upsert(self, entry: dict[str, Any]) -> None:
        slug = entry.get("slug")
        if not isinstance(slug, str) or not slug:
            raise ValueError("entry must have a non-empty 'slug' string")
        i = self._wc._slug_index.get(slug)
        if i is None:
            self._wc.entries.append(dict(entry))
            self._wc._slug_index[slug] = len(self._wc.entries) - 1
        else:
            self._wc.entries[i] = dict(entry)

    def remove(self, slug: str) -> bool:
        i = self._wc._slug_index.pop(slug, None)
        if i is None:
            return False
        del self._wc.entries[i]
        self._wc.reindex()
        return True

    def save(self) -> None:
        """Write atomically via temp file + rename."""
        fd, tmp = tempfile.mkstemp(
            prefix=f".{self.name}-", suffix=".json.tmp",
            dir=str(self._root),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(
                    self._wc.entries, f,
                    ensure_ascii=False, indent=2, sort_keys=False,
                )
                f.write("\n")
            os.replace(tmp, self._path)
        except Exception:
            # Clean temp on failure so we don't leave orphans.
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    def validate(self) -> list:
        """Validate the in-memory state (without needing to save first)."""
        return validate_backlog(self.name, data=self._wc.entries, root=self._root)

    # ----- Convenience iteration ------------------------------------- #

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.entries())

    def __len__(self) -> int:
        return len(self._wc.entries)

    def __contains__(self, slug: object) -> bool:
        return isinstance(slug, str) and slug in self._wc._slug_index

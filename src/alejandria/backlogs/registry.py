"""Multi-backlog facade keyed by slug.

The four backlogs are independent stores, but most operational questions
("what's the state of slug X?", "list slugs that are researched but not
indexed") cut across all four. :class:`BacklogRegistry` answers those.

Facade pattern: callers interact with the registry, not with four
separate :class:`JsonBacklog` objects. The registry owns the four
instances and exposes slug-level queries.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alejandria.backlogs.repository import JsonBacklog
from alejandria.backlogs.validate import BACKLOG_NAMES, DEFAULT_BACKLOGS_ROOT


@dataclass(frozen=True)
class SlugState:
    """Snapshot of what the four backlogs say about one slug."""

    slug: str
    discovery: dict[str, Any] | None
    research: dict[str, Any] | None
    downloads: dict[str, Any] | None
    indexing: dict[str, Any] | None

    def present_in(self) -> list[str]:
        """Names of backlogs where this slug has an entry."""
        return [
            name for name, entry in (
                ("discovery", self.discovery),
                ("research", self.research),
                ("downloads", self.downloads),
                ("indexing", self.indexing),
            )
            if entry is not None
        ]

    def is_researched(self) -> bool:
        return (self.research or {}).get("status") == "completa"

    def is_downloaded(self) -> bool:
        return (self.downloads or {}).get("status") == "descargado"

    def is_indexed(self) -> bool:
        return (self.indexing or {}).get("status") == "indexado"


class BacklogRegistry:
    """Facade over the four :class:`JsonBacklog` instances."""

    def __init__(self, root: Path = DEFAULT_BACKLOGS_ROOT) -> None:
        self._root = Path(root)
        self._backlogs: dict[str, JsonBacklog] = {
            name: JsonBacklog(name, root=self._root) for name in BACKLOG_NAMES
        }

    # ----- Individual backlog access --------------------------------- #

    @property
    def discovery(self) -> JsonBacklog:
        return self._backlogs["discovery"]

    @property
    def research(self) -> JsonBacklog:
        return self._backlogs["research"]

    @property
    def downloads(self) -> JsonBacklog:
        return self._backlogs["downloads"]

    @property
    def indexing(self) -> JsonBacklog:
        return self._backlogs["indexing"]

    def __getitem__(self, name: str) -> JsonBacklog:
        return self._backlogs[name]

    # ----- Slug-level cross-queries ---------------------------------- #

    def state(self, slug: str) -> SlugState:
        """Return what the four backlogs say about ``slug``."""
        return SlugState(
            slug=slug,
            discovery=self.discovery.get(slug),
            research=self.research.get(slug),
            downloads=self.downloads.get(slug),
            indexing=self.indexing.get(slug),
        )

    def all_slugs(self) -> set[str]:
        """Union of slugs across all four backlogs."""
        slugs: set[str] = set()
        for bl in self._backlogs.values():
            for e in bl.entries():
                s = e.get("slug")
                if isinstance(s, str):
                    slugs.add(s)
        return slugs

    def slugs_by_state(self, *, researched: bool | None = None,
                       downloaded: bool | None = None,
                       indexed: bool | None = None) -> list[str]:
        """List slugs matching the requested filter combination.

        ``None`` means "don't care". Example: ``slugs_by_state(researched=True,
        indexed=False)`` returns slugs with a completed reseña but not yet
        indexed in Postgres.
        """
        result: list[str] = []
        for slug in sorted(self.all_slugs()):
            st = self.state(slug)
            if researched is not None and st.is_researched() != researched:
                continue
            if downloaded is not None and st.is_downloaded() != downloaded:
                continue
            if indexed is not None and st.is_indexed() != indexed:
                continue
            result.append(slug)
        return result

    # ----- Lifecycle ------------------------------------------------- #

    def save_all(self) -> None:
        """Persist every backlog that has pending mutations.

        Idempotent: saving an unmodified backlog rewrites the same bytes.
        """
        for bl in self._backlogs.values():
            bl.save()

    def validate_all(self) -> list:
        """Aggregate validate() across the four backlogs."""
        errors = []
        for bl in self._backlogs.values():
            errors.extend(bl.validate())
        return errors

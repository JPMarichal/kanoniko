"""Backlog entry dataclasses.

These mirror the JSON Schema in ``backlogs/schemas/*.schema.json``.
Kept as plain dataclasses (not pydantic) for two reasons:

* Fewer runtime deps — validation already happens via ``jsonschema``.
* The schema files are the contract; the dataclasses are a convenience
  for code that wants attribute access. Schema + validator are canonical.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


# --------------------------------------------------------------------------- #
# Status enums kept as string literals, not Enum subclasses, so JSON
# serialisation is transparent and schemas can declare them as plain strings.
# --------------------------------------------------------------------------- #

DISCOVERY_STATUSES = ("propuesto", "clasificado", "descartado")
RESEARCH_STATUSES = ("pendiente", "en_progreso", "completa")
DOWNLOAD_STATUSES = ("pendiente", "descargado", "fallido")
INDEXING_STATUSES = ("pendiente", "indexado", "stale")


@dataclass
class _Base:
    """Minimal shared surface: every entry has a slug."""

    slug: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiscoveryEntry(_Base):
    """One candidate resource identified but not necessarily acted upon."""

    title: str
    source: str = ""           # human label of origin (site, person, series)
    language: str = ""         # "en" | "es" | "multi"
    category: str = ""         # corpus category hint (books/, manuals/, …)
    target_path: str = ""      # future path under corpus/{lang}/{category}/…
    status: str = "propuesto"
    notes: str = ""


@dataclass
class ResearchEntry(_Base):
    """Reseña doc status. The reseña itself lives in prods/reseñas/{slug}/reseña.md."""

    review_path: str = ""
    status: str = "pendiente"
    completed_at: str | None = None  # ISO-8601 when status becomes 'completa'


@dataclass
class DownloadEntry(_Base):
    """Raw-file download state."""

    source_url: str = ""
    skill: str = ""                 # gospelink | byu-studies | rsc-byu | manual | …
    raw_path: str = ""              # local cache path if downloaded
    sha256: str = ""                # of the raw bytes
    status: str = "pendiente"
    error: str = ""                 # last error message if fallido


@dataclass
class IndexingEntry(_Base):
    """Ingestion state per slug — mirrors Postgres ``document_registry`` at
    the slug granularity (one slug may map to multiple corpus files)."""

    paths: list[str] = field(default_factory=list)   # corpus-relative
    last_sha: str = ""        # aggregate SHA of all paths at last index
    indexed_at: str | None = None                   # ISO-8601
    status: str = "pendiente"

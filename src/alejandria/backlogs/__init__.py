"""Ingestion workflow backlogs (§Level B of ``docs/ingestion-workflow.md``).

Four JSON-backed backlogs, keyed by ``slug``, track material moving through
the 9-step ingestion workflow:

* **discovery** — candidate material identified; classification + target path.
* **research** — reseña documents produced in ``prods/reseñas/{slug}/``.
* **downloads** — raw files pulled from sources into the local cache.
* **indexing** — Postgres ingestion state (SHA tracking + stale detection).

Design:

* Each backlog is a :class:`JsonBacklog` (Repository pattern over a flat JSON
  file). All four implement the same :class:`Backlog` Protocol.
* :class:`BacklogRegistry` is a facade that cross-references all four by slug.
* :class:`Reconciler` runs a list of :class:`ReconcileCheck` strategies over
  filesystem + Postgres state and produces :class:`ReconcileFinding` DTOs.
  Dry-run by default; ``--apply`` materialises.

See ``backlogs/README.md`` for the operational workflow.
"""
from alejandria.backlogs.models import (
    DiscoveryEntry,
    DownloadEntry,
    IndexingEntry,
    ResearchEntry,
)
from alejandria.backlogs.repository import Backlog, JsonBacklog
from alejandria.backlogs.registry import BacklogRegistry, SlugState

__all__ = [
    "Backlog",
    "BacklogRegistry",
    "DiscoveryEntry",
    "DownloadEntry",
    "IndexingEntry",
    "JsonBacklog",
    "ResearchEntry",
    "SlugState",
]

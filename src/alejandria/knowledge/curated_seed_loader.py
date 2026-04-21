"""Curated seed loader — orchestration, not persistence.

Reads a JSON seed file and instructs a :class:`KnowledgeGraphWriter` to
merge the relations it declares. Lives outside the Writer Protocol
(ADR 0001 v2) because the JSON shape, bidirectional expansion, and
default property plumbing are orchestration concerns, not storage.

The JSON schema (per relation-type key) is::

    {
        "<REL_TYPE>": [
            {
                "from": {"name": "...", "type": "..."},
                "to":   {"name": "...", "type": "..."},
                "source_ref":   "...",           # optional
                "confidence":   "curated",       # optional, default "curated"
                "source":       "curated_seed",  # optional, forced to "curated_seed"
                "verified":     true,             # optional
                "role":         "...",           # optional (AUTHORED roles)
                "verse_range":  "...",           # optional
                "bidirectional": true             # optional — writes reverse too
            },
            ...
        ],
        ...
    }

Missing files return ``{}`` rather than raising — tolerated so the
ingestion pipeline can run without curated seeds in bare installations.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from alejandria.storage.kg_writer import KnowledgeGraphWriter

logger = logging.getLogger(__name__)


_OPTIONAL_PROP_KEYS: tuple[str, ...] = (
    "source_ref",
    "confidence",
    "verified",
    "role",
    "verse_range",
)


class CuratedSeedLoader:
    """Loads curated relations from a JSON seed file via a ``KGWriter``."""

    def __init__(self, kg_writer: KnowledgeGraphWriter) -> None:
        self._kg_writer = kg_writer

    def load(self, path: str | Path) -> dict[str, int]:
        """Load seeds from ``path``. Returns per-rel_type counts (including
        bidirectional expansions)."""
        p = Path(path)
        if not p.exists():
            logger.info("curated seeds not found at %s — skipping", p)
            return {}

        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logger.warning(
                "curated seeds at %s has unexpected root type %s — skipping",
                p, type(data).__name__,
            )
            return {}

        rels_batch: list[dict[str, Any]] = []
        counts: dict[str, int] = {}

        for rel_type, entries in data.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                from_ent = entry.get("from") or {}
                to_ent = entry.get("to") or {}
                from_name = from_ent.get("name") or entry.get("from_name")
                to_name = to_ent.get("name") or entry.get("to_name")
                if not (from_name and to_name):
                    continue
                from_type = from_ent.get("type") or entry.get("from_type", "person")
                to_type = to_ent.get("type") or entry.get("to_type", "person")

                props: dict[str, Any] = {}
                for key in _OPTIONAL_PROP_KEYS:
                    if key in entry:
                        props[key] = entry[key]
                props.setdefault("confidence", "curated")
                props["source"] = "curated_seed"  # always, even if overridden

                rels_batch.append({
                    "from_name": from_name, "from_type": from_type,
                    "rel_type": rel_type,
                    "to_name": to_name, "to_type": to_type,
                    "props": props,
                })
                counts[rel_type] = counts.get(rel_type, 0) + 1

                if entry.get("bidirectional"):
                    rels_batch.append({
                        "from_name": to_name, "from_type": to_type,
                        "rel_type": rel_type,
                        "to_name": from_name, "to_type": from_type,
                        "props": props,
                    })
                    counts[rel_type] = counts.get(rel_type, 0) + 1

        if rels_batch:
            self._kg_writer.batch_merge_relations(rels_batch)
            total = sum(counts.values())
            logger.info(
                "loaded %d curated relations across %d types from %s",
                total, len(counts), p,
            )

        return counts

"""Scripture long-chain structure: divisions, parts, and pericopae.

P1 Phase 3 — Loads structural JSON data (volumes, divisions, books, parts,
pericopae) and resolves the full long-chain for any scripture file path
and verse range.

The long chain is:
  Volume → Division → Book → Part → Chapter → Pericope(s)

Each level has bilingual names (EN/ES). This module provides:
- `load_structure()` — load all JSON files once
- `resolve_long_chain(file_path, verse_start, verse_end)` → structural metadata
- `get_all_structural_entities()` — for KG node creation
- `get_structural_relations()` — for KG edge creation
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "scripture_structure"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Volume:
    slug: str
    name_es: str
    name_en: str
    abbreviation_es: str = ""
    abbreviation_en: str = ""


@dataclass
class Division:
    volume_slug: str
    name_es: str
    name_en: str


@dataclass
class Book:
    volume_slug: str
    division_name_es: str
    book_slug: str
    name_es: str
    name_en: str
    abbreviation_es: str = ""
    abbreviation_en: str = ""


@dataclass
class Part:
    book_slug: str
    volume_slug: str
    order: int
    name_es: str
    name_en: str


@dataclass
class Pericope:
    corpus_path: str  # e.g. "ot/genesis/1.txt"
    volume_slug: str
    book_slug: str
    chapter_num: int
    verse_start: int | None
    verse_end: int | None
    name_es: str
    name_en: str


@dataclass
class LongChain:
    """Full structural context for a scripture chunk."""
    volume: Volume | None = None
    division: Division | None = None
    book: Book | None = None
    parts: list[Part] = field(default_factory=list)
    pericopae: list[Pericope] = field(default_factory=list)

    def to_dict(self, lang: str = "en") -> dict[str, Any]:
        """Convert to a flat metadata dict for chunk enrichment."""
        name_key = f"name_{lang}"
        result: dict[str, Any] = {}
        if self.volume:
            result["volume_name"] = getattr(self.volume, name_key)
        if self.division:
            result["division"] = getattr(self.division, name_key)
        if self.book:
            result["book_name"] = getattr(self.book, name_key)
        if self.parts:
            result["part"] = getattr(self.parts[0], name_key)
            if len(self.parts) > 1:
                result["parts"] = [getattr(p, name_key) for p in self.parts]
        if self.pericopae:
            result["pericope"] = getattr(self.pericopae[0], name_key)
            if len(self.pericopae) > 1:
                result["pericopae"] = [getattr(p, name_key) for p in self.pericopae]
        return result


# ---------------------------------------------------------------------------
# Structure store (singleton-like, loaded once)
# ---------------------------------------------------------------------------

class ScriptureStructure:
    """Loads and resolves the scripture long-chain structure."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or _DATA_DIR
        self._loaded = False

        self.volumes: dict[str, Volume] = {}
        self.divisions: list[Division] = []
        self.books: dict[str, Book] = {}  # keyed by book_slug
        self.parts: list[Part] = []
        self.pericopae: list[Pericope] = []

        # Lookup indices built after load
        self._divisions_by_volume: dict[str, list[Division]] = {}
        self._books_by_division: dict[str, list[Book]] = {}  # key: division name_es
        self._parts_by_book: dict[str, list[Part]] = {}  # key: book_slug
        self._pericopae_by_path: dict[str, list[Pericope]] = {}  # key: corpus_path

    def load(self) -> None:
        """Load all structure JSON files and build indices."""
        if self._loaded:
            return

        try:
            self._load_volumes()
            self._load_divisions()
            self._load_books()
            self._load_parts()
            self._load_pericopae()
            self._build_indices()
            self._loaded = True
            logger.info(
                "Scripture structure loaded: %d volumes, %d divisions, "
                "%d books, %d parts, %d pericopae",
                len(self.volumes), len(self.divisions),
                len(self.books), len(self.parts), len(self.pericopae),
            )
        except FileNotFoundError as e:
            logger.warning("Scripture structure data not found: %s", e)
        except Exception:
            logger.exception("Failed to load scripture structure")

    def _load_volumes(self) -> None:
        data = json.loads((self._data_dir / "volumes.json").read_text("utf-8"))
        for item in data:
            v = Volume(
                slug=item["slug"],
                name_es=item["name_es"],
                name_en=item["name_en"],
                abbreviation_es=item.get("abbreviation_es", ""),
                abbreviation_en=item.get("abbreviation_en", ""),
            )
            self.volumes[v.slug] = v

    def _load_divisions(self) -> None:
        data = json.loads((self._data_dir / "divisions.json").read_text("utf-8"))
        for item in data:
            self.divisions.append(Division(
                volume_slug=item["volume_slug"],
                name_es=item["name_es"],
                name_en=item["name_en"],
            ))

    def _load_books(self) -> None:
        data = json.loads((self._data_dir / "books.json").read_text("utf-8"))
        for item in data:
            b = Book(
                volume_slug=item["volume_slug"],
                division_name_es=item["division_name_es"],
                book_slug=item["book_slug"],
                name_es=item["name_es"],
                name_en=item["name_en"],
                abbreviation_es=item.get("abbreviation_es", ""),
                abbreviation_en=item.get("abbreviation_en", ""),
            )
            self.books[b.book_slug] = b

    def _load_parts(self) -> None:
        data = json.loads((self._data_dir / "parts.json").read_text("utf-8"))
        for item in data:
            self.parts.append(Part(
                book_slug=item["book_slug"],
                volume_slug=item["volume_slug"],
                order=item["order"],
                name_es=item["name_es"],
                name_en=item["name_en"],
            ))

    def _load_pericopae(self) -> None:
        data = json.loads((self._data_dir / "pericopae.json").read_text("utf-8"))
        for item in data:
            self.pericopae.append(Pericope(
                corpus_path=item["corpus_path"],
                volume_slug=item["volume_slug"],
                book_slug=item["book_slug"],
                chapter_num=item["chapter_num"],
                verse_start=item.get("verse_start"),
                verse_end=item.get("verse_end"),
                name_es=item["name_es"],
                name_en=item["name_en"],
            ))

    def _build_indices(self) -> None:
        """Build lookup dicts for fast resolution."""
        # Divisions by volume
        for d in self.divisions:
            self._divisions_by_volume.setdefault(d.volume_slug, []).append(d)

        # Books by division (using division name_es as key since that's in books.json)
        for b in self.books.values():
            self._books_by_division.setdefault(b.division_name_es, []).append(b)

        # Parts by book
        for p in self.parts:
            self._parts_by_book.setdefault(p.book_slug, []).append(p)
        # Sort parts by order within each book
        for parts_list in self._parts_by_book.values():
            parts_list.sort(key=lambda p: p.order)

        # Pericopae by corpus_path
        for p in self.pericopae:
            self._pericopae_by_path.setdefault(p.corpus_path, []).append(p)
        # Sort pericopae by verse_start within each file
        for peri_list in self._pericopae_by_path.values():
            peri_list.sort(key=lambda p: p.verse_start or 0)

    def resolve_long_chain(
        self,
        file_path: str,
        verse_start: int | None = None,
        verse_end: int | None = None,
        lang: str | None = None,
    ) -> LongChain:
        """Resolve the full structural chain for a scripture chunk.

        Parameters
        ----------
        file_path:
            Relative corpus path (e.g., "en/scriptures/ot/genesis/1.txt"
            or the internal form "ot/genesis/1.txt").
        verse_start, verse_end:
            Optional verse range to match pericopae and parts.
        lang:
            Language code extracted from path (auto-detected if None).

        Returns
        -------
        LongChain with as much structural context as can be resolved.
        """
        if not self._loaded:
            self.load()

        chain = LongChain()

        # Normalise path: strip lang prefix if present
        norm = file_path.replace("\\", "/")
        # Strip leading lang/ and scriptures/ prefixes
        parts_path = norm.split("/")
        # Find "scriptures" in path and take everything after it
        try:
            idx = parts_path.index("scriptures")
            corpus_key = "/".join(parts_path[idx + 1:])
        except ValueError:
            # Maybe it's already in internal form like "ot/genesis/1.txt"
            corpus_key = norm.lstrip("/")

        # Parse volume and book from corpus_key
        # Expected: {volume}/{book}/{chapter}.txt or {volume}/{chapter}.txt (D&C)
        key_parts = corpus_key.split("/")
        if len(key_parts) < 2:
            return chain

        volume_slug = key_parts[0]
        chain.volume = self.volumes.get(volume_slug)

        book_slug: str | None = None
        if len(key_parts) == 3:
            book_slug = key_parts[1]
        elif volume_slug == "dc":
            book_slug = None  # D&C has no book level in path

        # Resolve book
        if book_slug and book_slug in self.books:
            chain.book = self.books[book_slug]
        elif volume_slug == "dc":
            # D&C: find the "Secciones" book or first dc book
            for b in self.books.values():
                if b.volume_slug == "dc":
                    chain.book = b
                    break

        # Resolve division
        if chain.book:
            div_name = chain.book.division_name_es
            for d in self.divisions:
                if d.name_es == div_name and d.volume_slug == volume_slug:
                    chain.division = d
                    break

        # Resolve parts — find the part(s) that contain this chapter's verses
        if chain.book:
            all_parts = self._parts_by_book.get(
                chain.book.book_slug if chain.book else book_slug or "", []
            )
            if all_parts:
                # Parts are ordered; we need to figure out which part covers
                # the given chapter. We use pericopae to determine this:
                # find the pericope for our chapter, then find which part
                # the pericope's verse range falls under.
                # For simplicity, if we have chapter pericopae, use the first one's
                # position to determine part. Otherwise return all parts.
                matched_pericopae = self._pericopae_by_path.get(corpus_key, [])
                if matched_pericopae and verse_start is not None:
                    # Filter pericopae to those overlapping our verse range
                    for p in matched_pericopae:
                        if p.verse_start is None or p.verse_end is None:
                            chain.pericopae.append(p)
                        elif verse_end is not None:
                            if p.verse_start <= verse_end and p.verse_end >= verse_start:
                                chain.pericopae.append(p)
                        elif p.verse_start <= verse_start <= p.verse_end:
                            chain.pericopae.append(p)
                elif matched_pericopae:
                    # No verse range specified, return all pericopae for this chapter
                    chain.pericopae = matched_pericopae

                # For parts, we can't determine from verses alone which part
                # the chapter belongs to without a chapter→part mapping.
                # Use a heuristic: the parts JSON has per-book parts ordered,
                # and the pericopae tell us the chapter position within the book.
                # For now, include all parts for the book (typically 1-8).
                chain.parts = all_parts

        # If no pericope matched via verse range, try all for this chapter
        if not chain.pericopae:
            chain.pericopae = self._pericopae_by_path.get(corpus_key, [])

        return chain

    # ------------------------------------------------------------------
    # KG entity/relation export
    # ------------------------------------------------------------------

    def get_structural_entities(self) -> list[dict[str, str]]:
        """Return all structural entities for KG node creation.

        Each dict has: name, name_es, name_en, type, volume_slug.
        """
        if not self._loaded:
            self.load()

        entities: list[dict[str, str]] = []

        for v in self.volumes.values():
            entities.append({
                "name": v.name_en,
                "name_es": v.name_es,
                "name_en": v.name_en,
                "type": "volume",
                "volume_slug": v.slug,
            })

        for d in self.divisions:
            entities.append({
                "name": d.name_en,
                "name_es": d.name_es,
                "name_en": d.name_en,
                "type": "division",
                "volume_slug": d.volume_slug,
            })

        for b in self.books.values():
            entities.append({
                "name": b.name_en,
                "name_es": b.name_es,
                "name_en": b.name_en,
                "type": "book",
                "volume_slug": b.volume_slug,
            })

        for p in self.parts:
            entities.append({
                "name": p.name_en,
                "name_es": p.name_es,
                "name_en": p.name_en,
                "type": "part",
                "volume_slug": p.volume_slug,
            })

        # Pericopae are too numerous (~5K) to all be KG nodes.
        # They're better as chunk metadata. Only create nodes for
        # well-known pericopae (future enhancement).

        return entities

    def get_structural_relations(self) -> list[dict[str, str]]:
        """Return PART_OF / CONTAINS relations for KG edge creation.

        Returns list of dicts with: from_name, from_type, relation, to_name, to_type.
        """
        if not self._loaded:
            self.load()

        relations: list[dict[str, str]] = []

        # Division PART_OF Volume
        for d in self.divisions:
            vol = self.volumes.get(d.volume_slug)
            if vol:
                relations.append({
                    "from_name": d.name_en,
                    "from_type": "division",
                    "relation": "PART_OF",
                    "to_name": vol.name_en,
                    "to_type": "volume",
                })

        # Book PART_OF Division
        for b in self.books.values():
            relations.append({
                "from_name": b.name_en,
                "from_type": "book",
                "relation": "PART_OF",
                "to_name": b.division_name_es,  # We need EN name
                "to_type": "division",
            })

        # Fix: resolve division EN name from ES name
        div_es_to_en = {d.name_es: d.name_en for d in self.divisions}
        for r in relations:
            if r["to_type"] == "division" and r["relation"] == "PART_OF":
                en_name = div_es_to_en.get(r["to_name"])
                if en_name:
                    r["to_name"] = en_name

        # Part PART_OF Book
        for p in self.parts:
            book = self.books.get(p.book_slug)
            if book:
                relations.append({
                    "from_name": p.name_en,
                    "from_type": "part",
                    "relation": "PART_OF",
                    "to_name": book.name_en,
                    "to_type": "book",
                })

        return relations


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_instance: ScriptureStructure | None = None


def get_structure() -> ScriptureStructure:
    """Get or create the module-level ScriptureStructure singleton."""
    global _instance
    if _instance is None:
        _instance = ScriptureStructure()
        _instance.load()
    return _instance


def resolve_long_chain(
    file_path: str,
    verse_start: int | None = None,
    verse_end: int | None = None,
) -> LongChain:
    """Convenience function: resolve long chain using the singleton."""
    return get_structure().resolve_long_chain(file_path, verse_start, verse_end)

"""Definition lookup from BD/GEE study aids.

Provides doctrinal context to the RAG pipeline by looking up relevant
definitions from the Bible Dictionary (EN) and Guide to the Scriptures (GEE).

Zero LLM cost — reads directly from corpus files and a prebuilt index.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Maximum definition text to inject into RAG context (chars)
MAX_DEFINITION_CHARS = 800

# Maximum definitions per question
MAX_DEFINITIONS = 3


@dataclass
class Definition:
    """A definition from BD or GEE."""
    term: str
    text: str
    source: str     # "bible-dictionary" or "guide-to-scriptures"
    lang: str       # "en" or "es"
    authority_note: str = ""  # e.g., "BD disclaimer: not official doctrine"


class DefinitionLookup:
    """Index and retrieve definitions from BD/GEE corpus files.

    Builds an in-memory index of term -> file path on first use.
    Subsequent lookups are O(1) dict lookups + file reads.
    Supports bilingual queries via the concept bridge (GEE ES <-> TG/BD EN).
    """

    def __init__(self, corpus_dir: str | Path):
        self._corpus_dir = Path(corpus_dir)
        self._index: dict[str, list[dict]] | None = None
        self._bridge: dict[str, list[str]] | None = None  # es_norm -> [en_norm]

    def _build_index(self) -> dict[str, list[dict]]:
        """Build term -> [{path, source, lang}] index from .meta.json files."""
        index: dict[str, list[dict]] = {}

        sources = [
            ("en", "study-aids/bible-dictionary", "bible-dictionary"),
            ("en", "study-aids/guide-to-scriptures", "guide-to-scriptures"),
            ("es", "study-aids/guide-to-scriptures", "guide-to-scriptures"),
        ]

        for lang, subdir, source_name in sources:
            aid_dir = self._corpus_dir / lang / subdir
            if not aid_dir.exists():
                continue

            for meta_file in aid_dir.glob("*.meta.json"):
                if meta_file.name.startswith("_"):
                    continue
                txt_file = meta_file.with_suffix("").with_suffix(".txt")
                if not txt_file.exists():
                    continue

                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    title = meta.get("title", "")
                    if not title or title.lower() == "introduction":
                        continue
                except (json.JSONDecodeError, OSError):
                    continue

                # Normalize key: lowercase, strip accents for matching
                key = _normalize_term(title)
                if key not in index:
                    index[key] = []

                index[key].append({
                    "path": str(txt_file),
                    "title": title,
                    "source": source_name,
                    "lang": lang,
                })

        logger.info("Definition index built: %d terms", len(index))
        return index

    def _build_bridge(self) -> dict[str, list[str]]:
        """Load bilingual concept bridge: es_normalized -> [en_normalized]."""
        bridge_file = self._corpus_dir / "bilingual-concept-bridge.json"
        bridge: dict[str, list[str]] = {}
        if not bridge_file.exists():
            return bridge
        try:
            with open(bridge_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for entry in data:
                es_key = _normalize_term(entry.get("es_title", ""))
                en_keys = [
                    _normalize_term(m["title"])
                    for m in entry.get("en_matches", [])
                ]
                if es_key and en_keys:
                    bridge[es_key] = en_keys
        except (json.JSONDecodeError, OSError):
            pass
        logger.info("Bilingual bridge loaded: %d ES->EN mappings", len(bridge))
        return bridge

    @property
    def index(self) -> dict[str, list[dict]]:
        if self._index is None:
            self._index = self._build_index()
        return self._index

    @property
    def bridge(self) -> dict[str, list[str]]:
        if self._bridge is None:
            self._bridge = self._build_bridge()
        return self._bridge

    def lookup(self, term: str, lang_preference: str = "en") -> Definition | None:
        """Look up a single term. Returns the best matching definition.

        Prefers:
        1. BD for EN queries (richer doctrinal essays)
        2. GEE for ES queries
        3. Matching language
        4. Falls back to bilingual bridge (ES term -> EN definition)
        """
        key = _normalize_term(term)
        entries = self.index.get(key)

        # If not found directly, try bilingual bridge
        if not entries and key in self.bridge:
            for en_key in self.bridge[key]:
                entries = self.index.get(en_key)
                if entries:
                    break

        if not entries:
            return None

        # Sort by preference
        def sort_key(e: dict) -> tuple:
            lang_match = 0 if e["lang"] == lang_preference else 1
            # BD first for EN, GEE first for ES
            if lang_preference == "en":
                source_pref = 0 if e["source"] == "bible-dictionary" else 1
            else:
                source_pref = 0 if e["source"] == "guide-to-scriptures" else 1
            return (lang_match, source_pref)

        entries_sorted = sorted(entries, key=sort_key)
        best = entries_sorted[0]

        try:
            text = Path(best["path"]).read_text(encoding="utf-8").strip()
        except OSError:
            return None

        if not text:
            return None

        # Truncate if too long (keep first paragraph or MAX_DEFINITION_CHARS)
        if len(text) > MAX_DEFINITION_CHARS:
            # Try to cut at a paragraph boundary
            cut = text.find("\n\n", MAX_DEFINITION_CHARS // 2)
            if cut > 0 and cut < MAX_DEFINITION_CHARS:
                text = text[:cut]
            else:
                text = text[:MAX_DEFINITION_CHARS] + "..."

        authority_note = ""
        if best["source"] == "bible-dictionary":
            authority_note = "(BD: scholarly reference, not official doctrine)"
        elif best["source"] == "guide-to-scriptures":
            authority_note = "(GEE: official study aid)"

        return Definition(
            term=best["title"],
            text=text,
            source=best["source"],
            lang=best["lang"],
            authority_note=authority_note,
        )

    def lookup_for_question(
        self, question: str, entities: list[str] | None = None,
        lang: str = "en",
    ) -> list[Definition]:
        """Find relevant definitions for a question.

        Uses entity names extracted from the question (by KG extractor)
        to look up matching definitions. Falls back to keyword matching
        if no entities provided.

        Args:
            question: The user's question text.
            entities: Entity names extracted from the question (optional).
            lang: Preferred language for definitions.

        Returns:
            List of up to MAX_DEFINITIONS definitions, most relevant first.
        """
        candidates: list[Definition] = []
        seen_terms: set[str] = set()

        # 1. Try entity names first (most precise)
        if entities:
            for entity in entities:
                key = _normalize_term(entity)
                if key in seen_terms:
                    continue
                defn = self.lookup(entity, lang_preference=lang)
                if defn:
                    seen_terms.add(key)
                    candidates.append(defn)
                    if len(candidates) >= MAX_DEFINITIONS:
                        break

        # 2. If not enough, try significant words from the question
        if len(candidates) < MAX_DEFINITIONS:
            words = _extract_concept_words(question)
            for word in words:
                key = _normalize_term(word)
                if key in seen_terms:
                    continue
                defn = self.lookup(word, lang_preference=lang)
                if defn:
                    seen_terms.add(key)
                    candidates.append(defn)
                    if len(candidates) >= MAX_DEFINITIONS:
                        break

        return candidates


def _normalize_term(term: str) -> str:
    """Normalize a term for index matching."""
    # Lowercase
    t = term.lower().strip()
    # Remove accents (basic)
    replacements = {
        "\u00e1": "a", "\u00e9": "e", "\u00ed": "i", "\u00f3": "o", "\u00fa": "u",
        "\u00f1": "n", "\u00fc": "u",
    }
    for src, dst in replacements.items():
        t = t.replace(src, dst)
    # Remove punctuation except hyphens
    t = re.sub(r"[^\w\s-]", "", t)
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _extract_concept_words(question: str) -> list[str]:
    """Extract potential concept words from a question.

    Returns capitalized words and multi-word terms that might match
    BD/GEE entries.
    """
    # Remove common question words
    stop = {
        "what", "who", "where", "when", "how", "why", "which", "is", "are",
        "was", "were", "do", "does", "did", "the", "a", "an", "in", "of",
        "and", "or", "to", "for", "with", "about", "from", "that", "this",
        "que", "quien", "donde", "cuando", "como", "por", "cual", "es",
        "son", "fue", "el", "la", "los", "las", "un", "una", "de", "en",
        "y", "o", "del", "al", "con", "se", "su", "nos",
    }

    words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", question)
    words += [w for w in question.split() if w.lower() not in stop and len(w) > 3]

    # Deduplicate preserving order
    seen = set()
    result = []
    for w in words:
        wl = w.lower()
        if wl not in seen:
            seen.add(wl)
            result.append(w)
    return result

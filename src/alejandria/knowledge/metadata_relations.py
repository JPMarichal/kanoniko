"""Extract typed relations from chapter metadata (P6 Phase 7).

Core logic extracted from scripts/extract_metadata_relations.py for pipeline integration.

Parses study_intro, section_headings, subtitle fields on Chapter nodes
to create structured relations:

  D&C study_intro -> REVEALED_TO, REVEALED_AT, REVEALED_ON
  Psalm superscriptions -> AUTHORED (with role=author)
  PGP subtitles -> WRITTEN_DURING (temporal)
"""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)


# ── D&C study_intro patterns ──────────────────────────────────────────────

_DC_PERSON_RE = re.compile(
    r"(?:given (?:through|to)|relating (?:the words of|to))\s+"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:the\s+)?(?:Prophet|Elder|Seer))?)",
    re.IGNORECASE,
)

_DC_PLACE_RE = re.compile(
    r"at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
)

_DC_DATE_RE = re.compile(
    r"(?:on\s+)?(?:the\s+evening\s+of\s+)?"
    r"((?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"(?:\s+\d{1,2})?,?\s*\d{4})",
    re.IGNORECASE,
)

_DC_RECIPIENT_RE = re.compile(
    r"to\s+(?:his\s+\w+,?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Sr\.|Jr\.))?)"
)

_DC_PERSON_ES_RE = re.compile(
    r"(?:dada (?:por intermedio de|a)|[Rr]evelaci[oó]n dada (?:por intermedio de|a))\s+"
    r"([A-Z][a-záéíóúñ]+(?:\s+[A-Z][a-záéíóúñ]+)*(?:\s+(?:el\s+)?(?:Profeta|[EÉ]lder))?)",
)

_DC_PLACE_ES_RE = re.compile(
    r"en\s+([A-Z][a-záéíóúñ]+(?:\s+[A-Z][a-záéíóúñ]+)*),\s*"
    r"([A-Z][a-záéíóúñ]+(?:\s+[A-Z][a-záéíóúñ]+)*)",
)

_DC_DATE_ES_RE = re.compile(
    r"(?:el\s+\d{1,2}\s+de\s+)?"
    r"((?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    r"(?:\s+de)?\s+\d{4})",
    re.IGNORECASE,
)


def parse_dc_study_intro(slug: str, text_en: str | None, text_es: str | None) -> list[dict]:
    """Extract relations from a D&C study_intro field."""
    relations = []
    ref = slug.replace("dc/sections/", "D&C ").replace("dc/official-declarations/", "OD ")

    for text, lang in [(text_en, "en"), (text_es, "es")]:
        if not text:
            continue

        if lang == "en":
            m = _DC_PERSON_RE.search(text)
            if m:
                person = m.group(1).strip()
                person = re.sub(r"\s+the\s+Prophet$", "", person)
                person = re.sub(r"\s+the\s+Elder$", "", person)
                person = re.sub(r"\s+the\s+Seer$", "", person)
                person = re.sub(r"^the\s+angel\s+\w+\s+to\s+", "", person, flags=re.IGNORECASE)
                relations.append({
                    "rel_type": "REVEALED_TO",
                    "from": {"name": ref, "type": "scripture"},
                    "to": {"name": person, "type": "person"},
                    "source_ref": ref,
                    "lang": lang,
                })

            main_person = person if m else ""
            for rm in _DC_RECIPIENT_RE.finditer(text):
                recipient = rm.group(1).strip()
                recipient = re.sub(r"\s+the\s+Prophet$", "", recipient)
                if recipient.lower() in ("the", "this", "a", "an", "all", "every", "some"):
                    continue
                if recipient == main_person:
                    continue
                if re.match(r"^(The|This|His|Her|Its|Our|Their|Each|Some|Many|All)", recipient):
                    continue
                relations.append({
                    "rel_type": "REVEALED_TO",
                    "from": {"name": ref, "type": "scripture"},
                    "to": {"name": recipient, "type": "person"},
                    "source_ref": ref,
                    "lang": lang,
                })

            pm = _DC_PLACE_RE.search(text)
            if pm:
                place = f"{pm.group(1)}, {pm.group(2)}"
                relations.append({
                    "rel_type": "REVEALED_AT",
                    "from": {"name": ref, "type": "scripture"},
                    "to": {"name": place, "type": "place"},
                    "source_ref": ref,
                    "lang": lang,
                })

            dm = _DC_DATE_RE.search(text)
            if dm:
                date = dm.group(1).strip()
                relations.append({
                    "rel_type": "REVEALED_ON",
                    "from": {"name": ref, "type": "scripture"},
                    "to": {"name": date, "type": "period"},
                    "source_ref": ref,
                    "lang": lang,
                })

    return relations


# ── Psalm superscription patterns ─────────────────────────────────────────

_PSALM_AUTHOR_RE = re.compile(
    r"(?:A (?:Psalm|Song|Prayer|Maskil|Miktam|Shiggaion) of|of)\s+"
    r"(David|Asaph|Solomon|Moses|Ethan|Heman|Korah)",
    re.IGNORECASE,
)

_PSALM_AUTHOR_ES_RE = re.compile(
    r"(?:Salmo de|de|Cántico de|Oración de|Masquil de)\s+"
    r"(David|Asaf|Salomón|Moisés|Etán|Hemán|Coré)",
    re.IGNORECASE,
)

_SONS_OF_KORAH_RE = re.compile(r"sons? of Korah", re.IGNORECASE)
_HIJOS_CORE_RE = re.compile(r"hijos? de Coré", re.IGNORECASE)

_PSALM_AUTHOR_MAP = {
    "david": "David",
    "asaph": "Asaph",
    "asaf": "Asaph",
    "solomon": "Solomon",
    "salomón": "Solomon",
    "moses": "Moses",
    "moisés": "Moses",
    "ethan": "Ethan",
    "etán": "Ethan",
    "heman": "Heman",
    "hemán": "Heman",
    "korah": "Sons of Korah",
    "coré": "Sons of Korah",
}


def parse_psalm_superscription(slug: str, headings_en: str | None, headings_es: str | None) -> list[dict]:
    """Extract AUTHORED relations from Psalm superscriptions."""
    relations = []
    chapter_num = slug.split("/")[-1]
    ref = f"Psalm {chapter_num}"
    seen_authors: set[str] = set()

    for text_raw, lang in [(headings_en, "en"), (headings_es, "es")]:
        if not text_raw:
            continue

        try:
            headings = json.loads(text_raw) if isinstance(text_raw, str) else text_raw
        except (json.JSONDecodeError, TypeError):
            headings = [text_raw] if text_raw else []

        full_text = " ".join(str(h) for h in headings)

        if _SONS_OF_KORAH_RE.search(full_text) or _HIJOS_CORE_RE.search(full_text):
            author = "Sons of Korah"
            if author not in seen_authors:
                relations.append({
                    "rel_type": "AUTHORED",
                    "from": {"name": author, "type": "people"},
                    "to": {"name": ref, "type": "scripture"},
                    "role": "author",
                    "source_ref": f"{ref} superscription",
                    "lang": lang,
                })
                seen_authors.add(author)

        pattern = _PSALM_AUTHOR_RE if lang == "en" else _PSALM_AUTHOR_ES_RE
        m = pattern.search(full_text)
        if m:
            raw = m.group(1).strip().lower()
            author = _PSALM_AUTHOR_MAP.get(raw, m.group(1).strip())
            if author not in seen_authors:
                author_type = "people" if author == "Sons of Korah" else "person"
                relations.append({
                    "rel_type": "AUTHORED",
                    "from": {"name": author, "type": author_type},
                    "to": {"name": ref, "type": "scripture"},
                    "role": "author",
                    "source_ref": f"{ref} superscription",
                    "lang": lang,
                })
                seen_authors.add(author)

    return relations


# ── PGP subtitle (temporal) ───────────────────────────────────────────────

_PGP_DATE_RE = re.compile(r"\(([A-Za-z\u2013\u2014\u00e9\u00f3 ]+\d{4})\)")
_PGP_DATE_ES_RE = re.compile(r"\(([a-z\u00e9\u00f3\u2013\u2014 ]+de\s+\d{4})\)", re.IGNORECASE)


def parse_pgp_subtitle(slug: str, subtitle_en: str | None, subtitle_es: str | None) -> list[dict]:
    """Extract WRITTEN_DURING from PGP subtitles containing dates."""
    relations = []
    book = slug.split("/")[1]
    ref_map = {"moses": "Moses", "abraham": "Abraham", "js-history": "JS-History", "js-matthew": "JS-Matthew"}
    chapter_num = slug.split("/")[-1]
    ref = f"{ref_map.get(book, book)} {chapter_num}"

    for text, lang in [(subtitle_en, "en"), (subtitle_es, "es")]:
        if not text:
            continue

        dm = _PGP_DATE_RE.search(text) if lang == "en" else _PGP_DATE_ES_RE.search(text)
        if dm:
            date = dm.group(1).strip()
            relations.append({
                "rel_type": "WRITTEN_DURING",
                "from": {"name": ref, "type": "scripture"},
                "to": {"name": date, "type": "period"},
                "source_ref": f"{ref} subtitle",
                "lang": lang,
            })

    return relations


# ── Pipeline entry point ─────────────────────────────────────────────────

def extract_metadata_relations(driver) -> dict[str, int]:
    """Extract metadata relations from Chapter nodes using an existing driver.

    Returns counts dict: {REVEALED_TO, REVEALED_AT, REVEALED_ON, AUTHORED, WRITTEN_DURING, total}.
    """
    all_relations: list[dict] = []
    counts: dict[str, int] = {}

    with driver.session() as session:
        # 1. D&C study_intro
        result = session.run(
            "MATCH (c:Chapter) WHERE c.volume_slug = 'dc' "
            "RETURN c.slug AS slug, c.study_intro_en AS intro_en, c.study_intro_es AS intro_es"
        )
        for rec in result:
            all_relations.extend(parse_dc_study_intro(rec["slug"], rec["intro_en"], rec["intro_es"]))

        # 2. Psalm superscriptions
        result = session.run(
            "MATCH (c:Chapter) WHERE c.book_slug = 'psalms' "
            "RETURN c.slug AS slug, c.section_headings_en AS sh_en, c.section_headings_es AS sh_es"
        )
        for rec in result:
            all_relations.extend(parse_psalm_superscription(rec["slug"], rec["sh_en"], rec["sh_es"]))

        # 3. PGP subtitles
        result = session.run(
            "MATCH (c:Chapter) WHERE c.volume_slug = 'pgp' "
            "RETURN c.slug AS slug, c.subtitle_en AS sub_en, c.subtitle_es AS sub_es"
        )
        for rec in result:
            all_relations.extend(parse_pgp_subtitle(rec["slug"], rec["sub_en"], rec["sub_es"]))

    # Count by type
    for r in all_relations:
        counts[r["rel_type"]] = counts.get(r["rel_type"], 0) + 1

    if not all_relations:
        logger.info("Metadata relations: no Chapter nodes with metadata found (hierarchy may not be loaded yet)")
        return counts

    # Load into Neo4j
    with driver.session() as session:
        for rel in all_relations:
            props = {
                "confidence": "metadata",
                "source": "metadata_extraction",
                "source_ref": rel.get("source_ref", ""),
                "lang": rel.get("lang", "en"),
            }
            if rel.get("role"):
                props["role"] = rel["role"]

            session.run(
                f"MERGE (a:Entity {{name: $from_name, type: $from_type}}) "
                f"MERGE (b:Entity {{name: $to_name, type: $to_type}}) "
                f"MERGE (a)-[r:{rel['rel_type']}]->(b) "
                "SET r += $props",
                from_name=rel["from"]["name"], from_type=rel["from"]["type"],
                to_name=rel["to"]["name"], to_type=rel["to"]["type"],
                props=props,
            )

    counts["total"] = len(all_relations)
    logger.info(
        "Metadata relations loaded: %s",
        ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
    )
    return counts

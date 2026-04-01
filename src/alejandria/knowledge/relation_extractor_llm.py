"""LLM-powered relation extraction from scripture passages.

P6 Phase 3 — Uses structured prompts to extract typed relations
from text passages where entities are already identified.

Similar pattern to profile_generator.py: batch processing with
tiered model selection, JSON output parsing, token tracking.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from alejandria.chat.llm import complete_with_model
from alejandria.chat.models import Tier, select_model
from alejandria.config import settings

logger = logging.getLogger(__name__)

# All valid relation types the LLM can output.
# Grouped by category for the prompt.
VALID_RELATION_TYPES = {
    # Family
    "FATHER_OF", "MOTHER_OF", "SPOUSE_OF", "BROTHER_OF", "SISTER_OF",
    "SON_OF", "DAUGHTER_OF", "ANCESTOR_OF", "DESCENDANT_OF",
    # Governance / Leadership
    "SUCCESSOR_OF", "PREDECESSOR_OF", "CALLED_AS", "RULED_OVER",
    # Attributes
    "HAS_TITLE", "TRIBE_OF",
    # Prophetic / Doctrinal
    "PROPHESIED_ABOUT", "TAUGHT", "PROPHESIED_TO", "PROPHECY_OF",
    # Geographic
    "TRAVELED_TO", "LIVED_IN", "BORN_IN", "DIED_IN", "FOUNDED",
    # Temporal
    "LIVED_DURING", "WRITTEN_DURING",
    # Authorship
    "AUTHORED",
    # Conflict / Interaction
    "FOUGHT_AGAINST", "ALLIED_WITH", "COMMANDED_BY", "SERVED_UNDER", "CONQUERED",
    # Spiritual
    "BAPTIZED_BY", "ORDAINED_BY", "BLESSED_BY", "HEALED_BY",
    "CONVERTED_BY", "APPEARED_TO", "SAW_IN_VISION",
    # Intertextuality
    "QUOTES", "ALLUDES_TO", "JST_OF",
    # Typology / Symbolism
    "TYPE_OF", "SYMBOLIZES",
    # Covenants / Priesthood
    "COVENANT_WITH", "HOLDS_PRIESTHOOD", "CONFERRED_KEYS_TO",
    # Dispensational
    "DISPENSATION_HEAD", "RESTORED",
    # Record keeping
    "RECORD_KEPT_BY", "ABRIDGED_BY",
    # Literary
    "CHIASM_IN", "GENRE_OF",
    # Organizational structure (handbook)
    "PRESIDES_OVER", "COUNSELOR_TO", "REPORTS_TO",
    "MEMBER_OF", "ORGANIZED_UNDER", "UNIT_CONTAINS",
    # Authority and keys (handbook)
    "AUTHORIZED_TO_PERFORM", "REQUIRES_APPROVAL_OF",
    "KEYS_FOR", "SET_APART_BY", "CALLED_BY",
    # Ordinances and covenants (handbook)
    "PREREQUISITE_FOR", "ORDINANCE_REQUIRES", "SEALED_TO", "COVENANT_OF",
    # Administration (handbook)
    "MANAGES_FUND", "MAINTAINS_RECORD", "CONDUCTS_INTERVIEW",
    "GOVERNS_POLICY", "CREATION_REQUIRES",
    # Discipline and membership (handbook)
    "ADJUDICATES", "RESTRICTS", "ANNOTATES",
    # Scripture structure (P1 Phase 3)
    "PART_OF", "CONTAINS",
    # Conference talks
    "CITES", "DELIVERED_BY",
}

_SYSTEM_PROMPT = """\
You are a biblical/scriptural knowledge graph specialist. Your task is to extract \
EXPLICIT typed relations between named entities from scripture passages.

RULES:
1. Extract ONLY relations that are EXPLICITLY stated or clearly implied in the passage.
2. Do NOT infer relations from general theological knowledge — only from the text provided.
3. Each relation must use one of the allowed relation types.
4. Include a brief source_ref indicating which verse(s) support the relation.
5. Assign confidence: "llm_high" if the relation is directly stated, "llm_low" if reasonably implied.
6. Output valid JSON only — no markdown, no extra text.

ALLOWED RELATION TYPES:
- Family: FATHER_OF, MOTHER_OF, SPOUSE_OF, BROTHER_OF, SISTER_OF, SON_OF, DAUGHTER_OF, ANCESTOR_OF, DESCENDANT_OF
- Leadership: SUCCESSOR_OF, PREDECESSOR_OF, CALLED_AS, RULED_OVER
- Attributes: HAS_TITLE, TRIBE_OF
- Prophetic: PROPHESIED_ABOUT, TAUGHT, PROPHESIED_TO, PROPHECY_OF
- Geographic: TRAVELED_TO, LIVED_IN, BORN_IN, DIED_IN, FOUNDED
- Temporal: LIVED_DURING, WRITTEN_DURING
- Authorship: AUTHORED
- Interaction: FOUGHT_AGAINST, ALLIED_WITH, COMMANDED_BY, SERVED_UNDER, CONQUERED
- Spiritual: BAPTIZED_BY, ORDAINED_BY, BLESSED_BY, HEALED_BY, CONVERTED_BY, APPEARED_TO, SAW_IN_VISION
- Intertextuality: QUOTES, ALLUDES_TO
- Typology: TYPE_OF, SYMBOLIZES
- Covenants: COVENANT_WITH, HOLDS_PRIESTHOOD, CONFERRED_KEYS_TO
- Dispensational: DISPENSATION_HEAD, RESTORED
- Record: RECORD_KEPT_BY, ABRIDGED_BY
- Organizational: PRESIDES_OVER, COUNSELOR_TO, REPORTS_TO, MEMBER_OF, ORGANIZED_UNDER, UNIT_CONTAINS
- Authority: AUTHORIZED_TO_PERFORM, REQUIRES_APPROVAL_OF, KEYS_FOR, SET_APART_BY, CALLED_BY
- Ordinances: PREREQUISITE_FOR, ORDINANCE_REQUIRES, SEALED_TO, COVENANT_OF
- Administration: MANAGES_FUND, MAINTAINS_RECORD, CONDUCTS_INTERVIEW, GOVERNS_POLICY, CREATION_REQUIRES
- Discipline: ADJUDICATES, RESTRICTS, ANNOTATES
- Structure: PART_OF, CONTAINS"""

_USER_PROMPT_TEMPLATE = """\
PASSAGE ({reference}):
{text}

KNOWN ENTITIES IN THIS PASSAGE:
{entities}

Extract all typed relations between these entities that are stated or clearly implied \
in the passage above. Return a JSON object:
{{
  "relations": [
    {{
      "from_name": "Entity A",
      "from_type": "person|place|people|concept|object|period|scripture|organization|calling|council|ordinance|unit|program|policy|document|volume|division|book|part",
      "rel_type": "RELATION_TYPE",
      "to_name": "Entity B",
      "to_type": "person|place|people|concept|object|period|scripture",
      "confidence": "llm_high|llm_low",
      "source_ref": "verse reference"
    }}
  ]
}}

If no relations can be extracted, return {{"relations": []}}."""


@dataclass
class LLMRelation:
    """A relation extracted by the LLM."""
    from_name: str
    from_type: str
    rel_type: str
    to_name: str
    to_type: str
    confidence: str = "llm_low"
    source_ref: str = ""


@dataclass
class ExtractionBatch:
    """A batch of passages to process."""
    file_path: str
    reference: str
    text: str
    entities: list[dict]  # [{"name": ..., "type": ...}]


@dataclass
class ExtractionStats:
    """Statistics from a batch extraction run."""
    passages_processed: int = 0
    relations_extracted: int = 0
    relations_loaded: int = 0
    duplicates_skipped: int = 0
    errors: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    elapsed_seconds: float = 0.0


class LLMRelationExtractor:
    """Extract typed relations from passages using LLM."""

    def __init__(self, tier: str = "fast") -> None:
        self._tier = Tier(tier) if tier in ("fast", "balanced", "quality") else Tier.FAST
        self._total_input_tokens = 0
        self._total_output_tokens = 0

    def extract_from_passage(
        self, text: str, reference: str, entities: list[dict],
    ) -> list[LLMRelation]:
        """Extract relations from a single passage.

        Args:
            text: The passage text.
            reference: Scripture reference (e.g., "Genesis 25:19-34").
            entities: Known entities in this passage [{"name": ..., "type": ...}].

        Returns list of LLMRelation objects.
        """
        if not entities or len(entities) < 2:
            return []  # Need at least 2 entities for a relation

        model = select_model(self._tier)
        if model is None:
            logger.warning("No LLM model available for relation extraction")
            return []

        # Format entities for prompt (limit to 30 most important to avoid huge prompts)
        entity_lines = []
        for e in entities[:30]:
            entity_lines.append(f"- {e['name']} ({e['type']})")
        entities_text = "\n".join(entity_lines)

        user_msg = _USER_PROMPT_TEMPLATE.format(
            reference=reference,
            text=text[:3000],  # Limit passage length
            entities=entities_text,
        )

        try:
            response = complete_with_model(_SYSTEM_PROMPT, user_msg, model)
            self._total_input_tokens += response.input_tokens
            self._total_output_tokens += response.output_tokens
        except Exception:
            logger.exception("LLM call failed for %s", reference)
            return []

        return self._parse_response(response.text, reference)

    def _parse_response(self, text: str, reference: str) -> list[LLMRelation]:
        """Parse LLM JSON response into LLMRelation objects."""
        data = None

        # Strategy 1: Direct JSON parse
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from markdown code block (greedy to get full JSON)
        if data is None:
            match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass

        # Strategy 3: Find the outermost { ... } in the response
        if data is None:
            start = text.find("{")
            if start >= 0:
                # Find matching closing brace
                depth = 0
                for i in range(start, len(text)):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            try:
                                data = json.loads(text[start:i+1])
                            except json.JSONDecodeError:
                                pass
                            break

        # Strategy 4: Truncated response — try to salvage partial JSON
        if data is None:
            # Find all complete relation objects via regex
            pattern = r'\{[^{}]*?"from_name"\s*:\s*"[^"]*"[^{}]*?"rel_type"\s*:\s*"[^"]*"[^{}]*?"to_name"\s*:\s*"[^"]*"[^{}]*?\}'
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                salvaged = []
                for m in matches:
                    try:
                        salvaged.append(json.loads(m))
                    except json.JSONDecodeError:
                        continue
                if salvaged:
                    data = {"relations": salvaged}
                    logger.info("Salvaged %d relations from truncated response for %s", len(salvaged), reference)

        if data is None:
            logger.warning("Failed to parse LLM response for %s: %.200s", reference, text)
            return []

        relations = []
        for r in data.get("relations", []):
            rel_type = r.get("rel_type", "")
            if rel_type not in VALID_RELATION_TYPES:
                logger.debug("Skipping invalid relation type: %s", rel_type)
                continue

            confidence = r.get("confidence", "llm_low")
            if confidence not in ("llm_high", "llm_low"):
                confidence = "llm_low"

            relations.append(LLMRelation(
                from_name=r.get("from_name", ""),
                from_type=r.get("from_type", "unknown"),
                rel_type=rel_type,
                to_name=r.get("to_name", ""),
                to_type=r.get("to_type", "unknown"),
                confidence=confidence,
                source_ref=r.get("source_ref", reference),
            ))

        return relations

    def extract_batch(
        self,
        batches: list[ExtractionBatch],
        neo4j_client=None,
        dry_run: bool = False,
    ) -> ExtractionStats:
        """Process a batch of passages, optionally loading into Neo4j.

        Args:
            batches: List of ExtractionBatch to process.
            neo4j_client: Optional Neo4jClient to load results. None = collect only.
            dry_run: If True, extract but don't load.

        Returns ExtractionStats.
        """
        start = time.time()
        self._total_input_tokens = 0
        self._total_output_tokens = 0

        stats = ExtractionStats()
        all_relations: list[LLMRelation] = []
        seen_keys: set[str] = set()

        for i, batch in enumerate(batches):
            try:
                relations = self.extract_from_passage(
                    text=batch.text,
                    reference=batch.reference,
                    entities=batch.entities,
                )
                stats.passages_processed += 1

                for rel in relations:
                    # Dedup key
                    key = f"{rel.from_name}|{rel.rel_type}|{rel.to_name}"
                    if key in seen_keys:
                        stats.duplicates_skipped += 1
                        continue
                    seen_keys.add(key)
                    all_relations.append(rel)
                    stats.relations_extracted += 1

            except Exception:
                logger.exception("Error processing %s", batch.reference)
                stats.errors += 1

            if (i + 1) % 20 == 0:
                logger.info(
                    "LLM extraction: %d/%d passages, %d relations, %d tokens in/out",
                    i + 1, len(batches), stats.relations_extracted,
                    self._total_input_tokens + self._total_output_tokens,
                )

        # Load into Neo4j if not dry_run
        if neo4j_client and not dry_run:
            for rel in all_relations:
                try:
                    neo4j_client.merge_relation(
                        from_name=rel.from_name,
                        from_type=rel.from_type,
                        rel_type=rel.rel_type,
                        to_name=rel.to_name,
                        to_type=rel.to_type,
                        properties={
                            "confidence": rel.confidence,
                            "source": "llm",
                            "source_ref": rel.source_ref,
                        },
                    )
                    stats.relations_loaded += 1
                except Exception:
                    logger.exception("Failed to load relation: %s", rel)
                    stats.errors += 1

        stats.input_tokens = self._total_input_tokens
        stats.output_tokens = self._total_output_tokens
        stats.elapsed_seconds = round(time.time() - start, 1)

        logger.info(
            "LLM extraction complete: %d passages, %d relations (%d loaded), "
            "%d duplicates, %d errors, %d/%d tokens in %.1fs",
            stats.passages_processed, stats.relations_extracted,
            stats.relations_loaded, stats.duplicates_skipped,
            stats.errors, stats.input_tokens, stats.output_tokens,
            stats.elapsed_seconds,
        )

        return stats, all_relations


def build_batches_from_index(
    max_passages: int = 100,
    min_entities: int = 3,
    volumes: list[str] | None = None,
) -> list[ExtractionBatch]:
    """Build extraction batches from the FTS index.

    Selects passages that have the most entity mentions (richest for relations).

    Args:
        max_passages: Maximum passages to process.
        min_entities: Minimum entities per passage to be included.
        volumes: Optional filter to specific volumes (e.g., ["ot", "nt", "bom"]).

    Returns list of ExtractionBatch objects.
    """
    from alejandria.knowledge.extractor import KGExtractor

    import sqlite3

    db_path = Path(settings.sqlite_db_path)
    if not db_path.exists():
        logger.error("SQLite DB not found: %s", db_path)
        return []

    extractor = KGExtractor()
    batches: list[ExtractionBatch] = []

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        # Get chunks with most entity variety
        # Exclude .meta.json files (cross-references) — prefer actual passage text
        query = """
            SELECT file_path, chunk_index, text, reference
            FROM chunks
            WHERE length(text) > 100
              AND file_path NOT LIKE '%.meta.json'
        """
        params: list[Any] = []

        if volumes:
            placeholders = ",".join("?" * len(volumes))
            # Filter by volume prefix in file_path
            conditions = " OR ".join(f"file_path LIKE ?" for _ in volumes)
            query += f" AND ({conditions})"
            for v in volumes:
                params.append(f"%/scriptures/{v}/%")

        query += " ORDER BY length(text) DESC LIMIT ?"
        params.append(max_passages * 5)  # Get more than needed, filter by entity count

        rows = conn.execute(query, params).fetchall()

    # Score each passage by entity count
    scored: list[tuple[int, dict]] = []
    for row in rows:
        content = row["text"]
        result = extractor.extract(content, source_file=row["file_path"])
        entity_count = len([e for e in result.entities if e.source == "gazetteer"])

        if entity_count >= min_entities:
            entities = [
                {"name": e.name, "type": e.type}
                for e in result.entities
                if e.type != "scripture"  # Skip scripture refs as entities
            ]
            # Deduplicate entities
            seen = set()
            unique_entities = []
            for e in entities:
                k = f"{e['name']}:{e['type']}"
                if k not in seen:
                    seen.add(k)
                    unique_entities.append(e)

            scored.append((
                len(unique_entities),
                {
                    "file_path": row["file_path"],
                    "reference": row["reference"] or row["file_path"],
                    "text": content,
                    "entities": unique_entities,
                },
            ))

    # Sort by entity count descending, take top passages
    scored.sort(key=lambda x: x[0], reverse=True)

    for _, data in scored[:max_passages]:
        batches.append(ExtractionBatch(**data))

    logger.info(
        "Built %d extraction batches from %d candidates (min_entities=%d)",
        len(batches), len(rows), min_entities,
    )
    return batches

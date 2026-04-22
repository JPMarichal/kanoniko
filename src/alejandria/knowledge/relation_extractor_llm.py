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
    "HAS_TITLE", "HAS_ROLE", "CALLED_BY_NAME", "TRIBE_OF",
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
    "TYPE_OF", "SYMBOLIZES", "ANTITYPE_OF", "DUAL_FULFILLMENT",
    # Covenants / Priesthood
    "COVENANT_WITH", "HOLDS_PRIESTHOOD", "CONFERRED_KEYS_TO", "KEYBEARER_OF",
    # Dispensational
    "DISPENSATION_HEAD", "RESTORED", "DISPENSATION_OF",
    # Record keeping
    "RECORD_KEPT_BY", "ABRIDGED_BY",
    # Literary / Linguistic
    "CHIASM_IN", "GENRE_OF", "TRANSLATES_AS",
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
- Typology: TYPE_OF, SYMBOLIZES, ANTITYPE_OF, DUAL_FULFILLMENT
- Covenants: COVENANT_WITH, HOLDS_PRIESTHOOD, CONFERRED_KEYS_TO, KEYBEARER_OF
- Dispensational: DISPENSATION_HEAD, RESTORED, DISPENSATION_OF
- Record: RECORD_KEPT_BY, ABRIDGED_BY
- Linguistic: TRANSLATES_AS
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
    cost_usd: float = 0.0


class LLMRelationExtractor:
    """Extract typed relations from passages using LLM."""

    def __init__(self, tier: str = "fast", budget_usd: float = 0.0) -> None:
        self._tier = Tier(tier) if tier in ("fast", "balanced", "quality") else Tier.FAST
        self._budget_usd = budget_usd  # 0 = unlimited
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._model_def: Any = None  # Cache for cost tracking

    @property
    def spent_usd(self) -> float:
        """Current accumulated cost in USD."""
        if self._model_def is None:
            return 0.0
        return (
            self._total_input_tokens / 1_000_000 * self._model_def.cost_input
            + self._total_output_tokens / 1_000_000 * self._model_def.cost_output
        )

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

        # Budget check before making the call
        if self._budget_usd > 0 and self.spent_usd >= self._budget_usd:
            logger.warning("Budget exhausted ($%.2f / $%.2f), skipping", self.spent_usd, self._budget_usd)
            return []

        model = select_model(self._tier)
        if model is None:
            logger.warning("No LLM model available for relation extraction")
            return []
        self._model_def = model

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
        graph_client=None,
        dry_run: bool = False,
    ) -> ExtractionStats:
        """Process a batch of passages, optionally loading into the KG.

        Args:
            batches: List of ExtractionBatch to process.
            graph_client: Optional graph client (e.g. PostgresGraphClient) with
                ``batch_merge_relations(list[dict])``. None = collect only.
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

            # Budget gate — stop early if budget exhausted
            if self._budget_usd > 0 and self.spent_usd >= self._budget_usd:
                logger.warning(
                    "Budget cap reached ($%.2f / $%.2f) after %d passages",
                    self.spent_usd, self._budget_usd, i + 1,
                )
                break

            if (i + 1) % 20 == 0:
                logger.info(
                    "LLM extraction: %d/%d passages, %d relations, $%.2f spent",
                    i + 1, len(batches), stats.relations_extracted,
                    self.spent_usd,
                )

        # Load into the KG if not dry_run — single batch for performance.
        if graph_client and not dry_run:
            batch = [
                {
                    "from_name": rel.from_name,
                    "from_type": rel.from_type,
                    "rel_type": rel.rel_type,
                    "to_name": rel.to_name,
                    "to_type": rel.to_type,
                    "props": {
                        "confidence": rel.confidence,
                        "source": "llm",
                        "source_ref": rel.source_ref,
                    },
                }
                for rel in all_relations
            ]
            try:
                graph_client.batch_merge_relations(batch)
                stats.relations_loaded = len(batch)
            except Exception:
                logger.exception("Failed to batch-load %d relations", len(batch))
                stats.errors += len(batch)

        stats.input_tokens = self._total_input_tokens
        stats.output_tokens = self._total_output_tokens
        stats.elapsed_seconds = round(time.time() - start, 1)

        stats.cost_usd = round(self.spent_usd, 4)

        logger.info(
            "LLM extraction complete: %d passages, %d relations (%d loaded), "
            "%d duplicates, %d errors, %d/%d tokens, $%.2f in %.1fs",
            stats.passages_processed, stats.relations_extracted,
            stats.relations_loaded, stats.duplicates_skipped,
            stats.errors, stats.input_tokens, stats.output_tokens,
            stats.cost_usd, stats.elapsed_seconds,
        )

        return stats, all_relations


def build_batches_from_index(
    max_passages: int = 100,
    min_entities: int = 3,
    volumes: list[str] | None = None,
) -> list[ExtractionBatch]:
    """Build extraction batches from the FTS index.

    Selects passages that have the most entity mentions (richest for relations).
    Uses lightweight gazetteer-only matching for scoring (no spaCy NER,
    no disambiguation) to keep memory and CPU usage low.

    Args:
        max_passages: Maximum passages to process.
        min_entities: Minimum entities per passage to be included.
        volumes: Optional filter to specific volumes (e.g., ["ot", "nt", "bom"]).

    Returns list of ExtractionBatch objects.
    """
    import heapq

    from alejandria.knowledge.extractor import KGExtractor
    from alejandria.storage.postgres.connection import get_connection

    # Build a lightweight gazetteer regex + lookup — skip spaCy and disambiguation
    extractor = KGExtractor()
    gaz_re = extractor._gazetteer_re
    gaz_lookup = extractor._lookup
    if not gaz_re:
        logger.error("Gazetteer regex not available")
        return []

    query = (
        "SELECT file_path, chunk_index, text, reference "
        "FROM chunks "
        "WHERE length(text) > 100 "
        "  AND file_path NOT LIKE %s"
    )
    params: list[Any] = ["%.meta.json"]

    if volumes:
        conditions = " OR ".join("file_path LIKE %s" for _ in volumes)
        query += f" AND ({conditions})"
        for v in volumes:
            params.append(f"%/scriptures/{v}/%")

    # Use a min-heap of size max_passages to avoid storing all scored rows
    # Heap entries: (entity_count, row_index, data_dict)
    heap: list[tuple[int, int, dict]] = []
    total_candidates = 0

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        batch_size = 5000

        row_idx = 0
        while True:
            rows = cur.fetchmany(batch_size)
            if not rows:
                break

            for row in rows:
                # Postgres tuple: (file_path, chunk_index, text, reference)
                file_path, chunk_index, content, reference = row
                text_lower = content.lower()

                # Lightweight gazetteer-only entity counting
                seen: set[str] = set()
                for match in gaz_re.finditer(text_lower):
                    term = match.group(1).lower()
                    for canonical, etype in gaz_lookup.get(term, []):
                        if etype != "scripture":
                            seen.add(f"{canonical}:{etype}")

                entity_count = len(seen)
                if entity_count < min_entities:
                    continue

                total_candidates += 1

                # Build entity list for the batch
                entities = [
                    {"name": k.rsplit(":", 1)[0], "type": k.rsplit(":", 1)[1]}
                    for k in seen
                ]

                entry = (
                    entity_count,
                    row_idx,
                    {
                        "file_path": file_path,
                        "reference": reference or file_path,
                        "text": content,
                        "entities": entities,
                    },
                )

                if len(heap) < max_passages:
                    heapq.heappush(heap, entry)
                elif entity_count > heap[0][0]:
                    heapq.heapreplace(heap, entry)

                row_idx += 1

            logger.info(
                "Batch scoring: processed %d rows, %d candidates, heap size %d",
                row_idx, total_candidates, len(heap),
            )

    # Extract from heap sorted by entity count descending
    heap.sort(key=lambda x: x[0], reverse=True)
    batches = [ExtractionBatch(**entry[2]) for entry in heap]

    logger.info(
        "Built %d extraction batches from %d candidates (min_entities=%d)",
        len(batches), total_candidates, min_entities,
    )
    return batches

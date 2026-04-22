"""RAG pipeline — retrieves context from all search modes and generates answers.

Uses tiered model selection:
- Internal calls (query expansion, reranking) use the cheapest available model
- Answer generation routes to the appropriate tier based on question complexity
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from alejandria.authority import (
    AuthorityMeta,
    authority_label,
    classify_query_type,
    degrade_importance,
    derive_authority,
    effective_authority,
    importance_boost,
)
from alejandria.chat.definitions import DefinitionLookup
from alejandria.chat.jst_pairing import JSTLookup
from alejandria.config import settings

logger = logging.getLogger(__name__)


def _extract_authority_from_result(result) -> tuple[int | None, str | None]:
    """Extract authority score and label from a search result's metadata.

    Works with both hybrid results (with .metadata dict) and raw dicts.
    Falls back to path-based derivation if metadata has no authority.
    """
    meta = getattr(result, "metadata", None)
    if isinstance(meta, dict):
        auth_data = meta.get("auth")
        if isinstance(auth_data, dict):
            auth_val = auth_data.get("authority")
            if auth_val is not None:
                return auth_val, authority_label(AuthorityMeta(authority=auth_val))

    # Fallback: derive from file_path
    file_path = getattr(result, "file_path", "") or ""
    if file_path:
        parts = file_path.replace("\\", "/").split("/")
        source = parts[1] if len(parts) >= 3 and parts[0] in ("en", "es") else parts[0]
        meta_obj = derive_authority(source, file_path)
        return meta_obj.authority, authority_label(meta_obj)

    return None, None


def _authority_for_path(file_path: str) -> tuple[int, str]:
    """Derive authority score and label from a corpus file path."""
    parts = file_path.replace("\\", "/").split("/")
    source = parts[1] if len(parts) >= 3 and parts[0] in ("en", "es") else parts[0]
    meta_obj = derive_authority(source, file_path)
    return meta_obj.authority, authority_label(meta_obj)

SYSTEM_PROMPT = """\
You are Alejandría, a bilingual (Spanish/English) research assistant specialized \
in the scriptures and gospel of The Church of Jesus Christ of Latter-day Saints.

INSTRUCTIONS:
- Answer based ONLY on the provided context passages. If insufficient, say so.
- Respond in the same language the user used.
- Be CONCISE. Give a focused answer, not an essay. Cite the key verses and \
explain the connection briefly. Avoid repeating the same idea in multiple ways.
- When context includes cross-referenced verses (footnote-xref sources), these \
are official Church footnote cross-references — highlight them as such.

KNOWLEDGE GRAPH:
- Context may include a "Knowledge Graph" section with typed relations between \
entities (e.g., Father Of, Covenant With, Type Of, Quotes, Prophecy Of).
- Use these relations to enrich your answer with structural connections — e.g., \
genealogical links, covenant chains, typological parallels, prophecy fulfillments.
- Relations marked with scripture references are curated facts — trust them.
- Entity profiles provide authoritative summaries — use them as background.

CITATION RULES:
- Cite using scripture references (e.g., 1 Nephi 3:7, D&C 76:22).
- Quote scripture LITERALLY as it appears in context — never paraphrase as quote.
- Every quote MUST include its reference in parentheses.
- Inline style preferred: Nefi dijo "Iré y haré" (1 Nefi 3:7).
- Do not invent text not present in the context passages.

AUTHORITY:
- Each source is tagged with its authority tier (Canon, Prophetic, Correlated, etc.).
- When sources conflict, prefer higher-authority sources.
- Canon (scriptures) > Prophetic (conference talks) > Correlated (manuals) > other.
- When citing non-canonical sources, acknowledge their tier if relevant to the answer.
- Never present a lower-authority source as having the same weight as scripture.

STUDY AIDS:
- Context may include "Doctrinal definitions" from the Bible Dictionary (BD) or \
Guide to the Scriptures (GEE). Use these as background framing, NOT as citable \
doctrine. The BD explicitly disclaims official doctrinal status.
- JST variants may appear alongside Bible passages. When present, note the JST \
reading as Joseph Smith's inspired revision — it carries quasi-canonical authority.
- The Book of Mormon Title Page is ancient translated text by Moroni — treat it \
as canonical scripture, not as modern editorial material.\
"""


@dataclass
class ChatSource:
    text: str
    file_path: str
    chunk_index: int
    score: float
    mode: str  # "text", "semantic", "hybrid", or "cross-ref"
    reference: str | None = None
    authority: int | None = None     # Doctrinal authority (1-100)
    authority_label: str | None = None  # Human-readable authority tier


@dataclass
class ChatResponse:
    answer: str
    sources: list[ChatSource]
    graph_context: str | None = None
    model: str = ""
    tier: str = ""          # Tier used for the answer
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class RAGPipeline:
    """Retrieval-Augmented Generation pipeline combining all search modes."""

    textual_search: object  # TextualSearch
    semantic_search: object | None = None  # SemanticSearch or None
    graph_client: object | None = None  # PostgresGraphClient or None
    profile_store: object | None = None  # ProfileStore or None
    definition_lookup: DefinitionLookup | None = None  # BD/GEE definitions
    jst_lookup: JSTLookup | None = None  # JST variant pairing

    def ask(
        self,
        question: str,
        source_filter: str | None = None,
        provider_override: str | None = None,
        model_override: str | None = None,
        tier_override: str | None = None,
    ) -> ChatResponse:
        """Answer a question using RAG over the corpus.

        Args:
            question: The user's question.
            source_filter: Optional corpus path filter.
            provider_override: If set, use this LLM provider for the answer.
            model_override: If set, use this model name with the provider.
            tier_override: If set, force a specific tier ("fast", "balanced",
                "quality") or model ID for the answer.
        """
        # Determine effective tier early — needed for context sizing and max_tokens
        effective_tier = self._resolve_tier(question, tier_override, provider_override, model_override)

        # 0. Direct scripture lookup: if the question mentions specific references,
        #    fetch those verses directly so they're always in context
        direct_sources, detected_refs = self._direct_scripture_lookup(question)

        # 0b. If we found specific verses, also fetch their official cross-references
        #     directly (read the actual verse text, don't rely on FTS keywords)
        xref_sources = self._direct_xref_lookup(detected_refs) if detected_refs else []

        # 1. Expand query for better retrieval (uses internal/fast tier)
        fts_query = self._expand_query(question)

        # 2. KG-boosted retrieval: find entity documents before searching
        kg_file_hints = self._get_kg_file_hints(question)

        # 3. Retrieve from all available search modes + KG hints
        #    Use more context chunks for QUALITY tier questions
        context_chunks = (
            settings.rag_context_chunks_quality
            if effective_tier == "quality"
            else settings.rag_context_chunks
        )
        sources = self._retrieve(question, fts_query, source_filter, kg_file_hints,
                                 context_chunks=context_chunks)

        # Prepend direct lookups and cross-refs (highest priority)
        if direct_sources or xref_sources:
            sources = direct_sources + xref_sources + sources

        # 4. Build graph context if available
        graph_context = self._get_graph_context(question)

        # 4b. Look up BD/GEE definitions for key concepts (zero LLM cost)
        definition_context = self._get_definition_context(question, kg_file_hints)

        # 5. Assemble the context prompt
        context_text = self._build_context(sources, graph_context,
                                           definition_context)

        # 5. Call LLM for the answer — use shorter output for FAST tier
        max_tokens = (
            settings.llm_max_tokens_fast
            if effective_tier == "fast"
            else None  # default (settings.llm_max_tokens)
        )
        user_message = f"CONTEXT:\n{context_text}\n\nQUESTION:\n{question}"
        llm_response, used_model, used_tier = self._generate_answer(
            user_message, question,
            provider_override=provider_override,
            model_override=model_override,
            tier_override=tier_override,
            max_tokens=max_tokens,
        )

        return ChatResponse(
            answer=llm_response.text,
            sources=sources,
            graph_context=graph_context,
            model=llm_response.model,
            tier=used_tier,
            input_tokens=llm_response.input_tokens,
            output_tokens=llm_response.output_tokens,
        )

    @staticmethod
    def _resolve_tier(
        question: str,
        tier_override: str | None = None,
        provider_override: str | None = None,
        model_override: str | None = None,
    ) -> str:
        """Resolve the effective tier name early (no LLM call).

        Returns a tier string: "fast", "balanced", "quality", "override", or "legacy".
        Used to size context chunks and max_tokens before calling _generate_answer().
        """
        if provider_override or model_override:
            return "override"

        from alejandria.chat.models import Tier, classify_complexity, select_model_by_id

        tier_setting = tier_override or settings.llm_answer_tier
        if tier_setting == "auto":
            return classify_complexity(question).value
        if tier_setting in ("fast", "balanced", "quality"):
            return tier_setting
        # Model ID — resolve its tier
        model_def = select_model_by_id(tier_setting)
        if model_def:
            return model_def.tier.value
        return "balanced"

    def _generate_answer(
        self,
        user_message: str,
        question: str,
        *,
        provider_override: str | None = None,
        model_override: str | None = None,
        tier_override: str | None = None,
        max_tokens: int | None = None,
    ):
        """Generate the final answer using tiered model selection.

        Returns (LLMResponse, ModelDef|None, tier_name).
        """
        from alejandria.chat.llm import complete, complete_with_model
        from alejandria.chat.models import (
            Tier, classify_complexity, select_model, select_model_by_id,
        )

        # Explicit provider/model override — bypass tier system
        if provider_override or model_override:
            from alejandria.chat.models import get_api_key
            provider = provider_override or settings.llm_provider
            model = model_override or settings.llm_model
            api_key = get_api_key(provider)
            response = complete(SYSTEM_PROMPT, user_message,
                                provider=provider, model=model, api_key=api_key,
                                max_tokens=max_tokens)
            return response, None, "override"

        # Determine tier
        tier_setting = tier_override or settings.llm_answer_tier

        if tier_setting == "auto":
            tier = classify_complexity(question)
            logger.info("Auto-classified question complexity: %s", tier.value)
        elif tier_setting in ("fast", "balanced", "quality"):
            tier = Tier(tier_setting)
        else:
            # Treat as model ID
            model_def = select_model_by_id(tier_setting)
            if model_def:
                response = complete_with_model(SYSTEM_PROMPT, user_message, model_def,
                                               max_tokens=max_tokens)
                return response, model_def, model_def.tier.value
            # Unknown — default to balanced
            tier = Tier.BALANCED

        # Try models in the tier, falling back to next on connection errors
        from alejandria.chat.models import get_available_models
        candidates = [m for m in get_available_models() if m.tier == tier]
        if not candidates:
            # No models in exact tier — use select_model which handles fallback
            candidates = [select_model(tier)] if select_model(tier) else []

        for model_def in candidates:
            try:
                logger.info("Selected model: %s (tier=%s)", model_def.id, model_def.tier.value)
                response = complete_with_model(SYSTEM_PROMPT, user_message, model_def,
                                               max_tokens=max_tokens)
                return response, model_def, model_def.tier.value
            except Exception as e:
                logger.warning("Model %s failed: %s — trying next", model_def.id, str(e)[:100])
                continue

        if not candidates:
            # No tiered models available — fall back to legacy settings
            logger.warning("No tiered models available, using legacy settings")
            response = complete(SYSTEM_PROMPT, user_message, max_tokens=max_tokens)
            return response, None, "legacy"

    def _complete_internal(self, system_prompt: str, user_message: str):
        """Make an internal LLM call (expansion, reranking) using the cheapest tier.

        Returns an LLMResponse. Falls back to legacy settings if no tiered model available.
        """
        from alejandria.chat.llm import complete, complete_with_model
        from alejandria.chat.models import Tier, select_model, select_model_by_id

        tier_setting = settings.llm_internal_tier
        if tier_setting in ("fast", "balanced", "quality"):
            tier = Tier(tier_setting)
        else:
            model_def = select_model_by_id(tier_setting)
            if model_def:
                return complete_with_model(system_prompt, user_message, model_def)
            tier = Tier.FAST

        from alejandria.chat.models import get_available_models
        candidates = [m for m in get_available_models() if m.tier == tier]
        if not candidates:
            m = select_model(tier)
            candidates = [m] if m else []

        for model_def in candidates:
            try:
                return complete_with_model(system_prompt, user_message, model_def)
            except Exception as e:
                logger.warning("Internal model %s failed: %s — trying next", model_def.id, str(e)[:100])
                continue

        return complete(system_prompt, user_message)

    def _expand_query(self, question: str) -> str:
        """Generate effective search keywords for FTS retrieval.

        Uses LLM only for vague/abstract questions. If the question already
        contains specific names or scripture references, returns it directly
        (saves one LLM call per question in ~40-60% of cases).
        """
        # Skip expansion if the question already has specific search terms
        if self._has_specific_terms(question):
            logger.info("Query expansion skipped (specific terms detected): '%s'", question)
            return question

        try:
            expansion_prompt = (
                "You are a search query optimizer for a scripture corpus (Bible, "
                "Book of Mormon, Doctrine and Covenants, Pearl of Great Price). "
                "Given a user question, output ONLY the most relevant keywords and "
                "phrases that would appear in the actual scripture text answering "
                "this question. Include key nouns, verbs, and distinctive phrases "
                "from the relevant passages. Output keywords separated by spaces, "
                "nothing else. No explanations."
            )
            result = self._complete_internal(expansion_prompt, question)
            expanded = result.text.strip()
            logger.info("Query expansion: '%s' -> '%s' [model=%s]", question, expanded, result.model)
            return expanded if expanded else question
        except Exception:
            logger.warning("Query expansion failed, using original question")
            return question

    @staticmethod
    def _has_specific_terms(question: str) -> bool:
        """Check if the question already has entity names or scripture refs.

        If so, FTS will work well without LLM expansion.
        """
        import re
        # Scripture references (e.g., "1 Nephi 3:7", "D&C 76")
        if re.search(r'\b\d?\s?(?:Nephi|Alma|Mosiah|Helaman|Ether|Mormon|Moroni|'
                      r'Genesis|Exodus|Isaiah|Psalm|Matthew|John|Acts|Romans|'
                      r'Revelation|D&C|Abraham|Moses)\s+\d', question, re.IGNORECASE):
            return True
        # Proper names (2+ capitalized words in a row = likely entity)
        proper_nouns = re.findall(r'\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*\b', question)
        if len(proper_nouns) >= 2:
            return True
        # Question has 6+ words and at least one proper noun — probably specific enough
        words = question.split()
        if len(words) >= 6 and proper_nouns:
            return True
        return False

    def _get_kg_file_hints(self, question: str) -> list[tuple[str, str]]:
        """Find KG documents related to entities in the question.

        Uses the gazetteer extractor (zero LLM cost) instead of an LLM call.
        The gazetteer has 2,600+ entities with aliases — sufficient for entity
        extraction from short questions.

        Returns list of (file_path, entity_label) tuples.
        """
        if self.graph_client is None:
            return []

        try:
            # Step 1: Extract entities using gazetteer (no LLM call)
            entity_names = self._extract_entities_from_question(question)
            if not entity_names:
                return []

            # Step 2: Batch search KG for matching entities (1 query instead of N)
            matches = self.graph_client.find_nodes_batch(entity_names)
            matched_entities = [m.get("name", "") for m in matches if m.get("name")]
            if not matched_entities:
                return []

            # Step 3: Batch get documents for all matched entities (1 query instead of N)
            docs_map = self.graph_client.get_documents_for_entities_batch(matched_entities)

            file_hints: list[tuple[str, str]] = []
            seen_files: set[str] = set()
            for ename, file_paths in docs_map.items():
                for fp in file_paths:
                    if fp and fp not in seen_files:
                        seen_files.add(fp)
                        file_hints.append((fp, ename))

            if matched_entities:
                logger.info(
                    "KG entity search: names=%s → %d entities → %d documents (2 queries)",
                    entity_names, len(matched_entities), len(file_hints),
                )

            return file_hints
        except Exception:
            logger.warning("KG file hint extraction failed")
            return []

    def _extract_entities_from_question(self, question: str) -> list[str]:
        """Extract entity names from the question using the gazetteer.

        Zero LLM cost — uses the curated gazetteer (2,600+ entities with
        bilingual aliases) to find entities mentioned in the question.
        Handles plurals and common variations via alias matching.
        """
        try:
            from alejandria.knowledge.extractor import KGExtractor
            extractor = KGExtractor()
            extraction = extractor.extract(question)

            # Collect unique canonical names (prefer gazetteer over NER)
            names: list[str] = []
            seen: set[str] = set()
            for entity in extraction.entities:
                if entity.type == "scripture":
                    continue  # Skip scripture refs
                if entity.name not in seen:
                    seen.add(entity.name)
                    names.append(entity.name)

            if names:
                logger.info("Gazetteer entity extraction: '%s' → %s", question, names)
            return names
        except Exception:
            logger.warning("Gazetteer entity extraction failed")
            return []

    @staticmethod
    def _is_enumeration_query(question: str) -> bool:
        """Detect questions that ask for exhaustive lists (how many, list all, etc.)."""
        import re
        patterns = [
            r"\bcu[aá]nt[ao]s\b", r"\bhow many\b",
            r"\btod[ao]s l[ao]s\b", r"\ball the\b", r"\bevery\b",
            r"\blista\b.*\bmencion", r"\blist\b.*\bmention",
            r"\bqu[ée] .*\bse mencionan\b", r"\bwho .*\bare mentioned\b",
            r"\benumera\b", r"\benumerate\b",
        ]
        q = question.lower()
        return any(re.search(p, q) for p in patterns)

    # ── Scripture reference detection (shared by direct lookup + xref) ────

    @staticmethod
    def _build_ref_abbrevs() -> dict[str, tuple[str, str]]:
        """Build abbreviation → (volume, book_slug) mapping for reference detection."""
        from alejandria.ingestion.scripture_meta import BOOK_REGISTRY, VOLUME_BOOKS

        abbrevs: dict[str, tuple[str, str]] = {}
        for slug, names in BOOK_REGISTRY.items():
            vol = next((v for v, slugs in VOLUME_BOOKS.items() if slug in slugs), None)
            if vol is None:
                continue
            abbrevs[names["en"].lower()] = (vol, slug)
            abbrevs[names["es"].lower()] = (vol, slug)

        abbrevs.update({
            "1 ne": ("bom", "1-nephi"), "2 ne": ("bom", "2-nephi"),
            "3 ne": ("bom", "3-nephi"), "4 ne": ("bom", "4-nephi"),
            "1 nefi": ("bom", "1-nephi"), "2 nefi": ("bom", "2-nephi"),
            "3 nefi": ("bom", "3-nephi"), "4 nefi": ("bom", "4-nephi"),
            "d&c": ("dc", "sections"), "dyc": ("dc", "sections"),
            "gen": ("ot", "genesis"), "ex": ("ot", "exodus"),
            "isa": ("ot", "isaiah"), "jer": ("ot", "jeremiah"),
            "matt": ("nt", "matthew"), "rom": ("nt", "romans"),
            "heb": ("nt", "hebrews"), "rev": ("nt", "revelation"),
            "alma": ("bom", "alma"), "mosiah": ("bom", "mosiah"),
            "morm": ("bom", "mormon"), "ether": ("bom", "ether"),
            "hel": ("bom", "helaman"), "moro": ("bom", "moroni"),
            "js\u2014h": ("pgp", "js-history"), "js\u2014m": ("pgp", "js-matthew"),
            "abr": ("pgp", "abraham"), "moses": ("pgp", "moses"),
            "sal": ("ot", "psalms"), "prov": ("ot", "proverbs"),
            "deut": ("ot", "deuteronomy"), "acts": ("nt", "acts"),
            "hechos": ("nt", "acts"), "lucas": ("nt", "luke"),
            "mateo": ("nt", "matthew"), "juan": ("nt", "john"),
            "apoc": ("nt", "revelation"), "jacob": ("bom", "jacob"),
        })
        return abbrevs

    @staticmethod
    def _detect_scripture_refs(question: str) -> list[dict]:
        """Detect scripture references in a question string.

        Returns list of dicts: {volume, book_slug, chapter, verse_start, verse_end}
        """
        import re

        abbrevs = RAGPipeline._build_ref_abbrevs()
        sorted_keys = sorted(abbrevs.keys(), key=len, reverse=True)
        pattern = "|".join(re.escape(k) for k in sorted_keys)

        ref_regex = re.compile(
            rf"({pattern})"
            r"\.?\s+"
            r"(\d+)"
            r"(?::(\d+)(?:\s*[-\u2013]\s*(\d+))?)?"
            , re.IGNORECASE
        )

        detected = []
        for m in ref_regex.finditer(question):
            book_key = m.group(1).lower()
            resolved = abbrevs.get(book_key)
            if not resolved:
                continue
            volume, book_slug = resolved
            detected.append({
                "volume": volume,
                "book_slug": book_slug,
                "chapter": int(m.group(2)),
                "verse_start": int(m.group(3)) if m.group(3) else None,
                "verse_end": int(m.group(4)) if m.group(4) else (int(m.group(3)) if m.group(3) else None),
            })
        return detected

    @staticmethod
    def _read_verse_text(
        volume: str, book_slug: str, chapter: int,
        verse_start: int | None, verse_end: int | None,
        lang: str = "es",
        include_footnotes: bool = False,
    ) -> tuple[str, str, str] | None:
        """Read verse text directly from corpus file.

        Returns (verse_text, reference_string, rel_path) or None.
        If include_footnotes=True, appends footnote data from .meta.json.
        """
        import json as _json
        from alejandria.ingestion.scripture_meta import format_reference, parse_verses

        if volume == "dc":
            rel_path = f"{lang}/scriptures/dc/sections/{chapter}.txt"
        else:
            rel_path = f"{lang}/scriptures/{volume}/{book_slug}/{chapter}.txt"

        file_path = settings.corpus_path / rel_path
        if not file_path.exists():
            return None

        text = file_path.read_text(encoding="utf-8")
        all_verses = parse_verses(text)
        if not all_verses:
            return None

        if verse_start is not None:
            ctx_start = max(1, verse_start - 2)
            ctx_end = (verse_end or verse_start) + 3
            context_verses = [
                (n, t) for n, t in all_verses if ctx_start <= n <= ctx_end
            ]
        else:
            context_verses = all_verses[:10]

        if not context_verses:
            return None

        verse_text = "\n".join(f"{n} {t}" for n, t in context_verses)

        # Append footnotes if requested
        if include_footnotes and verse_start is not None:
            meta_path = file_path.with_suffix(".meta.json")
            if meta_path.exists():
                try:
                    meta = _json.loads(meta_path.read_text(encoding="utf-8"))
                    footnotes = meta.get("footnotes", {})
                    # Collect footnotes for the requested verses
                    fn_lines = []
                    for v in range(verse_start, (verse_end or verse_start) + 1):
                        for suffix in "abcdefghij":
                            fn_key = f"note{v}_{suffix}"
                            if fn_key in footnotes:
                                fn_lines.append(f"  [{fn_key}] {footnotes[fn_key]}")
                    if fn_lines:
                        verse_text += "\n\nFootnotes:\n" + "\n".join(fn_lines)
                except Exception:
                    pass

        ref = format_reference(
            book_slug=book_slug if volume != "dc" else None,
            volume=volume, chapter=chapter,
            verse_start=context_verses[0][0],
            verse_end=context_verses[-1][0],
            lang=lang,
        )
        return verse_text, ref, rel_path

    def _direct_scripture_lookup(
        self, question: str,
    ) -> tuple[list[ChatSource], list[dict]]:
        """Detect scripture references in the question and fetch those verses.

        Returns (sources, detected_refs) where detected_refs can be used
        for cross-reference expansion.
        """
        detected = self._detect_scripture_refs(question)
        if not detected:
            return [], []

        sources: list[ChatSource] = []
        for ref_info in detected:
            for lang in ("es", "en"):
                result = self._read_verse_text(
                    ref_info["volume"], ref_info["book_slug"],
                    ref_info["chapter"], ref_info["verse_start"],
                    ref_info["verse_end"], lang=lang,
                    include_footnotes=True,  # include .meta.json footnotes
                )
                if result:
                    verse_text, ref_str, rel_path = result
                    auth, auth_lbl = _authority_for_path(rel_path)
                    sources.append(ChatSource(
                        text=verse_text,
                        file_path=rel_path,
                        chunk_index=0,
                        score=100.0,
                        mode="direct-lookup",
                        reference=ref_str,
                        authority=auth,
                        authority_label=auth_lbl,
                    ))
                    break  # one language per reference

        if sources:
            logger.info(
                "Direct scripture lookup: found %d references in question",
                len(sources),
            )
        return sources, detected

    def _direct_xref_lookup(self, detected_refs: list[dict]) -> list[ChatSource]:
        """Fetch official cross-referenced verses for detected scripture references.

        Instead of relying on FTS within cross-referenced chapters (which misses
        verses that don't share keywords with the question), this reads the
        actual cross-referenced verse text directly from the corpus.
        """
        import json
        from pathlib import Path

        from alejandria.ingestion.scripture_meta import format_reference, parse_verses

        # Load cross-references JSON
        xref_path = Path(__file__).resolve().parent.parent.parent / (
            "data/scripture_structure/cross_references.json"
        )
        if not xref_path.exists():
            # Try container path
            xref_path = settings.corpus_path.parent / "data" / "scripture_structure" / "cross_references.json"
        if not xref_path.exists():
            return []

        try:
            with open(xref_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return []

        # Build quick lookup: source canonical_key → list of target canonical_keys
        xref_by_source: dict[str, list[str]] = {}
        for ref in data.get("references", []):
            src = ref.get("source", "")
            tgt = ref.get("target", "")
            if src and tgt:
                xref_by_source.setdefault(src, []).append(tgt)

        sources: list[ChatSource] = []
        seen_chapters: set[str] = set()

        for ref_info in detected_refs:
            vol = ref_info["volume"]
            book = ref_info["book_slug"]
            ch = ref_info["chapter"]
            vs = ref_info["verse_start"]

            if vs is None:
                continue

            # Build canonical key to look up cross-references
            canonical = f"{vol}/{book}/{ch}:{vs}"
            targets = xref_by_source.get(canonical, [])

            if not targets:
                continue

            logger.info(
                "Direct xref lookup: %s has %d cross-references",
                canonical, len(targets),
            )

            # Read each cross-referenced verse (limit to avoid context overflow)
            for target_key in targets[:15]:
                # Parse "volume/book/chapter:verse[-end]"
                if ":" not in target_key:
                    continue

                path_part, verse_part = target_key.rsplit(":", 1)
                parts = path_part.split("/")
                if len(parts) != 3:
                    continue

                t_vol, t_book, t_ch_str = parts
                t_ch = int(t_ch_str) if t_ch_str.isdigit() else 0
                if t_ch == 0:
                    continue

                # Parse verse range
                if "-" in verse_part:
                    t_vs, t_ve = verse_part.split("-", 1)
                    t_vs, t_ve = int(t_vs), int(t_ve)
                else:
                    t_vs = int(verse_part) if verse_part.isdigit() else 0
                    t_ve = t_vs

                if t_vs == 0:  # whole-chapter ref
                    t_vs, t_ve = 1, 5

                # Deduplicate by chapter (don't read same chapter multiple times)
                ch_key = f"{t_vol}/{t_book}/{t_ch}"
                if ch_key in seen_chapters:
                    continue
                seen_chapters.add(ch_key)

                # Read the verse directly — just the specific verse, minimal context
                for lang in ("es", "en"):
                    result = self._read_verse_text(
                        t_vol, t_book, t_ch, t_vs, t_ve, lang=lang,
                    )
                    if result:
                        verse_text, ref_str, rel_path = result
                        auth, auth_lbl = _authority_for_path(rel_path)
                        sources.append(ChatSource(
                            text=verse_text,
                            file_path=rel_path,
                            chunk_index=0,
                            score=50.0,  # High but below direct-lookup
                            mode="footnote-xref",
                            reference=ref_str,
                            authority=auth,
                            authority_label=auth_lbl,
                        ))
                        break

        if sources:
            logger.info(
                "Direct xref lookup: added %d cross-referenced verse passages",
                len(sources),
            )
        return sources

    def _retrieve(
        self, question: str, fts_query: str, source_filter: str | None,
        kg_file_hints: list[str] | None = None,
        context_chunks: int | None = None,
    ) -> list[ChatSource]:
        """Retrieve chunks using hybrid search + KG hints + cross-refs + reranking."""
        from alejandria.search.hybrid import reciprocal_rank_fusion

        base_chunks = context_chunks or settings.rag_context_chunks
        # Enumeration queries need broader recall
        is_enum = self._is_enumeration_query(question)
        candidate_limit = settings.rag_search_limit * 2 if is_enum else settings.rag_search_limit
        if is_enum:
            logger.info("Enumeration query detected — doubling search limit to %d", candidate_limit)
        text_dicts: list[dict] = []
        sem_dicts: list[dict] = []

        # Run FTS and semantic search in parallel (saves 30-50ms)
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def _fts_search():
            results = []
            try:
                for r in self.textual_search.search(
                    query=fts_query, limit=candidate_limit, file_path_filter=source_filter,
                ):
                    results.append({
                        "chunk_id": r.chunk_id, "text": r.text, "score": r.score,
                        "file_path": r.file_path, "chunk_index": r.chunk_index,
                        "metadata": r.metadata if isinstance(r.metadata, dict) else {},
                        "reference": r.reference,
                    })
            except Exception:
                logger.warning("Text search failed during RAG retrieval")
            return results

        def _semantic_search():
            results = []
            if self.semantic_search is None:
                return results
            try:
                from alejandria.embeddings.model import encode_single
                query_vector = encode_single(question).tolist()
                for r in self.semantic_search.search(
                    query_vector=query_vector, limit=candidate_limit,
                    source_filter=source_filter,
                ):
                    results.append({
                        "chunk_id": r.chunk_id, "text": r.text, "score": r.score,
                        "file_path": r.file_path, "chunk_index": r.chunk_index,
                        "metadata": {}, "reference": r.reference,
                    })
            except Exception:
                logger.warning("Semantic search failed during RAG retrieval")
            return results

        with ThreadPoolExecutor(max_workers=2) as executor:
            fts_future = executor.submit(_fts_search)
            sem_future = executor.submit(_semantic_search)
            text_dicts = fts_future.result()
            sem_dicts = sem_future.result()

        # Combine via Reciprocal Rank Fusion — fetch extra for cross-ref expansion
        context_limit = base_chunks * 2 if is_enum else base_chunks
        rrf_limit = context_limit + 10  # room for cross-refs
        hybrid_results = reciprocal_rank_fusion(
            text_results=text_dicts,
            semantic_results=sem_dicts,
            text_weight=0.5,
            semantic_weight=0.5,
            limit=rrf_limit,
        )

        sources = []
        for r in hybrid_results:
            auth, auth_lbl = _extract_authority_from_result(r)
            sources.append(ChatSource(
                text=r.text,
                file_path=r.file_path,
                chunk_index=r.chunk_index,
                score=r.combined_score,
                mode="hybrid",
                reference=r.reference,
                authority=auth,
                authority_label=auth_lbl,
            ))

        # Authority-based score boost: higher authority sources get a boost
        for s in sources:
            if s.authority is not None:
                # Normalize authority (0-100) to a small boost factor (1.0-1.5)
                auth_boost = 1.0 + (s.authority / 200.0)
                s.score *= auth_boost

        # KG-boosted retrieval: boost scores for chunks from KG-relevant documents
        # instead of re-running FTS per hint (avoids N extra queries)
        if kg_file_hints:
            hint_paths = {fp for fp, _ in kg_file_hints}
            hint_labels = {fp: label for fp, label in kg_file_hints}
            boosted = 0
            for s in sources:
                if s.file_path in hint_paths:
                    s.score *= 1.5  # Boost KG-relevant chunks
                    s.mode = "hybrid+kg"
                    boosted += 1

            # For hint documents NOT already in results, do a single batch FTS
            already_covered = {s.file_path for s in sources}
            missing_hints = [(fp, label) for fp, label in kg_file_hints
                             if fp not in already_covered]
            if missing_hints:
                seen_keys = {(s.file_path, s.chunk_index) for s in sources}
                kg_sources: list[ChatSource] = []
                for hint_path, entity_label in missing_hints[:10]:  # Cap at 10 extra queries
                    try:
                        results = self.textual_search.search(
                            query=fts_query, limit=2, file_path_filter=hint_path,
                        )
                        for r in results:
                            key = (r.file_path, r.chunk_index)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                tagged_text = f"[KG: {entity_label}] {r.text}"
                                kg_sources.append(ChatSource(
                                    text=tagged_text, file_path=r.file_path,
                                    chunk_index=r.chunk_index, score=r.score * 0.001,
                                    mode="kg-boost", reference=r.reference,
                                ))
                    except Exception:
                        continue
                if kg_sources:
                    sources.extend(kg_sources)

            if boosted or missing_hints:
                logger.info("KG boost: %d existing boosted, %d new from %d hints",
                            boosted, len(sources) - len(already_covered), len(kg_file_hints))

        # Cross-reference expansion: pull in parallel scripture narratives
        sources = self._expand_cross_references(sources, fts_query, source_filter)

        # Footnote cross-reference expansion: pull in officially cross-referenced chapters
        sources = self._expand_footnote_xrefs(sources, fts_query)

        # Deduplicate by (file_path, chunk_index)
        seen: set[tuple[str, int]] = set()
        deduped: list[ChatSource] = []
        for s in sources:
            key = (s.file_path, s.chunk_index)
            if key not in seen:
                seen.add(key)
                deduped.append(s)
        sources = deduped

        # Rerank: use LLM to select the most relevant chunks
        sources = self._rerank(question, sources, max_select=context_limit)

        return sources[:context_limit]

    def _expand_cross_references(
        self,
        sources: list[ChatSource],
        fts_query: str,
        source_filter: str | None,
    ) -> list[ChatSource]:
        """Expand retrieved sources with parallel scripture narratives."""
        try:
            from alejandria.ingestion.cross_references import get_all_parallels_for_results
        except ImportError:
            return sources

        retrieved_paths = [s.file_path for s in sources]
        parallel_paths = get_all_parallels_for_results(retrieved_paths)

        if not parallel_paths:
            return sources

        logger.info(
            "Cross-reference expansion: found %d parallel paths from %d sources",
            len(parallel_paths), len(retrieved_paths),
        )

        # Search FTS within each parallel file for relevant chunks
        seen_keys = {(s.file_path, s.chunk_index) for s in sources}
        new_sources: list[ChatSource] = []

        for parallel_path in parallel_paths:
            try:
                results = self.textual_search.search(
                    query=fts_query, limit=3, file_path_filter=parallel_path,
                )
                for r in results:
                    key = (r.file_path, r.chunk_index)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        new_sources.append(ChatSource(
                            text=r.text,
                            file_path=r.file_path,
                            chunk_index=r.chunk_index,
                            score=r.score * 0.001,  # low base score, reranker decides
                            mode="cross-ref",
                            reference=r.reference,
                        ))
            except Exception:
                continue

        if new_sources:
            logger.info("Added %d chunks from parallel narratives", len(new_sources))

        return sources + new_sources

    def _expand_footnote_xrefs(
        self,
        sources: list[ChatSource],
        fts_query: str,
    ) -> list[ChatSource]:
        """Expand retrieved sources with footnote cross-referenced chapters.

        Uses the bidirectional cross-reference index built from official Church
        footnotes (~86k verse pairs). Unlike parallel narratives (same event,
        different books), these are thematic/doctrinal connections between
        specific verses across all five standard works.
        """
        try:
            from alejandria.ingestion.cross_references import get_all_xref_chapters_for_results
        except ImportError:
            return sources

        retrieved_paths = [s.file_path for s in sources]
        xref_paths = get_all_xref_chapters_for_results(
            retrieved_paths, max_per_source=3,
        )

        if not xref_paths:
            return sources

        logger.info(
            "Footnote xref expansion: found %d cross-referenced chapters from %d sources",
            len(xref_paths), len(retrieved_paths),
        )

        seen_keys = {(s.file_path, s.chunk_index) for s in sources}
        new_sources: list[ChatSource] = []

        for xref_path in xref_paths:
            try:
                results = self.textual_search.search(
                    query=fts_query, limit=2, file_path_filter=xref_path,
                )
                for r in results:
                    key = (r.file_path, r.chunk_index)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        new_sources.append(ChatSource(
                            text=r.text,
                            file_path=r.file_path,
                            chunk_index=r.chunk_index,
                            score=r.score * 0.001,
                            mode="footnote-xref",
                            reference=r.reference,
                        ))
            except Exception:
                continue

        if new_sources:
            logger.info("Added %d chunks from footnote cross-references", len(new_sources))

        return sources + new_sources

    def _rerank(self, question: str, sources: list[ChatSource], max_select: int | None = None) -> list[ChatSource]:
        """Rerank candidate sources using the LLM for relevance scoring.

        Uses the internal (cheapest) tier for reranking.
        """
        target = max_select or settings.rag_context_chunks
        if len(sources) <= target:
            return sources  # Nothing to prune

        # Skip LLM reranking if marginal gain is small (saves ~1000 tokens)
        # Just truncate by existing score order — the RRF already ranked them
        if len(sources) <= int(target * 1.5):
            logger.info("Rerank skipped (%d candidates for %d slots — marginal gain)", len(sources), target)
            return sources[:target]

        try:
            # Build a compact list of candidates for the LLM
            candidate_lines = []
            for i, s in enumerate(sources):
                label = s.reference or s.file_path
                auth_tag = f" ({s.authority_label})" if s.authority_label else ""
                excerpt = s.text[:200].replace("\n", " ")
                candidate_lines.append(f"{i}: [{label}]{auth_tag} {excerpt}")

            candidates_text = "\n".join(candidate_lines)
            target_count = target

            rerank_prompt = (
                "You are a relevance judge for a scripture study system. "
                "Given a question and a numbered list of candidate passages, "
                f"select the {target_count} MOST relevant passages that best "
                "answer the question. Consider:\n"
                "- Direct answers to the question\n"
                "- Parallel accounts of the same event from different books\n"
                "- Supporting context that enriches the answer\n"
                "- Source authority: Canon > Prophetic > Correlated > other. "
                "Prefer higher-authority sources when relevance is similar.\n\n"
                "Output ONLY a comma-separated list of the candidate numbers "
                f"(e.g., '0,3,5,1,7,2,9,4,11,6'), ordered by relevance (most relevant first). "
                "Output nothing else."
            )
            user_msg = f"QUESTION: {question}\n\nCANDIDATES:\n{candidates_text}"

            result = self._complete_internal(rerank_prompt, user_msg)
            response_text = result.text.strip()

            # Parse the indices
            indices = []
            for token in response_text.replace(" ", "").split(","):
                token = token.strip()
                if token.isdigit():
                    idx = int(token)
                    if 0 <= idx < len(sources) and idx not in indices:
                        indices.append(idx)

            if len(indices) >= target_count // 2:  # Accept if we got enough
                reranked = [sources[i] for i in indices]
                logger.info(
                    "Reranked %d -> %d sources [model=%s]",
                    len(sources), len(reranked), result.model,
                )
                return reranked
            else:
                logger.warning(
                    "Reranker returned too few indices (%d), falling back", len(indices)
                )
                return sources

        except Exception:
            logger.warning("Reranking failed, using original order")
            return sources

    # Relation types to exclude from graph context (too noisy/generic)
    _NOISE_RELATION_TYPES = frozenset({
        "CO_OCCURS_WITH", "REFERENCED_IN", "MENTIONED_IN",
        "ASSOCIATED_WITH", "RELATED_TO", "BELONGS_TO",
    })

    def _get_graph_context(self, question: str) -> str | None:
        """Extract entity info from the knowledge graph relevant to the question.

        Prioritizes structured, typed relations (curated/metadata/llm) over
        generic co-occurrence. Includes entity profiles when available.
        """
        if self.graph_client is None:
            return None

        try:
            from alejandria.knowledge.extractor import KGExtractor
            extractor = KGExtractor()
            extraction = extractor.extract(question)

            if not extraction.entities:
                return None

            # Detect question language for profile summaries
            lang = "es" if any(
                w in question.lower()
                for w in ("quién", "qué", "cuál", "cómo", "dónde", "cuándo", "cuántos", "por qué")
            ) else "en"

            parts = []
            profiled_names: set[str] = set()

            # Include entity profiles first (richer context)
            if self.profile_store is not None:
                for entity in extraction.entities:
                    try:
                        profiles = self.profile_store.find_profiles(entity.name, limit=5)
                        for profile in profiles:
                            if profile.entity_name in profiled_names:
                                continue
                            summary = profile.summary_es if lang == "es" else profile.summary_en
                            if summary:
                                profiled_names.add(profile.entity_name)
                                line = f"- {profile.entity_name} ({profile.entity_type}): {summary}"
                                if profile.aliases:
                                    line += f" [Also known as: {', '.join(profile.aliases[:5])}]"
                                parts.append(line)
                    except Exception:
                        pass

            # Add typed relations for all entities in a single batch query
            relation_parts = []
            seen_rels: set[str] = set()
            entity_names_for_rels = [e.name for e in extraction.entities]
            try:
                all_relations = self.graph_client.get_typed_relations_batch(
                    entity_names=entity_names_for_rels,
                    confidence_min="ner",  # Skip co_occurrence (lowest tier)
                )
                for rel in all_relations:
                    rel_type = rel.get("rel_type", "")
                    if rel_type in self._NOISE_RELATION_TYPES:
                        continue

                    from_name = rel.get("from_name", "?")
                    to_name = rel.get("to_name", "?")
                    key = f"{from_name}|{rel_type}|{to_name}"
                    if key in seen_rels:
                        continue
                    seen_rels.add(key)

                    # Format relation in readable way
                    props = rel.get("props") or {}
                    source_ref = props.get("source_ref", "")
                    ref_note = f" ({source_ref})" if source_ref else ""
                    readable = rel_type.replace("_", " ").title()
                    relation_parts.append(
                        f"  {from_name} --[{readable}]--> {to_name}{ref_note}"
                    )
            except Exception:
                pass

            if relation_parts:
                parts.append("Typed Relations:")
                # Limit to 25 most relevant relations
                parts.extend(relation_parts[:25])

            # Fallback: for entities with no profile and no typed relations,
            # add basic neighbor info
            entities_with_context = profiled_names | {
                r.split("|")[0] for r in seen_rels
            } | {
                r.split("|")[2] for r in seen_rels
            }
            for entity in extraction.entities:
                if entity.name in entities_with_context:
                    continue
                try:
                    result = self.graph_client.get_neighbors(
                        name=entity.name, depth=1, limit=10,
                    )
                    if result["nodes"]:
                        neighbors = ", ".join(
                            f"{n['name']}" for n in result["nodes"][:8]
                        )
                        parts.append(f"- {entity.name}: related to {neighbors}")
                except Exception:
                    pass

            if not parts:
                return None

            return "Knowledge Graph:\n" + "\n".join(parts)
        except Exception:
            logger.warning("Graph context extraction failed")
            return None

    def _get_definition_context(
        self, question: str, kg_file_hints: list[tuple[str, str]],
    ) -> str | None:
        """Look up BD/GEE definitions for concepts in the question.

        Uses entity names from KG hints (already extracted, zero additional cost).
        Returns formatted definitions block or None.
        """
        # Lazy-init: build definition index on first use
        if self.definition_lookup is None:
            try:
                self.definition_lookup = DefinitionLookup(settings.corpus_dir)
            except Exception:
                logger.debug("Could not initialize DefinitionLookup", exc_info=True)
                return None

        # Detect language
        lang = "es" if any(
            w in question.lower()
            for w in ("quien", "que", "cual", "como", "donde", "cuando", "por que")
        ) else "en"

        # Use entity names from KG hints (already extracted from gazetteer)
        entity_names = list({label for _, label in kg_file_hints}) if kg_file_hints else None

        definitions = self.definition_lookup.lookup_for_question(
            question, entities=entity_names, lang=lang,
        )

        if not definitions:
            return None

        parts = ["Doctrinal definitions (study aids):"]
        for defn in definitions:
            parts.append(f"\n- {defn.term} {defn.authority_note}:")
            parts.append(f"  {defn.text}")

        return "\n".join(parts)

    def _build_context(
        self,
        sources: list[ChatSource],
        graph_context: str | None,
        definition_context: str | None = None,
    ) -> str:
        """Assemble the context string for the LLM prompt."""
        parts = []

        if graph_context:
            parts.append(graph_context)
            parts.append("")

        if definition_context:
            parts.append(definition_context)
            parts.append("")

        if sources:
            # Lazy-init JST lookup for Bible passage pairing
            if self.jst_lookup is None:
                try:
                    self.jst_lookup = JSTLookup(settings.corpus_dir)
                except Exception:
                    pass

            parts.append("Retrieved passages:")
            for i, s in enumerate(sources, 1):
                source_label = s.reference if s.reference else f"{s.file_path} (chunk {s.chunk_index})"
                auth_tag = f", {s.authority_label}" if s.authority_label else ""
                parts.append(f"\n[{i}] Source: {source_label} ({s.mode} search{auth_tag})")
                parts.append(s.text)

                # Append JST variant if this is a Bible passage
                if self.jst_lookup and s.file_path and "/scriptures/" in s.file_path:
                    path_norm = s.file_path.replace("\\", "/")
                    if "/ot/" in path_norm or "/nt/" in path_norm:
                        jst_text = self.jst_lookup.find_jst_for_passage(s.file_path)
                        if jst_text:
                            parts.append(f"\n    [JST variant for {source_label}]:")
                            # Truncate to avoid overwhelming context
                            if len(jst_text) > 600:
                                jst_text = jst_text[:600] + "..."
                            parts.append(f"    {jst_text}")

        if not parts:
            parts.append("No relevant context found in the corpus.")

        return "\n".join(parts)

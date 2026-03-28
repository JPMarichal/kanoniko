"""RAG pipeline — retrieves context from all search modes and generates answers.

Uses tiered model selection:
- Internal calls (query expansion, reranking) use the cheapest available model
- Answer generation routes to the appropriate tier based on question complexity
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from alejandria.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are Alejandría, a bilingual (Spanish/English) research assistant specialized \
in the scriptures and gospel of The Church of Jesus Christ of Latter-day Saints.

INSTRUCTIONS:
- Answer the user's question based ONLY on the provided context passages.
- If the context is insufficient to fully answer, say so honestly and share what \
you can infer from the available passages.
- Respond in the same language the user used for their question.
- Be thorough: for biographical or chronological questions, organize information \
clearly with dates, events, and references when available.
- When the context contains information from the knowledge graph (entities and \
relationships), weave it naturally into your answer.

CITATION RULES (CRITICAL):
- ALWAYS cite sources using the scripture reference (e.g., Gálatas 5:22-23, \
1 Nephi 3:7, D&C 76:22-24). Only fall back to file paths when no reference \
is available.
- Quote scripture text LITERALLY as it appears in the context — never paraphrase \
and present it as a direct quote.
- Every scripture quote MUST include its reference in parentheses.
- Two citation styles:
  * Inline: woven into your text — Nefi dijo "Iré y haré lo que el Señor ha \
mandado" (1 Nefi 3:7).
  * Block: a full passage in its own paragraph, followed by (Reference).
- For conference talks or other materials, cite as: Author, "Title", source.
- Do not invent or hallucinate text not present in the context passages.\
"""


@dataclass
class ChatSource:
    text: str
    file_path: str
    chunk_index: int
    score: float
    mode: str  # "text", "semantic", "hybrid", or "cross-ref"
    reference: str | None = None


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
    neo4j_client: object | None = None  # Neo4jClient or None

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
        # 1. Expand query for better retrieval (uses internal/fast tier)
        fts_query = self._expand_query(question)

        # 2. KG-boosted retrieval: find entity documents before searching
        kg_file_hints = self._get_kg_file_hints(question)

        # 3. Retrieve from all available search modes + KG hints
        sources = self._retrieve(question, fts_query, source_filter, kg_file_hints)

        # 4. Build graph context if available
        graph_context = self._get_graph_context(question)

        # 4. Assemble the context prompt
        context_text = self._build_context(sources, graph_context)

        # 5. Call LLM for the answer
        user_message = f"CONTEXT:\n{context_text}\n\nQUESTION:\n{question}"
        llm_response, used_model, used_tier = self._generate_answer(
            user_message, question,
            provider_override=provider_override,
            model_override=model_override,
            tier_override=tier_override,
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

    def _generate_answer(
        self,
        user_message: str,
        question: str,
        *,
        provider_override: str | None = None,
        model_override: str | None = None,
        tier_override: str | None = None,
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
                                provider=provider, model=model, api_key=api_key)
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
                response = complete_with_model(SYSTEM_PROMPT, user_message, model_def)
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
                response = complete_with_model(SYSTEM_PROMPT, user_message, model_def)
                return response, model_def, model_def.tier.value
            except Exception as e:
                logger.warning("Model %s failed: %s — trying next", model_def.id, str(e)[:100])
                continue

        if not candidates:
            # No tiered models available — fall back to legacy settings
            logger.warning("No tiered models available, using legacy settings")
            response = complete(SYSTEM_PROMPT, user_message)
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
        """Use LLM to generate effective search keywords for FTS retrieval.

        Returns a keyword string optimized for full-text search.
        Falls back to the original question on error.
        """
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

    def _get_kg_file_hints(self, question: str) -> list[tuple[str, str]]:
        """Use LLM + KG to find documents related to entities in the question.

        Instead of relying on the gazetteer extractor (which has bias toward
        the most prominent entity match), this method:
        1. Asks the LLM to extract entity names from the question
        2. Searches the KG for ALL matching entities (not just the first)
        3. Collects documents for every match, tagged with the entity name

        Returns list of (file_path, entity_label) tuples.
        """
        if self.neo4j_client is None:
            return []

        try:
            # Step 1: LLM extracts entity names (no gazetteer bias)
            entity_names = self._extract_entities_from_question(question)
            if not entity_names:
                return []

            # Step 2: Search KG for ALL matching entities per name
            file_hints: list[tuple[str, str]] = []
            seen_files: set[str] = set()
            matched_entities: list[str] = []

            for name in entity_names:
                try:
                    matches = self.neo4j_client.find_node(search=name, limit=15)
                    for match in matches:
                        ename = match.get("name", "")
                        if ename:
                            matched_entities.append(ename)
                except Exception:
                    continue

            # Step 3: Get documents for every matched entity, tagged
            for ename in matched_entities:
                try:
                    docs = self.neo4j_client.get_documents_for_entity(ename)
                    for doc in docs:
                        fp = doc.get("file_path", "")
                        if fp and fp not in seen_files:
                            seen_files.add(fp)
                            file_hints.append((fp, ename))
                except Exception:
                    continue

            if matched_entities:
                logger.info(
                    "KG entity search: names=%s → %d entities → %d documents",
                    entity_names, len(matched_entities), len(file_hints),
                )

            return file_hints
        except Exception:
            logger.warning("KG file hint extraction failed")
            return []

    def _extract_entities_from_question(self, question: str) -> list[str]:
        """Use the LLM to extract entity names from the question.

        Unlike the gazetteer extractor, the LLM understands that "Marys" means
        "Mary", "fruits of the Spirit" is a concept, etc. No bias toward any
        particular entity — just returns the names to search for.
        """
        try:
            prompt = (
                "Extract the proper nouns, person names, place names, and key "
                "religious/doctrinal concepts from this question. Return ONLY "
                "a comma-separated list of the base entity names (singular form, "
                "no articles). If the question mentions a plural like 'Marys', "
                "return 'Mary'. If no entities found, return 'NONE'. "
                "Output nothing else."
            )
            result = self._complete_internal(prompt, question)
            text = result.text.strip()

            if not text or text.upper() == "NONE":
                return []

            names = [n.strip() for n in text.split(",") if n.strip()]
            logger.info("LLM entity extraction: '%s' → %s", question, names)
            return names
        except Exception:
            logger.warning("LLM entity extraction failed")
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

    def _retrieve(
        self, question: str, fts_query: str, source_filter: str | None,
        kg_file_hints: list[str] | None = None,
    ) -> list[ChatSource]:
        """Retrieve chunks using hybrid search + KG hints + cross-refs + reranking."""
        from alejandria.search.hybrid import reciprocal_rank_fusion

        # Enumeration queries need broader recall
        is_enum = self._is_enumeration_query(question)
        candidate_limit = settings.rag_search_limit * 2 if is_enum else settings.rag_search_limit
        if is_enum:
            logger.info("Enumeration query detected — doubling search limit to %d", candidate_limit)
        text_dicts: list[dict] = []
        sem_dicts: list[dict] = []

        # Text search (FTS) — use expanded keywords for better recall
        try:
            text_results = self.textual_search.search(
                query=fts_query, limit=candidate_limit, file_path_filter=source_filter,
            )
            for r in text_results:
                text_dicts.append({
                    "chunk_id": r.chunk_id,
                    "text": r.text,
                    "score": r.score,
                    "file_path": r.file_path,
                    "chunk_index": r.chunk_index,
                    "metadata": r.metadata if isinstance(r.metadata, dict) else {},
                    "reference": r.reference,
                })
        except Exception:
            logger.warning("Text search failed during RAG retrieval")

        # Semantic search
        if self.semantic_search is not None:
            try:
                from alejandria.embeddings.model import encode_single
                query_vector = encode_single(question).tolist()
                sem_results = self.semantic_search.search(
                    query_vector=query_vector, limit=candidate_limit,
                    source_filter=source_filter,
                )
                for r in sem_results:
                    sem_dicts.append({
                        "chunk_id": r.chunk_id,
                        "text": r.text,
                        "score": r.score,
                        "file_path": r.file_path,
                        "chunk_index": r.chunk_index,
                        "metadata": {},
                        "reference": r.reference,
                    })
            except Exception:
                logger.warning("Semantic search failed during RAG retrieval")

        # Combine via Reciprocal Rank Fusion — fetch extra for cross-ref expansion
        context_limit = settings.rag_context_chunks * 2 if is_enum else settings.rag_context_chunks
        rrf_limit = context_limit + 10  # room for cross-refs
        hybrid_results = reciprocal_rank_fusion(
            text_results=text_dicts,
            semantic_results=sem_dicts,
            text_weight=0.5,
            semantic_weight=0.5,
            limit=rrf_limit,
        )

        sources = [
            ChatSource(
                text=r.text,
                file_path=r.file_path,
                chunk_index=r.chunk_index,
                score=r.combined_score,
                mode="hybrid",
                reference=r.reference,
            )
            for r in hybrid_results
        ]

        # KG-boosted retrieval: search within documents the KG knows are relevant
        if kg_file_hints:
            seen_keys = {(s.file_path, s.chunk_index) for s in sources}
            kg_sources: list[ChatSource] = []
            for hint_path, entity_label in kg_file_hints:
                try:
                    results = self.textual_search.search(
                        query=fts_query, limit=2, file_path_filter=hint_path,
                    )
                    for r in results:
                        key = (r.file_path, r.chunk_index)
                        if key not in seen_keys:
                            seen_keys.add(key)
                            # Prepend KG entity tag so the reranker knows WHY
                            # this chunk is a candidate
                            tagged_text = f"[KG: {entity_label}] {r.text}"
                            kg_sources.append(ChatSource(
                                text=tagged_text,
                                file_path=r.file_path,
                                chunk_index=r.chunk_index,
                                score=r.score * 0.001,
                                mode="kg-boost",
                                reference=r.reference,
                            ))
                except Exception:
                    continue
            if kg_sources:
                logger.info("KG boost: added %d chunks from %d hinted documents", len(kg_sources), len(kg_file_hints))
                sources.extend(kg_sources)

        # Cross-reference expansion: pull in parallel scripture narratives
        sources = self._expand_cross_references(sources, fts_query, source_filter)

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

    def _rerank(self, question: str, sources: list[ChatSource], max_select: int | None = None) -> list[ChatSource]:
        """Rerank candidate sources using the LLM for relevance scoring.

        Uses the internal (cheapest) tier for reranking.
        """
        target = max_select or settings.rag_context_chunks
        if len(sources) <= target:
            return sources  # Nothing to prune

        try:
            # Build a compact list of candidates for the LLM
            candidate_lines = []
            for i, s in enumerate(sources):
                label = s.reference or s.file_path
                excerpt = s.text[:200].replace("\n", " ")
                candidate_lines.append(f"{i}: [{label}] {excerpt}")

            candidates_text = "\n".join(candidate_lines)
            target_count = target

            rerank_prompt = (
                "You are a relevance judge for a scripture study system. "
                "Given a question and a numbered list of candidate passages, "
                f"select the {target_count} MOST relevant passages that best "
                "answer the question. Consider:\n"
                "- Direct answers to the question\n"
                "- Parallel accounts of the same event from different books\n"
                "- Supporting context that enriches the answer\n\n"
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

    def _get_graph_context(self, question: str) -> str | None:
        """Extract entity info from the knowledge graph relevant to the question."""
        if self.neo4j_client is None:
            return None

        try:
            from alejandria.knowledge.extractor import KGExtractor
            extractor = KGExtractor()
            extraction = extractor.extract(question)

            if not extraction.entities:
                return None

            parts = []
            for entity in extraction.entities:
                # Get neighbors for each detected entity
                try:
                    result = self.neo4j_client.get_neighbors(
                        name=entity.name, depth=1, limit=20,
                    )
                    if result["nodes"]:
                        neighbors = ", ".join(
                            f"{n['name']} ({n['type']})" for n in result["nodes"]
                        )
                        parts.append(f"- {entity.name} ({entity.type}): connected to {neighbors}")

                        for e in result["edges"]:
                            src = e.get("from") or e.get("source", "?")
                            rel = e.get("type") or e.get("relation", "?")
                            tgt = e.get("to") or e.get("target", "?")
                            parts.append(f"  {src} --[{rel}]--> {tgt}")
                except Exception:
                    parts.append(f"- {entity.name} ({entity.type})")

            if not parts:
                return None

            return "Knowledge Graph:\n" + "\n".join(parts)
        except Exception:
            logger.warning("Graph context extraction failed")
            return None

    def _build_context(self, sources: list[ChatSource], graph_context: str | None) -> str:
        """Assemble the context string for the LLM prompt."""
        parts = []

        if graph_context:
            parts.append(graph_context)
            parts.append("")

        if sources:
            parts.append("Retrieved passages:")
            for i, s in enumerate(sources, 1):
                source_label = s.reference if s.reference else f"{s.file_path} (chunk {s.chunk_index})"
                parts.append(f"\n[{i}] Source: {source_label} ({s.mode} search)")
                parts.append(s.text)

        if not parts:
            parts.append("No relevant context found in the corpus.")

        return "\n".join(parts)

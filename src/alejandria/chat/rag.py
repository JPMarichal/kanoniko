"""RAG pipeline — retrieves context from all search modes and generates answers."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field

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
    mode: str  # "text", "semantic", or "hybrid"
    reference: str | None = None


@dataclass
class ChatResponse:
    answer: str
    sources: list[ChatSource]
    graph_context: str | None = None
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class RAGPipeline:
    """Retrieval-Augmented Generation pipeline combining all search modes."""

    textual_search: object  # TextualSearch
    semantic_search: object | None = None  # SemanticSearch or None
    neo4j_client: object | None = None  # Neo4jClient or None

    def ask(self, question: str, source_filter: str | None = None) -> ChatResponse:
        """Answer a question using RAG over the corpus."""
        # 1. Expand query for better retrieval
        fts_query = self._expand_query(question)

        # 2. Retrieve from all available search modes
        sources = self._retrieve(question, fts_query, source_filter)

        # 3. Build graph context if available
        graph_context = self._get_graph_context(question)

        # 4. Assemble the context prompt
        context_text = self._build_context(sources, graph_context)

        # 5. Call LLM
        from alejandria.chat.llm import complete

        user_message = f"CONTEXT:\n{context_text}\n\nQUESTION:\n{question}"
        llm_response = complete(SYSTEM_PROMPT, user_message)

        return ChatResponse(
            answer=llm_response.text,
            sources=sources,
            graph_context=graph_context,
            model=llm_response.model,
            input_tokens=llm_response.input_tokens,
            output_tokens=llm_response.output_tokens,
        )

    def _expand_query(self, question: str) -> str:
        """Use LLM to generate effective search keywords for FTS retrieval.

        Returns a keyword string optimized for full-text search.
        Falls back to the original question on error.
        """
        try:
            from alejandria.chat.llm import complete

            expansion_prompt = (
                "You are a search query optimizer for a scripture corpus (Bible, "
                "Book of Mormon, Doctrine and Covenants, Pearl of Great Price). "
                "Given a user question, output ONLY the most relevant keywords and "
                "phrases that would appear in the actual scripture text answering "
                "this question. Include key nouns, verbs, and distinctive phrases "
                "from the relevant passages. Output keywords separated by spaces, "
                "nothing else. No explanations."
            )
            result = complete(expansion_prompt, question)
            expanded = result.text.strip()
            logger.info("Query expansion: '%s' -> '%s'", question, expanded)
            return expanded if expanded else question
        except Exception:
            logger.warning("Query expansion failed, using original question")
            return question

    def _retrieve(
        self, question: str, fts_query: str, source_filter: str | None,
    ) -> list[ChatSource]:
        """Retrieve chunks using hybrid search + cross-reference expansion + reranking."""
        from alejandria.search.hybrid import reciprocal_rank_fusion

        # Fetch more candidates than needed — reranker will prune
        candidate_limit = settings.rag_search_limit
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
        rrf_limit = settings.rag_context_chunks + 10  # room for cross-refs
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
        sources = self._rerank(question, sources)

        return sources[:settings.rag_context_chunks]

    def _expand_cross_references(
        self,
        sources: list[ChatSource],
        fts_query: str,
        source_filter: str | None,
    ) -> list[ChatSource]:
        """Expand retrieved sources with parallel scripture narratives.

        If any retrieved chunk comes from a file that has known parallel accounts
        (e.g., Genesis 1 → Moses 2 + Abraham 4), fetch the best-matching chunks
        from those parallel files and add them to the source list.
        """
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

    def _rerank(self, question: str, sources: list[ChatSource]) -> list[ChatSource]:
        """Rerank candidate sources using the LLM for relevance scoring.

        Sends chunk references and short excerpts to the LLM, which returns
        an ordered list of the most relevant ones. Falls back to the original
        order on error.
        """
        if len(sources) <= settings.rag_context_chunks:
            return sources  # Nothing to prune

        try:
            from alejandria.chat.llm import complete

            # Build a compact list of candidates for the LLM
            candidate_lines = []
            for i, s in enumerate(sources):
                label = s.reference or s.file_path
                excerpt = s.text[:200].replace("\n", " ")
                candidate_lines.append(f"{i}: [{label}] {excerpt}")

            candidates_text = "\n".join(candidate_lines)
            target_count = settings.rag_context_chunks

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

            result = complete(rerank_prompt, user_msg)
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
                    "Reranked %d -> %d sources (from %d candidates)",
                    len(sources), len(reranked), len(sources),
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

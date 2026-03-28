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
- Cite your sources using the file path and chunk index, e.g. (scriptures/1-nefi-1.txt, chunk 0).
- When the context contains information from the knowledge graph (entities and \
relationships), weave it naturally into your answer.
- Respond in the same language the user used for their question.
- Be thorough: for biographical or chronological questions, organize information \
clearly with dates, events, and references when available.
- Do not invent or hallucinate information not present in the context.\
"""


@dataclass
class ChatSource:
    text: str
    file_path: str
    chunk_index: int
    score: float
    mode: str  # "text", "semantic", or "hybrid"


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
        # 1. Retrieve from all available search modes
        sources = self._retrieve(question, source_filter)

        # 2. Build graph context if available
        graph_context = self._get_graph_context(question)

        # 3. Assemble the context prompt
        context_text = self._build_context(sources, graph_context)

        # 4. Call LLM
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

    def _retrieve(self, question: str, source_filter: str | None) -> list[ChatSource]:
        """Retrieve and deduplicate chunks from text + semantic search."""
        seen: set[tuple[str, int]] = set()
        sources: list[ChatSource] = []
        limit = settings.rag_search_limit

        # Text search (FTS)
        try:
            text_results = self.textual_search.search(
                query=question, limit=limit, file_path_filter=source_filter,
            )
            for r in text_results:
                key = (r.file_path, r.chunk_index)
                if key not in seen:
                    seen.add(key)
                    sources.append(ChatSource(
                        text=r.text, file_path=r.file_path,
                        chunk_index=r.chunk_index, score=r.score, mode="text",
                    ))
        except Exception:
            logger.warning("Text search failed during RAG retrieval")

        # Semantic search
        if self.semantic_search is not None:
            try:
                from alejandria.embeddings.model import encode_single
                query_vector = encode_single(question).tolist()
                sem_results = self.semantic_search.search(
                    query_vector=query_vector, limit=limit, source_filter=source_filter,
                )
                for r in sem_results:
                    key = (r.file_path, r.chunk_index)
                    if key not in seen:
                        seen.add(key)
                        sources.append(ChatSource(
                            text=r.text, file_path=r.file_path,
                            chunk_index=r.chunk_index, score=r.score, mode="semantic",
                        ))
            except Exception:
                logger.warning("Semantic search failed during RAG retrieval")

        # Sort by score (higher is better) and take top N
        sources.sort(key=lambda s: s.score, reverse=True)
        return sources[:settings.rag_context_chunks]

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
                parts.append(f"\n[{i}] Source: {s.file_path} (chunk {s.chunk_index}, {s.mode} search)")
                parts.append(s.text)

        if not parts:
            parts.append("No relevant context found in the corpus.")

        return "\n".join(parts)

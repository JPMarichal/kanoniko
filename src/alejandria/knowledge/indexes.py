"""Create Neo4j composite indexes for KG query performance (P6 Phase 14).

Called early in rebuild_kg() to ensure indexes exist before data loading.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Index definitions: (index_name, cypher_statement)
_INDEXES = [
    # Entity indexes
    (
        "entity_name_type",
        "CREATE INDEX entity_name_type IF NOT EXISTS FOR (n:Entity) ON (n.name, n.type)",
    ),
    (
        "entity_type",
        "CREATE INDEX entity_type IF NOT EXISTS FOR (n:Entity) ON (n.type)",
    ),
    # Document indexes
    (
        "document_file_path",
        "CREATE INDEX document_file_path IF NOT EXISTS FOR (n:Document) ON (n.file_path)",
    ),
    (
        "document_source",
        "CREATE INDEX document_source IF NOT EXISTS FOR (n:Document) ON (n.source)",
    ),
    # Chapter indexes (hierarchy queries)
    (
        "chapter_volume",
        "CREATE INDEX chapter_volume IF NOT EXISTS FOR (n:Chapter) ON (n.volume_slug)",
    ),
    (
        "chapter_book",
        "CREATE INDEX chapter_book IF NOT EXISTS FOR (n:Chapter) ON (n.book_slug)",
    ),
    (
        "chapter_corpus_path",
        "CREATE INDEX chapter_corpus_path IF NOT EXISTS FOR (n:Chapter) ON (n.corpus_path)",
    ),
    # Narrative index (parallels)
    (
        "narrative_label",
        "CREATE INDEX narrative_label IF NOT EXISTS FOR (n:Narrative) ON (n.label)",
    ),
    # Full-text index for fuzzy entity search
    (
        "entity_fulltext",
        "CREATE FULLTEXT INDEX entity_fulltext IF NOT EXISTS FOR (n:Entity) ON EACH [n.name]",
    ),
]


def ensure_indexes(driver) -> dict[str, int]:
    """Create composite indexes for KG query performance.

    Returns counts dict: {created, existing}.
    """
    counts = {"created": 0, "verified": 0}

    with driver.session() as session:
        # Get existing indexes
        result = session.run("SHOW INDEXES YIELD name RETURN collect(name) AS names")
        existing = set(result.single()["names"])

        for name, cypher in _INDEXES:
            try:
                session.run(cypher)
                if name in existing:
                    counts["verified"] += 1
                else:
                    counts["created"] += 1
            except Exception:
                logger.warning("Failed to create index %s", name, exc_info=True)

    logger.info(
        "Indexes: %d created, %d verified",
        counts["created"], counts["verified"],
    )
    return counts

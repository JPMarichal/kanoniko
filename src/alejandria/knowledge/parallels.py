"""Load parallel narrative relations into Neo4j (P6 Phase 2).

Core logic extracted from scripts/load_parallels_neo4j.py for pipeline integration.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Layer classification by narrative label
_LAYER_1_LABELS = {
    "Creation", "The Fall", "Cain and Abel", "Enoch's vision and Zion",
    "The Flood / Noah", "Sermon on the Mount / Sermon at the Temple",
    "Isaiah's prophecies (Book of Mormon quotation)",
    "Isaiah 29 / Nephi's prophecy of the Book of Mormon",
    "Isaiah 48-49 / Nephi quotes Isaiah",
    "Malachi quoted by Christ to the Nephites",
}

_LAYER_2_LABELS = {
    "Birth and infancy of Jesus",
    "John the Baptist's ministry and Jesus' baptism",
    "Temptation of Jesus", "Calling of the Twelve Apostles",
    "Feeding of the five thousand", "Peter's confession / Transfiguration",
    "Triumphal entry into Jerusalem",
    "Olivet discourse (Second Coming prophecy)",
    "The Last Supper and Sacrament", "Gethsemane and arrest of Jesus",
    "Trial of Jesus", "Christ's Crucifixion and death",
    "Resurrection and post-resurrection appearances",
    "Reign of Saul", "Reign of David",
    "Reign of Solomon and the Temple", "Divided Kingdom (Judah)",
    "Warnings against false teachers (Jude / 2 Peter)",
}


def _get_layer(label: str) -> tuple[str, int]:
    if label in _LAYER_1_LABELS:
        return "PARALLEL_NARRATIVE", 1
    elif label in _LAYER_2_LABELS:
        return "EDITORIAL_PARALLEL", 2
    return "THEMATIC_LINK", 3


def load_parallels(driver) -> dict[str, int]:
    """Load parallel narratives into Neo4j using an existing driver.

    Returns counts dict: {narratives, relations}.
    """
    from alejandria.ingestion.cross_references import PARALLEL_NARRATIVES

    counts = {"narratives": 0, "relations": 0}

    with driver.session() as session:
        session.run(
            "CREATE CONSTRAINT narrative_unique IF NOT EXISTS "
            "FOR (n:Narrative) REQUIRE n.label IS UNIQUE"
        )

        for narr in PARALLEL_NARRATIVES:
            label = narr["label"]
            rel_type, layer = _get_layer(label)

            session.run(
                "MERGE (n:Narrative {label: $label}) "
                "SET n.layer = $layer, n.rel_type = $rel_type",
                label=label, layer=layer, rel_type=rel_type,
            )
            counts["narratives"] += 1

            all_chapter_keys = []
            for account in narr["accounts"]:
                all_chapter_keys.extend(
                    f"{account['volume']}/{account['book']}/{ch}"
                    for ch in account["chapters"]
                )

            for ch_key in all_chapter_keys:
                for lang in ("en", "es"):
                    fp = f"{lang}/scriptures/{ch_key}.txt"
                    session.run(
                        "MATCH (d:Document {file_path: $fp}) "
                        "MATCH (n:Narrative {label: $label}) "
                        "MERGE (d)-[:HAS_PARALLEL_IN]->(n)",
                        fp=fp, label=label,
                    )

            for i, ch1 in enumerate(all_chapter_keys):
                for ch2 in all_chapter_keys[i + 1:]:
                    if ch1 == ch2:
                        continue
                    for lang in ("en", "es"):
                        fp1 = f"{lang}/scriptures/{ch1}.txt"
                        fp2 = f"{lang}/scriptures/{ch2}.txt"
                        session.run(
                            f"MATCH (d1:Document {{file_path: $fp1}}) "
                            f"MATCH (d2:Document {{file_path: $fp2}}) "
                            f"MERGE (d1)-[r:{rel_type}]->(d2) "
                            "SET r.narrative = $label, r.layer = $layer, "
                            "    r.confidence = 'curated', r.source = 'parallel_narratives'",
                            fp1=fp1, fp2=fp2, label=label, layer=layer,
                        )
                        counts["relations"] += 1

    logger.info(
        "Parallels loaded: %d narratives, %d relations",
        counts["narratives"], counts["relations"],
    )
    return counts

#!/usr/bin/env python3
"""P6 Phase 2 -- Load parallel narrative relations into Neo4j.

Reads PARALLEL_NARRATIVES from cross_references.py and creates:
  - Narrative nodes (label, layer type)
  - PARALLEL_ACCOUNT relations linking Document nodes to Narrative nodes
  - PARALLEL_TO relations between Document nodes in the same narrative

Three relation types based on the layer:
  - PARALLEL_NARRATIVE (Layer 1): Same event, different books
  - EDITORIAL_PARALLEL (Layer 2): Same period, different editorial purpose
  - THEMATIC_LINK (Layer 3): Doctrinal themes across volumes

Usage:
  python scripts/load_parallels_neo4j.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# Layer boundaries in PARALLEL_NARRATIVES (indexed by label)
# These determine which relation type to use
LAYER_1_LABELS = {
    "Creation", "The Fall", "Cain and Abel", "Enoch's vision and Zion",
    "The Flood / Noah", "Sermon on the Mount / Sermon at the Temple",
    "Isaiah's prophecies (Book of Mormon quotation)",
    "Isaiah 29 / Nephi's prophecy of the Book of Mormon",
    "Isaiah 48-49 / Nephi quotes Isaiah",
    "Malachi quoted by Christ to the Nephites",
}

LAYER_2_LABELS = {
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

# Layer 3 = everything else (thematic)


def get_layer(label: str) -> tuple[str, int]:
    """Return (relation_type, layer_number) for a narrative label."""
    if label in LAYER_1_LABELS:
        return "PARALLEL_NARRATIVE", 1
    elif label in LAYER_2_LABELS:
        return "EDITORIAL_PARALLEL", 2
    else:
        return "THEMATIC_LINK", 3


def account_to_chapter_keys(account: dict) -> list[str]:
    """Convert an account dict to chapter key strings like 'ot/genesis/1'."""
    return [
        f"{account['volume']}/{account['book']}/{ch}"
        for ch in account["chapters"]
    ]


def dry_run_report(narratives: list[dict]) -> None:
    """Print what would be loaded."""
    total_narratives = len(narratives)
    total_pairs = 0
    by_layer = {1: 0, 2: 0, 3: 0}

    for narr in narratives:
        label = narr["label"]
        _rel_type, layer = get_layer(label)
        by_layer[layer] += 1

        # Count chapter pairs within this narrative
        all_chapters = []
        for account in narr["accounts"]:
            all_chapters.extend(account_to_chapter_keys(account))
        n = len(all_chapters)
        pairs = n * (n - 1) // 2  # combinations
        total_pairs += pairs

        print(f"  [{layer}] {label}: {n} chapters, {pairs} pairs")

    print(f"\n  Layer 1 (PARALLEL_NARRATIVE): {by_layer[1]} narratives")
    print(f"  Layer 2 (EDITORIAL_PARALLEL): {by_layer[2]} narratives")
    print(f"  Layer 3 (THEMATIC_LINK): {by_layer[3]} narratives")
    print(f"  Total: {total_narratives} narratives, {total_pairs} chapter pairs")


def load_to_neo4j(narratives: list[dict], uri: str, user: str, password: str) -> dict:
    """Load parallel narratives into Neo4j."""
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user, password))
    counts = {"narratives": 0, "relations": 0}

    with driver.session() as session:
        # Ensure Narrative constraint
        session.run(
            "CREATE CONSTRAINT narrative_unique IF NOT EXISTS "
            "FOR (n:Narrative) REQUIRE n.label IS UNIQUE"
        )

        for narr in narratives:
            label = narr["label"]
            rel_type, layer = get_layer(label)

            # Create Narrative node
            session.run(
                "MERGE (n:Narrative {label: $label}) "
                "SET n.layer = $layer, n.rel_type = $rel_type",
                label=label, layer=layer, rel_type=rel_type,
            )
            counts["narratives"] += 1

            # Collect all chapter keys across accounts
            all_chapter_keys = []
            for account in narr["accounts"]:
                all_chapter_keys.extend(account_to_chapter_keys(account))

            # Link Documents to Narrative via HAS_PARALLEL_IN
            for ch_key in all_chapter_keys:
                for lang in ("en", "es"):
                    file_path = f"{lang}/scriptures/{ch_key}.txt"
                    session.run(
                        "MATCH (d:Document {file_path: $fp}) "
                        "MATCH (n:Narrative {label: $label}) "
                        "MERGE (d)-[:HAS_PARALLEL_IN]->(n)",
                        fp=file_path, label=label,
                    )

            # Create direct PARALLEL_TO between chapters (same narrative)
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

    driver.close()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Load parallel narratives into Neo4j")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="alejandria")
    args = parser.parse_args()

    # Import narratives
    from alejandria.ingestion.cross_references import PARALLEL_NARRATIVES

    if args.dry_run:
        print(f"\n=== DRY RUN: Parallel Narratives ===\n")
        dry_run_report(PARALLEL_NARRATIVES)
        return

    logger.info("Loading %d parallel narratives into Neo4j...", len(PARALLEL_NARRATIVES))
    counts = load_to_neo4j(PARALLEL_NARRATIVES, args.uri, args.user, args.password)

    print(f"\n=== Parallel Narratives Loaded ===")
    print(f"  Narrative nodes: {counts['narratives']}")
    print(f"  PARALLEL_TO relations: {counts['relations']}")


if __name__ == "__main__":
    main()

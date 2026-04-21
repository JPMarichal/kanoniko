#!/usr/bin/env python3
"""Load curated relations from gazetteers/relations.json into Neo4j.

Usage:
    python scripts/load_curated_relations.py [--migrate] [--dry-run]

Options:
    --migrate   Also migrate existing untyped relations to co_occurrence confidence
    --dry-run   Print what would be loaded without actually loading
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

RELATIONS_PATH = Path(__file__).resolve().parent.parent / "src" / "alejandria" / "knowledge" / "gazetteers" / "relations.json"


def dry_run(relations_path: Path) -> None:
    """Print summary of what would be loaded."""
    with open(relations_path, encoding="utf-8") as f:
        data = json.load(f)

    total = 0
    for rel_type, relations in data.items():
        count = len(relations)
        bidir = sum(1 for r in relations if r.get("bidirectional"))
        total += count
        print(f"  {rel_type}: {count} relations ({bidir} bidirectional -> {count + bidir} edges)")

    print(f"\n  Total: {total} relations -> {total + sum(sum(1 for r in rels if r.get('bidirectional')) for rels in data.values())} edges in graph")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load curated relations into Neo4j")
    parser.add_argument("--migrate", action="store_true", help="Migrate existing untyped relations")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be loaded")
    parser.add_argument("--relations-file", type=Path, default=RELATIONS_PATH, help="Path to relations JSON")
    args = parser.parse_args()

    if not args.relations_file.exists():
        logger.error("Relations file not found: %s", args.relations_file)
        sys.exit(1)

    if args.dry_run:
        print(f"\n=== DRY RUN: Relations from {args.relations_file.name} ===\n")
        dry_run(args.relations_file)
        return

    # Import Neo4j client only when actually connecting (not for dry-run)
    from alejandria.knowledge.curated_seed_loader import CuratedSeedLoader
    from alejandria.knowledge.neo4j_client import Neo4jClient

    logger.info("Connecting to Neo4j...")
    client = Neo4jClient()

    try:
        # Optionally migrate existing untyped relations first
        if args.migrate:
            logger.info("Migrating existing untyped relations...")
            migration_counts = client.migrate_untyped_relations()
            if migration_counts:
                for rel_type, count in migration_counts.items():
                    logger.info("  %s: %d relations -> co_occurrence", rel_type, count)
            else:
                logger.info("  No untyped relations to migrate")

        # Load curated relations
        logger.info("Loading curated relations from %s...", args.relations_file.name)
        counts = CuratedSeedLoader(client).load(args.relations_file)

        # Print summary
        print(f"\n=== Curated Relations Loaded ===\n")
        total = 0
        for rel_type, count in counts.items():
            print(f"  {rel_type}: {count}")
            total += count
        print(f"\n  Total: {total} relation types loaded")
        print(f"  Total relations: {sum(counts.values())}")

        # Verify by querying graph summary
        summary = client.graph_summary()
        print(f"\n=== Graph Summary ===")
        print(f"  Total nodes: {summary['total_nodes']}")
        print(f"  Total relationships: {summary['total_relationships']}")
        print(f"\n  Relationships by type:")
        for rel_stat in summary["relationships_by_type"]:
            print(f"    {rel_stat['type']}: {rel_stat['count']}")

    finally:
        client.close()


if __name__ == "__main__":
    main()

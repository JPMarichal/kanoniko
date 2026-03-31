#!/usr/bin/env python3
"""P6 Phase 3 -- LLM-powered relation extraction from scripture passages.

Selects entity-rich passages from the FTS index, sends them to an LLM
with structured prompts, and stores extracted typed relations in Neo4j.

Usage:
  python scripts/extract_relations_llm.py [--dry-run] [--max-passages 50] [--tier fast]
  python scripts/extract_relations_llm.py --volumes ot nt --min-entities 4
  python scripts/extract_relations_llm.py --dry-run --max-passages 10  # preview cost
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM relation extraction from scripture passages")
    parser.add_argument("--dry-run", action="store_true", help="Extract but don't load to Neo4j")
    parser.add_argument("--max-passages", type=int, default=50, help="Max passages to process")
    parser.add_argument("--min-entities", type=int, default=3, help="Min entities per passage")
    parser.add_argument("--tier", default="fast", choices=["fast", "balanced", "quality"],
                        help="LLM tier to use")
    parser.add_argument("--volumes", nargs="+", default=None,
                        help="Filter to specific volumes (e.g., ot nt bom dc pgp)")
    parser.add_argument("--show-sample", action="store_true",
                        help="Show sample batches without calling LLM")
    args = parser.parse_args()

    from alejandria.knowledge.relation_extractor_llm import (
        LLMRelationExtractor,
        build_batches_from_index,
    )

    # Build batches
    logger.info("Building extraction batches...")
    batches = build_batches_from_index(
        max_passages=args.max_passages,
        min_entities=args.min_entities,
        volumes=args.volumes,
    )

    if not batches:
        print("No passages found matching criteria.")
        return

    print(f"\n=== LLM Relation Extraction ===")
    print(f"  Passages: {len(batches)}")
    print(f"  Tier: {args.tier}")
    print(f"  Volumes: {args.volumes or 'all'}")
    print(f"  Min entities: {args.min_entities}")

    if args.show_sample:
        print(f"\n--- Sample Batches (first 5) ---")
        for b in batches[:5]:
            print(f"\n  {b.reference} ({len(b.entities)} entities)")
            print(f"    File: {b.file_path}")
            print(f"    Entities: {', '.join(e['name'] for e in b.entities[:10])}")
            print(f"    Text: {b.text[:150]}...")
        return

    # Estimate cost
    avg_input_tokens = 800  # ~passage + entities + prompt
    avg_output_tokens = 200  # ~JSON response
    from alejandria.chat.models import Tier as TierEnum, select_model, estimate_cost
    model = select_model(TierEnum(args.tier))
    if model:
        est_cost = estimate_cost(model, avg_input_tokens * len(batches), avg_output_tokens * len(batches))
        print(f"  Model: {model.id} (${model.cost_input}/${model.cost_output} per 1M tokens)")
        print(f"  Estimated cost: ~${est_cost:.3f}")
    else:
        print("  WARNING: No LLM model available for this tier!")
        return

    # Connect to Neo4j if not dry-run
    neo4j_client = None
    if not args.dry_run:
        from alejandria.knowledge.neo4j_client import Neo4jClient
        logger.info("Connecting to Neo4j...")
        neo4j_client = Neo4jClient()

    # Run extraction
    extractor = LLMRelationExtractor(tier=args.tier)
    stats, relations = extractor.extract_batch(
        batches=batches,
        neo4j_client=neo4j_client,
        dry_run=args.dry_run,
    )

    # Print results
    print(f"\n=== Results ===")
    print(f"  Passages processed: {stats.passages_processed}")
    print(f"  Relations extracted: {stats.relations_extracted}")
    print(f"  Relations loaded: {stats.relations_loaded}")
    print(f"  Duplicates skipped: {stats.duplicates_skipped}")
    print(f"  Errors: {stats.errors}")
    print(f"  Input tokens: {stats.input_tokens:,}")
    print(f"  Output tokens: {stats.output_tokens:,}")
    print(f"  Elapsed: {stats.elapsed_seconds}s")

    if model:
        actual_cost = estimate_cost(model, stats.input_tokens, stats.output_tokens)
        print(f"  Actual cost: ~${actual_cost:.4f}")

    # Show relation type breakdown
    if relations:
        by_type: dict[str, int] = {}
        by_confidence: dict[str, int] = {}
        for r in relations:
            by_type[r.rel_type] = by_type.get(r.rel_type, 0) + 1
            by_confidence[r.confidence] = by_confidence.get(r.confidence, 0) + 1

        print(f"\n  Relations by type:")
        for rt, cnt in sorted(by_type.items(), key=lambda x: -x[1]):
            print(f"    {rt}: {cnt}")

        print(f"\n  Relations by confidence:")
        for conf, cnt in sorted(by_confidence.items()):
            print(f"    {conf}: {cnt}")

        if args.dry_run:
            print(f"\n--- Sample Relations (first 20) ---")
            for r in relations[:20]:
                print(f"  {r.from_name} --{r.rel_type}--> {r.to_name} [{r.confidence}] ({r.source_ref})")

    if neo4j_client:
        neo4j_client.close()


if __name__ == "__main__":
    main()

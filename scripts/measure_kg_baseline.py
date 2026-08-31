"""Phase 0: Baseline measurement for PPR implementation."""
import os
import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

from alejandria.storage.postgres.connection import get_connection

def measure_kg():
    results = {}
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Size
            cur.execute("SELECT count(*) FROM entities")
            results["entities_total"] = cur.fetchone()[0]

            cur.execute("SELECT count(*) FROM relations")
            results["relations_total"] = cur.fetchone()[0]

            cur.execute("SELECT count(DISTINCT rel_type) FROM relations")
            results["relation_types"] = cur.fetchone()[0]

            # Degree stats
            cur.execute("""
                SELECT avg(degree), max(degree), min(degree)
                FROM (SELECT count(*) as degree FROM relations GROUP BY src_id) t
            """)
            row = cur.fetchone()
            results["avg_degree"] = round(float(row[0]), 2) if row[0] else 0
            results["max_degree"] = row[1]
            results["min_degree"] = row[2]

            # Entities with aliases
            cur.execute("SELECT count(*) FROM entity_aliases")
            results["aliases_total"] = cur.fetchone()[0]

            # Confidence distribution
            cur.execute("""
                SELECT confidence, count(*) FROM relations
                GROUP BY confidence ORDER BY confidence
            """)
            results["confidence_dist"] = {r[0]: r[1] for r in cur.fetchall()}

            # Top relation types
            cur.execute("""
                SELECT rel_type, count(*) FROM relations
                GROUP BY rel_type ORDER BY count(*) DESC LIMIT 10
            """)
            results["top_relation_types"] = [{"type": r[0], "count": r[1]} for r in cur.fetchall()]

            # Chunks
            cur.execute("SELECT count(*) FROM chunks")
            results["chunks_total"] = cur.fetchone()[0]

            # Documents
            cur.execute("SELECT count(*) FROM document_registry")
            results["documents_total"] = cur.fetchone()[0]

    return results


def measure_ppr_feasibility():
    """Quick check: can we load the full graph in memory?"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT src_id, dst_id FROM relations LIMIT 5")
            sample = cur.fetchall()
            return {
                "sample_edges": [(int(r[0]), int(r[1])) for r in sample],
                "feasible_for_memory": True,  # Will be refined after size check
            }


if __name__ == "__main__":
    print("=== Phase 0: KG Baseline Measurement ===")
    print()

    try:
        size = measure_kg()
        print("KG Size:")
        print(f"  Entities: {size.get('entities_total', 'N/A')}")
        print(f"  Relations: {size.get('relations_total', 'N/A')}")
        print(f"  Relation types: {size.get('relation_types', 'N/A')}")
        print(f"  Chunks: {size.get('chunks_total', 'N/A')}")
        print(f"  Documents: {size.get('documents_total', 'N/A')}")
        print(f"  Aliases: {size.get('aliases_total', 'N/A')}")
        print()
        print("Graph Density:")
        print(f"  Avg degree: {size.get('avg_degree', 'N/A')}")
        print(f"  Max degree: {size.get('max_degree', 'N/A')}")
        print(f"  Min degree: {size.get('min_degree', 'N/A')}")
        print()
        print("Confidence distribution:")
        for conf, cnt in size.get("confidence_dist", {}).items():
            print(f"  {conf}: {cnt}")
        print()
        print("Top relation types:")
        for rt in size.get("top_relation_types", []):
            print(f"  {rt['type']}: {rt['count']}")
        print()

        # Feasibility
        feas = measure_ppr_feasibility()
        print(f"Sample edges: {feas['sample_edges']}")
        print()

        # Decision
        nodes = size.get("entities_total", 0)
        edges = size.get("relations_total", 0)
        avg_deg = size.get("avg_degree", 0)

        if nodes < 500_000 and edges < 2_000_000:
            print(f"DECISION: In-memory NetworkX is FEASIBLE ({nodes} nodes, {edges} edges)")
        else:
            print(f"DECISION: In-memory NetworkX may be too large ({nodes} nodes, {edges} edges)")
            print("  Consider CTE recursiva en Postgres for Phase 2")

        if avg_deg >= 2:
            print(f"Graph density is ADEQUATE for PPR (avg degree = {avg_deg})")
        else:
            print(f"WARNING: Graph may be too sparse for PPR (avg degree = {avg_deg})")
            print("  Consider adding co-occurrence edges")

        # Save results
        output = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "size": size,
            "feasibility": feas,
            "decision": {
                "in_memory_feasible": nodes < 500_000 and edges < 2_000_000,
                "density_adequate": avg_deg >= 2,
            }
        }
        out_path = Path(__file__).parent.parent / "docs/architecture-proposals/ppr-baseline-metrics.json"
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nBaseline saved to {out_path}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

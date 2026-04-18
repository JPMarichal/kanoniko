"""Side-by-side comparison of two oracle captures (Neo4j vs Postgres).

Usage::

    python -m tests.parity.compare_oracles \
      --left tests/parity/oracle_neo4j.json \
      --right tests/parity/oracle_postgres.json

Produces a parity report: for each query, summary of how close the two
backends answer. Lightweight — intended as sanity gate, not full validation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--yaml", type=Path, default=Path("tests/parity/golden_queries.yaml"))
    args = parser.parse_args(argv)

    left = _load(args.left)
    right = _load(args.right)

    try:
        import yaml
        spec = yaml.safe_load(args.yaml.read_text(encoding="utf-8"))
        queries = {q["id"]: q for q in spec.get("queries", [])}
    except Exception:
        queries = {}

    print("=" * 78)
    print(f"PARITY REPORT  {args.left.name}  vs  {args.right.name}")
    print("=" * 78)

    common = sorted(set(left["results"]) & set(right["results"]))
    summary = {"ok": 0, "diverge": 0, "error": 0}

    for qid in common:
        l = left["results"][qid]
        r = right["results"][qid]
        q = queries.get(qid, {})
        method = q.get("method", l.get("method", "?"))
        qargs = q.get("args", l.get("args", {}))

        print(f"\n[{qid}] {method}({qargs})")
        print(f"  left : {l.get('elapsed_ms', 'skip')} ms  |  right: {r.get('elapsed_ms', 'skip')} ms")

        l_err = l.get("error")
        r_err = r.get("error")
        if l_err or r_err:
            print(f"  ERROR left={l_err} right={r_err}")
            summary["error"] += 1
            continue

        l_result = l.get("result")
        r_result = r.get("result")

        verdict = "ok"

        if method == "find_node":
            l_names = [x.get("name", "?") for x in (l_result or [])[:5]]
            r_names = [x.get("name", "?") for x in (r_result or [])[:5]]
            overlap = set(l_names) & set(r_names)
            print(f"  left top5 : {l_names}")
            print(f"  right top5: {r_names}")
            jaccard = len(overlap) / len(set(l_names) | set(r_names)) if (l_names or r_names) else 1
            if len(overlap) >= 1 or (not l_names and not r_names):
                print(f"  overlap: {len(overlap)}/5  jaccard: {jaccard:.2f}  -> OK")
            else:
                print(f"  overlap: {len(overlap)}/5  jaccard: {jaccard:.2f}  -> DIVERGE")
                verdict = "diverge"

        elif method == "get_neighbors":
            l_nodes = {x["name"] for x in (l_result or {}).get("nodes", [])}
            r_nodes = {x["name"] for x in (r_result or {}).get("nodes", [])}
            overlap = l_nodes & r_nodes
            union = l_nodes | r_nodes
            jaccard = len(overlap) / len(union) if union else 1
            print(f"  left |nodes|={len(l_nodes)}  right |nodes|={len(r_nodes)}  overlap={len(overlap)}  jaccard={jaccard:.2f}")
            if jaccard >= 0.3 or not union:
                print("  -> OK (reasonable overlap)")
            else:
                print("  -> DIVERGE")
                l_only = sorted(l_nodes - r_nodes)[:5]
                r_only = sorted(r_nodes - l_nodes)[:5]
                print(f"    left only : {l_only}")
                print(f"    right only: {r_only}")
                verdict = "diverge"

        elif method == "graph_summary":
            le = (l_result or {}).get("total_nodes", 0)
            re_ = (r_result or {}).get("total_nodes", 0)
            lr = (l_result or {}).get("total_relationships", 0)
            rr = (r_result or {}).get("total_relationships", 0)
            print(f"  left : entities={le:,} relations={lr:,}")
            print(f"  right: entities={re_:,} relations={rr:,}")
            e_ratio = min(le, re_) / max(le, re_) if max(le, re_) else 1
            r_ratio = min(lr, rr) / max(lr, rr) if max(lr, rr) else 1
            print(f"  entity ratio: {e_ratio:.2f}  relation ratio: {r_ratio:.2f}")
            # Postgres post R0+R7 has fewer than Neo4j by design.
            # Accept any ratio >= 0.2 (both in same order of magnitude).
            if e_ratio >= 0.2 and r_ratio >= 0.2:
                print("  -> OK (counts coherent with cleanup history)")
            else:
                print("  -> DIVERGE")
                verdict = "diverge"

        else:
            print(f"  (no comparator registered for method {method})")

        summary[verdict] += 1

    print()
    print("=" * 78)
    print(f"SUMMARY  ok={summary['ok']}  diverge={summary['diverge']}  error={summary['error']}")
    print("=" * 78)
    return 0 if summary["diverge"] == 0 and summary["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

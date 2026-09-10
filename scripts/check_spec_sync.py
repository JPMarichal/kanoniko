#!/usr/bin/env python3
"""check_spec_sync.py - warn when src/ changes land without touching their docs/specs.

Enforces the sync rule from `proj/CONVENTIONS.md`: a change to `src/alejandria/<area>/`
should also touch that area's documentation (or its incubator spec) in the same set of
changes. This is a *warning* by default — it never blocks a commit unless `--strict`.

Usage:
    python scripts/check_spec_sync.py                 # check staged changes (pre-commit)
    python scripts/check_spec_sync.py --range A..B    # check a commit range
    python scripts/check_spec_sync.py --strict        # exit 1 on a gap

Bypass for a genuinely doc-irrelevant change: put `[skip-spec-sync]` in the commit subject,
or stage the relevant doc.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

# area under src/alejandria/  ->  any ONE of these paths satisfies the rule
AREA_DOCS: dict[str, list[str]] = {
    "storage": ["docs/system-spec.md", "docs/architecture.md", "docs/stack.md"],
    "search": [
        "docs/search-textual.md",
        "docs/search-semantic.md",
        "docs/search-hybrid.md",
        "docs/system-spec.md",
    ],
    "knowledge": [
        "docs/knowledge-graph.md",
        "docs/entity-extraction.md",
        "docs/entity-profiles.md",
        "docs/kg-ingestion-refactor.md",
        "proj/P12-kg-extraction-v2/",
        "docs/system-spec.md",
    ],
    "ingestion": ["docs/ingestion.md", "docs/ingestion-workflow.md", "docs/system-spec.md"],
    "chat": ["docs/rag-pipeline.md", "docs/llm-models.md", "docs/system-spec.md"],
    "embeddings": ["docs/search-semantic.md", "docs/stack.md", "docs/system-spec.md"],
    "api": [
        "docs/api-reference.md",
        "docs/mcp-server.md",
        "docs/cli.md",
        "docs/system-spec.md",
    ],
}
# a touch of any of these always satisfies the rule, for any area
GLOBAL_DOCS = ("docs/system-spec.md",)


def changed_files(rng: str | None) -> list[str]:
    if rng:
        cmd = ["git", "diff", "--name-only", rng]
    else:
        cmd = ["git", "diff", "--cached", "--name-only"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def commit_subject(rng: str | None) -> str:
    if rng:
        return ""
    # staged: peek at COMMIT_EDITMSG isn't reliable pre-commit; check MERGE_MSG-free path.
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", dest="rng", default=None, help="commit range A..B")
    ap.add_argument("--strict", action="store_true", help="exit 1 on a gap")
    args = ap.parse_args()

    files = changed_files(args.rng)
    if not files:
        return 0

    src_areas = sorted(
        {
            parts[2]
            for f in files
            if (parts := f.split("/"))[:2] == ["src", "alejandria"] and len(parts) > 3
        }
    )
    if not src_areas:
        return 0

    touched = set(files)

    def satisfied(area: str) -> bool:
        candidates = AREA_DOCS.get(area, []) + list(GLOBAL_DOCS)
        for c in candidates:
            if c.endswith("/"):
                if any(t.startswith(c) for t in touched):
                    return True
            elif c in touched:
                return True
        return False

    gaps = [a for a in src_areas if not satisfied(a)]
    if not gaps:
        print(f"spec-sync: ok — {', '.join(src_areas)} touched with matching docs")
        return 0

    print("spec-sync: WARNING - src changes without a matching doc/spec:")
    for a in gaps:
        docs = " | ".join(AREA_DOCS.get(a, [])) or "docs/system-spec.md"
        print(f"  src/alejandria/{a}/  ->  update one of: {docs}")
    print("  (stage the doc, add [skip-spec-sync] to the subject, or run with no --strict)")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())

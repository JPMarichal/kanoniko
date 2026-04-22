#!/usr/bin/env python3
"""Reconcile ingestion backlogs against filesystem + Postgres state.

Usage::

    python scripts/reconcile_backlogs.py                  # dry-run scan
    python scripts/reconcile_backlogs.py --apply          # materialise updates
    python scripts/reconcile_backlogs.py --with-postgres  # include PG check
    python scripts/reconcile_backlogs.py --check review-file --check corpus-file

Default is dry-run: the command prints what it WOULD change and exits.
Pass ``--apply`` to write the updates back to the backlog JSON files
(the caller is responsible for committing the resulting diff).

Exit codes:
* 0 — no findings, or findings reported in dry-run mode.
* 0 — apply mode, all applicable findings materialised.
* 2 — Postgres requested with ``--with-postgres`` but unreachable.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from alejandria.backlogs.reconcile import (  # noqa: E402
    DEFAULT_CHECKS,
    Environment,
    Reconciler,
)


# Map --check names to Check instances (filter the default roster)
_CHECK_BY_NAME = {c.name: c for c in DEFAULT_CHECKS}


def _format_section(title: str, findings: list) -> str:
    if not findings:
        return ""
    lines = [f"\n=== {title} ({len(findings)}) ==="]
    for f in findings:
        lines.append(f"  {f.describe()}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true",
        help="Apply update findings to the backlog files (default: dry-run).",
    )
    parser.add_argument(
        "--with-postgres", action="store_true",
        help="Include the Postgres state check (requires SSH tunnel up).",
    )
    parser.add_argument(
        "--check", action="append", default=None,
        choices=sorted(_CHECK_BY_NAME.keys()),
        help="Run only the named check(s). Repeatable.",
    )
    parser.add_argument(
        "--repo-root", type=Path, default=_REPO_ROOT,
        help="Override the repo root (contains backlogs/, corpus/, …).",
    )
    args = parser.parse_args(argv)

    env = Environment.from_repo(args.repo_root, include_postgres=args.with_postgres)
    if args.with_postgres and env.postgres_document_registry is None:
        print(
            "ERROR: --with-postgres requested but Postgres is unreachable. "
            "Is the SSH tunnel up?",
            file=sys.stderr,
        )
        return 2

    if args.check:
        checks = [_CHECK_BY_NAME[n] for n in args.check]
    else:
        # Default: skip the postgres check unless explicitly opted in.
        checks = [
            c for c in DEFAULT_CHECKS
            if c.name != "postgres-state" or args.with_postgres
        ]
    reconciler = Reconciler(checks=checks)

    findings = reconciler.scan(env)

    updates = [f for f in findings if f.kind == "update"]
    orphans = [f for f in findings if f.kind == "orphan"]
    infos   = [f for f in findings if f.kind == "info"]

    print(f"\nReconcile scan: {len(findings)} finding(s) "
          f"({len(updates)} updates, {len(orphans)} orphans, {len(infos)} info).")
    for section in (
        _format_section("Updates (actionable)", updates),
        _format_section("Orphans (human review)", orphans),
        _format_section("Info", infos),
    ):
        if section:
            print(section)

    if args.apply:
        applied = reconciler.apply(env, findings)
        if applied:
            env.registry.save_all()
            print(f"\nApplied {len(applied)} update(s) and saved backlogs.")
        else:
            print("\nNothing to apply.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

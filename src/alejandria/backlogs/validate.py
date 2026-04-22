"""Schema validation for the four ingestion backlogs.

Thin wrapper over ``jsonschema.validate`` that:

* Locates the schema file by backlog name (``discovery`` → ``schemas/
  discovery.schema.json``).
* Aggregates all errors rather than failing on the first one — the
  pre-commit hook and the reconcile command both want a full report.
* Is usable both as a library and as a CLI (``python -m alejandria.backlogs
  .validate``).
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import jsonschema


#: Default root for the four backlogs + schemas/ subfolder.
DEFAULT_BACKLOGS_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "backlogs"

#: Canonical set of backlog names. Used for CLI --all and for schema lookup.
BACKLOG_NAMES = ("discovery", "research", "downloads", "indexing")


@dataclass(frozen=True)
class ValidationError:
    """One schema violation, with enough context for a human to fix it."""

    backlog: str
    index: int | None           # array index of the failing entry (None = root)
    path: str                   # JSON Pointer into the entry
    message: str

    def format(self) -> str:
        head = f"[{self.backlog}"
        if self.index is not None:
            head += f"#{self.index}"
        head += "]"
        if self.path:
            head += f" {self.path}"
        return f"{head}: {self.message}"


def _schema_path(root: Path, name: str) -> Path:
    return root / "schemas" / f"{name}.schema.json"


def _backlog_path(root: Path, name: str) -> Path:
    return root / f"{name}.json"


def load_schema(name: str, root: Path = DEFAULT_BACKLOGS_ROOT) -> dict[str, Any]:
    path = _schema_path(root, name)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_backlog(name: str, root: Path = DEFAULT_BACKLOGS_ROOT) -> list[dict[str, Any]]:
    path = _backlog_path(root, name)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise TypeError(f"{path}: backlog root must be a JSON array, got {type(data).__name__}")
    return data


def validate_backlog(
    name: str,
    data: list[dict[str, Any]] | None = None,
    root: Path = DEFAULT_BACKLOGS_ROOT,
) -> list[ValidationError]:
    """Validate one backlog; return a (possibly empty) list of errors.

    ``data`` can be pre-loaded; otherwise the JSON file is read from disk.
    """
    schema = load_schema(name, root)
    entries = load_backlog(name, root) if data is None else data

    validator = jsonschema.Draft202012Validator(schema)
    errors: list[ValidationError] = []

    for err in validator.iter_errors(entries):
        # err.path is a deque like [0, 'slug'] for array[0].slug
        parts = list(err.absolute_path)
        index: int | None = None
        pointer_parts: list[str] = []
        for i, p in enumerate(parts):
            if i == 0 and isinstance(p, int):
                index = p
            else:
                pointer_parts.append(str(p))
        errors.append(ValidationError(
            backlog=name,
            index=index,
            path=".".join(pointer_parts),
            message=err.message,
        ))

    # Enforce slug uniqueness inside each backlog (schema can't express this).
    slugs: dict[str, int] = {}
    for i, entry in enumerate(entries):
        if isinstance(entry, dict):
            s = entry.get("slug")
            if isinstance(s, str):
                if s in slugs:
                    errors.append(ValidationError(
                        backlog=name,
                        index=i,
                        path="slug",
                        message=f"duplicate slug '{s}' (also at index {slugs[s]})",
                    ))
                else:
                    slugs[s] = i

    return errors


def validate_all(
    names: Iterable[str] = BACKLOG_NAMES,
    root: Path = DEFAULT_BACKLOGS_ROOT,
) -> list[ValidationError]:
    """Validate every backlog in ``names`` (default: all four)."""
    all_errors: list[ValidationError] = []
    for n in names:
        all_errors.extend(validate_backlog(n, root=root))
    return all_errors


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for pre-commit + manual runs."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate ingestion backlog JSON files against their schemas.",
    )
    parser.add_argument(
        "names", nargs="*",
        help=(
            "Backlogs to validate: any of "
            f"{', '.join(BACKLOG_NAMES)}, 'all', or empty (= all)."
        ),
    )
    parser.add_argument(
        "--root", type=Path, default=DEFAULT_BACKLOGS_ROOT,
        help="Override the backlogs/ root directory.",
    )
    args = parser.parse_args(argv)

    requested = args.names or ["all"]
    allowed = set(BACKLOG_NAMES) | {"all"}
    invalid = [n for n in requested if n not in allowed]
    if invalid:
        parser.error(
            f"invalid backlog name(s) {invalid!r}; "
            f"choose from {list(BACKLOG_NAMES) + ['all']}"
        )
    names = BACKLOG_NAMES if ("all" in requested) else tuple(requested)
    errors = validate_all(names, root=args.root)

    if not errors:
        print(f"OK: {len(names)} backlog(s) pass schema + uniqueness checks.")
        return 0

    for err in errors:
        print(err.format(), file=sys.stderr)
    print(f"\nFAIL: {len(errors)} error(s) across {len(names)} backlog(s).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

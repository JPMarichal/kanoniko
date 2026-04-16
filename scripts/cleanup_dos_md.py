"""Delete Doctrines of Salvation .md entries from FTS + vectors + Neo4j + registry.

Run inside the alejandria-api container:
    docker exec alejandria-api python /app/scripts/cleanup_dos_md.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "/app/src")

from alejandria.api.dependencies import get_pipeline
from alejandria.config import settings


def main() -> None:
    corpus_root = Path(settings.corpus_path)
    dos_dir = corpus_root / "en" / "books" / "doctrines-of-salvation"

    # Collect all .md file paths (relative to corpus root)
    md_paths: list[str] = []
    for vol_dir in sorted(dos_dir.iterdir()):
        if not vol_dir.is_dir():
            continue
        for md_file in sorted(vol_dir.glob("*.md")):
            rel = md_file.relative_to(corpus_root).as_posix()
            md_paths.append(rel)

    print(f"Found {len(md_paths)} .md files to remove from index")
    if not md_paths:
        return

    pipeline = get_pipeline()
    for rel in md_paths:
        pipeline._delete_file(rel)

    print(f"\nDeleted {len(md_paths)} .md documents from FTS + vectors + Neo4j + registry")


if __name__ == "__main__":
    main()

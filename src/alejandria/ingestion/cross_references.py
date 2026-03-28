"""Cross-references between parallel scripture narratives.

Defines known parallel accounts across volumes (e.g., the Creation is narrated
in Genesis 1, Moses 2, and Abraham 4-5). Used by the RAG pipeline to expand
retrieval: when any one account is found, the system pulls in the parallel
accounts to ensure comprehensive coverage.

These are *narrative-level* parallels, not verse-level cross-references (which
the LDS scriptures have thousands of). We focus on multi-chapter parallel
accounts that a study-oriented system MUST retrieve together.
"""

from __future__ import annotations

# Each entry: a narrative label and the list of scripture file paths (relative
# to corpus root) that contain parallel accounts.  The paths use a placeholder
# ``{lang}`` so both EN and ES corpora are covered.
#
# Format: chapter ranges are expressed as lists of (volume, book_slug, chapters).
# At retrieval time, we expand these to actual file paths.

PARALLEL_NARRATIVES: list[dict] = [
    {
        "label": "Creation",
        "accounts": [
            {"volume": "ot", "book": "genesis", "chapters": [1, 2]},
            {"volume": "pgp", "book": "moses", "chapters": [2, 3]},
            {"volume": "pgp", "book": "abraham", "chapters": [4, 5]},
        ],
    },
    {
        "label": "The Fall",
        "accounts": [
            {"volume": "ot", "book": "genesis", "chapters": [3]},
            {"volume": "pgp", "book": "moses", "chapters": [4]},
        ],
    },
    {
        "label": "Sermon on the Mount / Sermon at the Temple",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [5, 6, 7]},
            {"volume": "bom", "book": "3-nephi", "chapters": [12, 13, 14]},
        ],
    },
    {
        "label": "Isaiah's prophecies (Book of Mormon quotation)",
        "accounts": [
            {"volume": "ot", "book": "isaiah", "chapters": list(range(2, 15))},
            {"volume": "bom", "book": "2-nephi", "chapters": list(range(12, 25))},
        ],
    },
    {
        "label": "Ten Commandments",
        "accounts": [
            {"volume": "ot", "book": "exodus", "chapters": [20]},
            {"volume": "ot", "book": "deuteronomy", "chapters": [5]},
            {"volume": "bom", "book": "mosiah", "chapters": [12, 13]},
        ],
    },
    {
        "label": "The Last Supper and Sacrament",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [26]},
            {"volume": "nt", "book": "mark", "chapters": [14]},
            {"volume": "nt", "book": "luke", "chapters": [22]},
            {"volume": "bom", "book": "3-nephi", "chapters": [18]},
        ],
    },
    {
        "label": "Christ's Crucifixion and Resurrection",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [27, 28]},
            {"volume": "nt", "book": "mark", "chapters": [15, 16]},
            {"volume": "nt", "book": "luke", "chapters": [23, 24]},
            {"volume": "nt", "book": "john", "chapters": [19, 20]},
        ],
    },
    {
        "label": "The First Vision",
        "accounts": [
            {"volume": "pgp", "book": "joseph-smith-history", "chapters": [1]},
        ],
    },
    {
        "label": "Priesthood restoration",
        "accounts": [
            {"volume": "dc", "book": "sections", "chapters": [13]},
            {"volume": "pgp", "book": "joseph-smith-history", "chapters": [1]},
        ],
    },
    {
        "label": "Plan of Salvation / Three Degrees of Glory",
        "accounts": [
            {"volume": "dc", "book": "sections", "chapters": [76]},
            {"volume": "dc", "book": "sections", "chapters": [131]},
            {"volume": "dc", "book": "sections", "chapters": [137]},
            {"volume": "bom", "book": "alma", "chapters": [40, 41, 42]},
        ],
    },
]


def _account_to_paths(account: dict) -> list[str]:
    """Convert one account entry to a list of relative file paths (both langs)."""
    paths = []
    for lang in ("en", "es"):
        for ch in account["chapters"]:
            paths.append(f"{lang}/scriptures/{account['volume']}/{account['book']}/{ch}.txt")
    return paths


def _build_path_index() -> dict[str, list[str]]:
    """Build a mapping from each file path to all its parallel file paths.

    Returns: {file_path: [parallel_path_1, parallel_path_2, ...]}
    Excludes the file itself from its parallels list.
    """
    index: dict[str, list[str]] = {}

    for narrative in PARALLEL_NARRATIVES:
        # Collect ALL paths across all accounts of this narrative
        all_paths: list[str] = []
        for account in narrative["accounts"]:
            all_paths.extend(_account_to_paths(account))

        # For each path, its parallels are all OTHER paths in this narrative
        for path in all_paths:
            if path not in index:
                index[path] = []
            for other in all_paths:
                if other != path and other not in index[path]:
                    index[path].append(other)

    return index


# Module-level singleton (built once on import)
_PARALLEL_INDEX: dict[str, list[str]] | None = None


def get_parallel_paths(file_path: str) -> list[str]:
    """Given a scripture file path, return paths of parallel accounts.

    Args:
        file_path: Relative corpus path like "en/scriptures/ot/genesis/1.txt"

    Returns:
        List of parallel file paths (may be empty).
    """
    global _PARALLEL_INDEX
    if _PARALLEL_INDEX is None:
        _PARALLEL_INDEX = _build_path_index()
    return _PARALLEL_INDEX.get(file_path, [])


def get_all_parallels_for_results(file_paths: list[str]) -> set[str]:
    """Given a list of retrieved file paths, return ALL parallel paths not already in the list.

    This is the main entry point for RAG expansion: after initial retrieval,
    call this with the file paths of retrieved chunks to discover parallel
    narratives that should also be searched.
    """
    existing = set(file_paths)
    parallels: set[str] = set()
    for fp in file_paths:
        for parallel in get_parallel_paths(fp):
            if parallel not in existing:
                parallels.add(parallel)
    return parallels

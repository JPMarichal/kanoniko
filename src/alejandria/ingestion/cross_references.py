"""Cross-references between parallel scripture narratives.

Defines known parallel accounts across volumes (e.g., the Creation is narrated
in Genesis 1, Moses 2, and Abraham 4-5). Used by the RAG pipeline to expand
retrieval: when any one account is found, the system pulls in the parallel
accounts to ensure comprehensive coverage.

Three layers of parallelism:

**Layer 1 — Direct narrative parallels**: Same event, different books.
  Genesis 1 ↔ Moses 2 ↔ Abraham 4 (Creation).

**Layer 2 — Editorial parallels**: Same period/ministry narrated with different
  editorial purpose. The four Gospels are the classic example; also
  Kings ↔ Chronicles ↔ Samuel for the Israelite monarchy, and Jude ↔ 2 Peter
  for apostolic warnings.

**Layer 3 — Thematic trans-volume parallels**: Doctrinal themes that recur
  across all standard works (e.g., the Ten Commandments in Exodus, Deuteronomy,
  Mosiah, and alluded to in D&C and the Sermon on the Mount). These are best
  served by the knowledge graph in the long term; only the most structurally
  explicit ones are encoded here.
"""

from __future__ import annotations

# Each entry: a narrative label and the list of scripture file paths (relative
# to corpus root) that contain parallel accounts.  The paths use a placeholder
# ``{lang}`` so both EN and ES corpora are covered.
#
# Format: chapter ranges are expressed as lists of (volume, book_slug, chapters).
# At retrieval time, we expand these to actual file paths.

PARALLEL_NARRATIVES: list[dict] = [
    # =========================================================================
    # LAYER 1 — Direct narrative parallels (same event, different books)
    # =========================================================================
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
        "label": "Cain and Abel",
        "accounts": [
            {"volume": "ot", "book": "genesis", "chapters": [4]},
            {"volume": "pgp", "book": "moses", "chapters": [5]},
        ],
    },
    {
        "label": "Enoch's vision and Zion",
        "accounts": [
            {"volume": "ot", "book": "genesis", "chapters": [5]},
            {"volume": "pgp", "book": "moses", "chapters": [6, 7]},
        ],
    },
    {
        "label": "The Flood / Noah",
        "accounts": [
            {"volume": "ot", "book": "genesis", "chapters": [6, 7, 8, 9]},
            {"volume": "pgp", "book": "moses", "chapters": [8]},
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
        "label": "Isaiah 29 / Nephi's prophecy of the Book of Mormon",
        "accounts": [
            {"volume": "ot", "book": "isaiah", "chapters": [29]},
            {"volume": "bom", "book": "2-nephi", "chapters": [27]},
        ],
    },
    {
        "label": "Isaiah 48-49 / Nephi quotes Isaiah",
        "accounts": [
            {"volume": "ot", "book": "isaiah", "chapters": [48, 49]},
            {"volume": "bom", "book": "1-nephi", "chapters": [20, 21]},
        ],
    },
    {
        "label": "Malachi quoted by Christ to the Nephites",
        "accounts": [
            {"volume": "ot", "book": "malachi", "chapters": [3, 4]},
            {"volume": "bom", "book": "3-nephi", "chapters": [24, 25]},
        ],
    },

    # =========================================================================
    # LAYER 2 — Editorial parallels (same period, different editorial purpose)
    # =========================================================================

    # --- THE FOUR GOSPELS ---
    # The ministry of Jesus narrated by four authors with different audiences
    # and editorial intent. Grouped by major narrative blocks.
    {
        "label": "Birth and infancy of Jesus",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [1, 2]},
            {"volume": "nt", "book": "luke", "chapters": [1, 2]},
        ],
    },
    {
        "label": "John the Baptist's ministry and Jesus' baptism",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [3]},
            {"volume": "nt", "book": "mark", "chapters": [1]},
            {"volume": "nt", "book": "luke", "chapters": [3]},
            {"volume": "nt", "book": "john", "chapters": [1]},
        ],
    },
    {
        "label": "Temptation of Jesus",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [4]},
            {"volume": "nt", "book": "mark", "chapters": [1]},
            {"volume": "nt", "book": "luke", "chapters": [4]},
        ],
    },
    {
        "label": "Calling of the Twelve Apostles",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [10]},
            {"volume": "nt", "book": "mark", "chapters": [3, 6]},
            {"volume": "nt", "book": "luke", "chapters": [6, 9]},
        ],
    },
    {
        "label": "Feeding of the five thousand",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [14]},
            {"volume": "nt", "book": "mark", "chapters": [6]},
            {"volume": "nt", "book": "luke", "chapters": [9]},
            {"volume": "nt", "book": "john", "chapters": [6]},
        ],
    },
    {
        "label": "Peter's confession / Transfiguration",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [16, 17]},
            {"volume": "nt", "book": "mark", "chapters": [8, 9]},
            {"volume": "nt", "book": "luke", "chapters": [9]},
        ],
    },
    {
        "label": "Triumphal entry into Jerusalem",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [21]},
            {"volume": "nt", "book": "mark", "chapters": [11]},
            {"volume": "nt", "book": "luke", "chapters": [19]},
            {"volume": "nt", "book": "john", "chapters": [12]},
        ],
    },
    {
        "label": "Olivet discourse (Second Coming prophecy)",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [24, 25]},
            {"volume": "nt", "book": "mark", "chapters": [13]},
            {"volume": "nt", "book": "luke", "chapters": [21]},
            {"volume": "pgp", "book": "joseph-smith-matthew", "chapters": [1]},
        ],
    },
    {
        "label": "The Last Supper and Sacrament",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [26]},
            {"volume": "nt", "book": "mark", "chapters": [14]},
            {"volume": "nt", "book": "luke", "chapters": [22]},
            {"volume": "nt", "book": "john", "chapters": [13, 14, 15, 16, 17]},
            {"volume": "bom", "book": "3-nephi", "chapters": [18]},
        ],
    },
    {
        "label": "Gethsemane and arrest of Jesus",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [26]},
            {"volume": "nt", "book": "mark", "chapters": [14]},
            {"volume": "nt", "book": "luke", "chapters": [22]},
            {"volume": "nt", "book": "john", "chapters": [18]},
        ],
    },
    {
        "label": "Trial of Jesus",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [26, 27]},
            {"volume": "nt", "book": "mark", "chapters": [14, 15]},
            {"volume": "nt", "book": "luke", "chapters": [22, 23]},
            {"volume": "nt", "book": "john", "chapters": [18, 19]},
        ],
    },
    {
        "label": "Christ's Crucifixion and death",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [27]},
            {"volume": "nt", "book": "mark", "chapters": [15]},
            {"volume": "nt", "book": "luke", "chapters": [23]},
            {"volume": "nt", "book": "john", "chapters": [19]},
        ],
    },
    {
        "label": "Resurrection and post-resurrection appearances",
        "accounts": [
            {"volume": "nt", "book": "matthew", "chapters": [28]},
            {"volume": "nt", "book": "mark", "chapters": [16]},
            {"volume": "nt", "book": "luke", "chapters": [24]},
            {"volume": "nt", "book": "john", "chapters": [20, 21]},
        ],
    },

    # --- OLD TESTAMENT HISTORICAL PARALLELS ---
    # Kings, Chronicles, and Samuel narrate the same Israelite monarchy
    # with different editorial emphasis.
    {
        "label": "Reign of Saul",
        "accounts": [
            {"volume": "ot", "book": "1-samuel", "chapters": list(range(9, 32))},
            {"volume": "ot", "book": "1-chronicles", "chapters": [10]},
        ],
    },
    {
        "label": "Reign of David",
        "accounts": [
            {"volume": "ot", "book": "2-samuel", "chapters": list(range(1, 25))},
            {"volume": "ot", "book": "1-chronicles", "chapters": list(range(11, 30))},
        ],
    },
    {
        "label": "Reign of Solomon and the Temple",
        "accounts": [
            {"volume": "ot", "book": "1-kings", "chapters": list(range(1, 12))},
            {"volume": "ot", "book": "2-chronicles", "chapters": list(range(1, 10))},
        ],
    },
    {
        "label": "Divided Kingdom (Judah)",
        "accounts": [
            {"volume": "ot", "book": "1-kings", "chapters": list(range(12, 23))},
            {"volume": "ot", "book": "2-kings", "chapters": list(range(1, 26))},
            {"volume": "ot", "book": "2-chronicles", "chapters": list(range(10, 37))},
        ],
    },

    # --- EPISTOLARY PARALLELS ---
    {
        "label": "Warnings against false teachers (Jude / 2 Peter)",
        "accounts": [
            {"volume": "nt", "book": "jude", "chapters": [1]},
            {"volume": "nt", "book": "2-peter", "chapters": [2]},
        ],
    },

    # =========================================================================
    # LAYER 3 — Thematic trans-volume parallels (explicit structural ones only;
    # subtler thematic links are better served by the knowledge graph)
    # =========================================================================
    {
        "label": "Ten Commandments",
        "accounts": [
            {"volume": "ot", "book": "exodus", "chapters": [20]},
            {"volume": "ot", "book": "deuteronomy", "chapters": [5]},
            {"volume": "bom", "book": "mosiah", "chapters": [12, 13]},
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
    {
        "label": "The Abrahamic Covenant",
        "accounts": [
            {"volume": "ot", "book": "genesis", "chapters": [12, 15, 17]},
            {"volume": "pgp", "book": "abraham", "chapters": [1, 2]},
            {"volume": "bom", "book": "1-nephi", "chapters": [15, 22]},
            {"volume": "bom", "book": "3-nephi", "chapters": [20]},
        ],
    },
    {
        "label": "The scattering and gathering of Israel",
        "accounts": [
            {"volume": "bom", "book": "1-nephi", "chapters": [10, 15, 22]},
            {"volume": "bom", "book": "2-nephi", "chapters": [6, 10, 25, 30]},
            {"volume": "bom", "book": "3-nephi", "chapters": [16, 20, 21]},
            {"volume": "dc", "book": "sections", "chapters": [110]},
        ],
    },
    {
        "label": "Christ's atonement — doctrinal expositions",
        "accounts": [
            {"volume": "bom", "book": "2-nephi", "chapters": [2, 9]},
            {"volume": "bom", "book": "alma", "chapters": [7, 34, 42]},
            {"volume": "bom", "book": "mosiah", "chapters": [3, 14, 15]},
            {"volume": "ot", "book": "isaiah", "chapters": [53]},
        ],
    },
    {
        "label": "Faith, repentance, and baptism",
        "accounts": [
            {"volume": "bom", "book": "2-nephi", "chapters": [31]},
            {"volume": "bom", "book": "3-nephi", "chapters": [11, 27]},
            {"volume": "bom", "book": "moroni", "chapters": [8]},
            {"volume": "dc", "book": "sections", "chapters": [20]},
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

"""JST verse pairing — surfaces JST variants alongside KJV/RV Bible passages.

When the RAG pipeline retrieves a Bible passage, this module checks if a JST
variant exists for that chapter and returns the relevant verses.

Zero LLM cost — direct file reads from the JST corpus directory.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# JST slug -> canonical Bible book slug mapping
_JST_TO_BIBLE: dict[str, str] = {
    "jst-gen": "genesis",
    "jst-ex": "exodus",
    "jst-ps": "psalms",
    "jst-isa": "isaiah",
    "jst-matt": "matthew",
    "jst-mark": "mark",
    "jst-luke": "luke",
    "jst-john": "john",
    "jst-acts": "acts",
    "jst-rom": "romans",
    "jst-1-cor": "1-corinthians",
    "jst-1-tim": "1-timothy",
    "jst-heb": "hebrews",
    "jst-james": "james",
    "jst-1-pet": "1-peter",
    "jst-1-jn": "1-john",
    "jst-rev": "revelation",
}

# Reverse: Bible book slug -> JST slug
_BIBLE_TO_JST: dict[str, str] = {v: k for k, v in _JST_TO_BIBLE.items()}

# Bible slug aliases (path variations in the corpus)
_BIBLE_SLUG_ALIASES: dict[str, str] = {
    "gen": "genesis",
    "ex": "exodus",
    "ps": "psalms",
    "isa": "isaiah",
    "matt": "matthew",
    "mk": "mark",
    "lk": "luke",
    "jn": "john",
    "rom": "romans",
    "1-cor": "1-corinthians",
    "1-tim": "1-timothy",
    "heb": "hebrews",
    "jas": "james",
    "1-pet": "1-peter",
    "1-jn": "1-john",
    "rev": "revelation",
}


class JSTLookup:
    """Look up JST variants for Bible passages."""

    def __init__(self, corpus_dir: str | Path):
        self._corpus_dir = Path(corpus_dir)
        self._jst_index: dict[str, list[str]] | None = None

    def _build_index(self) -> dict[str, list[str]]:
        """Build index: 'genesis/14' -> ['/path/to/jst-gen/14.txt']"""
        index: dict[str, list[str]] = {}

        for lang in ("en", "es"):
            jst_dir = self._corpus_dir / lang / "study-aids" / "jst-appendix"
            if not jst_dir.exists():
                continue

            for book_dir in jst_dir.iterdir():
                if not book_dir.is_dir():
                    continue
                bible_book = _JST_TO_BIBLE.get(book_dir.name)
                if not bible_book:
                    continue

                for txt_file in book_dir.glob("*.txt"):
                    chapter = txt_file.stem
                    if chapter.endswith("-meta") or not chapter.replace("-", "").isdigit():
                        continue
                    key = f"{bible_book}/{chapter}"
                    if key not in index:
                        index[key] = []
                    index[key].append(str(txt_file))

        logger.debug("JST index built: %d chapter mappings", len(index))
        return index

    @property
    def jst_index(self) -> dict[str, list[str]]:
        if self._jst_index is None:
            self._jst_index = self._build_index()
        return self._jst_index

    def find_jst_for_passage(self, file_path: str) -> str | None:
        """Given a Bible corpus file path, return JST variant text if available.

        Args:
            file_path: Corpus path like 'en/scriptures/ot/genesis/14.txt'

        Returns:
            JST variant text (verse-numbered) or None.
        """
        norm = file_path.replace("\\", "/")

        # Extract book and chapter from path
        # Expected: {lang}/scriptures/{ot|nt}/{book}/{chapter}.txt
        parts = norm.split("/")
        if len(parts) < 5:
            return None

        book_slug = parts[-2]  # e.g., "genesis"
        chapter = parts[-1].replace(".txt", "")

        # Normalize book slug
        canon_book = _BIBLE_SLUG_ALIASES.get(book_slug, book_slug)

        # Check if JST exists for this chapter
        key = f"{canon_book}/{chapter}"
        jst_files = self.jst_index.get(key)
        if not jst_files:
            return None

        # Read first matching JST file
        try:
            text = Path(jst_files[0]).read_text(encoding="utf-8").strip()
            if text:
                return text
        except OSError:
            pass

        return None

    def get_jst_verses_for_range(
        self, file_path: str, verse_start: int, verse_end: int,
    ) -> str | None:
        """Get JST verses that overlap with a specific verse range.

        Args:
            file_path: Bible corpus file path.
            verse_start: First verse number in the retrieved passage.
            verse_end: Last verse number in the retrieved passage.

        Returns:
            Matching JST verses or None.
        """
        full_text = self.find_jst_for_passage(file_path)
        if not full_text:
            return None

        # Parse verses from JST text
        matching_lines = []
        for line in full_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Extract verse number
            m = re.match(r"^(\d+)\s+", line)
            if m:
                verse_num = int(m.group(1))
                if verse_start <= verse_num <= verse_end:
                    matching_lines.append(line)

        if matching_lines:
            return "\n".join(matching_lines)
        return None

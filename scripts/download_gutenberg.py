#!/usr/bin/env python3
"""Download and split books from Project Gutenberg into corpus-ready chapters.

Fetches plain-text books via the Gutendex API, strips Gutenberg boilerplate,
splits into chapters, reflows line-wrapped paragraphs, parses footnotes, and
writes .txt + .meta.json per chapter.

Usage:
    python scripts/download_gutenberg.py --book-id 42238
    python scripts/download_gutenberg.py --book-id 42238 --dry-run
    python scripts/download_gutenberg.py --book-id 42238 35514 45149 47182 74447
    python scripts/download_gutenberg.py --list-books

Supported books (pre-configured with metadata):
    42238  The Articles of Faith — James E. Talmage
    35514  The Great Apostasy — James E. Talmage
    45149  The House of the Lord — James E. Talmage
    47182  The Vitality of Mormonism — James E. Talmage
    74447  Discourses of Brigham Young — Brigham Young (comp. Widtsoe)

Any Gutenberg book ID can be used; pre-configured books get richer metadata.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import ssl
import textwrap
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CORPUS_ROOT = Path(__file__).resolve().parent.parent / "corpus"
GUTENDEX_API = "https://gutendex.com/books/"

# ---------------------------------------------------------------------------
# Pre-configured book metadata
# ---------------------------------------------------------------------------

BOOK_CONFIGS: dict[int, dict] = {
    42238: {
        "slug": "articles-of-faith",
        "author": "James E. Talmage",
        "category": "books",
        "tags": ["doctrine", "apostle-authored", "lectures"],
        "authority": 45,
        "chapter_pattern": r"^(?:LECTURE|CHAPTER)\s+([IVXLC\d]+)\.?\s*$",
        "title_offset": 2,  # title line is 2 lines after chapter marker
        "has_toc": True,
        "note": "Originally delivered as lectures at LDS University, 1893. Published 1899. "
                "Commissioned by the First Presidency; adopted as official study text.",
    },
    35514: {
        "slug": "great-apostasy",
        "author": "James E. Talmage",
        "category": "books",
        "tags": ["doctrine", "apostle-authored", "church-history", "apostasy"],
        "authority": 45,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC\d]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Published 1909. Zion's Printing and Publishing Company. "
                "Used as missionary resource for decades.",
    },
    45149: {
        "slug": "house-of-the-lord",
        "author": "James E. Talmage",
        "category": "books",
        "tags": ["doctrine", "apostle-authored", "temples"],
        "authority": 45,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC\d]+)\.?\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Published 1912. First authorized book on LDS temples. "
                "First Presidency authorized interior photographs.",
    },
    47182: {
        "slug": "vitality-of-mormonism",
        "author": "James E. Talmage",
        "category": "books",
        "tags": ["doctrine", "apostle-authored", "essays"],
        "authority": 40,
        "chapter_pattern": r"^--\s*(\d+)\s*--\s*$",
        "title_offset": 1,
        "has_toc": False,
        "note": "104 brief essays published weekly over two years. Boston: Gorham Press.",
    },
    74447: {
        "slug": "discourses-brigham-young",
        "author": "Brigham Young",
        "category": "books",
        "tags": ["doctrine", "prophet-teachings", "journal-of-discourses"],
        "authority": 35,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\s*$",
        "title_offset": 2,
        "has_toc": True,
        "note": "Compiled by John A. Widtsoe (1941) from Journal of Discourses (1854-1886). "
                "Historical compilation, not official Church publication.",
    },
    # ----- B. H. Roberts -----
    46202: {
        "slug": "new-witness-for-god-vol1",
        "author": "B. H. Roberts",
        "category": "books",
        "tags": ["doctrine", "seventy-authored", "restoration", "apologetics"],
        "authority": 35,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 4,
        "has_toc": True,
        "note": "Volume 1 of 3. Published 1895 by George Q. Cannon & Sons. "
                "Argues the need for a new dispensation based on apostasy from primitive Christianity.",
    },
    47316: {
        "slug": "new-witnesses-for-god-vol2",
        "author": "B. H. Roberts",
        "category": "books",
        "tags": ["doctrine", "seventy-authored", "book-of-mormon", "apologetics"],
        "authority": 35,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 4,
        "has_toc": True,
        "note": "Volume 2 of 3. Published 1909 by Deseret News. "
                "The Book of Mormon as witness: discovery, translation, lands, civilizations.",
    },
    59951: {
        "slug": "new-witnesses-for-god-vol3",
        "author": "B. H. Roberts",
        "category": "books",
        "tags": ["doctrine", "seventy-authored", "book-of-mormon", "apologetics"],
        "authority": 35,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 4,
        "has_toc": True,
        "note": "Volume 3 of 3. Published 1909 by Deseret News. "
                "Evidences of the Book of Mormon and responses to objections.",
    },
    52391: {
        "slug": "outlines-ecclesiastical-history",
        "author": "B. H. Roberts",
        "category": "books",
        "tags": ["doctrine", "seventy-authored", "church-history", "apostasy", "reformation"],
        "authority": 35,
        "chapter_pattern": r"^SECTION\s+([IVXLC\d]+)\.?(?:\[\d+\])?\s*$",
        "title_offset": 4,
        "has_toc": True,
        "sequential_numbering": True,
        "note": "Third edition. Dedicated to the Seventies. Covers establishment of the Church, "
                "the apostasy, the Reformation, and the Restoration. Used as Seventy's study text.",
    },
    49526: {
        "slug": "missouri-persecutions",
        "author": "B. H. Roberts",
        "category": "books",
        "tags": ["church-history", "seventy-authored", "persecution", "missouri"],
        "authority": 35,
        "chapter_pattern": r"^CHAPTER\s+([IVXLC]+)\.?\s*$",
        "title_offset": 4,
        "has_toc": True,
        "note": "Published 1900 by George Q. Cannon & Sons. "
                "Detailed history of the Missouri period persecutions of the Latter-day Saints.",
    },
    35974: {
        "slug": "corianton",
        "author": "B. H. Roberts",
        "category": "books",
        "tags": ["fiction", "seventy-authored", "book-of-mormon", "nephite"],
        "authority": 20,
        "chapter_pattern": r"^CHAPTER\s+(ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN)\.?\s*$",
        "title_offset": 2,
        "has_toc": False,
        "note": "Historical fiction set in Book of Mormon times. Published 1902. "
                "A Nephite story exploring the Alma-Corianton narrative.",
    },
    60235: {
        "slug": "seventys-course-theology-1st",
        "author": "B. H. Roberts",
        "category": "books",
        "tags": ["doctrine", "seventy-authored", "theology", "curriculum"],
        "authority": 35,
        "chapter_pattern": r"^LESSON\s+([IVXLC]+)[\.\-]",
        "title_offset": 4,
        "has_toc": False,
        "sequential_numbering": True,
        "note": "First Year of the Seventy's Course in Theology. "
                "Compiled and edited by B. H. Roberts for the quorums of Seventy.",
    },
    60492: {
        "slug": "seventys-course-theology-5th",
        "author": "B. H. Roberts",
        "category": "books",
        "tags": ["doctrine", "seventy-authored", "theology", "curriculum", "divine-immanence"],
        "authority": 35,
        "chapter_pattern": r"^(?:LESSON|CHAPTER)\s+([IVXLC]+)\.?\s*$",
        "title_offset": 4,
        "has_toc": False,
        "note": "Fifth Year (final) of the Seventy's Course in Theology. "
                "Focuses on divine immanence, the Holy Spirit, and nature of God.",
    },
}


# ---------------------------------------------------------------------------
# Roman numeral conversion
# ---------------------------------------------------------------------------

def roman_to_int(s: str) -> int:
    """Convert a Roman numeral string to integer."""
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev = 0
    for c in reversed(s.upper()):
        v = vals.get(c, 0)
        if v < prev:
            total -= v
        else:
            total += v
        prev = v
    return total


_WORD_TO_NUM = {
    "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5,
    "SIX": 6, "SEVEN": 7, "EIGHT": 8, "NINE": 9, "TEN": 10,
    "ELEVEN": 11, "TWELVE": 12, "THIRTEEN": 13, "FOURTEEN": 14,
    "FIFTEEN": 15, "SIXTEEN": 16, "SEVENTEEN": 17, "EIGHTEEN": 18,
    "NINETEEN": 19, "TWENTY": 20,
}


def chapter_sort_key(num_str: str) -> int:
    """Convert chapter number (Roman, Arabic, or English word) to int for sorting."""
    num_str = num_str.strip()
    if num_str.isdigit():
        return int(num_str)
    word_val = _WORD_TO_NUM.get(num_str.upper())
    if word_val:
        return word_val
    return roman_to_int(num_str)


# ---------------------------------------------------------------------------
# Gutendex API
# ---------------------------------------------------------------------------

def fetch_book_metadata(book_id: int, ca_bundle: str | None = None) -> dict:
    """Fetch book metadata from Gutendex API."""
    url = f"{GUTENDEX_API}?ids={book_id}"
    ctx = ssl.create_default_context()
    if ca_bundle:
        ctx.load_verify_locations(ca_bundle)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = json.loads(resp.read())
    if not data.get("results"):
        raise ValueError(f"Book {book_id} not found on Gutenberg")
    return data["results"][0]


def fetch_book_text(book_id: int, ca_bundle: str | None = None) -> str:
    """Download the plain-text version of a Gutenberg book."""
    # Try the direct file URL first (more reliable), then the ebook URL
    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
    ]
    ctx = ssl.create_default_context()
    if ca_bundle:
        ctx.load_verify_locations(ca_bundle)

    for url in urls:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
                raw = resp.read()
                # Try UTF-8 first, fall back to latin-1
                try:
                    return raw.decode("utf-8-sig")
                except UnicodeDecodeError:
                    return raw.decode("latin-1")
        except Exception:
            continue

    raise RuntimeError(f"Could not download text for book {book_id} from any URL")


# ---------------------------------------------------------------------------
# Text processing
# ---------------------------------------------------------------------------

def strip_gutenberg_boilerplate(text: str) -> str:
    """Remove Project Gutenberg header and footer."""
    # Find start marker
    start_markers = ["*** START OF THE PROJECT GUTENBERG EBOOK",
                     "*** START OF THIS PROJECT GUTENBERG EBOOK"]
    for marker in start_markers:
        idx = text.find(marker)
        if idx >= 0:
            # Skip past the marker line
            nl = text.find("\n", idx)
            text = text[nl + 1:] if nl >= 0 else text[idx + len(marker):]
            break

    # Find end marker (multiple variants)
    end_markers = ["*** END OF THE PROJECT GUTENBERG EBOOK",
                   "*** END OF THIS PROJECT GUTENBERG EBOOK",
                   "End of the Project Gutenberg EBook",
                   "End of Project Gutenberg's",
                   "End of Project Gutenberg"]
    for marker in end_markers:
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
            break

    return text.strip()


def strip_transcriber_notes(text: str) -> str:
    """Remove transcriber/proofreader notes at the start and end of text."""
    # Start of text
    patterns = [
        r"(?i)^\s*\[?transcriber'?s?\s+note.*?\]?\s*\n(?:.*?\n)*?\n",
        r"(?i)^\s*\[?note:\s+.*?\]?\s*\n(?:.*?\n)*?\n",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, count=1)
    # End of text
    end_patterns = [
        r"(?i)\n\s*TRANSCRIBER'?S?\s+NOTE[S]?.*$",
    ]
    for pat in end_patterns:
        text = re.sub(pat, "", text, flags=re.DOTALL)
    return text


def strip_trailing_index(text: str) -> str:
    """Remove alphabetical book indices from the end of text.

    Gutenberg books often have an INDEX section at the end with entries like:
    'Aaron, 234, 236.' or 'Gospel, defined, 1-13; power of, 1'
    """
    lines = text.split("\n")

    # Search backwards for INDEX marker
    index_start = None
    for i in range(len(lines) - 1, max(0, len(lines) - 2000), -1):
        stripped = lines[i].strip()
        if stripped in ("INDEX", "INDEX.", "GENERAL INDEX", "ANALYTICAL INDEX"):
            index_start = i
            break

    if index_start is not None:
        text = "\n".join(lines[:index_start]).rstrip()

    return text


def reflow_paragraphs(text: str) -> str:
    """Re-join lines that were hard-wrapped at ~75 chars into full paragraphs.

    Preserves intentional breaks: blank lines, lines starting with special
    markers (chapters, footnotes, etc.), and short lines (poetry/lists).
    """
    lines = text.split("\n")
    result = []
    buffer = []

    def flush():
        if buffer:
            result.append(" ".join(buffer))
            buffer.clear()

    for line in lines:
        stripped = line.rstrip()

        # Blank line = paragraph break
        if not stripped:
            flush()
            result.append("")
            continue

        # Lines that start a new block (should NOT be joined to previous)
        is_new_block = (
            stripped.startswith(("CHAPTER ", "LECTURE ", "-- ", "---", "[Footnote",
                                "NOTES.", "NOTE.", "INDEX", "PREFACE", "CONTENTS",
                                "NOTES", "NOTE"))
            or re.match(r"^[IVXLC]+\.\s", stripped)
            or re.match(r"^_[A-Z]", stripped)
            or stripped.startswith(("  ", "\t"))
            or (stripped.isupper() and len(stripped) > 3)
        )

        if is_new_block:
            flush()
            result.append(stripped)
            continue

        # Continuation line: join to buffer (reflow)
        buffer.append(stripped)

    flush()

    # Collapse excessive blank lines
    text = "\n".join(result)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    # Strip single leading spaces from paragraph lines (dropped-cap artifact)
    text = re.sub(r"(?m)^ (?! )", "", text)
    return text


def parse_footnotes_inline(text: str) -> tuple[str, list[dict]]:
    """Extract [Footnote N: ...] blocks and return cleaned text + footnotes list."""
    footnotes = []

    # Multi-line footnotes: [Footnote A: ... text spanning lines ...]
    pattern = r"\[Footnote\s+([A-Za-z0-9]+):\s*(.*?)\]"
    for m in re.finditer(pattern, text, re.DOTALL):
        marker = m.group(1)
        content = re.sub(r"\s+", " ", m.group(2)).strip()
        footnotes.append({"marker": marker, "text": content})

    # Remove footnote blocks from text
    text = re.sub(r"\[Footnote\s+[A-Za-z0-9]+:\s*.*?\]", "", text, flags=re.DOTALL)

    return text.strip(), footnotes


def parse_jd_references(text: str) -> list[str]:
    """Extract Journal of Discourses references (e.g., '13:233') from text."""
    refs = re.findall(r"\b(\d{1,2}:\d{1,3})\b", text)
    return list(set(refs))


def clean_formatting(text: str) -> str:
    """Convert Gutenberg formatting markers to clean text."""
    # **bold** → bold
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    # _italic_ → italic (strip underscores used for emphasis)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    # =bold= → bold
    text = re.sub(r"=([^=]+)=", r"\1", text)
    # {N} page markers → remove
    text = re.sub(r"\{\d+\}", "", text)
    return text


# ---------------------------------------------------------------------------
# Chapter splitting
# ---------------------------------------------------------------------------

def split_into_chapters(text: str, config: dict) -> list[dict]:
    """Split text into chapters based on the configured pattern.

    Returns list of dicts: {number, title, body}
    """
    pattern = config["chapter_pattern"]
    title_offset = config.get("title_offset", 2)
    has_toc = config.get("has_toc", False)

    lines = text.split("\n")

    # Find all chapter boundary lines
    boundaries = []
    for i, line in enumerate(lines):
        m = re.match(pattern, line.strip())
        if m:
            boundaries.append((i, m.group(1)))

    if not boundaries:
        logger.warning("No chapter boundaries found with pattern: %s", pattern)
        return [{"number": "1", "title": "Full Text", "body": text}]

    # If has_toc, the chapters appear twice — TOC then body.
    # Find where the actual content starts: the second occurrence of chapter 1.
    if has_toc and len(boundaries) > 1:
        first_ch = boundaries[0][1]
        second_occurrence = None
        for idx, (line_num, ch_num) in enumerate(boundaries[1:], 1):
            if ch_num == first_ch:
                second_occurrence = idx
                break
        if second_occurrence:
            boundaries = boundaries[second_occurrence:]

    # Extract chapter content
    chapters = []
    for i, (line_num, ch_num) in enumerate(boundaries):
        # Get title from the line after the chapter marker
        title = ""
        for offset in range(1, title_offset + 2):
            if line_num + offset < len(lines):
                candidate = lines[line_num + offset].strip()
                if candidate and not re.match(pattern, candidate):
                    title = candidate
                    break

        # Clean up title
        title = re.sub(r"^_(.+)_$", r"\1", title)  # strip italic markers
        title = re.sub(r"\*\*(.+?)\*\*", r"\1", title)  # strip bold markers
        title = title.strip(".")

        # Get body: from after title to next chapter
        body_start = line_num + 1
        if i + 1 < len(boundaries):
            body_end = boundaries[i + 1][0]
        else:
            body_end = len(lines)

        body = "\n".join(lines[body_start:body_end]).strip()

        chapters.append({
            "number": ch_num,
            "title": title,
            "body": body,
        })

    return chapters


# ---------------------------------------------------------------------------
# Preface/intro extraction
# ---------------------------------------------------------------------------

def extract_preface(text: str, first_chapter_line: int, lines: list[str]) -> str | None:
    """Extract preface text before the first chapter."""
    # Look for PREFACE marker
    for i, line in enumerate(lines[:first_chapter_line]):
        if line.strip().upper().startswith("PREFACE"):
            preface_text = "\n".join(lines[i:first_chapter_line]).strip()
            if len(preface_text) > 200:
                return preface_text
    return None


# ---------------------------------------------------------------------------
# Main download logic
# ---------------------------------------------------------------------------

def download_book(book_id: int, dry_run: bool = False, ca_bundle: str | None = None) -> dict:
    """Download, split, and write a single Gutenberg book to the corpus."""
    config = BOOK_CONFIGS.get(book_id, {})
    slug = config.get("slug", f"gutenberg-{book_id}")

    # For pre-configured books, skip the slow Gutendex API call
    if config:
        author = config["author"]
        title = slug.replace("-", " ").title()
    else:
        logger.info("Fetching metadata for book %d from Gutendex...", book_id)
        try:
            guten_meta = fetch_book_metadata(book_id, ca_bundle)
        except Exception as e:
            logger.error("Failed to fetch metadata: %s", e)
            return {"book_id": book_id, "error": str(e)}
        title = guten_meta.get("title", f"Book {book_id}")
        authors = [a["name"] for a in guten_meta.get("authors", [])]
        author = authors[0] if authors else "Unknown"

    logger.info("Book: %s by %s", title, author)

    if dry_run:
        logger.info("[DRY RUN] Would download and split: %s", title)
        return {"book_id": book_id, "title": title, "author": author, "dry_run": True}

    # Download text
    logger.info("Downloading text...")
    raw_text = fetch_book_text(book_id, ca_bundle)
    logger.info("Downloaded %d chars (%.1f KB)", len(raw_text), len(raw_text) / 1024)

    # Process text
    text = strip_gutenberg_boilerplate(raw_text)
    text = strip_transcriber_notes(text)
    text = strip_trailing_index(text)

    # Split into chapters
    if config.get("chapter_pattern"):
        chapters = split_into_chapters(text, config)
    else:
        # No config — treat as single document
        chapters = [{"number": "1", "title": title, "body": text}]

    logger.info("Split into %d chapters", len(chapters))

    # Output directory
    output_dir = CORPUS_ROOT / "en" / config.get("category", "manuals") / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0

    use_sequential = config.get("sequential_numbering", False)

    for seq_idx, ch in enumerate(chapters, 1):
        ch_num = seq_idx if use_sequential else chapter_sort_key(ch["number"])
        filename = f"{ch_num:02d}-chapter-{ch_num}"

        txt_path = output_dir / f"{filename}.txt"
        meta_path = output_dir / f"{filename}.meta.json"

        if txt_path.exists():
            logger.info("  [%02d] Already exists, skipping: %s", ch_num, ch["title"][:50])
            skipped += 1
            continue

        # Process chapter body
        body = ch["body"]
        body = clean_formatting(body)
        body = reflow_paragraphs(body)
        body, footnotes = parse_footnotes_inline(body)
        # Remove "See page NNN" references (illustrations in physical book)
        body = re.sub(r"(?m)^\d*\.?\s*See pages? [\d,\s;:and\w-]+\.?\s*$", "", body)
        # Clean "See page" from inside footnotes, keeping any real content after
        body = re.sub(r"See pages? [\d,\s;:also pages-]+\.?\s*", "", body)
        body = re.sub(r"\n{3,}", "\n\n", body)
        # Strip any Gutenberg boilerplate that ended up in a chapter
        for marker in ("End of the Project Gutenberg",
                       "End of Project Gutenberg",
                       "*** END OF THE PROJECT GUTENBERG",
                       "*** END OF THIS PROJECT GUTENBERG"):
            idx = body.find(marker)
            if idx >= 0:
                body = body[:idx].rstrip()

        # Extract JD references for Brigham Young
        jd_refs = []
        if book_id == 74447:
            jd_refs = parse_jd_references(body)

        # Build metadata
        meta = {
            "title": ch["title"] or f"Chapter {ch_num}",
            "author": author,
            "book": title,
            "chapter": ch_num,
            "category": config.get("category", "manuals"),
            "subcategory": slug,
            "tags": config.get("tags", []),
            "authority": config.get("authority", 30),
            "lang": "eng",
            "source_url": f"https://www.gutenberg.org/ebooks/{book_id}",
            "source": "Project Gutenberg",
            "gutenberg_id": book_id,
        }

        if config.get("note"):
            meta["note"] = config["note"]
        if footnotes:
            meta["note_count"] = len(footnotes)
            meta["footnotes"] = footnotes
        if jd_refs:
            meta["journal_of_discourses_refs"] = jd_refs

        # Write files
        txt_path.write_text(body + "\n", encoding="utf-8")
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        logger.info("  [%02d] %s — %d chars, %d notes",
                     ch_num, ch["title"][:50], len(body), len(footnotes))
        written += 1

    stats = {
        "book_id": book_id,
        "title": title,
        "author": author,
        "chapters": len(chapters),
        "written": written,
        "skipped": skipped,
        "output_dir": str(output_dir),
    }
    logger.info("Done: %s — %d written, %d skipped", title, written, skipped)
    return stats


def list_books():
    """Print the list of pre-configured books."""
    print("\nPre-configured Gutenberg books:\n")
    print(f"  {'ID':<8} {'Title':<45} {'Author':<25} {'Authority'}")
    print(f"  {'—'*8} {'—'*45} {'—'*25} {'—'*9}")
    for book_id, cfg in sorted(BOOK_CONFIGS.items()):
        print(f"  {book_id:<8} {cfg['slug']:<45} {cfg['author']:<25} {cfg['authority']}")
    print(f"\nUsage: python {Path(__file__).name} --book-id <ID> [<ID> ...]")
    print(f"       python {Path(__file__).name} --book-id 42238 35514 45149 47182 74447  # all books")


def main():
    parser = argparse.ArgumentParser(
        description="Download books from Project Gutenberg into the Alejandría corpus"
    )
    parser.add_argument("--book-id", type=int, nargs="+",
                        help="Gutenberg book ID(s) to download")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be downloaded without writing files")
    parser.add_argument("--list-books", action="store_true",
                        help="List pre-configured books and exit")
    parser.add_argument("--ca-bundle", default=None,
                        help="Path to CA certificate bundle (for corporate proxies)")
    args = parser.parse_args()

    if args.list_books:
        list_books()
        return

    if not args.book_id:
        parser.error("--book-id is required (or use --list-books)")

    # Auto-detect CA bundle
    ca_bundle = args.ca_bundle
    if not ca_bundle:
        default_ca = Path(__file__).resolve().parent.parent / "docker" / "ca-certificates.crt"
        if default_ca.exists():
            ca_bundle = str(default_ca)

    all_stats = []
    for book_id in args.book_id:
        logger.info("=" * 60)
        stats = download_book(book_id, dry_run=args.dry_run, ca_bundle=ca_bundle)
        all_stats.append(stats)

    # Summary
    logger.info("=" * 60)
    logger.info("Summary:")
    for s in all_stats:
        if "error" in s:
            logger.error("  %d: ERROR — %s", s["book_id"], s["error"])
        elif s.get("dry_run"):
            logger.info("  %d: %s [DRY RUN]", s["book_id"], s["title"])
        else:
            logger.info("  %d: %s — %d chapters, %d written, %d skipped",
                        s["book_id"], s["title"], s["chapters"], s["written"], s["skipped"])


if __name__ == "__main__":
    main()

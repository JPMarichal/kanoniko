#!/usr/bin/env python
"""
Download ISBE (International Standard Bible Encyclopedia, 1915) from
internationalstandardbible.com into Alejandria corpus format.

Step 1: Fetch letter indexes (A-Z) to get all entry URLs
Step 2: Fetch each entry page and extract clean text
Step 3: Group entries by letter into corpus/en/reference/isbe/{Letter}.txt

Usage:
    python scripts/download_isbe.py              # full download
    python scripts/download_isbe.py --resume      # resume from where it left off
    python scripts/download_isbe.py --letter A    # download only letter A
"""

import json
import os
import re
import ssl
import sys
import time
import urllib.request
from collections import defaultdict
from html.parser import HTMLParser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CORPUS_DIR = os.path.join(PROJECT_ROOT, "corpus", "en", "reference", "isbe")
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "isbe")
STATE_FILE = os.path.join(RAW_DIR, "_download_state.json")

BASE_URL = "https://www.internationalstandardbible.com"
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Rate limiting
DELAY_BETWEEN_REQUESTS = 0.5  # seconds

# SSL context that skips verification (corporate proxy)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


class TextExtractor(HTMLParser):
    """Extract article text from ISBE entry HTML pages."""

    def __init__(self):
        super().__init__()
        self.in_article = False
        self.in_script = False
        self.in_style = False
        self.depth = 0
        self.parts = []
        self.current_tag = None
        self._found_content = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        tag_id = attrs_dict.get("id", "")

        if tag in ("script", "style"):
            self.in_script = True
            return

        # Look for the main content area
        if tag == "div" and ("entry" in cls or "article" in cls or "content" in cls
                             or tag_id in ("content", "article", "entry")):
            self.in_article = True
            self.depth = 1
            return

        if self.in_article:
            if tag == "div":
                self.depth += 1
            if tag == "p":
                self.parts.append("\n")
            if tag == "br":
                self.parts.append("\n")
            if tag in ("h1", "h2", "h3", "h4", "h5"):
                self.parts.append("\n### ")

        self.current_tag = tag

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.in_script = False
            return

        if self.in_article:
            if tag == "div":
                self.depth -= 1
                if self.depth <= 0:
                    self.in_article = False
            if tag in ("p", "h1", "h2", "h3", "h4", "h5"):
                self.parts.append("\n")

    def handle_data(self, data):
        if self.in_script or not self.in_article:
            return
        text = data.strip()
        if text:
            self.parts.append(data)
            self._found_content = True

    def get_text(self):
        text = "".join(self.parts)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()


class IndexExtractor(HTMLParser):
    """Extract entry links from an ISBE letter index page."""

    def __init__(self):
        super().__init__()
        self.links = []
        self.in_a = False
        self.current_href = None
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            href = attrs_dict.get("href", "")
            if href and href.endswith(".html") and not href.startswith("http"):
                self.in_a = True
                self.current_href = href
                self.current_text = ""

    def handle_data(self, data):
        if self.in_a:
            self.current_text += data

    def handle_endtag(self, tag):
        if tag == "a" and self.in_a:
            if self.current_href and self.current_text.strip():
                self.links.append({
                    "href": self.current_href,
                    "title": self.current_text.strip()
                })
            self.in_a = False


def fetch_url(url):
    """Fetch a URL and return the HTML content."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Alejandria-Corpus-Builder/1.0 (scholarly research)"
    })
    try:
        resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=30)
        return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"    ERROR fetching {url}: {e}")
        return None


def load_state():
    """Load download state for resume capability."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed_letters": [], "entries": {}}


def save_state(state):
    """Save download state."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def fetch_letter_index(letter):
    """Fetch the index page for a letter and return entry links."""
    url = "{}/{}/index.html".format(BASE_URL, letter)
    print(f"  Fetching index for {letter}...")
    html = fetch_url(url)
    if not html:
        return []

    parser = IndexExtractor()
    parser.feed(html)

    # Normalize links
    entries = []
    seen = set()
    for link in parser.links:
        href = link["href"]
        if href.startswith("/"):
            pass
        elif not href.startswith("http"):
            href = "/{}/{}".format(letter, href)

        if href not in seen:
            seen.add(href)
            entries.append({"href": href, "title": link["title"]})

    print(f"    Found {len(entries)} entries")
    return entries


def fetch_entry(letter, href, title):
    """Fetch a single entry page and extract text."""
    if href.startswith("/"):
        url = BASE_URL + href
    else:
        url = "{}/{}/{}".format(BASE_URL, letter, href)

    html = fetch_url(url)
    if not html:
        return None

    # Try the structured extractor first
    extractor = TextExtractor()
    extractor.feed(html)
    text = extractor.get_text()

    # Fallback: if no article div found, try extracting from body
    if not text or len(text) < 50:
        # Simple fallback: extract all text between common content markers
        # Remove scripts and styles
        cleaned = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<style[^>]*>.*?</style>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<nav[^>]*>.*?</nav>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<header[^>]*>.*?</header>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<footer[^>]*>.*?</footer>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        # Strip remaining tags
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = re.sub(r"&[a-zA-Z]+;", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Try to find the article content heuristically
        if title and title in cleaned:
            idx = cleaned.index(title)
            text = cleaned[idx:]
            # Trim at navigation/footer markers
            for marker in ["Previous", "Next", "Copyright", "Back to", "Home"]:
                end_idx = text.find(marker)
                if end_idx > 100:
                    text = text[:end_idx]
                    break

    return text.strip() if text else None


def write_corpus_letter(letter, entries):
    """Write entries for a letter to corpus format."""
    os.makedirs(CORPUS_DIR, exist_ok=True)

    if not entries:
        return 0

    lines = []
    all_refs = []
    for entry in entries:
        if not entry.get("text"):
            continue
        lines.append("## {}".format(entry["title"]))
        lines.append("")
        lines.append(entry["text"])
        lines.append("")

        # Extract scripture references from text
        refs = re.findall(
            r"(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|"
            r"1 Samuel|2 Samuel|1 Kings|2 Kings|1 Chronicles|2 Chronicles|"
            r"Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|"
            r"Song of Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|"
            r"Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|"
            r"Zephaniah|Haggai|Zechariah|Malachi|"
            r"Matthew|Mark|Luke|John|Acts|Romans|"
            r"1 Corinthians|2 Corinthians|Galatians|Ephesians|Philippians|"
            r"Colossians|1 Thessalonians|2 Thessalonians|1 Timothy|2 Timothy|"
            r"Titus|Philemon|Hebrews|James|1 Peter|2 Peter|"
            r"1 John|2 John|3 John|Jude|Revelation)"
            r"\s+\d+(?::\d+)?(?:[,-]\s*\d+)*",
            entry["text"]
        )
        all_refs.extend(refs)

    if not lines:
        return 0

    txt_path = os.path.join(CORPUS_DIR, "{}.txt".format(letter))
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    valid_entries = [e for e in entries if e.get("text")]
    meta = {
        "title": "International Standard Bible Encyclopedia - {}".format(letter),
        "author": "James Orr (editor)",
        "year": 1915,
        "language": "en",
        "source": "internationalstandardbible.com (SwordSearcher module)",
        "license": "Public Domain",
        "category": "reference",
        "subcategory": "bible-encyclopedia",
        "description": "Exhaustive 5-volume Bible encyclopedia with ~10,000 entries by 200+ scholars. Protestant evangelical perspective.",
        "entry_count": len(valid_entries),
        "entries": [e["title"] for e in valid_entries],
        "scripture_references": sorted(set(all_refs)),
        "authority": {
            "doctrinal": 15,
            "rigor": 75,
            "official": False,
            "notes": "1915 Protestant Bible encyclopedia; strong on history/archaeology/geography, dated on some scholarship"
        }
    }
    meta_path = os.path.join(CORPUS_DIR, "{}.meta.json".format(letter))
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"  Wrote {letter}.txt ({len(valid_entries)} entries)")
    return len(valid_entries)


def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    resume = "--resume" in sys.argv
    single_letter = None
    if "--letter" in sys.argv:
        idx = sys.argv.index("--letter")
        if idx + 1 < len(sys.argv):
            single_letter = sys.argv[idx + 1].upper()

    state = load_state() if resume else {"completed_letters": [], "entries": {}}
    letters = [single_letter] if single_letter else LETTERS

    total_entries = 0

    for letter in letters:
        if resume and letter in state["completed_letters"]:
            print(f"Skipping {letter} (already done)")
            continue

        print(f"\n{'='*50}")
        print(f"Letter {letter}")
        print(f"{'='*50}")

        # Step 1: Get index
        index_entries = fetch_letter_index(letter)
        time.sleep(DELAY_BETWEEN_REQUESTS)

        if not index_entries:
            print(f"  No entries found for {letter}, skipping")
            continue

        # Step 2: Fetch each entry
        letter_entries = []
        for i, entry_info in enumerate(index_entries):
            if resume and entry_info["href"] in state.get("entries", {}):
                # Use cached text
                letter_entries.append({
                    "title": entry_info["title"],
                    "text": state["entries"][entry_info["href"]]
                })
                continue

            text = fetch_entry(letter, entry_info["href"], entry_info["title"])
            if text and len(text) > 20:
                letter_entries.append({
                    "title": entry_info["title"],
                    "text": text
                })
                state.setdefault("entries", {})[entry_info["href"]] = text

            if (i + 1) % 50 == 0:
                print(f"    Progress: {i+1}/{len(index_entries)}")
                save_state(state)

            time.sleep(DELAY_BETWEEN_REQUESTS)

        # Step 3: Write corpus
        count = write_corpus_letter(letter, letter_entries)
        total_entries += count

        state["completed_letters"].append(letter)
        save_state(state)

    print(f"\n{'='*50}")
    print(f"ISBE download complete: {total_entries} entries")
    print(f"Corpus: {CORPUS_DIR}")


if __name__ == "__main__":
    main()

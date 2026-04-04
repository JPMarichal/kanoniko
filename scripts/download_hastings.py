#!/usr/bin/env python
"""
Download Hastings' Dictionary of the Bible from bibleportal.com
into Alejandria corpus format.

5,915 entries organized A-Z.

Usage:
    python scripts/download_hastings.py              # full download
    python scripts/download_hastings.py --resume      # resume
    python scripts/download_hastings.py --letter A    # single letter
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
CORPUS_DIR = os.path.join(PROJECT_ROOT, "corpus", "en", "reference", "hastings-dictionary-of-the-bible")
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "hastings")
STATE_FILE = os.path.join(RAW_DIR, "_download_state.json")

BASE_URL = "https://www.bibleportal.com"
DICT_PATH = "/dictionary/hastings-dictionary-of-the-bible"
LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

DELAY_BETWEEN_REQUESTS = 0.5

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


class LetterIndexExtractor(HTMLParser):
    """Extract entry links from a Hastings letter page on BiblePortal."""

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
            if href and "/dictionary/hastings-dictionary-of-the-bible/" in href:
                # Skip letter-level links, keep entry-level links
                path_parts = href.rstrip("/").split("/")
                if len(path_parts) > 0 and len(path_parts[-1]) > 1:
                    self.in_a = True
                    self.current_href = href
                    self.current_text = ""

    def handle_data(self, data):
        if self.in_a:
            self.current_text += data

    def handle_endtag(self, tag):
        if tag == "a" and self.in_a:
            title = self.current_text.strip()
            if title and self.current_href:
                self.links.append({
                    "href": self.current_href,
                    "title": title
                })
            self.in_a = False


class EntryExtractor(HTMLParser):
    """Extract article text from a BiblePortal entry page."""

    def __init__(self):
        super().__init__()
        self.in_article = False
        self.in_script = False
        self.depth = 0
        self.parts = []
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if tag in ("script", "style"):
            self.in_script = True
            return

        # BiblePortal uses various content div classes
        if tag == "div" and any(x in cls for x in ["entry-content", "article-content",
                                                      "definition", "dict-entry",
                                                      "content", "post-content"]):
            self.in_article = True
            self.depth = 1
            return

        # Also detect article tag
        if tag == "article":
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
            if tag in ("h1", "h2", "h3", "h4"):
                self.parts.append("\n### ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.in_script = False
            return

        if self.in_article:
            if tag in ("div", "article"):
                self.depth -= 1
                if self.depth <= 0:
                    self.in_article = False
            if tag in ("p", "h1", "h2", "h3", "h4"):
                self.parts.append("\n")

    def handle_data(self, data):
        if self.in_script or not self.in_article:
            return
        text = data
        if text.strip():
            self.parts.append(text)

    def get_text(self):
        text = "".join(self.parts)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()


def fetch_url(url):
    """Fetch a URL and return HTML content."""
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
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed_letters": [], "entries": {}}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def fetch_letter_index(letter):
    """Fetch list of entries for a letter."""
    url = "{}{}/{}".format(BASE_URL, DICT_PATH, letter)
    print(f"  Fetching index for {letter}...")
    html = fetch_url(url)
    if not html:
        return []

    parser = LetterIndexExtractor()
    parser.feed(html)

    # Deduplicate
    seen = set()
    entries = []
    for link in parser.links:
        href = link["href"]
        if href not in seen:
            seen.add(href)
            entries.append(link)

    print(f"    Found {len(entries)} entries")
    return entries


def fetch_entry(href, title):
    """Fetch a single entry and extract text."""
    if href.startswith("/"):
        url = BASE_URL + href
    elif href.startswith("http"):
        url = href
    else:
        url = BASE_URL + DICT_PATH + "/" + href

    html = fetch_url(url)
    if not html:
        return None

    # Try structured extraction
    extractor = EntryExtractor()
    extractor.feed(html)
    text = extractor.get_text()

    # Fallback: brute-force text extraction
    if not text or len(text) < 30:
        cleaned = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<style[^>]*>.*?</style>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<nav[^>]*>.*?</nav>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<header[^>]*>.*?</header>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<footer[^>]*>.*?</footer>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = re.sub(r"&[a-zA-Z]+;", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        if title and title.upper() in cleaned.upper():
            idx = cleaned.upper().index(title.upper())
            text = cleaned[idx:]
            for marker in ["See Also", "Related", "Copyright", "Dictionary", "Previous Entry",
                           "Next Entry", "Choose a letter"]:
                end_idx = text.find(marker)
                if end_idx > 100:
                    text = text[:end_idx]
                    break

    if text:
        # Clean BiblePortal navigation noise
        noise_patterns = [
            r"NIVLog In.*?Bible Book List\s*",
            r"James Hastings Hastings' Dictionary of the Bible.*?Read More\s*",
            r"Get Bible verse every day.*?Subscribe\s*",
            r"Read on Mobile\s*",
            r"Most Searched.*?Days\s*",
            r"### Group of Brands\s*",
            r"New International Version \(NIV\)\s*",
            r"We'll never share your email\s*",
            r"Complete and trustworthy.*?one-volume work\.\s*",
            r"Wikipedia\s*",
            r"\d+ Days\s*",
            r"Today\s*",
        ]
        for pat in noise_patterns:
            text = re.sub(pat, "", text, flags=re.DOTALL)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text.strip() if text and len(text) > 20 else None


def write_corpus_letter(letter, entries):
    """Write entries for a letter to corpus format."""
    os.makedirs(CORPUS_DIR, exist_ok=True)

    valid = [e for e in entries if e.get("text")]
    if not valid:
        return 0

    lines = []
    all_refs = []
    for entry in valid:
        lines.append("## {}".format(entry["title"]))
        lines.append("")
        lines.append(entry["text"])
        lines.append("")

        refs = re.findall(
            r"(?:Gen|Exod|Ex|Lev|Num|Deut|Dt|Josh|Judg|Jg|Ruth|Ru|"
            r"1 ?Sam|2 ?Sam|1 ?Ki|2 ?Ki|1 ?Chr|2 ?Chr|"
            r"Ezr|Neh|Est|Job|Ps|Prov|Pr|Eccl|Ec|"
            r"Song|Cant|Isa|Is|Jer|Lam|Ezek|Ezk|Dan|Dn|"
            r"Hos|Joel|Am|Ob|Jon|Mic|Nah|Hab|Zeph|Hag|Zec|Mal|"
            r"Mt|Mk|Lk|Jn|Ac|Ro|"
            r"1 ?Cor|2 ?Cor|Gal|Eph|Phil|Col|"
            r"1 ?Th|2 ?Th|1 ?Tim|2 ?Tim|Tit|Phm|He|Heb|"
            r"Jas|1 ?Pet|2 ?Pet|1 ?Jn|2 ?Jn|3 ?Jn|Jude|Rev|"
            r"Genesis|Exodus|Leviticus|Numbers|Deuteronomy|"
            r"Matthew|Mark|Luke|John|Acts|Romans|Hebrews|James|Revelation)"
            r"\.?\s*\d+(?:[:.]\d+)?(?:[,-]\s*\d+)*",
            entry["text"]
        )
        all_refs.extend(refs)

    txt_path = os.path.join(CORPUS_DIR, "{}.txt".format(letter))
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    meta = {
        "title": "Hastings' Dictionary of the Bible - {}".format(letter),
        "author": "James Hastings (editor)",
        "year": 1898,
        "language": "en",
        "source": "bibleportal.com",
        "license": "Public Domain",
        "category": "reference",
        "subcategory": "bible-dictionary",
        "description": "Comprehensive 4-volume Bible dictionary (1898) with 5,915 entries on persons, places, antiquities, archaeology, theology, and ethics.",
        "entry_count": len(valid),
        "entries": [e["title"] for e in valid],
        "scripture_references": sorted(set(all_refs)),
        "authority": {
            "doctrinal": 15,
            "rigor": 80,
            "official": False,
            "notes": "Late 19th-century critical scholarship; strong on source criticism and archaeology; higher rigor than Easton/Smith"
        }
    }
    meta_path = os.path.join(CORPUS_DIR, "{}.meta.json".format(letter))
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"  Wrote {letter}.txt ({len(valid)} entries)")
    return len(valid)


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

        index_entries = fetch_letter_index(letter)
        time.sleep(DELAY_BETWEEN_REQUESTS)

        if not index_entries:
            print(f"  No entries found for {letter}")
            continue

        letter_entries = []
        for i, entry_info in enumerate(index_entries):
            if resume and entry_info["href"] in state.get("entries", {}):
                letter_entries.append({
                    "title": entry_info["title"],
                    "text": state["entries"][entry_info["href"]]
                })
                continue

            text = fetch_entry(entry_info["href"], entry_info["title"])
            if text:
                letter_entries.append({
                    "title": entry_info["title"],
                    "text": text
                })
                state.setdefault("entries", {})[entry_info["href"]] = text

            if (i + 1) % 50 == 0:
                print(f"    Progress: {i+1}/{len(index_entries)}")
                save_state(state)

            time.sleep(DELAY_BETWEEN_REQUESTS)

        count = write_corpus_letter(letter, letter_entries)
        total_entries += count

        state["completed_letters"].append(letter)
        save_state(state)

    print(f"\n{'='*50}")
    print(f"Hastings download complete: {total_entries} entries")
    print(f"Corpus: {CORPUS_DIR}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Gospelink.com scraper — Playwright-based, AWS-WAF-aware.

Subcommands:

    bootstrap
        Open a visible Chrome, navigate to /users/login, autofill credentials
        from .env (GOSPELINK_USER / GOSPELINK_PWD). User solves any CAPTCHA,
        presses Enter to save the session to data/.gospelink-session.json.

    discover --contents-id N --slug <s>
        Fetch /library/contents/{N}, extract all doc IDs from the sidebar
        vertical_carousel, save to data/raw/gospelink/{slug}/_toc.json.
        Also reads book title/author from the contents page.

    fetch --slug <s> --title "..." --author "..." [options]
        Reads _toc.json for the doc-ID list. Downloads each /print/doc/{id},
        converts to corpus format under corpus/en/books/gospelink/{slug}/.
        Resumable via _state.json. Pauses headed for any WAF challenge.

All network calls run HEADED with anti-automation flags (required by AWS WAF).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from html.parser import HTMLParser
from typing import List, Optional, Tuple

# --- Paths -----------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
STORAGE_STATE = os.path.join(PROJECT_ROOT, "data", ".gospelink-session.json")
RAW_BASE = os.path.join(PROJECT_ROOT, "data", "raw", "gospelink")
CORPUS_BASE = os.path.join(PROJECT_ROOT, "corpus", "en", "books", "gospelink")

LOGIN_URL = "https://www.gospelink.com/users/login"
HOME_URL  = "https://www.gospelink.com/"
CONTENTS_URL = "https://www.gospelink.com/library/contents/{book_id}"
DOC_URL      = "https://www.gospelink.com/print/doc/{doc_id}"

CHROME_EXECUTABLE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

DELAY_MIN = 3.5
DELAY_MAX = 5.5

# Anti-detection Chrome args (required to pass AWS WAF headless checks).
CHROME_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--no-first-run",
]
INIT_SCRIPT = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
USER_AGENT  = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/147.0.0.0 Safari/537.36"
)

# --- Helpers ---------------------------------------------------------------

def jitter_sleep():
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def load_env():
    env = {}
    if not os.path.exists(ENV_FILE):
        return env
    with open(ENV_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _launch_headed(p):
    """Always launch headed with anti-detection. Required by AWS WAF."""
    exe = CHROME_EXECUTABLE if os.path.exists(CHROME_EXECUTABLE) else None
    kwargs = dict(headless=False, args=CHROME_ARGS)
    if exe:
        kwargs["executable_path"] = exe
    return p.chromium.launch(**kwargs)


def _new_context(browser, storage_state=None):
    kw = dict(
        user_agent=USER_AGENT,
        viewport={"width": 1280, "height": 900},
    )
    if storage_state and os.path.exists(storage_state):
        kw["storage_state"] = storage_state
    ctx = browser.new_context(**kw)
    ctx.add_init_script(INIT_SCRIPT)
    return ctx


WAF_MARKERS = ("aws-waf-token", "AWS WAF", "Verify you are human",
               "Let's confirm you are human", 'name="awswafblob"')


def looks_like_waf(html):
    if not html or len(html) < 1000:
        return True
    return any(m in html for m in WAF_MARKERS)


def looks_like_login_wall(html):
    return "users/login" in html and "logout" not in html.lower()


def looks_like_waf_js_challenge(html, page_title=""):
    """AWS WAF interstitial — JS-only or with image-grid CAPTCHA. Can take 10-20s."""
    if "awsWafCookie" in html or "challenge.js" in html:
        return True
    if "Human Verification" in (page_title or ""):
        return True
    if "Verify you are human" in html or "confirm you are human" in html.lower():
        return True
    return False


def goto_and_settle(page, url, max_wait=30.0):
    """Navigate and wait for AWS WAF challenge to clear.

    Returns (response, html). Polls every 0.5s up to max_wait. When WAF page
    is no longer detected, waits one extra step for real content to render,
    then returns. If still on WAF after max_wait, returns whatever is there
    (caller may need manual CAPTCHA solve).
    """
    resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
    elapsed = 0.0
    step    = 0.5
    while elapsed < max_wait:
        try:
            html  = page.content()
            title = page.title()
        except Exception:
            # Page is mid-navigation (WAF redirect). Wait and retry.
            time.sleep(step)
            elapsed += step
            continue
        if not looks_like_waf_js_challenge(html, title):
            time.sleep(step)
            try:
                return resp, page.content()
            except Exception:
                time.sleep(step)
                return resp, page.content()
        time.sleep(step)
        elapsed += step
    try:
        return resp, page.content()
    except Exception:
        time.sleep(1.0)
        return resp, page.content()


# --- HTML extractor for /print/doc pages -----------------------------------

class PrintDocExtractor(HTMLParser):
    """
    Extract text from gospelink /print/doc pages.
    The print pages are clean single-column HTML. We collect everything
    inside <body> minus scripts/styles/nav. Block tags become paragraph breaks.
    """

    BLOCK = {"p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6",
             "li", "tr", "blockquote", "section", "article", "hr"}
    SKIP  = {"script", "style", "noscript", "nav", "header", "footer",
             "form", "select", "button", "iframe"}
    HEADING = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_body   = False
        self.skip_depth = 0
        self.parts     = []
        self._title    = []
        self.in_title  = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
            return
        if tag == "body":
            self.in_body = True
            return
        if tag in self.SKIP:
            self.skip_depth += 1
            return
        if self.in_body and not self.skip_depth:
            if tag in self.HEADING:
                self.parts.append("\n\n### ")
            elif tag in self.BLOCK:
                self.parts.append("\n\n")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in self.SKIP:
            self.skip_depth = max(0, self.skip_depth - 1)

    def handle_data(self, data):
        if self.in_title:
            self._title.append(data)
        elif self.in_body and not self.skip_depth:
            self.parts.append(data)

    def page_title(self):
        t = re.sub(r"\s+", " ", "".join(self._title)).strip()
        # Strip site branding prefix.
        t = re.sub(r"^(GospeLink\.com\s*-\s*|GospeLink\s*-\s*)", "", t, flags=re.IGNORECASE)
        return t.strip()

    def body_text(self):
        raw = "".join(self.parts)
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        # Strip common boilerplate lines.
        clean = []
        for line in raw.split("\n"):
            ls = line.strip()
            if ls.lower() in {"login", "logout", "search", "home",
                              "back", "print", "close", "gospelink"}:
                continue
            clean.append(line)
        return "\n".join(clean).strip()


def convert_html(html):
    # type: (str) -> Tuple[str, str]
    ex = PrintDocExtractor()
    ex.feed(html)
    return ex.page_title(), ex.body_text()


# --- TOC extraction from /library/contents ---------------------------------

def extract_toc(html):
    # type: (str) -> dict
    """Return TOC metadata from a contents page."""
    doc_ids = []
    seen = set()
    for m in re.finditer(r'href="/library/document/(\d+)"', html):
        d = int(m.group(1))
        if d not in seen:
            seen.add(d)
            doc_ids.append(d)

    title_m  = re.search(r'<h1>([^<]+)</h1>', html)
    title    = title_m.group(1).strip() if title_m else ""

    author_m = re.search(r'<h2>([^<]+)</h2>', html)
    author   = author_m.group(1).strip() if author_m else ""

    # Year + publisher from copyright text.
    year = None
    publisher = ""
    cr_m = re.search(r'©\s*(\d{4})\s+([^<\n]+?)<', html)
    if cr_m:
        year = int(cr_m.group(1))
        publisher = cr_m.group(2).strip()

    # Volume from title (e.g., "..., vol. 1" or "Volume 2").
    volume = None
    vol_m = re.search(r'\bvol(?:\.|ume)?\s*(\d+)', title, re.IGNORECASE)
    if vol_m:
        volume = int(vol_m.group(1))

    # Topics / category (best-effort).
    topics = re.findall(r'href="/browse/topic/\d+">([^<]+)</a>', html)
    category_m = re.search(r'href="/browse/category/\d+">([^<]+)</a>', html)
    category = category_m.group(1).strip() if category_m else ""

    return {
        "doc_ids":   doc_ids,
        "title":     title,
        "author":    author,
        "year":      year,
        "publisher": publisher,
        "volume":    volume,
        "topics":    topics,
        "category":  category,
    }


# Header line in /print/doc body, e.g.
# "Bruce R. McConkie, Doctrinal New Testament Commentary, vol. 1 ( 1965)"
DOC_HEADER_RE = re.compile(
    r'^([^,\n]+),\s+(.+?)(?:,\s*vol\.?\s*(\d+))?\s*\(\s*(\d{4})\s*\)\s*$',
    re.MULTILINE,
)


def parse_doc_header(text):
    """From a converted doc text, return (author, book, volume, year, chapter_title) or Nones."""
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if not lines:
        return None, None, None, None, None
    chapter_title = None
    if lines[0].startswith("# "):
        chapter_title = lines[0][2:].strip()
    elif lines[0].startswith("### "):
        chapter_title = lines[0][4:].strip()
    author = book = year = volume = None
    for ln in lines[:8]:
        m = DOC_HEADER_RE.match(ln)
        if m:
            author = m.group(1).strip()
            book   = m.group(2).strip()
            volume = int(m.group(3)) if m.group(3) else None
            year   = int(m.group(4))
            break
    return author, book, volume, year, chapter_title


# --- bootstrap -------------------------------------------------------------

def cmd_bootstrap(args):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Run: pip install playwright && playwright install chromium", file=sys.stderr)
        return 2

    env = load_env()
    user = env.get("GOSPELINK_USER", "")
    pwd  = env.get("GOSPELINK_PWD", "")
    if not user or not pwd:
        print("Missing GOSPELINK_USER / GOSPELINK_PWD in .env", file=sys.stderr)
        return 2

    os.makedirs(os.path.dirname(STORAGE_STATE), exist_ok=True)

    print("Launching Chrome (headed — required by AWS WAF)...")
    print("Steps:")
    print("  1. Chrome opens to the login page.")
    print("  2. Credentials autofill from .env.")
    print("  3. Solve any CAPTCHA that appears, then click Login.")
    print("  4. Wait for the logged-in home page.")
    print("  5. Return here and press Enter to save the session.")
    print()

    with sync_playwright() as p:
        browser = _launch_headed(p)
        ctx  = _new_context(browser)
        page = ctx.new_page()
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)

        # Autofill best-effort.
        EMAIL_SELS = ('input[type="email"]', 'input[name="email"]',
                      'input[name="user[email]"]', 'input[name="login"]',
                      'input[name="username"]')
        PWD_SELS   = ('input[type="password"]', 'input[name="password"]',
                      'input[name="user[password]"]')
        for sel in EMAIL_SELS:
            try:
                if page.locator(sel).count():
                    page.locator(sel).first.fill(user)
                    print(f"  filled email -> {sel}")
                    break
            except Exception:
                pass
        for sel in PWD_SELS:
            try:
                if page.locator(sel).count():
                    page.locator(sel).first.fill(pwd)
                    print(f"  filled password -> {sel}")
                    break
            except Exception:
                pass

        print()
        input(">>> Solve CAPTCHA if shown, click Login, wait for home, then press Enter: ")

        ctx.storage_state(path=STORAGE_STATE)
        print(f"Session saved -> {STORAGE_STATE}")
        browser.close()
    return 0


# --- discover --------------------------------------------------------------

def cmd_discover(args):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Run: pip install playwright", file=sys.stderr)
        return 2

    raw_dir = os.path.join(RAW_BASE, args.slug)
    os.makedirs(raw_dir, exist_ok=True)
    toc_path = os.path.join(raw_dir, "_toc.json")

    url = CONTENTS_URL.format(book_id=args.contents_id)
    print(f"Fetching TOC from {url} ...")

    with sync_playwright() as p:
        browser = _launch_headed(p)
        ctx  = _new_context(browser, STORAGE_STATE)
        page = ctx.new_page()
        goto_and_settle(page, HOME_URL)
        _, html = goto_and_settle(page, url)
        browser.close()

    if looks_like_waf(html) or looks_like_login_wall(html):
        print("ERROR: WAF or login wall. Run bootstrap first.", file=sys.stderr)
        return 1

    info = extract_toc(html)
    doc_ids = info["doc_ids"]
    if not doc_ids:
        print("ERROR: no doc links found. Wrong contents-id?", file=sys.stderr)
        return 1

    info["contents_id"] = args.contents_id
    info["slug"] = args.slug
    with open(toc_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"TOC saved: {len(doc_ids)} docs, IDs {doc_ids[0]}..{doc_ids[-1]}")
    print(f"  Title:     {info['title']}")
    print(f"  Author:    {info['author']}")
    print(f"  Year:      {info.get('year')}")
    print(f"  Volume:    {info.get('volume')}")
    print(f"  Publisher: {info.get('publisher')}")
    print(f"  Topics:    {info.get('topics')}")
    print(f"  File:      {toc_path}")
    return 0


# --- fetch -----------------------------------------------------------------

def cmd_fetch(args):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Run: pip install playwright", file=sys.stderr)
        return 2

    raw_dir = os.path.join(RAW_BASE, args.slug)
    out_dir = os.path.join(CORPUS_BASE, args.slug)
    toc_path   = os.path.join(raw_dir, "_toc.json")
    state_path = os.path.join(raw_dir, "_state.json")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    # Load TOC.
    if not os.path.exists(toc_path):
        print(f"No _toc.json for slug '{args.slug}'. Run: discover --contents-id N --slug {args.slug}",
              file=sys.stderr)
        return 2
    with open(toc_path, encoding="utf-8") as f:
        toc = json.load(f)

    doc_ids = toc["doc_ids"]
    book_title  = args.title  or toc.get("title", "")
    book_author = args.author or toc.get("author", "")

    # Resume state.
    state = {"done": [], "failed": []}
    if os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as f:
            state = json.load(f)

    done_set   = set(state.get("done", []))
    pending    = [d for d in doc_ids if d not in done_set] if not args.force else doc_ids
    total      = len(pending)
    eta_min    = total * (DELAY_MIN + DELAY_MAX) / 2 / 60

    print(f"Slug:    {args.slug}")
    print(f"Book:    {book_title}")
    print(f"Author:  {book_author}")
    print(f"Total:   {len(doc_ids)} docs | Pending: {total}")
    print(f"ETA:     ~{eta_min:.1f} min")
    print(f"Output:  {out_dir}")
    print()

    with sync_playwright() as p:
        browser = _launch_headed(p)
        ctx  = _new_context(browser, STORAGE_STATE)
        page = ctx.new_page()
        goto_and_settle(page, HOME_URL)

        ok_count = 0
        for ordinal, doc_id in enumerate(pending, 1):
            url      = DOC_URL.format(doc_id=doc_id)
            raw_path = os.path.join(raw_dir, f"{doc_id}.html")
            # Corpus ordinal = position in full doc_ids list (1-based).
            corpus_idx = doc_ids.index(doc_id) + 1
            txt_path   = os.path.join(out_dir, f"{corpus_idx:04d}-doc-{doc_id}.txt")
            meta_path  = os.path.join(out_dir, f"{corpus_idx:04d}-doc-{doc_id}.meta.json")

            if os.path.exists(txt_path) and not args.force:
                done_set.add(doc_id)
                continue

            try:
                resp, html = goto_and_settle(page, url)
            except Exception as e:
                print(f"  [{ordinal}/{total}] doc {doc_id}: nav error ({e.__class__.__name__}), skip")
                state["failed"].append(doc_id)
                continue

            status = resp.status if resp else 0

            if status >= 400 or looks_like_waf(html) or looks_like_login_wall(html):
                print(f"  [{ordinal}/{total}] doc {doc_id}: WAF/login (status {status})")
                _save_state(state_path, state)
                if not _handle_waf_pause(page, doc_id):
                    print("Aborting. Rerun same command to resume.", file=sys.stderr)
                    browser.close()
                    return 1
                ctx.storage_state(path=STORAGE_STATE)
                resp, html = goto_and_settle(page, url)
                if looks_like_waf(html) or (resp and resp.status >= 400):
                    print(f"  doc {doc_id}: still blocked after manual solve, skipping.")
                    state["failed"].append(doc_id)
                    continue

            # Save raw.
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(html)

            page_title, body = convert_html(html)
            if not body or len(body) < 150:
                print(f"  [{ordinal}/{total}] doc {doc_id}: empty body ({len(body)} chars)")
                state["failed"].append(doc_id)
            else:
                _write_corpus(txt_path, meta_path, doc_id, corpus_idx,
                              page_title, body, book_title, book_author, args)
                done_set.add(doc_id)
                state["done"] = list(done_set)
                ok_count += 1
                if ok_count % 20 == 0 or ordinal <= 5:
                    print(f"  [{ordinal}/{total}] doc {doc_id}: ok ({len(body):,} chars) — '{page_title[:60]}'")

            if ordinal % 50 == 0:
                _save_state(state_path, state)

            jitter_sleep()

        state["done"] = list(done_set)
        _save_state(state_path, state)
        browser.close()

    print()
    print(f"Done. ok={ok_count}, failed={len(state['failed'])}, total_done={len(done_set)}/{len(doc_ids)}")
    if state["failed"]:
        print(f"Failed IDs: {state['failed'][:30]}{'...' if len(state['failed']) > 30 else ''}")
    return 0


def _handle_waf_pause(page, doc_id, max_wait_min=10):
    """
    Pause for the user to solve the WAF CAPTCHA in the visible Chrome window.

    If running interactively (TTY), wait for Enter. If running in background
    (no stdin), poll the page every 5s for up to max_wait_min minutes until
    the WAF page disappears (user solved it via the visible Chrome window).
    """
    print()
    print(f"  >>> Challenge on doc {doc_id}. Solve CAPTCHA in the visible Chrome window.")
    try:
        page.bring_to_front()
    except Exception:
        pass

    if sys.stdin.isatty():
        print(f"  >>> Press Enter when done, or type 'abort' + Enter to stop.")
        try:
            resp = input("  >>> ")
            return resp.strip().lower() != "abort"
        except EOFError:
            pass  # fall through to polling mode

    # Background / no-TTY mode: poll until the user solves it visually.
    print(f"  >>> No stdin (background mode). Polling for up to {max_wait_min} min ...")
    print(f"  >>> Open the Chrome window, solve the CAPTCHA, then leave it open.")
    deadline = time.time() + max_wait_min * 60
    poll_step = 5
    last_log = time.time()
    while time.time() < deadline:
        time.sleep(poll_step)
        try:
            html = page.content()
            title = page.title()
        except Exception:
            continue
        if not looks_like_waf_js_challenge(html, title) and len(html) > 5000:
            print(f"  >>> WAF cleared after {int(time.time() - (deadline - max_wait_min*60))}s.")
            return True
        if time.time() - last_log > 30:
            print(f"  >>> still waiting (title: {title[:40]!r}, len {len(html)})")
            last_log = time.time()
    print(f"  >>> Timed out waiting for CAPTCHA solve. Abort.")
    return False


def _save_state(path, state):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _write_corpus(txt_path, meta_path, doc_id, corpus_idx,
                  page_title, body, book_title, book_author, args):
    display_title = page_title or f"{book_title} — part {corpus_idx}"
    text = "# {}\n\n{}\n".format(display_title, body)

    meta = {
        "title":            display_title,
        "author":           book_author,
        "book":             book_title,
        "part":             corpus_idx,
        "doc_id":           doc_id,
        "category":         "books",
        "subcategory":      "gospelink",
        "collection_slug":  args.slug,
        "tags":             ["gospelink", args.slug] + (args.tag or []),
        "authority":        args.authority,
        "rigor":            args.rigor,
        "lang":             "eng",
        "source_url":       DOC_URL.format(doc_id=doc_id),
        "source":           "Gospelink (licensed, Deseret Book)",
        "official":         False,
        "current":          False,
        "context":          args.context,
        "audience":         "adult",
        "importance":       args.importance,
    }
    if args.note:
        meta["note"] = args.note
    if args.series:
        meta["series"] = args.series

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# --- enrich-meta -----------------------------------------------------------

def cmd_enrich_meta(args):
    """Post-process: parse year/volume/chapter from each .txt body and merge into .meta.json."""
    out_dir  = os.path.join(CORPUS_BASE, args.slug)
    raw_dir  = os.path.join(RAW_BASE, args.slug)
    toc_path = os.path.join(raw_dir, "_toc.json")

    toc = {}
    if os.path.exists(toc_path):
        with open(toc_path, encoding="utf-8") as f:
            toc = json.load(f)

    if not os.path.isdir(out_dir):
        print(f"No corpus dir: {out_dir}", file=sys.stderr)
        return 2

    txts = sorted(f for f in os.listdir(out_dir) if f.endswith(".txt"))
    enriched = 0
    for fname in txts:
        txt_path  = os.path.join(out_dir, fname)
        meta_path = txt_path[:-4] + ".meta.json"
        if not os.path.exists(meta_path):
            continue
        with open(txt_path, encoding="utf-8") as f:
            text = f.read()
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)

        author, book, volume, year, chapter_title = parse_doc_header(text)

        # Backfill from TOC if header parse missed something.
        if not year and toc.get("year"):
            year = toc["year"]
        if not volume and toc.get("volume"):
            volume = toc["volume"]
        if not author and toc.get("author"):
            author = toc["author"]
        if not book and toc.get("title"):
            book = toc["title"]

        # Chapter title = the line that comes right after the header line in the body.
        # In our converted text it's typically the H1 (already in meta['title']) or
        # the first non-header line.
        if chapter_title and chapter_title.lower() not in ("preface", "title page"):
            meta["chapter_title"] = chapter_title
        elif chapter_title:
            meta["chapter_title"] = chapter_title

        if year:
            meta["year"] = year
        if volume is not None:
            meta["volume"] = volume
        if author and not meta.get("author"):
            meta["author"] = author
        if book and not meta.get("book"):
            meta["book"] = book
        if toc.get("publisher"):
            meta["publisher"] = toc["publisher"]
        if toc.get("topics"):
            existing_tags = meta.get("tags", [])
            for t in toc["topics"]:
                tag = t.lower().replace(" ", "-")
                if tag not in existing_tags:
                    existing_tags.append(tag)
            meta["tags"] = existing_tags

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        enriched += 1

    print(f"Enriched {enriched} meta files in {out_dir}")
    return 0


# --- audit -----------------------------------------------------------------

def cmd_audit(args):
    """Compare TOC against downloaded files; report gaps and tiny outputs."""
    raw_dir  = os.path.join(RAW_BASE, args.slug)
    out_dir  = os.path.join(CORPUS_BASE, args.slug)
    toc_path = os.path.join(raw_dir, "_toc.json")

    if not os.path.exists(toc_path):
        print(f"No TOC: {toc_path}", file=sys.stderr)
        return 2
    with open(toc_path, encoding="utf-8") as f:
        toc = json.load(f)
    expected_ids = toc["doc_ids"]

    # Map doc_id -> txt path (if exists).
    have = {}
    if os.path.isdir(out_dir):
        for fname in os.listdir(out_dir):
            m = re.match(r"\d+-doc-(\d+)\.txt$", fname)
            if m:
                have[int(m.group(1))] = os.path.join(out_dir, fname)

    missing = [d for d in expected_ids if d not in have]
    tiny    = []
    for d, p in have.items():
        try:
            sz = os.path.getsize(p)
            if sz < args.min_size:
                tiny.append((d, sz))
        except OSError:
            pass

    print(f"Slug:         {args.slug}")
    print(f"TOC docs:     {len(expected_ids)}")
    print(f"Downloaded:   {len(have)}")
    print(f"Missing:      {len(missing)}")
    print(f"Tiny (<{args.min_size}b): {len(tiny)}")
    if missing:
        print(f"  Missing IDs ({len(missing)}): {missing[:50]}{'...' if len(missing) > 50 else ''}")
    if tiny:
        print(f"  Tiny IDs:")
        for d, sz in sorted(tiny, key=lambda x: x[1])[:20]:
            print(f"    {d}: {sz}b")

    if args.write_redo and (missing or tiny):
        redo = sorted(set(missing) | {d for d, _ in tiny})
        redo_path = os.path.join(raw_dir, "_redo.json")
        with open(redo_path, "w", encoding="utf-8") as f:
            json.dump({"doc_ids": redo}, f, indent=2)
        print(f"  -> Wrote {len(redo)} IDs to {redo_path}")
        print(f"  -> To redo: edit _toc.json's doc_ids to this list, run fetch --force")
    return 0


# --- CLI -------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)

    # bootstrap
    sp.add_parser("bootstrap", help="Headed login + save session.")

    # discover
    d = sp.add_parser("discover", help="Extract doc-ID list from a contents page.")
    d.add_argument("--contents-id", type=int, required=True,
                   help="Numeric ID in /library/contents/{N}")
    d.add_argument("--slug", required=True, help="Output folder slug.")

    # fetch
    f = sp.add_parser("fetch", help="Download all docs for a slug into the corpus.")
    f.add_argument("--slug",      required=True)
    f.add_argument("--title",     default="")
    f.add_argument("--author",    default="")
    f.add_argument("--series",    default="")
    f.add_argument("--authority", type=int, default=55)
    f.add_argument("--rigor",     type=int, default=70)
    f.add_argument("--importance",default="importante")
    f.add_argument("--context",   default="book-author")
    f.add_argument("--note",      default="")
    f.add_argument("--tag",       action="append")
    f.add_argument("--force",     action="store_true")

    # enrich-meta
    e = sp.add_parser("enrich-meta", help="Backfill year/volume/chapter into existing meta.json files.")
    e.add_argument("--slug", required=True)

    # audit
    a = sp.add_parser("audit", help="Compare TOC vs downloaded; report gaps and tiny files.")
    a.add_argument("--slug", required=True)
    a.add_argument("--min-size", type=int, default=400, help="Bytes; smaller .txt is suspicious.")
    a.add_argument("--write-redo", action="store_true",
                   help="Write IDs to redo to _redo.json.")

    args = ap.parse_args()
    if args.cmd == "bootstrap":
        return cmd_bootstrap(args)
    if args.cmd == "discover":
        return cmd_discover(args)
    if args.cmd == "fetch":
        return cmd_fetch(args)
    if args.cmd == "enrich-meta":
        return cmd_enrich_meta(args)
    if args.cmd == "audit":
        return cmd_audit(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())

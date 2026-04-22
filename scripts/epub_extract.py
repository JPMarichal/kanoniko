"""
EPUB -> Alejandria corpus extractor (v1, stdlib only).

Mechanical step: reads an EPUB, writes chapter-split .txt + .meta.json to a
preview directory. Authority values are left null on purpose — the Fase 0
research workflow (proj/P4-corpus-expansion/fase0/{slug}.md) assigns them
separately. See docs/project-memory/procedure_corpus_addition.md.

Usage:
  # Preview a single epub (default: writes to epub/_preview/)
  python scripts/epub_extract.py "epub/!Ready/Articles of Faith - James E. Talmage.epub" \\
      --lang en --category books

  # Apply straight to corpus/ (skips preview)
  python scripts/epub_extract.py <file.epub> --lang en --category books --apply

  # Override slug/author from CLI
  python scripts/epub_extract.py <file.epub> --lang en --category books \\
      --slug articles-of-faith --author "James E. Talmage"

  # Promote a previously previewed work to corpus/
  python scripts/epub_extract.py --promote epub/_preview/en/books/articles-of-faith

Flags:
  --lang {en,es}         override OPF language
  --category <name>      target corpus category (books, manuals, biographies, ...)
  --subcategory <name>   optional sub-bucket (e.g. priesthood under manuals/)
  --slug <slug>          override auto-slug
  --author <name>        override OPF creator
  --apply                skip preview, write directly to corpus/{lang}/{category}/<slug>/
  --promote <preview>    move a preview dir into corpus/ (idempotent)
  --min-chapter-chars N  ignore "chapters" shorter than N chars (default 80)
  --max-single-file-kb K if total text <= K kB, emit single file (default 10)
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
PREVIEW = ROOT / "epub" / "_preview"
CORPUS = ROOT / "corpus"
FASE0_DIR = ROOT / "proj" / "P4-corpus-expansion" / "fase0"

# Fields the Fase 0 sidecar may fill. Other keys in the sidecar are ignored
# (reserved for human annotations). Authority is only one axis — rigor,
# official, context, audience, importance, current, tags all come from the
# same research.
FASE0_FIELDS = (
    "authority", "rigor", "importance", "official", "current",
    "context", "audience", "tags", "note",
    # overrides that shape placement/meta:
    "category", "subcategory", "author", "source_url",
)

NS_OPF = {"opf": "http://www.idpf.org/2007/opf", "dc": "http://purl.org/dc/elements/1.1/"}
NS_CONTAINER = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}

BLOCK_TAGS = {"p", "div", "section", "article", "li", "blockquote", "pre"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
SKIP_TAGS = {"script", "style", "head", "nav", "title"}  # drop entirely

# Block-level text patterns to drop entirely (scrape artefacts, copyright
# footers, server-error boilerplate). Add new patterns here when new sources
# show up with their own noise.
BOILERPLATE_PATTERNS = [
    re.compile(r"^Server Error$", re.IGNORECASE),
    re.compile(r"There was a server error processing your request", re.IGNORECASE),
    re.compile(r"The error has been logged and will be investigated", re.IGNORECASE),
    re.compile(r"\bDeseret Book Company\.?\s*All Rights Reserved\b", re.IGNORECASE),
    re.compile(r"^home\s*\|\s*search\s*\|\s*browse", re.IGNORECASE),
    # bare 4-digit-year-only block (Deseret Book footer leaves the publication year alone)
    re.compile(r"^\d{4}$"),
]


def is_boilerplate(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    return any(p.search(t) for p in BOILERPLATE_PATTERNS)


# ---------- slug / normalization ----------

def slugify(text: str) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:80]


def lang_code(raw: str) -> str:
    v = (raw or "").strip().lower()
    if v.startswith("es"):
        return "es"
    if v.startswith("en"):
        return "en"
    return v[:2] or "en"


def load_fase0(slug: str, explicit_path: Path | None = None) -> dict:
    """Load structured Fase 0 sidecar for a work.

    Looks for:
      1. explicit_path if given
      2. proj/P4-corpus-expansion/fase0/{slug}.fase0.json

    Returns dict of FASE0_FIELDS (only keys present), or empty dict if absent.
    """
    path = explicit_path
    if path is None:
        path = FASE0_DIR / f"{slug}.fase0.json"
    if not path or not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"Fase 0 sidecar unreadable ({path}): {e}")
    if not isinstance(data, dict):
        raise SystemExit(f"Fase 0 sidecar must be a JSON object: {path}")
    return {k: v for k, v in data.items() if k in FASE0_FIELDS}


CHURCH_RE = re.compile(
    r"iglesia de jesucristo|church of jesus christ|lds church|latter-?day saints",
    re.IGNORECASE,
)


def normalize_author(raw: str) -> str:
    if not raw:
        return "(unknown)"
    r = re.sub(r"\s*\(\d+\)\s*$", "", raw.strip())
    rl = r.lower()
    if CHURCH_RE.search(rl):
        return "IJCSUD"
    if rl in {"desconocido", "unknown", "no specific author", "anonymous", ""}:
        return "(unknown)"
    if rl in {"various", "various authors", "varios", "varios autores"}:
        return "Various"
    # insert dot after bare single-letter initials
    parts = r.split()
    out = [p + "." if re.fullmatch(r"[A-ZÁÉÍÓÚÑ]", p) else p for p in parts]
    return " ".join(out)


# ---------- OPF reader ----------

def read_opf(zf: zipfile.ZipFile) -> tuple[dict, list[tuple[str, str]], str]:
    """Return (metadata, spine_hrefs, opf_dir).

    spine_hrefs: list of (spine_id, absolute-inside-zip path to XHTML).
    """
    container = ET.fromstring(zf.read("META-INF/container.xml"))
    rf = container.find(".//c:rootfile", NS_CONTAINER)
    opf_path = rf.attrib["full-path"]
    opf_dir = str(Path(opf_path).parent).replace("\\", "/")
    if opf_dir == ".":
        opf_dir = ""
    opf = ET.fromstring(zf.read(opf_path))

    meta: dict = {}
    for tag in ("title", "creator", "language", "publisher", "date", "identifier"):
        el = opf.find(f".//dc:{tag}", NS_OPF)
        if el is not None and el.text:
            meta[tag] = el.text.strip()

    manifest: dict[str, str] = {}
    for item in opf.findall(".//opf:manifest/opf:item", NS_OPF):
        manifest[item.attrib["id"]] = item.attrib["href"]

    spine = []
    for ir in opf.findall(".//opf:spine/opf:itemref", NS_OPF):
        sid = ir.attrib.get("idref")
        href = manifest.get(sid)
        if not href:
            continue
        full = f"{opf_dir}/{href}" if opf_dir else href
        spine.append((sid, full))

    return meta, spine, opf_dir


# ---------- HTML -> text ----------

FN_REF_RE = re.compile(r"#fn[-_]?(\d+)$", re.IGNORECASE)
FN_DEF_RE = re.compile(r"^\s*(\d+)\.\s+(.+)$", re.DOTALL)
CALIBRE_TOPIC_SPAN_RE = re.compile(r"/\s*$")


class _TextExtractor(HTMLParser):
    """Flatten HTML into typed blocks, preserving footnote refs and definitions.

    Output:
      self.blocks: [{type: 'heading'|'para'|'list', level, text, fn_refs}]
      self.footnotes: {number_str: definition_text}
      self.ref_order: [fn_number_str, ...] in appearance order

    Handles two Calibre patterns seen in this corpus:
      - topic-index prefix:  <p><span>TOPIC/</span>real text...  -> strip the span.
        The <span> has no attrs and its text ends in "/".
      - footnote definitions: <p class="chapter" id="1N1"><a>N. </a>body...</p>
        Routed to self.footnotes[N] instead of self.blocks.
      - inline footnote refs:  <a href="...#fn-N">N</a>  -> [^N] in body; N tracked.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[dict] = []
        self.footnotes: dict[str, str] = {}
        self.ref_order: list[str] = []
        self.first_bold: str | None = None  # first short <b>/<strong>, chapter-title fallback
        self.has_heading: bool = False
        self._stack: list[str] = []
        self._buf: list[str] = []
        self._fn_refs: list[str] = []
        self._skip_depth = 0
        self._span_stack: list[dict] = []
        self._in_fn_num: str | None = None
        self._bold_capture_start: int | None = None

    def _current_block_text_empty(self) -> bool:
        return not "".join(self._buf).strip()

    def _flush_block(self, kind: str, level: int = 0) -> None:
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self._buf.clear()
        refs = list(self._fn_refs)
        self._fn_refs = []
        if not text:
            return
        if is_boilerplate(text):
            return
        if self._in_fn_num is not None:
            # close the current footnote definition
            existing = self.footnotes.get(self._in_fn_num, "")
            self.footnotes[self._in_fn_num] = (existing + " " + text).strip()
            self._in_fn_num = None
            return
        # Detect footnote definition pattern: "N. rest"
        m = FN_DEF_RE.match(text)
        if m and kind == "para":
            num, body = m.group(1), m.group(2).strip()
            self.footnotes[num] = (self.footnotes.get(num, "") + " " + body).strip()
            return
        self.blocks.append({"type": kind, "level": level, "text": text, "fn_refs": refs})

    def handle_starttag(self, tag: str, attrs_list) -> None:
        tag = tag.lower()
        attrs = dict(attrs_list)

        if tag in SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return

        if tag == "br":
            self._buf.append(" ")
            return

        if tag in HEADING_TAGS:
            self.has_heading = True
            self._flush_block("para")
            self._stack.append(tag)
            return

        if tag in BLOCK_TAGS:
            self._flush_block("para")
            self._stack.append(tag)
            return

        if tag in ("b", "strong") and self.first_bold is None:
            self._bold_capture_start = len("".join(self._buf))
            return

        if tag == "span":
            # Track for Calibre topic-index stripping. A span is a candidate if
            # it has no attributes AND is the first content of a fresh paragraph.
            self._span_stack.append({
                "has_attrs": bool(attrs),
                "start_buf_len": len("".join(self._buf)),
                "is_first": self._current_block_text_empty(),
            })
            return

        if tag == "a":
            href = attrs.get("href", "")
            # Footnote *definition* anchor: <a id="fn-N"> with no href.
            # Mark the enclosing block so its flushed text is routed to footnotes[N].
            if not href:
                fid = attrs.get("id", "")
                m_def = FN_REF_RE.search("#" + fid) if fid else None
                if m_def:
                    self._in_fn_num = m_def.group(1)
                    return
            m = FN_REF_RE.search(href)
            if m:
                num = m.group(1)
                self._fn_refs.append(num)
                self.ref_order.append(num)
                self._buf.append(f"[^{num}]")
                # swallow the anchor's text (the visible number) to avoid duplication
                self._stack.append("a-fnref")
                return
            # Other anchors: pass through content
            return

        if tag == "sup":
            self._stack.append("sup")
            return

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag in SKIP_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if self._skip_depth:
            return

        if tag in HEADING_TAGS:
            level = int(tag[1])
            self._flush_block("heading", level=level)
            if self._stack and self._stack[-1] == tag:
                self._stack.pop()
            return

        if tag in BLOCK_TAGS:
            kind = "list" if tag == "li" else "para"
            self._flush_block(kind)
            if self._stack and self._stack[-1] == tag:
                self._stack.pop()
            return

        if tag in ("b", "strong") and self._bold_capture_start is not None:
            captured = "".join(self._buf)[self._bold_capture_start:]
            captured = re.sub(r"\s+", " ", captured).strip()
            if 3 <= len(captured) <= 80:
                self.first_bold = captured
            self._bold_capture_start = None
            return

        if tag == "span":
            if not self._span_stack:
                return
            info = self._span_stack.pop()
            if info["is_first"] and not info["has_attrs"]:
                buf_str = "".join(self._buf)
                span_text = buf_str[info["start_buf_len"]:]
                if CALIBRE_TOPIC_SPAN_RE.search(span_text):
                    # Drop the span content entirely
                    self._buf = [buf_str[:info["start_buf_len"]]]
            return

        if tag == "a":
            if self._stack and self._stack[-1] == "a-fnref":
                self._stack.pop()
            return

        if tag == "sup":
            if self._stack and self._stack[-1] == "sup":
                self._stack.pop()
            return

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        # Inside a footnote-ref anchor we already emitted [^N]; swallow inner text
        if self._stack and self._stack[-1] == "a-fnref":
            return
        self._buf.append(data)


def html_to_blocks(html: str) -> tuple[list[dict], dict[str, str], dict]:
    p = _TextExtractor()
    p.feed(html)
    p._flush_block("para")
    meta = {"has_heading": p.has_heading, "first_bold": p.first_bold, "ref_order": p.ref_order}
    return p.blocks, p.footnotes, meta


# ---------- chapter segmentation ----------

def segment_into_chapters(
    per_file: list[tuple[list[dict], dict[str, str], dict]],
    min_chars: int,
) -> list[dict]:
    """Group blocks into chapters and attach footnotes.

    Strategy:
      - If any file has h1/h2 headings, cut on h1/h2 as before.
      - If none do, fall back to one-chapter-per-spine-file with title from
        first <b>/<strong> in the file, or "Part N".

    Input: list of (blocks, footnotes, meta) per XHTML spine file.
    Output: [{title, text, fn_refs, footnotes: {N: def}}] in order.
    """
    # Use actual emitted heading blocks (not the raw parser flag) — empty
    # <h2>page-break</h2> tags set has_heading=True but produce no block.
    any_heading = any(
        b["type"] == "heading" and b["level"] in (1, 2)
        for blocks, _, _ in per_file
        for b in blocks
    )

    chapters: list[dict] = []
    current_title: str | None = None
    current_lines: list[str] = []
    current_refs: list[str] = []
    current_local_fn: dict[str, str] = {}
    # Running fallback for current chapter title when no explicit heading fires
    # before content starts (front-matter pages with bold-only "title" markup).
    pending_first_bold: str | None = None

    def flush() -> None:
        nonlocal pending_first_bold
        text = "\n\n".join(current_lines).strip()
        if len(text) < min_chars:
            pending_first_bold = None
            return
        used = {n: current_local_fn[n] for n in current_refs if n in current_local_fn}
        title = current_title or pending_first_bold or "Front Matter"
        chapters.append({
            "title": title,
            "text": text,
            "fn_refs": list(current_refs),
            "footnotes": used,
        })
        pending_first_bold = None

    for file_idx, (blocks, footnotes, fmeta) in enumerate(per_file, 1):
        current_local_fn.update(footnotes)

        # Remember this file's first bold in case current chapter has no title
        fb = fmeta.get("first_bold")
        if fb and pending_first_bold is None:
            pending_first_bold = fb

        if not any_heading:
            # Fallback: synthetic heading per spine file
            flush()
            current_title = fmeta.get("first_bold") or f"Part {file_idx}"
            current_lines = []
            current_refs = []

        for b in blocks:
            if b["type"] == "heading" and b["level"] in (1, 2):
                flush()
                current_title = b["text"]
                current_lines = []
                current_refs = []
            elif b["type"] == "heading" and b["level"] >= 3:
                current_lines.append(f"### {b['text']}")
            elif b["type"] == "list":
                current_lines.append(f"- {b['text']}")
            else:
                current_lines.append(b["text"])
            current_refs.extend(b.get("fn_refs") or [])
    flush()
    return chapters


# ---------- meta.json builder ----------

def build_meta(
    *,
    chapter_title: str,
    chapter_index: int,
    total_chapters: int,
    book_title: str,
    author: str,
    category: str,
    subcategory: str,
    lang: str,
    source_file: str,
    opf_meta: dict,
    fase0: dict | None = None,
) -> dict:
    """Full meta.json schema (aligned with corpus/en/books/articles-of-faith/*.meta.json).

    Fase 0 sidecar (if provided) fills authority/rigor/official/context/
    audience/importance/current/tags/note. Otherwise they stay null and
    authority_pending=True flags the work for Fase 0 research.
    """
    f = fase0 or {}
    meta = {
        "title": chapter_title,
        "author": f.get("author") or author,
        "book": book_title,
        "chapter": chapter_index if total_chapters > 1 else None,
        "total_chapters": total_chapters,
        "category": f.get("category") or category,
        "subcategory": f.get("subcategory") or (subcategory or None),
        "tags": f.get("tags") or [],
        "authority": f.get("authority"),
        "rigor": f.get("rigor"),
        "importance": f.get("importance"),
        "official": f.get("official"),
        "context": f.get("context"),
        "audience": f.get("audience"),
        "current": f.get("current"),
        "lang": {"en": "eng", "es": "spa"}.get(lang, lang),
        "source_url": f.get("source_url"),
        "source": "epub",
        "source_file": source_file,
        "opf_publisher": opf_meta.get("publisher") or None,
        "opf_date": (opf_meta.get("date")
                     if (opf_meta.get("date") and not opf_meta["date"].startswith("0101"))
                     else None),
        "opf_identifier": opf_meta.get("identifier") or None,
        "meta_description": None,
        "study_intro": None,
        "authority_pending": not bool(f),
        "note": f.get("note"),
    }
    return meta


# ---------- main extraction ----------

def extract_one(
    epub_path: Path,
    *,
    out_root: Path,
    lang_override: str | None,
    category: str,
    subcategory: str | None,
    slug_override: str | None,
    author_override: str | None,
    min_chapter_chars: int,
    max_single_file_kb: int,
    fase0_path: Path | None = None,
) -> Path:
    with zipfile.ZipFile(epub_path) as zf:
        opf_meta, spine, opf_dir = read_opf(zf)

        title = opf_meta.get("title") or epub_path.stem
        author = author_override or normalize_author(opf_meta.get("creator", ""))
        lang = lang_override or lang_code(opf_meta.get("language", ""))
        slug = slug_override or slugify(title)
        if not slug:
            slug = slugify(epub_path.stem)

        # Fase 0 sidecar (authority, rigor, official, context, audience, tags, ...)
        fase0 = load_fase0(slug, explicit_path=fase0_path)
        if fase0.get("category"):
            category = fase0["category"]
        if "subcategory" in fase0:
            subcategory = fase0["subcategory"]
        if fase0.get("author"):
            author = fase0["author"]

        per_file: list[tuple[list[dict], dict[str, str], dict]] = []
        for sid, href in spine:
            try:
                data = zf.read(href)
            except KeyError:
                continue
            html = data.decode("utf-8", errors="replace")
            blocks, fns, fmeta = html_to_blocks(html)
            per_file.append((blocks, fns, fmeta))

        chapters = segment_into_chapters(per_file, min_chapter_chars)
        if not chapters:
            raise SystemExit(f"No content extracted from {epub_path.name}")

        total_chars = sum(len(c["text"]) for c in chapters)
        single_file = len(chapters) == 1 or total_chars <= max_single_file_kb * 1024

        target_dir = out_root / lang / category / (subcategory or "") / slug
        # Clean empty-component if subcategory is None
        target_dir = Path(*[p for p in target_dir.parts if p != ""])
        target_dir.mkdir(parents=True, exist_ok=True)

        if single_file:
            chapter_title = chapters[0]["title"] if chapters else title
            parts = []
            merged_fns: dict[str, str] = {}
            for c in chapters:
                parts.append(c["text"])
                merged_fns.update(c.get("footnotes") or {})
            text = "\n\n".join(parts)
            if merged_fns:
                text += "\n\n---\nNotas:\n" + "\n".join(
                    f"[^{n}] {merged_fns[n]}" for n in sorted(merged_fns, key=lambda x: int(x) if x.isdigit() else 0)
                )
            (target_dir / f"{slug}.txt").write_text(text + "\n", encoding="utf-8")
            meta = build_meta(
                chapter_title=title,
                chapter_index=1,
                total_chapters=1,
                book_title=title,
                author=author,
                category=category,
                subcategory=subcategory or "",
                lang=lang,
                source_file=str(epub_path.relative_to(ROOT)).replace("\\", "/"),
                opf_meta=opf_meta,
                fase0=fase0,
            )
            (target_dir / f"{slug}.meta.json").write_text(
                json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
        else:
            for i, ch in enumerate(chapters, 1):
                prefix = f"{i:02d}"
                ch_slug = slugify(ch["title"]) or f"chapter-{i}"
                base = f"{prefix}-{ch_slug}"
                ch_text = ch["text"]
                fns = ch.get("footnotes") or {}
                if fns:
                    ch_text += "\n\n---\nNotas:\n" + "\n".join(
                        f"[^{n}] {fns[n]}"
                        for n in sorted(fns, key=lambda x: int(x) if x.isdigit() else 0)
                    )
                (target_dir / f"{base}.txt").write_text(ch_text + "\n", encoding="utf-8")
                meta = build_meta(
                    chapter_title=ch["title"],
                    chapter_index=i,
                    total_chapters=len(chapters),
                    book_title=title,
                    author=author,
                    category=category,
                    subcategory=subcategory or "",
                    lang=lang,
                    source_file=str(epub_path.relative_to(ROOT)).replace("\\", "/"),
                    opf_meta=opf_meta,
                    fase0=fase0,
                )
                (target_dir / f"{base}.meta.json").write_text(
                    json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )

        return target_dir


def promote(preview_dir: Path) -> Path:
    """Move epub/_preview/<lang>/<category>/<slug> -> corpus/<lang>/<category>/<slug>."""
    if not preview_dir.exists():
        raise SystemExit(f"Preview dir not found: {preview_dir}")
    rel = preview_dir.relative_to(PREVIEW)  # <lang>/<category>/[<sub>/]<slug>
    target = CORPUS / rel
    if target.exists():
        raise SystemExit(f"Target already exists, refusing to overwrite: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(preview_dir), str(target))
    return target


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("epub", nargs="?", help="EPUB file to extract (omit with --promote)")
    ap.add_argument("--lang", choices=("en", "es"))
    ap.add_argument("--category", help="Target corpus category (books, manuals, ...)")
    ap.add_argument("--subcategory", default=None)
    ap.add_argument("--slug", default=None)
    ap.add_argument("--author", default=None)
    ap.add_argument("--apply", action="store_true", help="Write directly to corpus/ (skip preview)")
    ap.add_argument("--promote", metavar="PREVIEW_DIR", help="Move a previewed work into corpus/")
    ap.add_argument("--min-chapter-chars", type=int, default=80)
    ap.add_argument("--max-single-file-kb", type=int, default=10)
    ap.add_argument("--fase0", metavar="PATH",
                    help="Explicit Fase 0 sidecar .json (overrides slug-based lookup)")
    args = ap.parse_args()

    if args.promote:
        target = promote(Path(args.promote).resolve())
        print(f"Promoted to: {target.relative_to(ROOT)}")
        return 0

    if not args.epub:
        ap.error("provide an EPUB file, or use --promote <preview_dir>")
    if not args.category:
        ap.error("--category is required")

    epub_path = Path(args.epub).resolve()
    if not epub_path.exists():
        ap.error(f"file not found: {epub_path}")

    out_root = CORPUS if args.apply else PREVIEW
    target = extract_one(
        epub_path,
        out_root=out_root,
        lang_override=args.lang,
        category=args.category,
        subcategory=args.subcategory,
        slug_override=args.slug,
        author_override=args.author,
        min_chapter_chars=args.min_chapter_chars,
        max_single_file_kb=args.max_single_file_kb,
        fase0_path=Path(args.fase0).resolve() if args.fase0 else None,
    )
    rel = target.relative_to(ROOT)
    mode = "APPLY (corpus/)" if args.apply else "PREVIEW"
    print(f"[{mode}] wrote -> {rel}")
    files = sorted(target.glob("*"))
    print(f"  {len(files)} files, {sum(f.stat().st_size for f in files)} bytes total")
    for f in files[:6]:
        print(f"  - {f.name}")
    if len(files) > 6:
        print(f"  ... (+{len(files)-6} more)")
    if not args.apply:
        print(f"\nReview, then promote:")
        print(f"  python scripts/epub_extract.py --promote {rel.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

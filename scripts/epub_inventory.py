"""
EPUB inventory & triage for epub/!Ready -> Alejandria corpus.

Read-only. Produces:
  epub/_inventory.csv       one row per file
  epub/_triage.md           buckets summary

No corpus writes, no ingestion. Stdlib only.

Buckets:
  - basura        : not a real epub (bad magic, PDF/QXD renamed, zero size)
  - duplicado-fs  : duplicate by SHA-256 inside !Ready (sufijo (1), etc.)
  - propio        : authored by Juan Pablo Marichal (do not re-ingest)
  - fuera-alcance : Rose Publishing / Thomas Nelson / similar non-LDS reference
  - duplicado-corpus : title slug already present under corpus/{lang}/**
  - revisar       : autor/título "Desconocido" o vacío
  - nuevo         : candidate for ingestion, propose dest path
"""
from __future__ import annotations
import csv
import hashlib
import os
import re
import sys
import unicodedata
import zipfile
import json
from difflib import SequenceMatcher
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
EPUB_DIR = ROOT / "epub" / "!Ready"
CORPUS = ROOT / "corpus"
OUT_CSV = ROOT / "epub" / "_inventory.csv"
OUT_MD = ROOT / "epub" / "_triage.md"

NS = {
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "container": "urn:oasis:names:tc:opendocument:xmlns:container",
}

OWN_AUTHOR_TOKENS = ("juan pablo marichal",)

FUZZY_TITLE_THRESHOLD = 0.88
FUZZY_AUTHOR_THRESHOLD = 0.80


def slugify(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:80]


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def is_real_epub(path: Path) -> tuple[bool, str]:
    """Validate epub: zip + mimetype=application/epub+zip."""
    try:
        with path.open("rb") as f:
            head = f.read(4)
        if head[:2] != b"PK":
            # check if it's actually a PDF
            if head[:4] == b"%PDF":
                return False, "es PDF renombrado"
            return False, "no es zip"
        with zipfile.ZipFile(path) as zf:
            try:
                mt = zf.read("mimetype").decode("ascii", "ignore").strip()
            except KeyError:
                return False, "falta mimetype"
            if mt != "application/epub+zip":
                return False, f"mimetype={mt!r}"
            return True, ""
    except zipfile.BadZipFile:
        return False, "zip corrupto"
    except Exception as e:
        return False, f"error:{e.__class__.__name__}"


def read_opf_meta(path: Path) -> dict:
    """Extract title/creator/language/date from the OPF inside the epub."""
    meta = {"title": "", "creator": "", "language": "", "publisher": "", "date": ""}
    try:
        with zipfile.ZipFile(path) as zf:
            # find OPF via container.xml
            try:
                container = zf.read("META-INF/container.xml")
            except KeyError:
                return meta
            root = ET.fromstring(container)
            rf = root.find(".//container:rootfile", NS)
            if rf is None:
                return meta
            opf_path = rf.attrib.get("full-path")
            if not opf_path:
                return meta
            opf_xml = zf.read(opf_path)
            opf = ET.fromstring(opf_xml)
            for tag in ("title", "creator", "language", "publisher", "date"):
                el = opf.find(f".//dc:{tag}", NS)
                if el is not None and el.text:
                    meta[tag] = el.text.strip()
    except Exception:
        pass
    return meta


def lang_code(value: str) -> str:
    if not value:
        return ""
    v = value.strip().lower()
    if v.startswith("es"):
        return "es"
    if v.startswith("en"):
        return "en"
    return v[:5]


def detect_lang_from_filename(name: str) -> str:
    # crude fallback: ascii-heavy filenames lean EN; presence of accents/spanish words EN_NEAR_LATIN -> ES
    if re.search(r"[áéíóúñ¿¡]", name, re.IGNORECASE):
        return "es"
    spanish_hits = sum(
        1 for w in (" de ", " la ", " los ", " del ", " santos ", " profeta ", " iglesia ")
        if w in f" {name.lower()} "
    )
    if spanish_hits >= 2:
        return "es"
    return "en"


def build_corpus_index() -> list[dict]:
    """Return list of corpus works: {slug, path, title, author, lang, category}."""
    works: list[dict] = []
    if not CORPUS.exists():
        return works
    for lang_dir in CORPUS.iterdir():
        if not lang_dir.is_dir() or lang_dir.name not in ("en", "es"):
            continue
        for cat in lang_dir.iterdir():
            if not cat.is_dir():
                continue
            for item in cat.iterdir():
                if not item.is_dir():
                    continue
                # Pull first .meta.json (any depth) for canonical title/author
                title = item.name.replace("-", " ")
                author = ""
                try:
                    meta_files = list(item.rglob("*.meta.json"))
                    if meta_files:
                        with meta_files[0].open(encoding="utf-8") as f:
                            m = json.load(f)
                        title = m.get("book") or m.get("title") or title
                        author = m.get("author") or ""
                except Exception:
                    pass
                works.append({
                    "slug": slugify(item.name),
                    "path": str(item.relative_to(ROOT)),
                    "title": title,
                    "author": author,
                    "lang": lang_dir.name,
                    "category": cat.name,
                })
    return works


def fuzzy_match_corpus(title: str, creator: str, lang: str, works: list[dict]) -> tuple[str, float, str]:
    """Return (matched_path, score, reason) or ('', 0, '')."""
    if not title:
        return "", 0.0, ""
    t_slug = slugify(title)
    c_slug = slugify(creator)
    best = ("", 0.0, "")
    for w in works:
        if lang and w["lang"] and w["lang"] != lang:
            continue
        # Exact slug match wins
        if w["slug"] == t_slug:
            return w["path"], 1.0, "slug exacto"
        t_ratio = SequenceMatcher(None, t_slug, w["slug"]).ratio()
        if t_ratio < FUZZY_TITLE_THRESHOLD:
            continue
        a_ratio = 1.0
        if c_slug and w["author"]:
            a_ratio = SequenceMatcher(None, c_slug, slugify(w["author"])).ratio()
        if a_ratio < FUZZY_AUTHOR_THRESHOLD:
            continue
        score = (t_ratio + a_ratio) / 2
        if score > best[1]:
            best = (w["path"], score, f"título~{t_ratio:.2f} autor~{a_ratio:.2f}")
    return best


def classify(row: dict) -> str:
    if row["bucket_pre"]:
        return row["bucket_pre"]
    creator_l = row["creator"].lower()
    if any(t in creator_l for t in OWN_AUTHOR_TOKENS):
        return "propio"
    if not row["title"]:
        return "revisar"
    if row["corpus_match"]:
        return "duplicado-corpus"
    return "nuevo"


def propose_dest(row: dict) -> str:
    lang = row["lang"] or "en"
    title_slug = slugify(row["title"]) or slugify(Path(row["file"]).stem)
    creator_l = row["creator"].lower()
    publisher_l = row["publisher"].lower()
    if "iglesia de jesucristo" in creator_l or "iglesia de jesucristo" in publisher_l:
        cat = "manuals"
    elif "biograph" in row["title"].lower() or "autobiograph" in row["title"].lower() or "vida de" in row["title"].lower():
        cat = "biographies"
    else:
        cat = "books"
    return f"corpus/{lang}/{cat}/{title_slug}/"


def main() -> int:
    if not EPUB_DIR.exists():
        print(f"ERROR: {EPUB_DIR} not found", file=sys.stderr)
        return 1

    files = sorted(p for p in EPUB_DIR.iterdir() if p.is_file())
    print(f"Scanning {len(files)} files in {EPUB_DIR} ...", file=sys.stderr)

    corpus_works = build_corpus_index()
    print(f"Corpus index: {len(corpus_works)} works", file=sys.stderr)

    rows = []
    seen_hash: dict[str, str] = {}

    for i, p in enumerate(files, 1):
        if i % 100 == 0:
            print(f"  {i}/{len(files)} ...", file=sys.stderr)
        row = {
            "file": p.name,
            "size": p.stat().st_size,
            "sha256": "",
            "title": "",
            "creator": "",
            "language": "",
            "publisher": "",
            "date": "",
            "lang": "",
            "title_slug": "",
            "corpus_match": "",
            "bucket_pre": "",
            "bucket": "",
            "dest_proposed": "",
            "note": "",
        }

        if p.stat().st_size == 0:
            row["bucket_pre"] = "basura"
            row["note"] = "tamaño 0"
        else:
            ok, why = is_real_epub(p)
            if not ok:
                row["bucket_pre"] = "basura"
                row["note"] = why

        if not row["bucket_pre"]:
            try:
                row["sha256"] = sha256_of(p)
            except Exception as e:
                row["bucket_pre"] = "basura"
                row["note"] = f"hash error:{e.__class__.__name__}"

            if row["sha256"]:
                if row["sha256"] in seen_hash:
                    row["bucket_pre"] = "duplicado-fs"
                    row["note"] = f"copia de {seen_hash[row['sha256']]}"
                else:
                    seen_hash[row["sha256"]] = p.name

            meta = read_opf_meta(p)
            row.update({
                "title": meta["title"],
                "creator": meta["creator"],
                "language": meta["language"],
                "publisher": meta["publisher"],
                "date": meta["date"],
            })
            row["lang"] = lang_code(meta["language"]) or detect_lang_from_filename(p.name)
            row["title_slug"] = slugify(meta["title"]) or slugify(p.stem)
            mpath, mscore, mreason = fuzzy_match_corpus(
                meta["title"], meta["creator"], row["lang"], corpus_works
            )
            if mpath:
                row["corpus_match"] = mpath
                row["note"] = mreason

        row["bucket"] = classify(row)
        if row["bucket"] == "nuevo":
            row["dest_proposed"] = propose_dest(row)
        rows.append(row)

    # Write CSV
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Triage summary
    from collections import Counter, defaultdict
    bucket_count = Counter(r["bucket"] for r in rows)
    by_bucket = defaultdict(list)
    for r in rows:
        by_bucket[r["bucket"]].append(r)

    lines = []
    lines.append(f"# EPUB triage — {len(rows)} archivos\n")
    lines.append(f"Fuente: `{EPUB_DIR.relative_to(ROOT)}`\n")
    lines.append("## Buckets\n")
    lines.append("| bucket | n | descripción |")
    lines.append("|---|---:|---|")
    descs = {
        "basura": "no es epub válido (PDF renombrado, zip corrupto, tamaño 0)",
        "duplicado-fs": "mismo SHA-256 que otro archivo del lote",
        "propio": "autoría Juan Pablo Marichal — no re-ingestar",
        "fuera-alcance": "Rose Publishing / Thomas Nelson — decisión editorial",
        "duplicado-corpus": "ya existe slug equivalente en `corpus/`",
        "revisar": "metadata incompleta (sin título / autor)",
        "nuevo": "candidato a ingreso",
    }
    for b in ("nuevo","duplicado-corpus","fuera-alcance","propio","duplicado-fs","basura","revisar"):
        lines.append(f"| {b} | {bucket_count.get(b,0)} | {descs.get(b,'')} |")
    lines.append("")

    # Top creators in 'nuevo' for batching
    lines.append("## Lotes sugeridos por autor (bucket=nuevo)\n")
    nuevo_creators = Counter(r["creator"] or "(sin autor)" for r in by_bucket["nuevo"])
    lines.append("| autor | n |")
    lines.append("|---|---:|")
    for a, n in nuevo_creators.most_common(40):
        lines.append(f"| {a} | {n} |")
    lines.append("")

    # Sample basura
    lines.append("## Muestra `basura` (primeras 20)\n")
    for r in by_bucket["basura"][:20]:
        lines.append(f"- `{r['file']}` — {r['note']}")
    lines.append("")

    # Sample duplicado-corpus
    lines.append("## Muestra `duplicado-corpus` (primeras 20)\n")
    for r in by_bucket["duplicado-corpus"][:20]:
        lines.append(f"- `{r['file']}` → `{r['corpus_match']}`")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nWrote {OUT_CSV.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}", file=sys.stderr)
    print("Bucket counts:", dict(bucket_count), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Smoke test for epub_extract.py on diverse EPUB typologies.

Runs extract on representative files from epub/!Ready, writes to
epub/_smoke/<typology>/, and prints a report card:
  - chapters detected
  - total body chars
  - footnotes captured (inline refs + definitions)
  - text-residual red flags (Calibre leftovers, empty chapters, dup prefixes)

Read-only with respect to corpus/. Safe to re-run.
"""
from __future__ import annotations
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPUB_DIR = ROOT / "epub" / "!Ready"
SMOKE_ROOT = ROOT / "epub" / "_smoke"
EXTRACTOR = ROOT / "scripts" / "epub_extract.py"

CASES = [
    # (typology, filename_prefix, lang, category)
    ("ijcsud_es_manual", "Antiguo Testamento, guía para el miembro", "es", "manuals"),
    ("various_en_anthology", "Abrahamic Covenant - The Encyclopedia of Mormonism", "en", "reference"),
    ("rose_short_single", "10 names of God", "en", "reference"),
    ("es_individual_author", "1844, la última asignación del profeta", "es", "history"),
]

# Red-flag regexes applied to extracted text
REDFLAGS = {
    "calibre_topic_prefix": re.compile(r"^[A-Z][\w ,']{2,40}/[A-Z]", re.MULTILINE),
    "raw_html_tag": re.compile(r"</?(p|div|span|a|sup|b|i|h[1-6])\b[^>]*>", re.IGNORECASE),
    "calibre_class_leak": re.compile(r"calibre\d+"),
    # "consecutive_footnote_nums" removed: false-positive on scripture refs ("Moisés 1:27-42; 2-3 3 Estudie")
}


def find_epub(prefix: str) -> Path | None:
    for p in EPUB_DIR.iterdir():
        if p.name.startswith(prefix):
            return p
    # Accent-insensitive fallback
    low = prefix.lower()
    for p in EPUB_DIR.iterdir():
        if p.name.lower().startswith(low[:20]):
            return p
    return None


def analyze_dir(d: Path) -> dict:
    txt_files = sorted(d.glob("**/*.txt"))
    meta_files = sorted(d.glob("**/*.meta.json"))
    total_chars = 0
    total_inline_refs = 0
    total_fn_defs = 0
    flags = {k: 0 for k in REDFLAGS}
    empty_chapters = 0
    samples: dict[str, list[str]] = {k: [] for k in REDFLAGS}

    for t in txt_files:
        s = t.read_text(encoding="utf-8", errors="replace")
        total_chars += len(s)
        if not s.strip():
            empty_chapters += 1
        # footnote markers in body vs Notas section
        body, _, notas = s.partition("\n---\nNotas:")
        total_inline_refs += len(re.findall(r"\[\^(\d+)\]", body))
        total_fn_defs += len(re.findall(r"^\[\^(\d+)\]", notas, re.MULTILINE))
        for name, pat in REDFLAGS.items():
            for m in pat.finditer(body):
                flags[name] += 1
                if len(samples[name]) < 2:
                    snippet = body[max(0, m.start()-30):m.end()+30].replace("\n", " ")
                    samples[name].append(snippet)

    return {
        "txt_count": len(txt_files),
        "meta_count": len(meta_files),
        "total_chars": total_chars,
        "inline_refs": total_inline_refs,
        "fn_defs": total_fn_defs,
        "empty_chapters": empty_chapters,
        "flags": flags,
        "samples": samples,
    }


def main() -> int:
    if not EXTRACTOR.exists():
        print("extractor missing", file=sys.stderr)
        return 1
    if SMOKE_ROOT.exists():
        shutil.rmtree(SMOKE_ROOT)
    SMOKE_ROOT.mkdir(parents=True)

    report: list[tuple[str, str, dict | str]] = []
    for typology, prefix, lang, category in CASES:
        epub = find_epub(prefix)
        if not epub:
            report.append((typology, "(not found)", f"no epub starting with {prefix!r}"))
            continue
        out_dir = SMOKE_ROOT / typology
        out_dir.mkdir(parents=True, exist_ok=True)
        # Run extractor writing to smoke dir (abuse --apply with a staged root via env hack)
        # Simpler: call extract_one via subprocess to PREVIEW, then move.
        cmd = [
            sys.executable, str(EXTRACTOR),
            str(epub),
            "--lang", lang,
            "--category", f"_smoke_{typology}",
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            report.append((typology, epub.name, "TIMEOUT"))
            continue
        if r.returncode != 0:
            report.append((typology, epub.name, f"ERROR rc={r.returncode}\n{r.stderr[-500:]}"))
            continue
        # Extractor wrote to epub/_preview/<lang>/_smoke_<typology>/<slug>/
        preview_dir = ROOT / "epub" / "_preview" / lang / f"_smoke_{typology}"
        slug_dirs = [p for p in preview_dir.iterdir() if p.is_dir()] if preview_dir.exists() else []
        if not slug_dirs:
            report.append((typology, epub.name, f"no output found in {preview_dir}"))
            continue
        # Move into smoke dir
        target = out_dir / slug_dirs[0].name
        shutil.move(str(slug_dirs[0]), str(target))
        shutil.rmtree(preview_dir.parent, ignore_errors=True) if not any(preview_dir.parent.iterdir()) else None
        report.append((typology, epub.name, analyze_dir(target)))

    # Print report
    print("=" * 78)
    print("EPUB EXTRACTOR SMOKE REPORT")
    print("=" * 78)
    for typology, fname, info in report:
        print(f"\n### {typology}")
        print(f"file: {fname}")
        if isinstance(info, str):
            print(f"  status: {info}")
            continue
        print(f"  chapters written : {info['txt_count']}")
        print(f"  meta files       : {info['meta_count']}")
        print(f"  body chars total : {info['total_chars']:,}")
        print(f"  inline fn refs   : {info['inline_refs']}")
        print(f"  fn definitions   : {info['fn_defs']}  (pair rate: {info['fn_defs']}/{info['inline_refs'] or '-'})")
        print(f"  empty chapters   : {info['empty_chapters']}")
        print(f"  red flags:")
        for k, n in info["flags"].items():
            mark = "X" if n else "."
            print(f"    {mark} {k:26s} {n}")
            if n and info["samples"][k]:
                for s in info["samples"][k][:1]:
                    print(f"        e.g. ...{s}...")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

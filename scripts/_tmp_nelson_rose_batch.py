#!/usr/bin/env python
"""Thomas Nelson (76) + Rose Publishing (28) — evangelical bible charts/reference.

Homogeneous treatment: category=reference, authority=15, evangelical, non-LDS.
Dedupe numeric-suffix variants first (e.g. 'Locations...10' vs 'Locations...' = dup).
Titles used as slugs; no bespoke fase0 note beyond title + publisher.
"""
import subprocess, sys, json, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def base_title(stem):
    # Strip author suffix
    m = re.match(r'^(.*?)\s*-\s*(?:Thomas Nelson|Rose Publishing)(?:\.epub)?$', stem)
    raw = m.group(1) if m else stem
    # Strip trailing digits (page-number suffix)
    return re.sub(r'\s*\d+$', '', raw).strip()

# Collect files by (author, normalized-base-title)
groups = {}
all_files = []
for p in sorted(READY.iterdir()):
    if not p.is_file() or p.suffix.lower() != '.epub': continue
    name = p.name
    if ' - Thomas Nelson.epub' in name:
        author = 'Thomas Nelson'
    elif ' - Rose Publishing.epub' in name:
        author = 'Rose Publishing'
    else:
        continue
    stem = p.stem
    base = base_title(stem)
    key = (author, norm(base))
    groups.setdefault(key, []).append(p)
    all_files.append(p)

# Archive duplicates (keep longest filename = most informative, or prefer no-digit)
archived_dups = 0
keep_files = []
for key, files in groups.items():
    if len(files) > 1:
        # Prefer the file whose base matches without trailing digits
        files_sorted = sorted(files, key=lambda x: (bool(re.search(r'\d+\.epub$', x.name)), -len(x.name)))
        keep = files_sorted[0]
        for f in files_sorted[1:]:
            f.rename(DONE / f.name)
            archived_dups += 1
        keep_files.append(keep)
    else:
        keep_files.append(files[0])

print(f'numeric-suffix dups archived: {archived_dups}')
print(f'unique to incorporate: {len(keep_files)}')

ok = 0
broken = []
for p in sorted(keep_files):
    stem = p.stem
    name = p.name
    if ' - Thomas Nelson.epub' in name:
        author = 'Thomas Nelson'
        pub = 'thomas-nelson'
    else:
        author = 'Rose Publishing'
        pub = 'rose-publishing'

    base = base_title(stem)
    lang = 'en'
    # Detect Spanish (heuristic: has ñ/accented chars or Spanish words)
    if re.search(r'[áéíóúñÑÁÉÍÓÚ]', base) or any(w in base.lower() for w in [
        'moneda', 'jesús', 'santo', 'dios', 'versión', 'doctrina', 'iglesia', 'conoció'
    ]):
        lang = 'es'
    slug = norm(base) + '-' + pub
    slug = slug[:80]
    if not slug or slug == '-' + pub:
        continue

    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    fase0.write_text(json.dumps({
        "authority": 15, "rigor": 60, "importance": "opcional",
        "official": False, "current": True, "context": "book-private",
        "audience": "all",
        "tags": ["evangelical", "bible-reference", "chart", "non-lds", pub],
        "category": "reference",
        "author": author,
        "source_url": None,
        "note": f"{author} bible chart/reference: {base}.",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    cmd = [sys.executable, str(EXTRACT), str(p),
           "--lang", lang, "--category", "reference", "--apply",
           "--slug", slug, "--author", author, "--fase0", str(fase0)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        p.rename(DONE / p.name)
    else:
        broken.append((p.name, r.stderr[-100:] if r.stderr else "?"))

print(f'\nNelson/Rose batch: {ok} OK, {len(broken)} broken')
for fn, err in broken[:15]:
    print(f'  - {fn[:60]}')
print(f'\n!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}')

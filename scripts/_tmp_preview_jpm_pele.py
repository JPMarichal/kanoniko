#!/usr/bin/env python
"""Extract JPM + Pelé works to preview + sample first chapter for triage."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
PREVIEW = ROOT / "epub" / "_preview" / "jpm_pele"
EXTRACT = ROOT / "scripts" / "epub_extract.py"
PREVIEW.mkdir(parents=True, exist_ok=True)

# Extract in preview mode (no --apply). Use --slug from filename stem.
import re
for src in sorted(READY.iterdir()):
    if not src.suffix.lower() == ".epub":
        continue
    stem = src.stem
    slug = re.sub(r'[^a-z0-9]+', '-', stem.lower()).strip('-')[:60]
    out = PREVIEW / slug
    if out.exists():
        print(f"  skip (exists): {slug}")
        continue
    cmd = [sys.executable, str(EXTRACT), str(src),
           "--lang", "es", "--category", "books", "--slug", slug,
           "--author", "JPM" if "Marichal" in stem else "Pele"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    # preview dir name may differ — find it
    print(f"  {'OK' if r.returncode==0 else 'FAIL'} {stem[:60]}")

# Now sample each preview dir
print("\n=== CONTENT SAMPLES ===")
preview_root = ROOT / "epub" / "_preview" / "es" / "books"
if preview_root.exists():
    for pdir in sorted(preview_root.iterdir()):
        if not pdir.is_dir():
            continue
        txts = sorted(pdir.glob("*.txt"))
        if not txts:
            print(f"\n### {pdir.name}: EMPTY")
            continue
        total_chars = sum(t.stat().st_size for t in txts)
        first = txts[0].read_text(encoding="utf-8", errors="replace")[:400]
        print(f"\n### {pdir.name}  [{len(txts)} chunks, ~{total_chars//1024}KB]")
        print(f"  first chunk: {first[:300]}")

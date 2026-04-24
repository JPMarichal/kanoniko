"""Preview the final 16 JPM+Pelé epubs to decide per-work."""
import subprocess, sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
EXTRACT = ROOT / "scripts" / "epub_extract.py"
PREV = ROOT / "epub" / "_preview"
if PREV.exists(): shutil.rmtree(PREV)

import re
for src in sorted(READY.iterdir()):
    if not src.suffix.lower() == ".epub": continue
    stem = src.stem
    slug = re.sub(r'[^a-z0-9]+', '-', stem.lower()).strip('-')[:50]
    cmd = [sys.executable, str(EXTRACT), str(src),
           "--lang", "es", "--category", "books",
           "--slug", slug, "--author", "PREVIEW"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    # Find output dir
    for pdir in (ROOT / "epub" / "_preview").rglob(slug):
        if pdir.is_dir():
            txts = sorted(pdir.glob("*.txt"))
            if txts:
                total = sum(t.stat().st_size for t in txts)
                first = txts[0].read_text(encoding='utf-8', errors='replace')[:500]
                print(f"\n=== {stem[:70]}")
                print(f"    {len(txts)} chunks, ~{total//1024}KB")
                print(f"    head: {first[:300]}")
            break

#!/usr/bin/env python
"""Reincorporate 5 works: Aesop, Tacitus x2, Boethius, Confucius.
Epubs already in !Done — extract in-place, no move."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

WORKS = [
    ("Aesop's Fables - Esopo.epub",
     "aesops-fables", "Aesop", 25, 70, "importante",
     "reference", "en", ["classical", "greek", "fables", "moral-literature", "primary-source", "illustration-source"],
     "Aesop (c. 620-564 BC) corpus of fables. Moral/illustrative value for gospel teaching (cf. Savior's parables)."),
    ("Annals - Tacitus.epub",
     "annals-tacitus", "Tacitus", 40, 85, "importante",
     "history", "en", ["classical", "roman-history", "1st-century", "primary-source", "christus-reference", "neronian-persecution", "nt-context"],
     "Tacitus (c. 56-120). Annales, c. 115-120. Contains 15.44 reference to 'Christus' under Pontius Pilate — key extra-biblical evidence for historical Jesus, and first Neronian persecution."),
    ("Histories - Tacitus.epub",
     "histories-tacitus", "Tacitus", 35, 80, "importante",
     "history", "en", ["classical", "roman-history", "1st-century", "primary-source", "post-apostolic-era"],
     "Tacitus. Historiae, c. 100-110. Covers 69-96 AD — post-apostolic Roman context."),
    ("Consolation of Philosophy - Boethius.epub",
     "consolation-of-philosophy-boethius", "Boethius", 35, 85, "importante",
     "reference", "en", ["late-antiquity", "6th-century", "christian-philosophy", "providence", "free-will", "primary-source"],
     "Boethius (c. 480-524), Christian philosopher martyred for faith. De Consolatione Philosophiae, c. 524. On providence, free will, evil — foundational Christian theodicy."),
    ("Analects - Confucius.epub",
     "analects-confucius", "Confucius", 30, 75, "importante",
     "reference", "en", ["classical", "chinese", "confucian", "ethics", "primary-source", "interreligious", "universal-moral-wisdom"],
     "Confucius (551-479 BC). Analects (Lunyu). Universal moral wisdom — cited in LDS interreligious discourse (Alma 29:8, 'to all nations')."),
]

ok = 0
broken = []
for fn, slug, author, auth, rigor, imp, cat, lang, tags, note in WORKS:
    src = DONE / fn
    if not src.exists():
        broken.append((fn, "MISSING in !Done"))
        continue
    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    fase0.write_text(json.dumps({
        "authority": auth, "rigor": rigor, "importance": imp,
        "official": False, "current": True, "context": "book-private",
        "audience": "adult", "tags": tags, "category": cat,
        "author": author, "source_url": None, "note": note,
    }, indent=2), encoding="utf-8")
    cmd = [sys.executable, str(EXTRACT), str(src),
           "--lang", lang, "--category", cat, "--apply",
           "--slug", slug, "--author", author, "--fase0", str(fase0)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        print(f"  OK {slug}")
    else:
        broken.append((fn, r.stderr[-150:] if r.stderr else "?"))
        print(f"  BROKEN {slug}")

print(f"\nReincorp 5: {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")

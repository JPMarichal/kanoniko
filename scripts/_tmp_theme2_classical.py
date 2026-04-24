#!/usr/bin/env python
"""Theme 2: Classical antiquity (14 works, individually curated)."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

WORKS = [
    ("Aeneid - Virgil.epub",
     "aeneid-virgil", "Virgil", 25, 80, "opcional",
     "reference", "en", ["classical", "roman-epic", "1st-century-bc", "primary-source", "latin-literature"],
     "Virgil (70-19 BC). Aeneid, Rome's national epic."),
    ("Aesop's Fables - Esopo.epub",
     "aesops-fables", "Aesop", 20, 65, "opcional",
     "reference", "en", ["classical", "greek", "fables", "moral-literature", "primary-source"],
     "Aesop (c. 620-564 BC) corpus of fables. Traditional attribution."),
    ("Agamenón - Esquilo.epub",
     "agamenon-esquilo", "Aeschylus", 25, 80, "opcional",
     "reference", "es", ["classical", "greek-tragedy", "5th-century-bc", "primary-source", "oresteia"],
     "Aeschylus (525-456 BC). Agamemnon, first play of the Oresteia trilogy, 458 BC."),
    ("Analects - Confucius.epub",
     "analects-confucius", "Confucius", 25, 75, "opcional",
     "reference", "en", ["classical", "chinese", "confucian", "ethics", "primary-source"],
     "Confucius (551-479 BC). Analects (Lunyu), compiled by disciples."),
    ("Antiquities of the Jews - Flavius Josephus.epub",
     "antiquities-of-the-jews-josephus", "Flavius Josephus", 40, 85, "importante",
     "history", "en", ["classical", "jewish-history", "1st-century", "primary-source", "second-temple"],
     "Josephus (37-100). Antiquitates Judaicae, c. 93-94. Critical source for Second Temple Judaism and NT era."),
    ("Antígona - Sófocles.epub",
     "antigona-sofocles", "Sophocles", 25, 80, "opcional",
     "reference", "es", ["classical", "greek-tragedy", "5th-century-bc", "primary-source", "theban-plays"],
     "Sophocles (c. 497-406 BC). Antigone, c. 441 BC."),
    ("Athenian Constitution - Aristóteles.epub",
     "athenian-constitution-aristotle", "Aristotle", 30, 80, "opcional",
     "reference", "en", ["classical", "greek", "political-philosophy", "4th-century-bc", "primary-source"],
     "Attributed to Aristotle (384-322 BC). Athenaion Politeia, rediscovered 1879."),
    ("Code of Hammurabi - Hammurabi.epub",
     "code-of-hammurabi", "Hammurabi", 35, 80, "importante",
     "history", "en", ["classical", "ancient-near-east", "law-code", "18th-century-bc", "primary-source", "babylonian"],
     "Hammurabi (c. 1810-1750 BC), king of Babylon. Code of Hammurabi, c. 1754 BC."),
    ("Commentaries on the Gallic and Civil Wars - Julius Caesar.epub",
     "commentaries-caesar", "Julius Caesar", 30, 80, "opcional",
     "history", "en", ["classical", "roman", "1st-century-bc", "primary-source", "military-history"],
     "Julius Caesar (100-44 BC). Commentarii de Bello Gallico and de Bello Civili."),
    ("Consolation of Philosophy - Boethius.epub",
     "consolation-of-philosophy-boethius", "Boethius", 30, 80, "importante",
     "reference", "en", ["late-antiquity", "6th-century", "christian-philosophy", "providence", "primary-source"],
     "Boethius (c. 480-524). De Consolatione Philosophiae, c. 524, written in prison before execution."),
    ("Fall of Troy - Smyrnaeus.epub",
     "fall-of-troy-smyrnaeus", "Quintus Smyrnaeus", 20, 70, "opcional",
     "reference", "en", ["classical", "greek-epic", "4th-century", "primary-source", "post-homeric"],
     "Quintus Smyrnaeus (fl. 4th c. AD). Posthomerica, continues Iliad through the fall of Troy."),
    ("History - Herodotus.epub",
     "history-herodotus", "Herodotus", 35, 80, "importante",
     "history", "en", ["classical", "greek", "5th-century-bc", "primary-source", "persian-wars"],
     "Herodotus (c. 484-425 BC), 'Father of History'. Histories, c. 430 BC."),
    ("History of the Peloponnesian War - Thucydides.epub",
     "peloponnesian-war-thucydides", "Thucydides", 35, 85, "importante",
     "history", "en", ["classical", "greek", "5th-century-bc", "primary-source", "peloponnesian-war"],
     "Thucydides (c. 460-400 BC). History of the Peloponnesian War, unfinished."),
    ("Iliad - Homer.epub",
     "iliad-homer", "Homer", 30, 85, "importante",
     "reference", "en", ["classical", "greek-epic", "8th-century-bc", "primary-source", "homeric"],
     "Homer (c. 8th c. BC). Iliad, foundational Greek epic."),
]

ok = 0
broken = []
for fn, slug, author, auth, rigor, imp, cat, lang, tags, note in WORKS:
    src = READY / fn
    if not src.exists():
        broken.append((fn, "MISSING"))
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
        src.rename(DONE / fn)
        print(f"  OK {slug}")
    else:
        broken.append((fn, r.stderr[-150:] if r.stderr else "?"))
        print(f"  BROKEN {slug}")

print(f"\nTheme 2 (Classical): {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

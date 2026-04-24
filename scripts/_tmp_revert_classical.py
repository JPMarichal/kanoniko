#!/usr/bin/env python
"""Revert 13 works incorrectly incorporated (literature + minor classics).

Per user: keep Josephus, Hammurabi, Herodotus. Archive the rest.
Removes: corpus/<lang>/<cat>/<slug>/ + fase0/<slug>.fase0.json.
Epub stays in !Done (already archived).
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVERTS = [
    # (lang, category, slug)
    ("en", "reference", "iliad-homer"),
    ("en", "reference", "aeneid-virgil"),
    ("en", "reference", "aesops-fables"),
    ("es", "reference", "agamenon-esquilo"),
    ("es", "reference", "antigona-sofocles"),
    ("en", "reference", "fall-of-troy-smyrnaeus"),
    ("en", "reference", "athenian-constitution-aristotle"),
    ("en", "reference", "analects-confucius"),
    ("en", "history", "commentaries-caesar"),
    ("en", "history", "peloponnesian-war-thucydides"),
    ("en", "reference", "consolation-of-philosophy-boethius"),
    ("en", "history", "annals-tacitus"),
    ("en", "history", "histories-tacitus"),
]

for lang, cat, slug in REVERTS:
    cdir = ROOT / "corpus" / lang / cat / slug
    if cdir.exists():
        shutil.rmtree(cdir)
        print(f"  removed corpus/{lang}/{cat}/{slug}/")
    else:
        print(f"  WARN missing corpus/{lang}/{cat}/{slug}/")
    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    if fase0.exists():
        fase0.unlink()
        print(f"    + removed fase0/{slug}.fase0.json")

print(f"\nReverted {len(REVERTS)} works (epubs remain archived in !Done).")

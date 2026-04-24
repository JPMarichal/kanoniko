#!/usr/bin/env python
"""Theme 3: Philosophy (12 works, individually curated)."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

WORKS = [
    ("Así hablo Zaratustra - Friedrich Nietzsche.epub",
     "asi-hablo-zaratustra-nietzsche", "Friedrich Nietzsche", 20, 75, "opcional",
     "reference", "es", ["philosophy", "19th-century", "existentialism", "primary-source", "non-lds"],
     "Nietzsche (1844-1900). Also sprach Zarathustra, 1883-1885."),
    ("Common Sense - Thomas Paine.epub",
     "common-sense-paine", "Thomas Paine", 25, 75, "importante",
     "history", "en", ["political-philosophy", "18th-century", "american-revolution", "primary-source"],
     "Thomas Paine (1737-1809). Common Sense, 1776. Pamphlet that galvanized American independence."),
    ("Critique of Pure Reason - Immanuel Kant.epub",
     "critique-of-pure-reason-kant", "Immanuel Kant", 25, 85, "importante",
     "reference", "en", ["philosophy", "18th-century", "epistemology", "german-idealism", "primary-source"],
     "Kant (1724-1804). Kritik der reinen Vernunft, 1781/1787. Foundational work of modern philosophy."),
    ("Discourse on Reason - Descartes.epub",
     "discourse-on-reason-descartes", "René Descartes", 25, 80, "importante",
     "reference", "en", ["philosophy", "17th-century", "rationalism", "primary-source"],
     "Descartes (1596-1650). Discours de la méthode, 1637. 'Cogito ergo sum'."),
    ("Essay Concerning Human Understanding - John Locke.epub",
     "essay-human-understanding-locke", "John Locke", 25, 80, "importante",
     "reference", "en", ["philosophy", "17th-century", "empiricism", "primary-source"],
     "Locke (1632-1704). Essay Concerning Human Understanding, 1689."),
    ("Essay on Man - Alexander Pope.epub",
     "essay-on-man-pope", "Alexander Pope", 20, 70, "opcional",
     "reference", "en", ["philosophy", "18th-century", "poetic-philosophy", "theodicy", "primary-source"],
     "Alexander Pope (1688-1744). An Essay on Man, 1733-1734. Philosophical poem."),
    ("Essays of Michel de Montaigne - Michel de Montaigne.epub",
     "essays-montaigne", "Michel de Montaigne", 25, 80, "opcional",
     "reference", "en", ["philosophy", "16th-century", "essay-form", "skepticism", "primary-source"],
     "Montaigne (1533-1592). Essais, 1580-1595. Founded the essay genre."),
    ("Essays of Ralph Waldo Emerson - Ralph Waldo Emerson.epub",
     "essays-emerson", "Ralph Waldo Emerson", 25, 75, "opcional",
     "reference", "en", ["philosophy", "19th-century", "transcendentalism", "primary-source"],
     "Emerson (1803-1882). Essays, 1841-1844. Core Transcendentalist texts."),
    ("Essays of Sir Francis Bacon - Francis Bacon.epub",
     "essays-bacon", "Francis Bacon", 25, 75, "opcional",
     "reference", "en", ["philosophy", "17th-century", "english-renaissance", "primary-source"],
     "Francis Bacon (1561-1626). Essays, 1597/1612/1625."),
    ("In Praise of Folly - Desiderius Erasmus.epub",
     "in-praise-of-folly-erasmus", "Desiderius Erasmus", 30, 80, "importante",
     "reference", "en", ["renaissance", "16th-century", "christian-humanism", "satire", "primary-source"],
     "Erasmus (1466-1536). Moriae Encomium, 1511. Renaissance satire of church corruption."),
    ("Inequality of Man - Jean Jacques Rousseau.epub",
     "inequality-of-man-rousseau", "Jean-Jacques Rousseau", 25, 80, "importante",
     "reference", "en", ["political-philosophy", "18th-century", "enlightenment", "primary-source"],
     "Rousseau (1712-1778). Discours sur l'origine de l'inégalité, 1755."),
    ("Leviathan - Thomas Hobbes.epub",
     "leviathan-hobbes", "Thomas Hobbes", 25, 85, "importante",
     "reference", "en", ["political-philosophy", "17th-century", "primary-source"],
     "Hobbes (1588-1679). Leviathan, 1651. Foundation of modern political theory."),
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

print(f"\nTheme 3 (Philosophy): {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

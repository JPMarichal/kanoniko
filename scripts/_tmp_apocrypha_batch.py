#!/usr/bin/env python
"""Apocrypha — new category scriptures-apocrypha (per DyC 91 cardinal guidance).

DyC 91:1-6: los apócrifos contienen muchas cosas verdaderas, son útiles
para quien se deja iluminar por el Espíritu; contienen también muchas
cosas no verdaderas (interpolaciones). No requieren traducción nueva.
"""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

WORKS = [
    ("Libro Apócrifo de Enoc, El - Desconocido.epub",
     "libro-apocrifo-de-enoc-es", "Desconocido (atribuido a Enoc)",
     "es", "scriptures-apocrypha",
     ["1-enoch", "pseudepigrapha", "second-temple", "dyc-91", "ethiopic-enoch", "primary-source"],
     "El Libro de Enoc (1 Enoc) — pseudepigrafía del Segundo Templo. Citado en Judas 1:14-15. Material enóquico incorporado en Moisés 6-7. DyC 91 aplica."),
    ("Libro de Enoc, El - Desconocido.epub",
     "libro-de-enoc-es-alt", "Desconocido (atribuido a Enoc)",
     "es", "scriptures-apocrypha",
     ["1-enoch", "pseudepigrapha", "second-temple", "dyc-91", "ethiopic-enoch", "primary-source", "alternate-edition"],
     "El Libro de Enoc (1 Enoc) — edición alternativa en español (texto más extenso que la otra edición)."),
    ("Old Testament Apocrypha - No specific author.epub",
     "old-testament-apocrypha-en", "Various (ancient)",
     "en", "scriptures-apocrypha",
     ["ot-apocrypha", "deuterocanonical", "septuagint", "dyc-91", "jst-context", "primary-source"],
     "Old Testament Apocrypha (Deuterocanon): Tobit, Judith, Wisdom, Sirach, 1-2 Macabeos, Baruc, etc. Presentes en LXX y Vulgata; Joseph Smith leyó los apócrifos (fondo de DyC 91). JST no los alteró."),
    ("Old Testament Pseudepigrapha - No specific author.epub",
     "old-testament-pseudepigrapha-en", "Various (ancient, pseudepigraphic)",
     "en", "scriptures-apocrypha",
     ["ot-pseudepigrapha", "second-temple", "intertestamental", "dyc-91", "primary-source"],
     "Old Testament Pseudepigrapha: Jubileos, Testamentos de los 12 Patriarcas, Apocalipsis de Abraham, 2-3 Enoc, Oráculos Sibilinos, etc."),
    ("New Testament Pseudepigrapha - No specific author.epub",
     "new-testament-pseudepigrapha-en", "Various (ancient, pseudepigraphic)",
     "en", "scriptures-apocrypha",
     ["nt-pseudepigrapha", "christian-apocrypha", "dyc-91", "primary-source"],
     "New Testament Pseudepigrapha: evangelios apócrifos (Tomás, María, Protoevangelio de Santiago), Hechos apócrifos, apocalipsis cristianos primitivos."),
]

ok = 0
broken = []
for fn, slug, author, lang, cat, tags, note in WORKS:
    src = READY / fn
    if not src.exists():
        broken.append((fn, "MISSING"))
        continue
    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    fase0.write_text(json.dumps({
        "authority": 30, "rigor": 75, "importance": "importante",
        "official": False, "current": True, "context": "scriptures-apocrypha",
        "audience": "adult",
        "tags": tags,
        "category": cat,
        "author": author,
        "source_url": None,
        "note": note,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
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
        print(f"  BROKEN {slug}: {r.stderr[-120:]}")

print(f"\nApocrypha batch: {ok} OK, {len(broken)} broken")
print(f"!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}")

#!/usr/bin/env python
"""Final JPM + Pelé. Per-content decision."""
import subprocess, sys, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"
PREV = ROOT / "epub" / "_preview"
if PREV.exists(): shutil.rmtree(PREV)

SKIP = [  # skip to !Done (not worthy of corpus)
    "Libro de Mormón (versión anotada), El - Juan Pablo Marichal Catalán.epub",
    "Libro de Mormón, El - Juan Pablo Marichal Catalán.epub",
    "Triple combinación - Juan Pablo Marichal Catalán.epub",
    "Los miembros de la Iglesia - Juan Pablo Marichal Catalán.epub",
    "Ya lo leí BOM - Juan Pablo Marichal Catalán.epub",
    "Writing a blog post - Juan Pablo Marichal Catalán.epub",
]

WORKS = [
    # JPM articles (6)
    ("Lucas como el biógrafo de María - Juan Pablo Marichal Catalán.epub",
     "lucas-biografo-maria-jpm", "Juan Pablo Marichal Catalán", 25, 70, "opcional",
     "books", "es", ["jpm", "luke", "mary-mother-of-jesus", "nt-analysis", "lds-independent-author"],
     "JPM. Lucas como el biógrafo de María — análisis estadístico de menciones marianas en el NT."),
    ("Nuestra ofrenda en la reunión sacramental - Juan Pablo Marichal Catalán.epub",
     "nuestra-ofrenda-sacramental-jpm", "Juan Pablo Marichal Catalán", 25, 70, "opcional",
     "discourses", "es", ["jpm", "sacrament-meeting", "offering", "discourse", "lds-independent-author"],
     "JPM. Nuestra ofrenda en la reunión sacramental (Barrio Plateros, 18 de junio de 2017)."),
    ("Patronímicos - Juan Pablo Marichal Catalán.epub",
     "patronimicos-jpm", "Juan Pablo Marichal Catalán", 25, 60, "opcional",
     "books", "es", ["jpm", "patronymics", "priesthood-order", "lds-independent-author"],
     "JPM. Patronímicos — nota sobre la genealogía del sacerdocio (DyC 107)."),
    ("Pendón a las naciones - Juan Pablo Marichal Catalán.epub",
     "pendon-a-las-naciones-jpm", "Juan Pablo Marichal Catalán", 25, 70, "opcional",
     "books", "es", ["jpm", "ensign-to-the-nations", "isaiah", "symbolism", "lds-independent-author"],
     "JPM. Pendón a las naciones — significado del símbolo en Isaías."),
    ("Reseña General - Juan Pablo Marichal Catalán.epub",
     "resena-general-jpm", "Juan Pablo Marichal Catalán", 25, 70, "importante",
     "study-aids", "es", ["jpm", "bible-overview", "study-aid", "pan-biblical", "lds-independent-author"],
     "JPM. Reseña General — índice pan-bíblico (autor, fecha, propósito, temas, estructura, citas) por libro. 90 capítulos."),
    ("significado de las últimas palabras de Jesús, El - Juan Pablo Marichal Catalán.epub",
     "significado-ultimas-palabras-jesus-jpm", "Juan Pablo Marichal Catalán", 25, 70, "opcional",
     "books", "es", ["jpm", "crucifixion", "last-sayings-of-jesus", "nt-study", "lds-independent-author"],
     "JPM. El significado de las últimas palabras de Jesús — carta a los élderes Espino con compilación de citas."),

    # Pelé (4)
    ("Lo-que-publique-en-la-seccion-de-Charla - Ernesto Pele.epub",
     "lo-que-publique-seccion-charla-pele", "Ernesto Pelé (Ernest C. Pyle)",
     25, 65, "opcional", "books", "es",
     ["pele", "jst", "melchizedek", "compilation", "lds-independent-author"],
     "Pelé. Lo que publiqué en la sección de Charla — compilación de JST Gen 14 y comentarios."),
    ("Los-científicos-y-los-astronautas-leen-la-Biblia - Ernesto Pele.epub",
     "cientificos-astronautas-leen-biblia-pele", "Ernesto Pelé (Ernest C. Pyle)",
     20, 55, "opcional", "books", "es",
     ["pele", "science-religion", "nasa-lore", "lds-independent-author"],
     "Pelé. Los científicos y los astronautas leen la Biblia (anécdota del programa espacial)."),
    ("Quién-tiene-la-autoridad-de-dar-interpretaciones-autorizadas-de-las-Escrituras - Ernesto Pele.epub",
     "quien-autoridad-interpretar-escrituras-pele", "Ernesto Pelé (Ernest C. Pyle)",
     25, 70, "importante", "books", "es",
     ["pele", "scripture-interpretation", "authority", "2-peter-1-20", "lds-independent-author"],
     "Pelé. ¿Quién tiene la autoridad de dar interpretaciones autorizadas de las Escrituras?"),
    ("Vision-del-futuro-de-los-lamanitas - Ernesto Pele.epub",
     "vision-futuro-lamanitas-pele-compilacion", "Ernesto Pelé (Ernest C. Pyle, compilador)",
     30, 70, "importante", "history", "es",
     ["pele", "eduardo-balderas", "spanish-translation-history", "lamanites", "compilation"],
     "Pelé (compilador). Visión del futuro de los lamanitas — Eduardo Balderas y la traducción al español de las ordenanzas del templo."),
]

# Skip
skipped = 0
for fn in SKIP:
    p = READY / fn
    if p.exists():
        p.rename(DONE / fn)
        skipped += 1
        print(f"  skip: {fn[:70]}")

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
        broken.append((fn, r.stderr[-120:] if r.stderr else "?"))
        print(f"  BROKEN {slug}")

print(f"\nJPM+Pelé final: {ok} OK, {len(broken)} broken, {skipped} skipped")
print(f"!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}")

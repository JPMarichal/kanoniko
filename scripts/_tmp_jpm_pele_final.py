#!/usr/bin/env python
"""Final: JPM articles (12) + Pelé (5). Individually curated per user directives."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
PREVIEW = ROOT / "epub" / "_preview"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

import shutil

# Clean up preview dir first
if PREVIEW.exists():
    shutil.rmtree(PREVIEW)

WORKS = [
    # === JPM — independent LDS author ===
    ("Antecedentes de la vida de Moisés.md - Juan Pablo Marichal Catalán.epub",
     "antecedentes-vida-moises-jpm", "Juan Pablo Marichal Catalán", 25, 65, "opcional",
     "books", "es", ["jpm", "moses", "old-testament", "historical-note", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. Antecedentes de la vida de Moisés."),
    ("Apuntes sobre el Convenio de Abraham, forma T - Juan Pablo Marichal Catalán.epub",
     "apuntes-convenio-abraham-jpm", "Juan Pablo Marichal Catalán", 25, 65, "opcional",
     "books", "es", ["jpm", "abrahamic-covenant", "forma-t", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. Apuntes sobre el Convenio de Abraham (Forma T format, small)."),
    ("artículo de fe número 10, El - Juan Pablo Marichal Catalán.epub",
     "articulo-fe-10-jpm", "Juan Pablo Marichal Catalán", 25, 70, "opcional",
     "discourses", "es", ["jpm", "articles-of-faith", "tenth-article-of-faith", "discourse", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. El Artículo de Fe número 10 (discurso)."),
    ("autobiografía de Lucas en el Libro de Hechos, La - Juan Pablo Marichal Catalán.epub",
     "autobiografia-lucas-hechos-jpm", "Juan Pablo Marichal Catalán", 25, 70, "opcional",
     "books", "es", ["jpm", "luke", "acts", "new-testament", "biblical-studies", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. La autobiografía de Lucas en el Libro de Hechos. Análisis de los 'we-passages'."),
    ("Capítulos y versículos clave - Juan Pablo Marichal Catalán.epub",
     "capitulos-versiculos-clave-jpm", "Juan Pablo Marichal Catalán", 25, 60, "opcional",
     "study-aids", "es", ["jpm", "study-aid", "bible-index", "key-chapters", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. Capítulos y versículos clave (tabla de referencia de estudio)."),
    ("Datos biográficos de Amasa M. Lyman - Juan Pablo Marichal Catalán.epub",
     "datos-biograficos-amasa-lyman-jpm", "Juan Pablo Marichal Catalán", 25, 65, "opcional",
     "biographies", "es", ["jpm", "amasa-lyman", "early-apostle", "biographical-sketch", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. Datos biográficos de Amasa M. Lyman (Q12 1842-1870). Ficha compilada."),
    ("creación de la tierra no fue a partir de la nada, La - Juan Pablo Marichal Catalán.epub",
     "creacion-no-ex-nihilo-jpm", "Juan Pablo Marichal Catalán", 25, 70, "opcional",
     "books", "es", ["jpm", "creation", "ex-nihilo", "genesis", "hebrew-bara", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. La creación de la tierra no fue a partir de la nada (análisis del verbo hebreo 'bará')."),
    ("Escrituras perdidas - Juan Pablo Marichal Catalán.epub",
     "escrituras-perdidas-jpm", "Juan Pablo Marichal Catalán", 25, 65, "opcional",
     "books", "es", ["jpm", "lost-scriptures", "bible-canon", "apocrypha", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. Escrituras perdidas (libros mencionados en la Biblia ausentes del canon)."),
    ("Esquema del método temático de enseñanza - Juan Pablo Marichal Catalán.epub",
     "esquema-metodo-tematico-ensenanza-jpm", "Juan Pablo Marichal Catalán", 25, 65, "opcional",
     "books", "es", ["jpm", "teaching-method", "thematic-instruction", "boyd-k-packer", "prerequisites-principle", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. Esquema del método temático de enseñanza (Packer's prerequisites principle)."),
    ("honradez y el sentido interior de congruencia, La - Juan Pablo Marichal Catalán.epub",
     "honradez-sentido-congruencia-jpm", "Juan Pablo Marichal Catalán", 25, 70, "opcional",
     "discourses", "es", ["jpm", "honesty", "integrity", "congruence", "covenants", "discourse", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. La honradez y el sentido interior de congruencia (discurso de estaca)."),
    ("Identidad de los lamanitas - Juan Pablo Marichal Catalán.epub",
     "identidad-lamanitas-jpm", "Juan Pablo Marichal Catalán", 25, 65, "opcional",
     "books", "es", ["jpm", "lamanites", "book-of-mormon", "latin-american-lds", "ethnic-identity", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. Identidad de los lamanitas (respuesta a Hno. Barrera sobre miembros latinoamericanos y el linaje lamanita)."),
    ("Levirato - Juan Pablo Marichal Catalán.epub",
     "levirato-jpm", "Juan Pablo Marichal Catalán", 25, 60, "opcional",
     "books", "es", ["jpm", "levirate", "ancient-near-east", "biblical-law", "lds-independent-author"],
     "Juan Pablo Marichal Catalán. La ley del levirato (nota)."),

    # === Pelé — independent LDS author ===
    ("Carta-de-la-Primera-Presidencia -15-de-diciembre-de-1969 - Ernesto Pele.epub",
     "carta-fp-15dic1969-pele-compilacion", "Ernesto Pelé (Ernest C. Pyle, compilador)", 40, 70, "importante",
     "history", "es", ["pele", "first-presidency-letter", "1969", "civil-rights", "primary-source-compilation"],
     "Ernesto Pelé (compilador). Carta de la Primera Presidencia del 15 de diciembre de 1969 (contexto derechos civiles)."),
    ("Comentarios - Ernesto Pele.epub",
     "comentarios-pele", "Ernesto Pelé (Ernest C. Pyle)", 25, 60, "opcional",
     "books", "es", ["pele", "columbus", "americas", "commentary", "lds-independent-author"],
     "Ernesto Pelé. Comentarios (ensayo sobre el descubrimiento de América)."),
    ("El-Templo-de-Kirtland - Ernesto Pele.epub",
     "templo-kirtland-pele", "Ernesto Pelé (Ernest C. Pyle)", 30, 70, "importante",
     "history", "es", ["pele", "kirtland-temple", "church-history", "compilation-analysis", "lds-independent-author"],
     "Ernesto Pelé. El Templo de Kirtland (compilación y análisis histórico)."),
    ("La-estrella-de-Belén - Ernesto Pele.epub",
     "estrella-belen-pele", "Ernesto Pelé (Ernest C. Pyle)", 25, 60, "opcional",
     "books", "es", ["pele", "star-of-bethlehem", "samuel-the-lamanite", "compilation", "lds-independent-author"],
     "Ernesto Pelé. La estrella de Belén (compilación y análisis)."),
    ("La-Segunda-Unción - Ernesto Pele.epub",
     "segunda-uncion-pele", "Ernesto Pelé (Ernest C. Pyle)", 25, 70, "importante",
     "books", "es", ["pele", "second-anointing", "temple", "fullness-of-priesthood", "compilation-analysis", "lds-independent-author"],
     "Ernesto Pelé. La Segunda Unción (compilación extensa y análisis doctrinal)."),
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

print(f"\nJPM+Pelé final: {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

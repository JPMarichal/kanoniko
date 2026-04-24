#!/usr/bin/env python
"""Sub-batch 4: multi-author clusters (non-JPM, non-Pelé, non-singleton).

Archives:
  - 3 FamilySearch .pdf.epub (genealogy charts, not prose)
  - 2 intra-dups ((1) variants)

Incorporates 24 works across 12 clusters.
"""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

ARCHIVE_ONLY = [
    "20180224Cuadro genealógico verticalLN2P-21D.pdf - FamilySearch.epub",
    "20180318Cuadro genealógicoLN2P-21T.pdf - FamilySearch.epub",
    "20180318Cuadro genealógicoLN2P-26R.pdf - FamilySearch.epub",
    "En mi lugar - Horatius Bonar (1).epub",
    "Escrito está--alabado sea el Señor - Lee Roy Shelton, Jr_ (1).epub",
]

# (filename, slug, author, auth, rigor, imp, cat, lang, tags, note)
WORKS = [
    # Arthur W. Pink (3) - evangelical reformed
    ("Arrepiéntete o perecerás - Arthur W. Pink.epub",
     "arrepientete-o-pereceras-pink", "Arthur W. Pink", 15, 50, "opcional",
     "reference", "es", ["evangelical", "reformed", "repentance", "non-lds"],
     "Reformed Baptist exposition on repentance. Non-LDS reference."),
    ("Culto familiar - Arthur W. Pink.epub",
     "culto-familiar-pink", "Arthur W. Pink", 15, 50, "opcional",
     "reference", "es", ["evangelical", "reformed", "family-worship", "non-lds"],
     "Reformed Baptist on family worship. Non-LDS reference."),
    ("camino de la salvación, El - Arthur W. Pink.epub",
     "el-camino-de-la-salvacion-pink", "Arthur W. Pink", 15, 50, "opcional",
     "reference", "es", ["evangelical", "reformed", "salvation", "non-lds"],
     "Reformed Baptist on the way of salvation. Non-LDS reference."),
    # Horatius Bonar (1 unique) - 19th-c Scottish evangelical
    ("En mi lugar - Horatius Bonar.epub",
     "en-mi-lugar-bonar", "Horatius Bonar", 15, 50, "opcional",
     "reference", "es", ["evangelical", "19th-century", "substitutionary-atonement", "non-lds"],
     "19th-c Scottish evangelical on substitutionary atonement."),
    ("Belén y las buenas nuevas - Horatius Bonar.epub",
     "belen-y-las-buenas-nuevas-bonar", "Horatius Bonar", 15, 50, "opcional",
     "reference", "es", ["evangelical", "19th-century", "nativity", "non-lds"],
     "19th-c Scottish evangelical on the nativity."),
    # Lee Roy Shelton Jr (1 unique) - Baptist preacher
    ("Arrepentimiento bíblico - Lee Roy Shelton, Jr_.epub",
     "arrepentimiento-biblico-shelton", "Lee Roy Shelton Jr.", 15, 45, "opcional",
     "reference", "es", ["evangelical", "baptist", "repentance", "non-lds"],
     "Baptist preacher on biblical repentance. Non-LDS reference."),
    ("Escrito está--alabado sea el Señor - Lee Roy Shelton, Jr_.epub",
     "escrito-esta-shelton", "Lee Roy Shelton Jr.", 15, 45, "opcional",
     "reference", "es", ["evangelical", "baptist", "scripture-authority", "non-lds"],
     "Baptist preacher on scripture authority. Non-LDS reference."),
    # Various General Authorities (3) - compilations
    ("Book of Mormon Treasury, Selections from the Pages of the Improvement Era - Various General Authorities.epub",
     "book-of-mormon-treasury-improvement-era", "Various General Authorities", 45, 60, "importante",
     "books", "en", ["book-of-mormon", "improvement-era", "apostle-authored", "anthology"],
     "Deseret Book anthology of Improvement Era BoM articles by GAs."),
    ("Heroes from the Book of Mormon - Various General Authorities.epub",
     "heroes-from-the-book-of-mormon", "Various General Authorities", 45, 60, "importante",
     "books", "en", ["book-of-mormon", "heroes", "apostle-authored", "anthology"],
     "Deseret Book anthology on BoM heroes by GAs."),
    ("Heroes of the Restoration - Various General Authorities.epub",
     "heroes-of-the-restoration", "Various General Authorities", 45, 60, "importante",
     "books", "en", ["restoration", "heroes", "apostle-authored", "anthology"],
     "Deseret Book anthology on Restoration heroes by GAs."),
    # Tacitus (2) - classical historian
    ("Annals - Tacitus.epub",
     "annals-tacitus", "Tacitus", 30, 80, "importante",
     "history", "en", ["classical", "roman-history", "primary-source", "1st-century"],
     "Tacitus's Annals. Classical Roman history, Neronian era."),
    ("Histories - Tacitus.epub",
     "histories-tacitus", "Tacitus", 30, 80, "importante",
     "history", "en", ["classical", "roman-history", "primary-source", "1st-century"],
     "Tacitus's Histories. Classical Roman history."),
    # James Allen (2) - self-help, EN/ES pair
    ("As a Man Thinketh - James Allen.epub",
     "as-a-man-thinketh", "James Allen", 15, 40, "opcional",
     "reference", "en", ["self-help", "victorian", "non-lds"],
     "Allen's 1903 essay on thought and character."),
    ("Así como el hombre piensa - James Allen.epub",
     "asi-como-el-hombre-piensa", "James Allen", 15, 40, "opcional",
     "reference", "es", ["self-help", "victorian", "non-lds"],
     "Spanish translation of Allen's 1903 essay."),
    # J. H. Ward (2) - 19th-c LDS writer
    ("Gospel Philosophy _ Showing the Absurdities of Infid of the Gospel with Science and History - J. H. Ward.epub",
     "gospel-philosophy-ward", "J. H. Ward", 25, 55, "opcional",
     "books", "en", ["19th-century-lds", "apologetics", "gospel-science"],
     "1884 LDS apologetic work on gospel, science, and history."),
    ("hand of Providence, The - J. H. Ward.epub",
     "hand-of-providence-ward", "J. H. Ward", 25, 55, "opcional",
     "history", "en", ["19th-century-lds", "providence", "history-of-nations"],
     "1883 LDS work on divine providence in history."),
    # Compilation (2) - Faith-Promoting Series
    ("Helpful Visions, Faith-Promoting Series, no_ 14 - Compilation.epub",
     "helpful-visions-fps-14", "Various (Compilation)", 30, 55, "opcional",
     "books", "en", ["faith-promoting-series", "19th-century-lds", "visions", "anthology"],
     "19th-c LDS Faith-Promoting Series #14."),
    ("Labors in the Vineyard, Faith-Promoting Series, no_ 12 - Compilation.epub",
     "labors-in-the-vineyard-fps-12", "Various (Compilation)", 30, 55, "opcional",
     "books", "en", ["faith-promoting-series", "19th-century-lds", "missionary", "anthology"],
     "19th-c LDS Faith-Promoting Series #12."),
    # Alexis de Tocqueville (2) - political philosophy
    ("Democracy in America, vol_ 1 - Alexis de Tocqueville.epub",
     "democracy-in-america-vol-1-tocqueville", "Alexis de Tocqueville", 35, 85, "importante",
     "history", "en", ["political-philosophy", "19th-century", "american-history", "primary-source"],
     "Tocqueville's Democracy in America, vol. 1 (1835)."),
    ("Democracy in America, vol_ 2 - Alexis de Tocqueville.epub",
     "democracy-in-america-vol-2-tocqueville", "Alexis de Tocqueville", 35, 85, "importante",
     "history", "en", ["political-philosophy", "19th-century", "american-history", "primary-source"],
     "Tocqueville's Democracy in America, vol. 2 (1840)."),
    # Agustín (2) - patristic
    ("City of God - Agustín.epub",
     "city-of-god-augustine", "Augustine of Hippo", 35, 85, "importante",
     "reference", "en", ["patristic", "5th-century", "christian-theology", "primary-source"],
     "Augustine's City of God (c. 413-426 AD). Patristic classic."),
    ("Confessions - Agustín.epub",
     "confessions-augustine", "Augustine of Hippo", 35, 85, "importante",
     "reference", "en", ["patristic", "4th-century", "autobiography", "primary-source"],
     "Augustine's Confessions (c. 397-400 AD). Patristic classic."),
    # Jamieson, Fausset & Brown (2) - biblical commentary
    ("Comentario exegético y explicativo de la Biblia, Tomo 1 - Roberto Jamieson & A. R. Fausset & David Brown.epub",
     "jfb-comentario-biblia-tomo-1", "Robert Jamieson, A. R. Fausset & David Brown", 20, 65, "opcional",
     "reference", "es", ["bible-commentary", "19th-century", "evangelical", "reference-work"],
     "Jamieson-Fausset-Brown Bible Commentary, vol. 1 (OT). Non-LDS reference."),
    ("Comentario exegético y explicativo de la Biblia, Tomo 2 - Roberto Jamieson & A. R. Fausset & David Brown.epub",
     "jfb-comentario-biblia-tomo-2", "Robert Jamieson, A. R. Fausset & David Brown", 20, 65, "opcional",
     "reference", "es", ["bible-commentary", "19th-century", "evangelical", "reference-work"],
     "Jamieson-Fausset-Brown Bible Commentary, vol. 2 (NT). Non-LDS reference."),
]

# archive non-prose / intra-dups
for fn in ARCHIVE_ONLY:
    src = READY / fn
    if src.exists():
        src.rename(DONE / fn)
        print(f"  archived: {fn[:70]}")

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
           "--slug", slug, "--author", author,
           "--fase0", str(fase0)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        src.rename(DONE / fn)
        print(f"  OK {slug}")
    else:
        broken.append((fn, r.stderr[-150:] if r.stderr else "?"))
        print(f"  BROKEN {slug}")

print(f"\nBatch 4: {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

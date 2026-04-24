#!/usr/bin/env python
"""Unknown-author (Desconocido/Various/No specific author) batch."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

ARCHIVE = [
    "Manual para construir una estufa solar - Desconocido.epub",   # off-topic
    "mundo críptido, El - Desconocido.epub",                       # cryptid, off-topic
    "presentacion primaria 2022-1 - Desconocido.epub",             # local bulletin
    "Plan Area 2018 v2 - Desconocido.epub",                        # local plan
    "Plan Área 2018-Líderes - Desconocido.epub",                   # local plan
    "Rose Bible eCharts Deluxe1116 NT - Desconocido.epub",         # already have Rose charts
    "Libro de Mormón_ Edición paralela Español Inglés - Desconocido.epub",  # canonical dup
    "Reina Valera 1990 - Various.epub",                            # canonical dup
]

# Apocrypha/pseudepigrapha — go to scriptures-apocrypha
APOCRYPHA = [
    ("Testamento de los Doce Patriarcas - Desconocido.epub",
     "testamento-12-patriarcas-es", "Desconocido (pseudepigraphic)", "es",
     ["ot-pseudepigrapha", "testaments-12-patriarchs", "second-temple", "dyc-91"],
     "Testamento de los Doce Patriarcas (ES) — pseudepígrafo del AT, referido por Joseph Smith."),
    ("Narrative of Zosimus - No specific author.epub",
     "narrative-of-zosimus", "Anonymous (Christian pseudepig.)", "en",
     ["christian-apocrypha", "rechabites", "pseudepigrapha", "dyc-91"],
     "Narrative of Zosimus concerning the Life of the Blessed. Pseudepigrafal Christian narrative — citado por Nibley."),
    ("libro de Jaser, El - Desconocido.epub",
     "libro-de-jaser-es", "Desconocido (pseudepig.)", "es",
     ["ot-apocrypha", "sefer-hayashar", "book-of-jasher", "joshua-2-samuel", "dyc-91"],
     "El Libro de Jaser (Sefer HaYashar) ES — referenciado en Josué 10:13 y 2 Samuel 1:18."),
]

# Patristic
PATRISTIC = [
    ("Martyrdom of Polycarp - No specific author.epub",
     "martyrdom-of-polycarp", "Anonymous", "en", "reference",
     ["patristic", "2nd-century", "martyrdom", "polycarp", "primary-source", "apostolic-fathers"],
     "Martyrdom of Polycarp, c. 155-160. Earliest Christian martyrology outside the NT."),
    ("Martyrdom of the Holy Martyrs - No specific author.epub",
     "martyrdom-of-the-holy-martyrs", "Anonymous", "en", "reference",
     ["patristic", "2nd-century", "martyrdom", "primary-source"],
     "Martyrdom of the Holy Martyrs Justin, Chariton, et al."),
]

# Reference / compilations / misc
WORKS = [
    ("New Jerusalem - The Encyclopedia of Mormonism - Various.epub",
     "new-jerusalem-enc-mormonism", "Various (Enc. Mormonism)", "en", "reference",
     40, 80, "importante",
     ["encyclopedia-of-mormonism", "new-jerusalem", "reference-article"],
     "New Jerusalem article from Encyclopedia of Mormonism (1992)."),
    ("Patriarch - The Encyclopedia of Mormonism - Various.epub",
     "patriarch-enc-mormonism", "Various (Enc. Mormonism)", "en", "reference",
     40, 80, "opcional",
     ["encyclopedia-of-mormonism", "patriarch", "reference-article"],
     "Patriarch article from Encyclopedia of Mormonism."),
    ("Patriarchal Blessings - The Encyclopedia of Mormonism - Various.epub",
     "patriarchal-blessings-enc-mormonism", "Various (Enc. Mormonism)", "en", "reference",
     40, 80, "importante",
     ["encyclopedia-of-mormonism", "patriarchal-blessings", "reference-article"],
     "Patriarchal Blessings article from Encyclopedia of Mormonism."),
    ("Plural Marriage - The Encyclopedia of Mormonism - Various.epub",
     "plural-marriage-enc-mormonism", "Various (Enc. Mormonism)", "en", "reference",
     40, 80, "importante",
     ["encyclopedia-of-mormonism", "plural-marriage", "polygamy", "reference-article"],
     "Plural Marriage article from Encyclopedia of Mormonism."),
    ("Polygamy - The Encyclopedia of Mormonism - Various.epub",
     "polygamy-enc-mormonism", "Various (Enc. Mormonism)", "en", "reference",
     40, 80, "importante",
     ["encyclopedia-of-mormonism", "polygamy", "reference-article"],
     "Polygamy article from Encyclopedia of Mormonism."),
    ("Race, Racism - The Encyclopedia of Mormonism - Various.epub",
     "race-racism-enc-mormonism", "Various (Enc. Mormonism)", "en", "reference",
     40, 80, "importante",
     ["encyclopedia-of-mormonism", "race", "racism", "reference-article"],
     "Race, Racism article from Encyclopedia of Mormonism."),
    ("Regional Studies in LDS History, Arizona - Various authors.epub",
     "regional-studies-lds-arizona", "Various (BYU RSC)", "en", "history",
     40, 80, "importante",
     ["byu-religious-studies-center", "regional-studies", "arizona", "anthology"],
     "Regional Studies in LDS History: Arizona (BYU RSC)."),
    ("Regional Studies in LDS History, British Isles - Various authors.epub",
     "regional-studies-lds-british-isles", "Various (BYU RSC)", "en", "history",
     40, 80, "importante",
     ["byu-religious-studies-center", "regional-studies", "british-isles", "anthology"],
     "Regional Studies in LDS History: British Isles."),
    ("Regional Studies in LDS History, Illinois - Various authors.epub",
     "regional-studies-lds-illinois", "Various (BYU RSC)", "en", "history",
     40, 80, "importante",
     ["byu-religious-studies-center", "regional-studies", "illinois", "nauvoo"],
     "Regional Studies in LDS History: Illinois."),
    ("Regional Studies in LDS History, Missouri - Various authors.epub",
     "regional-studies-lds-missouri", "Various (BYU RSC)", "en", "history",
     40, 80, "importante",
     ["byu-religious-studies-center", "regional-studies", "missouri", "far-west"],
     "Regional Studies in LDS History: Missouri."),
    ("Regional Studies in LDS History, New England - Various authors.epub",
     "regional-studies-lds-new-england", "Various (BYU RSC)", "en", "history",
     40, 80, "importante",
     ["byu-religious-studies-center", "regional-studies", "new-england"],
     "Regional Studies in LDS History: New England."),
    ("Simposio Doctrina y Convenios 2002, BYU - Various.epub",
     "simposio-dc-2002-byu-es", "Various (BYU Sperry Symposium)", "es", "books",
     40, 80, "importante",
     ["byu-academic", "sperry-symposium", "doctrine-and-covenants", "2002", "spanish"],
     "Simposio BYU 2002 sobre Doctrina y Convenios (ES)."),
    ("Simposio Libro de Mormón, agosto 1986, BYU - Various.epub",
     "simposio-bom-1986-byu-es", "Various (BYU Sperry Symposium)", "es", "books",
     40, 80, "importante",
     ["byu-academic", "sperry-symposium", "book-of-mormon", "1986", "spanish"],
     "Simposio BYU agosto 1986 sobre Libro de Mormón (ES)."),
    ("Prophet of Palmyra, The - Various authors.epub",
     "prophet-of-palmyra", "Various", "en", "biographies",
     30, 70, "opcional",
     ["joseph-smith", "palmyra", "19th-century"],
     "The Prophet of Palmyra (biographical-historical work on Joseph Smith)."),
    ("William Smith On Mormonism - Various authors.epub",
     "william-smith-on-mormonism", "William Smith et al.", "en", "history",
     35, 70, "importante",
     ["william-smith", "smith-family", "19th-century-lds", "primary-source"],
     "William Smith On Mormonism (1883). William Smith (1811-1893), apóstol y hermano del profeta."),
    ("Mormon in Motion, The Life and Journals of James H_ Hart 1825-1906 - Various authors.epub",
     "mormon-in-motion-james-h-hart", "Various (ed.)", "en", "biographies",
     35, 75, "opcional",
     ["james-h-hart", "19th-20th-century-lds", "journals", "primary-source"],
     "Mormon in Motion: James H. Hart 1825-1906 journals."),
    ("Reynolds Cahoon and His Stalwart Sons - Various authors.epub",
     "reynolds-cahoon-stalwart-sons", "Various (Cahoon family, eds.)", "en", "biographies",
     30, 70, "opcional",
     ["reynolds-cahoon", "cahoon-family", "19th-century-lds", "pioneer-biography"],
     "Reynolds Cahoon (1790-1861) and His Stalwart Sons — family biographical compilation."),
    ("Windows, A Mormon Family - Various authors.epub",
     "windows-mormon-family", "Various", "en", "biographies",
     25, 60, "opcional",
     ["mormon-family-memoir", "20th-century"],
     "Windows: A Mormon Family (family memoir anthology)."),
    ("Women_s Voices - Various authors.epub",
     "womens-voices-anthology", "Various (eds.)", "en", "books",
     35, 75, "importante",
     ["lds-women", "anthology", "historical-voices", "primary-source"],
     "Women's Voices: LDS women's historical writings anthology."),
    ("Ohio Observer, The - Various authors.epub",
     "ohio-observer", "Various", "en", "history",
     25, 65, "opcional",
     ["19th-century", "ohio", "newspaper", "primary-source"],
     "The Ohio Observer — 19th-c newspaper relevant to Kirtland-era LDS context."),
    ("Ten Years Before the Mast - Various authors.epub",
     "ten-years-before-the-mast", "Various", "en", "history",
     20, 65, "opcional",
     ["seafaring", "19th-century", "memoir"],
     "Ten Years Before the Mast (seafaring memoir, 19th-c)."),
    ("Mormon Artifacts on Display at the Smithsonian - Desconocido.epub",
     "mormon-artifacts-smithsonian", "Desconocido", "en", "reference",
     20, 60, "opcional",
     ["artifacts", "smithsonian", "exhibition"],
     "Mormon Artifacts on Display at the Smithsonian (exhibition notes)."),
    ("Outline of Book of Mormon - Desconocido.epub",
     "outline-of-book-of-mormon", "Desconocido", "en", "study-aids",
     30, 65, "opcional",
     ["book-of-mormon", "study-outline", "study-aid"],
     "Outline of Book of Mormon."),
    ("Referencias de las escrituras - Desconocido.epub",
     "referencias-escrituras-es", "Desconocido", "es", "study-aids",
     30, 65, "opcional",
     ["scripture-references", "study-aid", "spanish"],
     "Referencias de las escrituras (ES study aid)."),
    ("Reyes de Asiria, de Israel, Profetas y Reyes de Judá - Desconocido.epub",
     "reyes-asiria-israel-profetas-juda-es", "Desconocido", "es", "reference",
     25, 70, "opcional",
     ["ot-kings", "chronology", "biblical-chart", "spanish"],
     "Reyes de Asiria, Israel, Profetas y Reyes de Judá (ES chronological chart)."),
    ("Reyes de Israel y Judá_ Una guía fascinante del anilónicas de Samaria y Jerusalén, Los - Desconocido.epub",
     "reyes-israel-juda-guia-es", "Desconocido", "es", "reference",
     20, 65, "opcional",
     ["ot-kings", "history-israel-judah", "spanish"],
     "Los Reyes de Israel y Judá: Una guía fascinante (ES)."),
    ("Usos y costumbres de las tierras bíblicas - Desconocido.epub",
     "usos-costumbres-tierras-biblicas-es", "Desconocido", "es", "reference",
     25, 70, "opcional",
     ["bible-customs", "ancient-near-east", "cultural-background", "spanish"],
     "Usos y costumbres de las tierras bíblicas (ES)."),
    ("Léxico hebreo-español y arameo-español - Desconocido.epub",
     "lexico-hebreo-arameo-espanol", "Desconocido", "es", "reference",
     30, 80, "importante",
     ["hebrew-lexicon", "aramaic-lexicon", "biblical-languages", "spanish"],
     "Léxico hebreo-español y arameo-español (ES)."),
    ("templo en la Iglesia Primitiva, El - Desconocido.epub",
     "templo-iglesia-primitiva-es", "Desconocido", "es", "books",
     30, 70, "importante",
     ["early-christian-temple", "patristic-temple-studies", "spanish"],
     "El templo en la Iglesia Primitiva (ES)."),
    ("Sacerdocio en acción, El - Desconocido.epub",
     "sacerdocio-en-accion-es", "Desconocido", "es", "books",
     30, 65, "opcional",
     ["priesthood", "melchizedek", "spanish-lds"],
     "El Sacerdocio en acción (ES)."),
    ("Portavoz de la gracia 195s - Desconocido.epub",
     "portavoz-gracia-195s-es", "Desconocido (evangelical periodical)", "es", "reference",
     15, 50, "opcional",
     ["evangelical-periodical", "spanish", "non-lds"],
     "Portavoz de la Gracia (periodical issue)."),
    ("Portavoz de la gracia_ Conversión - Desconocido.epub",
     "portavoz-gracia-conversion-es", "Desconocido (evangelical periodical)", "es", "reference",
     15, 50, "opcional",
     ["evangelical-periodical", "conversion", "spanish", "non-lds"],
     "Portavoz de la Gracia: Conversión."),
    ("Popol Vuh - Desconocido.epub",
     "popol-vuh-es", "Anonymous (K'iche' Maya)", "es", "scriptures-apocrypha",
     35, 80, "importante",
     ["mesoamerican", "kiche-maya", "creation-myth", "primary-source", "book-of-mormon-context"],
     "Popol Vuh (ES). Texto sagrado K'iche' Maya, con posibles conexiones con el Libro de Mormón (mesoamerica)."),
    ("Ten Commandments Today - No specific author.epub",
     "ten-commandments-today", "Anonymous", "en", "reference",
     15, 55, "opcional",
     ["ten-commandments", "pamphlet"],
     "Ten Commandments Today (pamphlet)."),
    ("Subsequent Amendments to the Constitution - No specific author.epub",
     "subsequent-amendments-constitution", "Anonymous", "en", "reference",
     20, 70, "opcional",
     ["us-constitution", "amendments", "civic"],
     "Subsequent Amendments to the US Constitution."),
    ("Moment_s Pause - No specific author.epub",
     "moments-pause", "Anonymous", "en", "books",
     15, 50, "opcional",
     ["devotional", "reflection"],
     "A Moment's Pause (devotional fragment)."),
]

ok = 0
broken = []
archived = 0

# Archive
for fn in ARCHIVE:
    p = READY / fn
    if p.exists():
        p.rename(DONE / fn)
        archived += 1
        print(f"  archived: {fn[:60]}")

# Apocrypha to scriptures-apocrypha
for fn, slug, author, lang, tags, note in APOCRYPHA:
    src = READY / fn
    if not src.exists():
        broken.append((fn, "MISSING"))
        continue
    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    fase0.write_text(json.dumps({
        "authority": 30, "rigor": 75, "importance": "importante",
        "official": False, "current": True, "context": "scriptures-apocrypha",
        "audience": "adult", "tags": tags, "category": "scriptures-apocrypha",
        "author": author, "source_url": None, "note": note,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    cmd = [sys.executable, str(EXTRACT), str(src),
           "--lang", lang, "--category", "scriptures-apocrypha", "--apply",
           "--slug", slug, "--author", author, "--fase0", str(fase0)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        src.rename(DONE / fn)
        print(f"  OK [apoc] {slug}")
    else:
        broken.append((fn, r.stderr[-120:] if r.stderr else "?"))
        print(f"  BROKEN [apoc] {slug}")

# Patristic
for fn, slug, author, lang, cat, tags, note in PATRISTIC:
    src = READY / fn
    if not src.exists():
        broken.append((fn, "MISSING"))
        continue
    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    fase0.write_text(json.dumps({
        "authority": 40, "rigor": 80, "importance": "importante",
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
        print(f"  OK [patr] {slug}")
    else:
        broken.append((fn, r.stderr[-120:] if r.stderr else "?"))
        print(f"  BROKEN [patr] {slug}")

# Main works
for fn, slug, author, lang, cat, auth, rigor, imp, tags, note in WORKS:
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

print(f"\nUnknown batch: {ok} OK, {len(broken)} broken, {archived} archived")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}")

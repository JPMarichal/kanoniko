#!/usr/bin/env python
"""Apostles batch — Packer (7) + Maxwell (9) + McConkie (5) + Roberts (1 new).

Individual Fase 0 per work.
"""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

WORKS = [
    # Packer (7)
    ("Memorable Stories and Parables - Boyd K. Packer.epub",
     "memorable-stories-and-parables-packer", "Boyd K. Packer",
     55, 75, "importante", "books", "en",
     ["apostle-authored", "stories", "parables", "teaching-illustrations"],
     "Pres. Boyd K. Packer (1924-2015), Q12 / Pres. Q12. Memorable Stories and Parables."),
    ("Santo Templo, El - Boyd K. Packer.epub",
     "santo-templo-packer-es", "Boyd K. Packer",
     55, 85, "importante", "books", "es",
     ["apostle-authored", "temple", "spanish-translation", "holy-temple"],
     "Pres. Boyd K. Packer. El Santo Templo (traducción ES de The Holy Temple, 1980). Obra clásica de Packer sobre la doctrina del templo."),
    ("Sólo para varones jóvenes - Boyd K. Packer.epub",
     "solo-para-varones-jovenes-packer", "Boyd K. Packer",
     55, 75, "importante", "books", "es",
     ["apostle-authored", "young-men", "moral-cleanliness", "spanish-lds"],
     "Pres. Boyd K. Packer. Sólo para varones jóvenes (To Young Men Only, 1976) — charla clásica sobre pureza moral."),
    ("The Arts and the Spirit of the Lord - Boyd K. Packer.epub",
     "arts-and-spirit-of-the-lord-packer", "Boyd K. Packer",
     55, 80, "importante", "discourses", "en",
     ["apostle-authored", "arts", "inspiration", "classic-devotional", "byu-devotional"],
     "Pres. Boyd K. Packer. The Arts and the Spirit of the Lord (BYU Devotional, 1 feb 1976). Clásico sobre artes y testimonio."),
    ("The One Pure Defense - Boyd K. Packer.epub",
     "the-one-pure-defense-packer", "Boyd K. Packer",
     55, 75, "importante", "discourses", "en",
     ["apostle-authored", "defense", "teaching"],
     "Pres. Boyd K. Packer. The One Pure Defense."),
    ("The Unwritten Order of Things - Boyd K. Packer.epub",
     "unwritten-order-of-things-packer", "Boyd K. Packer",
     55, 80, "importante", "discourses", "en",
     ["apostle-authored", "church-administration", "classic-devotional", "byu-devotional"],
     "Pres. Boyd K. Packer. The Unwritten Order of Things (BYU Devotional, 15 oct 1996). Clásico sobre la cultura no escrita del sacerdocio."),
    ("Things of the Soul - Boyd K. Packer.epub",
     "things-of-the-soul-packer", "Boyd K. Packer",
     55, 75, "importante", "books", "en",
     ["apostle-authored", "spirituality", "soul"],
     "Pres. Boyd K. Packer. Things of the Soul, 1996."),

    # Maxwell (9)
    ("Men and Women of Christ - Neal A Maxwell.epub",
     "men-and-women-of-christ-maxwell", "Neal A. Maxwell",
     50, 80, "importante", "books", "en",
     ["apostle-authored", "discipleship", "christlike-character"],
     "Elder Neal A. Maxwell (1926-2004), Q12. Men and Women of Christ, 1991."),
    ("Neal A_ Maxwell Quote Book - Neal A Maxwell.epub",
     "neal-a-maxwell-quote-book", "Neal A. Maxwell",
     45, 70, "opcional", "reference", "en",
     ["apostle-authored", "quotations", "compilation", "reference-work"],
     "Elder Neal A. Maxwell. The Neal A. Maxwell Quote Book (compilación de citas)."),
    ("One More Strain of Praise - Neal A Maxwell.epub",
     "one-more-strain-of-praise-maxwell", "Neal A. Maxwell",
     50, 80, "importante", "books", "en",
     ["apostle-authored", "praise", "gratitude"],
     "Elder Neal A. Maxwell. One More Strain of Praise, 1999."),
    ("Promise of Discipleship, The - Neal A Maxwell.epub",
     "promise-of-discipleship-maxwell", "Neal A. Maxwell",
     50, 80, "importante", "books", "en",
     ["apostle-authored", "discipleship", "promise"],
     "Elder Neal A. Maxwell. The Promise of Discipleship, 2001."),
    ("Sermons Not Spoken - Neal A Maxwell.epub",
     "sermons-not-spoken-maxwell", "Neal A. Maxwell",
     50, 75, "importante", "books", "en",
     ["apostle-authored", "essays"],
     "Elder Neal A. Maxwell. Sermons Not Spoken, 1985."),
    ("Smallest Part - Neal A Maxwell.epub",
     "smallest-part-maxwell", "Neal A. Maxwell",
     50, 75, "importante", "books", "en",
     ["apostle-authored", "humility", "agency"],
     "Elder Neal A. Maxwell. The Smallest Part, 1973."),
    ("Time to Choose - Neal A Maxwell.epub",
     "time-to-choose-maxwell", "Neal A. Maxwell",
     50, 75, "importante", "books", "en",
     ["apostle-authored", "choice", "agency"],
     "Elder Neal A. Maxwell. A Time to Choose, 1972."),
    ("Wonderful Flood of Light - Neal A Maxwell.epub",
     "wonderful-flood-of-light-maxwell", "Neal A. Maxwell",
     50, 75, "importante", "books", "en",
     ["apostle-authored", "restoration", "light"],
     "Elder Neal A. Maxwell. A Wonderful Flood of Light, 1990."),
    ("mandamiento firme y dulce, El - Neal A. Maxwell.epub",
     "mandamiento-firme-y-dulce-maxwell", "Neal A. Maxwell",
     50, 75, "importante", "books", "es",
     ["apostle-authored", "commandment", "discipline", "spanish-translation"],
     "Elder Neal A. Maxwell. El mandamiento firme y dulce (ES translation)."),

    # McConkie (5)
    ("Mortal Messiah, From Bethlehem to Calvary, vol_ 1 - Bruce R. McConkie.epub",
     "mortal-messiah-vol-1-mcconkie", "Bruce R. McConkie",
     55, 85, "importante", "books", "en",
     ["apostle-authored", "messiah-series", "nt-life-of-christ", "classic-nt-commentary"],
     "Elder Bruce R. McConkie (1915-1985), Q12. The Mortal Messiah vol. 1, 1979. Parte de la tetralogía Messiah (distinta de Millennial Messiah)."),
    ("Mortal Messiah, From Bethlehem to Calvary, vol_ 2 - Bruce R. McConkie.epub",
     "mortal-messiah-vol-2-mcconkie", "Bruce R. McConkie",
     55, 85, "importante", "books", "en",
     ["apostle-authored", "messiah-series", "nt-life-of-christ"],
     "Elder Bruce R. McConkie. The Mortal Messiah vol. 2, 1980."),
    ("Mortal Messiah, From Bethlehem to Calvary, vol_ 3 - Bruce R. McConkie.epub",
     "mortal-messiah-vol-3-mcconkie", "Bruce R. McConkie",
     55, 85, "importante", "books", "en",
     ["apostle-authored", "messiah-series", "nt-life-of-christ"],
     "Elder Bruce R. McConkie. The Mortal Messiah vol. 3, 1981."),
    ("Mortal Messiah, From Bethlehem to Calvary, vol_ 4 - Bruce R. McConkie.epub",
     "mortal-messiah-vol-4-mcconkie", "Bruce R. McConkie",
     55, 85, "importante", "books", "en",
     ["apostle-authored", "messiah-series", "nt-life-of-christ"],
     "Elder Bruce R. McConkie. The Mortal Messiah vol. 4, 1981."),
    ("Predicador de Rectitud - Bruce R. McConkie.epub",
     "predicador-de-rectitud-mcconkie-es", "Bruce R. McConkie",
     55, 80, "importante", "books", "es",
     ["apostle-authored", "noah", "priesthood", "spanish-translation"],
     "Elder Bruce R. McConkie. Predicador de Rectitud (ES). Reflexión sobre Noé y el sacerdocio."),

    # Roberts (1 — only non-dup)
    ("Rasha the Jew - B. H. Roberts.epub",
     "rasha-the-jew-roberts", "B. H. Roberts",
     40, 70, "opcional", "books", "en",
     ["b-h-roberts", "historical-novel", "jewish-theme", "19th-century-lds"],
     "B. H. Roberts (1857-1933), First Council of Seventy. Rasha the Jew, 1932 — novela de corte histórico-religioso."),
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
        print(f"  BROKEN {slug}")

print(f"\nApostles batch: {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}")

#!/usr/bin/env python
"""Pairs batch 2: more 2-count clusters. Archive Twain."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

ARCHIVE = [
    "Prince and the Pauper - Mark Twain.epub",
    "Roughing It, Part 2. - Mark Twain.epub",
]

WORKS = [
    # Augustine (2)
    ("On Christian Doctrine - Agustín.epub",
     "on-christian-doctrine-augustine", "Augustine of Hippo",
     40, 85, "importante", "reference", "en",
     ["patristic", "4th-5th-century", "hermeneutics", "augustine", "primary-source"],
     "Augustine. De Doctrina Christiana (On Christian Doctrine), c. 397-426. Foundational hermeneutic work."),
    ("On the Trinity - Agustín.epub",
     "on-the-trinity-augustine", "Augustine of Hippo",
     40, 85, "importante", "reference", "en",
     ["patristic", "4th-5th-century", "trinity", "augustine", "primary-source"],
     "Augustine. De Trinitate, c. 400-428. Magnum opus on Trinitarian theology."),
    # Morrison Seventy (2)
    ("Visions of Zion - Alexander B. Morrison.epub",
     "visions-of-zion-morrison", "Alexander B. Morrison",
     45, 75, "importante", "books", "en",
     ["seventy-authored", "zion", "gathering"],
     "Elder Alexander B. Morrison, Seventy. Visions of Zion."),
    ("Zion, A Light in the Darkness - Alexander B. Morrison.epub",
     "zion-light-in-darkness-morrison", "Alexander B. Morrison",
     45, 75, "importante", "books", "en",
     ["seventy-authored", "zion", "latter-days"],
     "Elder Alexander B. Morrison. Zion: A Light in the Darkness."),
    # Van Orden (2)
    ("Prisoner for Conscience_ Sake, The Life of George Reynolds - Bruce A. Van Orden.epub",
     "prisoner-conscience-george-reynolds-vanorden", "Bruce A. Van Orden",
     35, 80, "importante", "biographies", "en",
     ["byu-academic", "george-reynolds", "polygamy-trials", "late-19th-century"],
     "Bruce A. Van Orden, BYU. Prisoner for Conscience' Sake: The Life of George Reynolds, 1992."),
    ("Proceedings before the Committee on Privileges angainst the Hight of Hon_ Ree - Bruce A. Van Orden.epub",
     "proceedings-smoot-hearings-vanorden", "Bruce A. Van Orden (ed.)",
     40, 85, "importante", "history", "en",
     ["smoot-hearings", "reed-smoot", "senate-proceedings", "early-20th-century-lds", "primary-source"],
     "Bruce A. Van Orden (ed.). Proceedings before the Committee on Privileges re Reed Smoot."),
    # Charles D. Tate (2)
    ("Second Nephi, The Doctrinal Structure - Charles D. Tate.epub",
     "second-nephi-doctrinal-structure-tate", "Charles D. Tate (ed.)",
     35, 80, "importante", "books", "en",
     ["byu-academic", "2-nephi", "book-of-mormon"],
     "Charles D. Tate Jr. (ed.), BYU. Second Nephi: The Doctrinal Structure."),
    ("View of the Hebrews, 1825 2nd Edition Complete Text - Charles D. Tate.epub",
     "view-of-the-hebrews-1825-tate", "Charles D. Tate (ed.)",
     30, 80, "importante", "history", "en",
     ["ethan-smith", "view-of-hebrews", "1825", "primary-source", "book-of-mormon-sources-debate"],
     "Ethan Smith (1762-1849), ed. Charles D. Tate. A View of the Hebrews, 1825 2nd edition — frequently cited in BoM-sources discussions."),
    # Spurgeon (2) — evangelical
    ("proceso de la salvación, El - Charles H. Spurgeon.epub",
     "proceso-de-la-salvacion-spurgeon-es", "Charles H. Spurgeon",
     20, 70, "opcional", "reference", "es",
     ["evangelical", "baptist", "19th-century", "salvation", "non-lds", "spurgeon"],
     "Charles H. Spurgeon (1834-1892). El proceso de la salvación (ES)."),
    ("tesoro de David, El - Charles H. Spurgeon.epub",
     "tesoro-de-david-spurgeon-es", "Charles H. Spurgeon",
     20, 75, "opcional", "reference", "es",
     ["evangelical", "baptist", "19th-century", "psalms-commentary", "non-lds", "spurgeon"],
     "Charles H. Spurgeon. El tesoro de David — comentario exhaustivo sobre los Salmos (ES)."),
    # Clement of Alexandria (2)
    ("Paedagogus - Clemente de Alejandría.epub",
     "paedagogus-clement-alexandria", "Clement of Alexandria",
     40, 85, "importante", "reference", "en",
     ["patristic", "2nd-3rd-century", "ante-nicene", "clement-of-alexandria", "primary-source"],
     "Clement of Alexandria (c. 150-215). Paedagogus (The Instructor)."),
    ("Stromata - Clemente de Alejandría.epub",
     "stromata-clement-alexandria", "Clement of Alexandria",
     40, 85, "importante", "reference", "en",
     ["patristic", "2nd-3rd-century", "ante-nicene", "clement-of-alexandria", "primary-source"],
     "Clement of Alexandria. Stromata (Miscellanies). Major theological work."),
    # Daniel H. Ludlow (2)
    ("Marking the Scriptures - Daniel H. Ludlow.epub",
     "marking-the-scriptures-dh-ludlow", "Daniel H. Ludlow",
     45, 75, "opcional", "study-aids", "en",
     ["scripture-marking", "byu-religious-studies", "study-method"],
     "Daniel H. Ludlow. Marking the Scriptures."),
    ("Selected Writings of Daniel H_ Ludlow, Gospel Scholars Series - Daniel H. Ludlow.epub",
     "selected-writings-dh-ludlow", "Daniel H. Ludlow",
     45, 80, "importante", "books", "en",
     ["byu-religious-studies", "gospel-scholars-series", "collected-writings"],
     "Daniel H. Ludlow. Selected Writings (Gospel Scholars Series). DH Ludlow was editor of Encyclopedia of Mormonism."),
    # David O. McKay (2)
    ("Pathways to Happiness - David O. McKay.epub",
     "pathways-to-happiness-mckay", "David O. McKay",
     55, 80, "importante", "books", "en",
     ["prophet-authored", "happiness", "mid-20th-century"],
     "Pres. David O. McKay (1873-1970). Pathways to Happiness."),
    ("Steppingstones to an Abundant Life - David O. McKay.epub",
     "steppingstones-abundant-life-mckay", "David O. McKay",
     55, 80, "importante", "books", "en",
     ["prophet-authored", "abundant-life", "mid-20th-century"],
     "Pres. David O. McKay. Steppingstones to an Abundant Life."),
    # James E. Faust (2)
    ("Reach Up for the Light - James E Faust.epub",
     "reach-up-for-the-light-faust", "James E. Faust",
     55, 80, "importante", "books", "en",
     ["first-presidency-authored", "light", "discipleship"],
     "Pres. James E. Faust (1920-2007), Second Counselor. Reach Up for the Light."),
    ("To Reach Even unto You - James E Faust.epub",
     "to-reach-even-unto-you-faust", "James E. Faust",
     55, 80, "importante", "books", "en",
     ["first-presidency-authored", "ministering"],
     "Pres. James E. Faust. To Reach Even unto You."),
    # John Bytheway (2)
    ("What I Wish I_d Known in High School, A Crash Course in Teenage Survival - John Bytheway.epub",
     "what-i-wish-known-high-school-bytheway", "John Bytheway",
     30, 60, "opcional", "books", "en",
     ["byu-popular", "youth", "teens", "humor"],
     "John Bytheway. What I Wish I'd Known in High School."),
    ("What I Wish I_d Known in High School, The Second Semester - John Bytheway.epub",
     "what-i-wish-known-high-school-2-bytheway", "John Bytheway",
     30, 60, "opcional", "books", "en",
     ["byu-popular", "youth", "teens", "humor"],
     "John Bytheway. What I Wish I'd Known in High School: The Second Semester."),
    # JF Smith (2)
    ("Progress of Man - Joseph Fielding Smith.epub",
     "progress-of-man-jfs", "Joseph Fielding Smith",
     55, 80, "importante", "books", "en",
     ["prophet-authored", "progress", "evolution-debate"],
     "Pres. Joseph Fielding Smith (1876-1972). The Progress of Man, 1936/1964."),
    ("Take Heed to Yourselves - Joseph Fielding Smith.epub",
     "take-heed-to-yourselves-jfs", "Joseph Fielding Smith",
     55, 80, "importante", "books", "en",
     ["prophet-authored", "sermons-compilation"],
     "Pres. Joseph Fielding Smith. Take Heed to Yourselves — sermon compilation."),
    # Kent P. Jackson (2)
    ("Studies in Scripture, Vol_ 4, 1 Kings to Malachi - Kent P Jackson.epub",
     "studies-in-scripture-vol-4-jackson", "Kent P. Jackson (ed.)",
     40, 80, "importante", "books", "en",
     ["byu-religious-studies", "studies-in-scripture-series", "ot-commentary"],
     "Kent P. Jackson (ed.). Studies in Scripture, Vol. 4: 1 Kings to Malachi."),
    ("Studies in Scripture, Vol_ 8, Alma 30 to Moroni - Kent P Jackson.epub",
     "studies-in-scripture-vol-8-jackson", "Kent P. Jackson (ed.)",
     40, 80, "importante", "books", "en",
     ["byu-religious-studies", "studies-in-scripture-series", "book-of-mormon"],
     "Kent P. Jackson (ed.). Studies in Scripture, Vol. 8: Alma 30 to Moroni."),
    # Martin Luther (2)
    ("Smalcald Articles - Martin Luther.epub",
     "smalcald-articles-luther", "Martin Luther",
     30, 85, "importante", "reference", "en",
     ["lutheran", "reformation", "16th-century", "confession", "primary-source", "non-lds"],
     "Martin Luther. Smalcald Articles, 1537. Lutheran confession."),
    ("Treatise on Good Works - Martin Luther.epub",
     "treatise-good-works-luther", "Martin Luther",
     30, 80, "importante", "reference", "en",
     ["lutheran", "reformation", "16th-century", "works-and-faith", "primary-source", "non-lds"],
     "Martin Luther. A Treatise on Good Works, 1520."),
]

# Archive Twain
archived = 0
for fn in ARCHIVE:
    p = READY / fn
    if p.exists():
        p.rename(DONE / fn)
        archived += 1
        print(f"  archived (literature): {fn[:60]}")

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

print(f"\nPairs 2 batch: {ok} OK, {len(broken)} broken, {archived} archived")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}")

#!/usr/bin/env python
"""LDS author clusters: Millet (6), Barlow (6), Cook (4), Crowther ES (4),
Widtsoe (4), Andrus (4), SW Kimball (2+1 dup), Preston Nibley (3),
Crowder (4), Hartshorn (3), D.W. Parry (3), Shelton ES (3)."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

ARCHIVE_DUPS = [
    "MILAGRO DEL PERDON, EL - Spencer W. Kimball.epub",  # dup of 'milagro del perdón, El'
]

WORKS = [
    # Millet (6)
    ("Mormon Faith, Understanding Restored Christianity - Robert L Millet.epub",
     "mormon-faith-understanding-millet", "Robert L. Millet", 40, 80, "importante",
     "books", "en", ["byu-religious-studies", "apologetics", "interfaith"],
     "Robert L. Millet, BYU. A Mormon Faith: Understanding Restored Christianity."),
    ("Selected Writings of Robert L_ Millet, Gospel Scholars Series - Robert L Millet.epub",
     "selected-writings-millet", "Robert L. Millet", 40, 75, "opcional",
     "books", "en", ["byu-religious-studies", "gospel-scholars-series", "collected-writings"],
     "Robert L. Millet. Selected Writings (Gospel Scholars Series)."),
    ("Steadfast and Immovable, Striving for Spiritual Maturity - Robert L Millet.epub",
     "steadfast-and-immovable-millet", "Robert L. Millet", 40, 75, "importante",
     "books", "en", ["byu-religious-studies", "spiritual-maturity", "discipleship"],
     "Robert L. Millet. Steadfast and Immovable."),
    ("Studies in Scripture, Vol_ 6, Acts to Revelation - Robert L Millet.epub",
     "studies-in-scripture-vol-6-millet", "Robert L. Millet (ed.)", 40, 80, "importante",
     "books", "en", ["byu-religious-studies", "studies-in-scripture-series", "nt-commentary"],
     "Robert L. Millet (ed.). Studies in Scripture, Vol. 6: Acts to Revelation, 1987."),
    ("When a Child Wanders - Robert L Millet.epub",
     "when-a-child-wanders-millet", "Robert L. Millet", 40, 70, "importante",
     "books", "en", ["byu-religious-studies", "parenting", "wayward-children", "pastoral"],
     "Robert L. Millet. When a Child Wanders."),
    ("Within Reach - Robert L Millet.epub",
     "within-reach-millet", "Robert L. Millet", 40, 75, "opcional",
     "books", "en", ["byu-religious-studies", "gospel-living"],
     "Robert L. Millet. Within Reach."),

    # Barlow (6)
    ("Twelve Traps in Today_s Marriage and How to Avoid Them - Brent A. Barlow.epub",
     "twelve-traps-marriage-barlow", "Brent A. Barlow", 35, 70, "opcional",
     "books", "en", ["byu-family-life", "marriage", "pastoral"],
     "Brent A. Barlow, BYU. Twelve Traps in Today's Marriage."),
    ("Understanding Death - Brent A. Barlow.epub",
     "understanding-death-barlow", "Brent A. Barlow", 35, 70, "opcional",
     "books", "en", ["byu-family-life", "death", "grief", "pastoral"],
     "Brent A. Barlow. Understanding Death."),
    ("What Husbands Expect of Wives - Brent A. Barlow.epub",
     "what-husbands-expect-of-wives-barlow", "Brent A. Barlow", 30, 65, "opcional",
     "books", "en", ["byu-family-life", "marriage", "gender-roles"],
     "Brent A. Barlow. What Husbands Expect of Wives."),
    ("What Wives Expect of Husbands - Brent A. Barlow.epub",
     "what-wives-expect-of-husbands-barlow", "Brent A. Barlow", 30, 65, "opcional",
     "books", "en", ["byu-family-life", "marriage", "gender-roles"],
     "Brent A. Barlow. What Wives Expect of Husbands."),
    ("Worth Waiting For, Sexual Abstinence Before Marriage - Brent A. Barlow.epub",
     "worth-waiting-for-barlow", "Brent A. Barlow", 35, 70, "opcional",
     "books", "en", ["byu-family-life", "chastity", "youth", "premarital"],
     "Brent A. Barlow. Worth Waiting For: Sexual Abstinence Before Marriage."),
    ("relaciones íntimas en el matrimonio, Las - Brent A. Barlow.epub",
     "relaciones-intimas-matrimonio-barlow-es", "Brent A. Barlow", 30, 65, "opcional",
     "books", "es", ["byu-family-life", "marriage", "intimacy"],
     "Brent A. Barlow. Las relaciones íntimas en el matrimonio (ES)."),

    # Gene R. Cook (4)
    ("Raising Up a Family to the Lord - Gene R. Cook.epub",
     "raising-up-a-family-cook", "Gene R. Cook", 45, 70, "importante",
     "books", "en", ["seventy-authored", "family", "parenting"],
     "Elder Gene R. Cook, Seventy. Raising Up a Family to the Lord."),
    ("Receiving Answers to Our Prayers - Gene R. Cook.epub",
     "receiving-answers-cook", "Gene R. Cook", 45, 70, "importante",
     "books", "en", ["seventy-authored", "prayer", "answers"],
     "Elder Gene R. Cook. Receiving Answers to Our Prayers."),
    ("Searching the Scriptures - Gene R. Cook.epub",
     "searching-the-scriptures-cook", "Gene R. Cook", 45, 70, "importante",
     "books", "en", ["seventy-authored", "scripture-study"],
     "Elder Gene R. Cook. Searching the Scriptures."),
    ("The eternal nature of the law of chastity - Gene R. Cook.epub",
     "eternal-nature-law-chastity-cook", "Gene R. Cook", 45, 70, "importante",
     "discourses", "en", ["seventy-authored", "chastity", "byu-devotional"],
     "Elder Gene R. Cook. The Eternal Nature of the Law of Chastity (devotional)."),

    # Crowther (4)
    ("Puebras bíblicas sobre la Iglesia restaurada y el Libro de Mormón - Duane S. Crowther.epub",
     "pruebas-biblicas-iglesia-restaurada-crowther-es", "Duane S. Crowther",
     30, 65, "opcional", "books", "es",
     ["apologetics", "bible-proofs", "spanish-lds"],
     "Duane S. Crowther. Pruebas bíblicas sobre la Iglesia restaurada (ES)."),
    ("profecía, llave al futuro, La - Duane S. Crowther.epub",
     "profecia-llave-al-futuro-crowther-es", "Duane S. Crowther",
     30, 65, "opcional", "books", "es",
     ["prophecy", "last-days", "spanish-lds"],
     "Duane S. Crowther. La profecía, llave al futuro (ES)."),
    ("vida sempiterna, volúmen 1, La - Duane S. Crowther.epub",
     "vida-sempiterna-vol-1-crowther-es", "Duane S. Crowther",
     30, 65, "opcional", "books", "es",
     ["afterlife", "spirit-world", "spanish-lds"],
     "Duane S. Crowther. La vida sempiterna, vol. 1 (ES). Sobre el mundo de los espíritus."),
    ("vida sempiterna, volúmen 2, La - Duane S. Crowther.epub",
     "vida-sempiterna-vol-2-crowther-es", "Duane S. Crowther",
     30, 65, "opcional", "books", "es",
     ["afterlife", "spirit-world", "resurrection", "spanish-lds"],
     "Duane S. Crowther. La vida sempiterna, vol. 2 (ES)."),

    # Widtsoe (4)
    ("Rational Theology - John A Widtsoe.epub",
     "rational-theology-widtsoe", "John A. Widtsoe", 50, 85, "importante",
     "books", "en", ["apostle-authored", "rational-theology", "classic-doctrinal"],
     "Elder John A. Widtsoe (1872-1952), Q12. A Rational Theology, 1915."),
    ("Seven Claims of the Book of Mormon - John A Widtsoe.epub",
     "seven-claims-bom-widtsoe", "John A. Widtsoe", 50, 80, "importante",
     "books", "en", ["apostle-authored", "book-of-mormon", "apologetics"],
     "Elder John A. Widtsoe. Seven Claims of the Book of Mormon."),
    ("Understandable Religion - John A Widtsoe.epub",
     "understandable-religion-widtsoe", "John A. Widtsoe", 50, 80, "importante",
     "books", "en", ["apostle-authored", "gospel-accessibility"],
     "Elder John A. Widtsoe. Understandable Religion."),
    ("Word of Wisdom, A Modern Interpretation - John A Widtsoe.epub",
     "word-of-wisdom-widtsoe", "John A. Widtsoe & Leah D. Widtsoe", 50, 80, "importante",
     "books", "en", ["apostle-authored", "word-of-wisdom", "classic-health"],
     "Elder John A. Widtsoe & Leah D. Widtsoe. The Word of Wisdom: A Modern Interpretation, 1937."),

    # Andrus (4) — classic BYU theologian
    ("Liberalism, Conservatism, Mormonism - Hyrum L. Andrus.epub",
     "liberalism-conservatism-mormonism-andrus", "Hyrum L. Andrus", 35, 70, "opcional",
     "books", "en", ["byu-theology", "political-philosophy", "mid-20th-century-lds"],
     "Hyrum L. Andrus, BYU. Liberalism, Conservatism, Mormonism."),
    ("Mormonism and the Rise of Western Civilization - Hyrum L. Andrus.epub",
     "mormonism-rise-western-civ-andrus", "Hyrum L. Andrus", 35, 75, "opcional",
     "books", "en", ["byu-theology", "civilization-history"],
     "Hyrum L. Andrus. Mormonism and the Rise of Western Civilization."),
    ("Principles of Perfection - Hyrum L. Andrus.epub",
     "principles-of-perfection-andrus", "Hyrum L. Andrus", 35, 80, "importante",
     "books", "en", ["byu-theology", "exaltation", "eternal-progression"],
     "Hyrum L. Andrus. Principles of Perfection."),
    ("War and Saints - Hyrum L. Andrus.epub",
     "war-and-saints-andrus", "Hyrum L. Andrus", 35, 70, "opcional",
     "books", "en", ["byu-theology", "war", "pacifism"],
     "Hyrum L. Andrus. War and Saints."),

    # SW Kimball (2 unique; 1 dup archived)
    ("milagro del perdón, El - Spencer W. Kimball.epub",
     "milagro-del-perdon-kimball-es", "Spencer W. Kimball", 55, 85, "importante",
     "books", "es", ["prophet-authored", "repentance", "classic", "spanish-translation"],
     "Pres. Spencer W. Kimball (1895-1985). El Milagro del Perdón (ES) — clásico doctrinal sobre arrepentimiento."),
    ("Visión del futuro de los lamanitas - Spencer W. Kimball.epub",
     "vision-futuro-lamanitas-kimball-es", "Spencer W. Kimball", 55, 80, "importante",
     "discourses", "es", ["prophet-authored", "lamanites", "spanish-discourse"],
     "Pres. Spencer W. Kimball. Visión del futuro de los lamanitas."),

    # Preston Nibley (3)
    ("Missionary Experiences - Preston Nibley.epub",
     "missionary-experiences-p-nibley", "Preston Nibley", 35, 70, "opcional",
     "books", "en", ["church-historian", "missionary-stories", "mid-20th-century"],
     "Preston Nibley (1884-1966), Assistant Church Historian. Missionary Experiences."),
    ("Pioneer Stories - Preston Nibley.epub",
     "pioneer-stories-p-nibley", "Preston Nibley", 35, 70, "importante",
     "history", "en", ["pioneer-stories", "church-historian"],
     "Preston Nibley. Pioneer Stories."),
    ("Stalwarts of Mormonism - Preston Nibley.epub",
     "stalwarts-of-mormonism-p-nibley", "Preston Nibley", 35, 70, "opcional",
     "biographies", "en", ["biographical-sketches", "church-historian"],
     "Preston Nibley. Stalwarts of Mormonism."),

    # Benjamin Crowder (4) — scripture reader's editions
    ("New Testament, The - Benjamin Crowder.epub",
     "nt-readers-edition-crowder", "Benjamin Crowder (ed.)", 25, 65, "opcional",
     "study-aids", "en", ["bible", "readers-edition", "new-testament"],
     "Benjamin Crowder. The New Testament (reader's edition)."),
    ("Novum Testamentum Graece_ Reader's Edition - Benjamin Crowder.epub",
     "novum-testamentum-graece-crowder", "Benjamin Crowder (ed.)", 30, 80, "importante",
     "study-aids", "en", ["greek-nt", "readers-edition", "biblical-greek"],
     "Benjamin Crowder. Novum Testamentum Graece: Reader's Edition."),
    ("Old Testament, The - Benjamin Crowder.epub",
     "ot-readers-edition-crowder", "Benjamin Crowder (ed.)", 25, 65, "opcional",
     "study-aids", "en", ["bible", "readers-edition", "old-testament"],
     "Benjamin Crowder. The Old Testament (reader's edition)."),
    ("Plan de Salvación, diagrama - Benjamin Crowder.epub",
     "plan-salvacion-diagrama-crowder-es", "Benjamin Crowder", 20, 55, "opcional",
     "reference", "es", ["plan-of-salvation", "diagram"],
     "Benjamin Crowder. Plan de Salvación, diagrama (ES)."),

    # Hartshorn (3)
    ("Outstanding Stories by General Authorities, vol_ 1 - Leon R Hartshorn.epub",
     "outstanding-stories-gas-vol-1-hartshorn", "Leon R. Hartshorn (ed.)", 40, 70, "importante",
     "books", "en", ["general-authorities", "stories", "anthology"],
     "Leon R. Hartshorn (ed.). Outstanding Stories by General Authorities, vol. 1."),
    ("Outstanding Stories by General Authorities, vol_ 2 - Leon R Hartshorn.epub",
     "outstanding-stories-gas-vol-2-hartshorn", "Leon R. Hartshorn (ed.)", 40, 70, "importante",
     "books", "en", ["general-authorities", "stories", "anthology"],
     "Leon R. Hartshorn (ed.). Outstanding Stories by General Authorities, vol. 2."),
    ("Outstanding Stories by General Authorities, vol_ 3 - Leon R Hartshorn.epub",
     "outstanding-stories-gas-vol-3-hartshorn", "Leon R. Hartshorn (ed.)", 40, 70, "importante",
     "books", "en", ["general-authorities", "stories", "anthology"],
     "Leon R. Hartshorn (ed.). Outstanding Stories by General Authorities, vol. 3."),

    # Donald W. Parry (3)
    ("Understanding Isaiah - Donald W. Parry.epub",
     "understanding-isaiah-parry", "Donald W. Parry", 40, 85, "importante",
     "books", "en", ["isaiah", "byu-academic", "dead-sea-scrolls"],
     "Donald W. Parry, BYU Dead Sea Scrolls scholar. Understanding Isaiah."),
    ("Understanding the Book of Revelation - Donald W. Parry.epub",
     "understanding-revelation-parry", "Donald W. Parry", 40, 80, "importante",
     "books", "en", ["revelation", "apocalyptic", "byu-academic"],
     "Donald W. Parry. Understanding the Book of Revelation."),
    ("Understanding the Signs of the Times - Donald W. Parry.epub",
     "understanding-signs-times-parry", "Donald W. Parry", 40, 75, "importante",
     "books", "en", ["signs-of-the-times", "last-days", "byu-academic"],
     "Donald W. Parry. Understanding the Signs of the Times."),

    # Lee Roy Shelton Jr (3, evangelical Baptist)
    ("pecado de mentir, El - Lee Roy Shelton, Jr_.epub",
     "pecado-de-mentir-shelton-es", "Lee Roy Shelton Jr.", 15, 45, "opcional",
     "reference", "es", ["evangelical", "baptist", "sin", "non-lds"],
     "Lee Roy Shelton Jr. El pecado de mentir (ES evangelical)."),
    ("pecado de robar, El - Lee Roy Shelton, Jr_.epub",
     "pecado-de-robar-shelton-es", "Lee Roy Shelton Jr.", 15, 45, "opcional",
     "reference", "es", ["evangelical", "baptist", "sin", "non-lds"],
     "Lee Roy Shelton Jr. El pecado de robar (ES evangelical)."),
    ("verdadero evangelio_. versus evangelio falso, El - Lee Roy Shelton, Jr_.epub",
     "verdadero-evangelio-shelton-es", "Lee Roy Shelton Jr.", 15, 45, "opcional",
     "reference", "es", ["evangelical", "baptist", "gospel", "non-lds"],
     "Lee Roy Shelton Jr. El verdadero evangelio versus evangelio falso (ES)."),
]

for fn in ARCHIVE_DUPS:
    p = READY / fn
    if p.exists():
        p.rename(DONE / fn)
        print(f"  dup archived: {fn[:60]}")

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

print(f"\nLDS clusters: {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}")

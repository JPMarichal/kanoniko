#!/usr/bin/env python
"""Pairs batch — authors with 2 works in !Ready. Individual Fase 0."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

ARCHIVE_DUPS = [
    "Orson Pratt_s Works - Orson Pratt.epub",  # dup of 'Orson Pratt's Works'
]

WORKS = [
    ("Principles and Practices of the Restored Gospel - Victor L Ludlow.epub",
     "principles-practices-restored-gospel-ludlow", "Victor L. Ludlow",
     40, 80, "importante", "books", "en",
     ["byu-religious-studies", "doctrinal-compendium"],
     "Victor L. Ludlow, BYU. Principles and Practices of the Restored Gospel, 1992."),
    ("Unlocking the Old Testament - Victor L Ludlow.epub",
     "unlocking-the-ot-ludlow", "Victor L. Ludlow",
     40, 80, "importante", "books", "en",
     ["old-testament", "byu-academic"],
     "Victor L. Ludlow. Unlocking the Old Testament, 1981."),
    ("Radiant Life - Truman G Madsen.epub",
     "radiant-life-madsen", "Truman G. Madsen",
     40, 75, "importante", "books", "en",
     ["byu-philosophy", "gospel-living", "classic-byu-devotional"],
     "Truman G. Madsen (1926-2009), BYU. Radiant Life."),
    ("Reflections on Mormonism, Judaeo-Christian Parallels - Truman G Madsen.epub",
     "reflections-mormonism-judeo-christian-madsen", "Truman G. Madsen (ed.)",
     40, 85, "importante", "books", "en",
     ["byu-academic", "jewish-studies", "religious-studies-center"],
     "Truman G. Madsen (ed.). Reflections on Mormonism: Judeo-Christian Parallels, 1978."),
    ("Principles, Promises, and Powers - Sterling W Sill.epub",
     "principles-promises-powers-sill", "Sterling W. Sill",
     45, 70, "opcional", "books", "en",
     ["seventy-authored", "gospel-living"],
     "Elder Sterling W. Sill (1903-1994), Seventy. Principles, Promises, and Powers."),
    ("Wealth of Wisdom - Sterling W Sill.epub",
     "wealth-of-wisdom-sill", "Sterling W. Sill",
     45, 70, "opcional", "books", "en",
     ["seventy-authored", "wisdom-quotations"],
     "Elder Sterling W. Sill. Wealth of Wisdom."),
    ("Liderazgo centrado en principios - Stephen R. Covey.epub",
     "liderazgo-centrado-principios-covey-es", "Stephen R. Covey",
     25, 75, "opcional", "reference", "es",
     ["self-help", "lds-author", "leadership", "bestseller"],
     "Stephen R. Covey. Liderazgo centrado en principios (ES translation of Principle-Centered Leadership)."),
    ("octavo hábito, El - Stephen R. Covey.epub",
     "octavo-habito-covey-es", "Stephen R. Covey",
     25, 70, "opcional", "reference", "es",
     ["self-help", "lds-author", "leadership"],
     "Stephen R. Covey. El 8º Hábito (ES translation)."),
    ("Miracle of Forgiveness - Spencer W Kimball.epub",
     "miracle-of-forgiveness-kimball", "Spencer W. Kimball",
     55, 85, "importante", "books", "en",
     ["prophet-authored", "repentance", "forgiveness", "classic"],
     "Pres. Spencer W. Kimball. The Miracle of Forgiveness, 1969 — classic doctrinal work."),
    ("My Beloved Sisters - Spencer W Kimball.epub",
     "my-beloved-sisters-kimball", "Spencer W. Kimball",
     55, 80, "importante", "books", "en",
     ["prophet-authored", "women", "sisters"],
     "Pres. Spencer W. Kimball. My Beloved Sisters, 1979."),
    ("Spirit of the Old Testament - Sidney B Sperry.epub",
     "spirit-of-the-ot-sperry", "Sidney B. Sperry",
     40, 80, "importante", "books", "en",
     ["byu-academic", "old-testament"],
     "Sidney B. Sperry (1895-1977), BYU. Spirit of the Old Testament, 1940."),
    ("Voice of Israel_s Prophets - Sidney B Sperry.epub",
     "voice-of-israels-prophets-sperry", "Sidney B. Sperry",
     40, 80, "importante", "books", "en",
     ["byu-academic", "old-testament", "prophets"],
     "Sidney B. Sperry. The Voice of Israel's Prophets, 1952."),
    ("Perfection Pending, and Other Favorite Discourses - Russell M Nelson.epub",
     "perfection-pending-nelson", "Russell M. Nelson",
     55, 80, "importante", "books", "en",
     ["prophet-authored", "discourses-compilation"],
     "Pres. Russell M. Nelson. Perfection Pending and Other Favorite Discourses."),
    ("Power within Us - Russell M Nelson.epub",
     "power-within-us-nelson", "Russell M. Nelson",
     55, 80, "importante", "books", "en",
     ["prophet-authored", "personal-power", "discipleship"],
     "Pres. Russell M. Nelson. The Power Within Us, 1988."),
    ("Prophet of the Jubilee - Ronald D Dennis.epub",
     "prophet-of-the-jubilee-dennis", "Ronald D. Dennis",
     35, 75, "importante", "biographies", "en",
     ["byu-academic", "dan-jones-missionary", "welsh-mission"],
     "Ronald D. Dennis, BYU. Prophet of the Jubilee (Dan Jones biography)."),
    ("Welsh Mormon Writings from 1844 to 1862, A Historical Bibliography - Ronald D Dennis.epub",
     "welsh-mormon-writings-bibliography-dennis", "Ronald D. Dennis",
     35, 80, "opcional", "reference", "en",
     ["welsh-mission", "bibliography", "byu-academic"],
     "Ronald D. Dennis. Welsh Mormon Writings 1844-1862: A Historical Bibliography."),
    ("The Two Davids - Rodney Turner.epub",
     "two-davids-turner", "Rodney Turner",
     35, 70, "opcional", "books", "en",
     ["byu-religious-studies", "david-of-old", "david-o-mckay"],
     "Rodney Turner, BYU. The Two Davids."),
    ("Woman and the Priesthood - Rodney Turner.epub",
     "woman-and-the-priesthood-turner", "Rodney Turner",
     35, 75, "importante", "books", "en",
     ["byu-religious-studies", "women", "priesthood"],
     "Rodney Turner. Woman and the Priesthood, 1972."),
    ("Studies in Scripture, Vol_ 3, Genesis to 2 Samuel - Robert L Millet & Kent P Jackson.epub",
     "studies-in-scripture-vol-3-millet-jackson", "Robert L. Millet & Kent P. Jackson (eds.)",
     40, 80, "importante", "books", "en",
     ["byu-religious-studies", "studies-in-scripture-series", "ot-commentary"],
     "Millet & Jackson (eds.). Studies in Scripture, Vol. 3: Genesis to 2 Samuel."),
    ("Studies in Scripture, Vol_ 5, The Gospels - Robert L Millet & Kent P Jackson.epub",
     "studies-in-scripture-vol-5-millet-jackson", "Robert L. Millet & Kent P. Jackson (eds.)",
     40, 80, "importante", "books", "en",
     ["byu-religious-studies", "studies-in-scripture-series", "gospels"],
     "Millet & Jackson (eds.). Studies in Scripture, Vol. 5: The Gospels."),
    ("Life Beyond - Robert L Millet & Joseph Fielding McConkie.epub",
     "life-beyond-millet-mcconkie", "Robert L. Millet & Joseph Fielding McConkie",
     40, 80, "importante", "books", "en",
     ["byu-religious-studies", "afterlife", "spirit-world"],
     "Millet & J.F. McConkie. Life Beyond."),
    ("Man Adam - Robert L Millet & Joseph Fielding McConkie.epub",
     "man-adam-millet-mcconkie", "Robert L. Millet & Joseph Fielding McConkie",
     40, 80, "importante", "books", "en",
     ["byu-religious-studies", "adam", "first-man"],
     "Millet & J.F. McConkie. The Man Adam."),
    ("Teaching Children Charity - Richard Eyre & Linda Eyre.epub",
     "teaching-children-charity-eyres", "Richard Eyre & Linda Eyre",
     30, 65, "opcional", "books", "en",
     ["parenting", "charity", "family-values"],
     "Richard & Linda Eyre. Teaching Your Children Charity."),
    ("Teaching Children Joy - Richard Eyre & Linda Eyre.epub",
     "teaching-children-joy-eyres", "Richard Eyre & Linda Eyre",
     30, 65, "opcional", "books", "en",
     ["parenting", "joy", "family-values"],
     "Richard & Linda Eyre. Teaching Your Children Joy."),
    ("Prepare with Honor, Helps for Future Missionaries - Randy L Bott.epub",
     "prepare-with-honor-bott", "Randy L. Bott",
     30, 65, "opcional", "books", "en",
     ["byu-religious-studies", "missionary-preparation"],
     "Randy L. Bott, BYU. Prepare with Honor."),
    ("Serve with Honor, Helps for Missionaries - Randy L Bott.epub",
     "serve-with-honor-bott", "Randy L. Bott",
     30, 65, "opcional", "books", "en",
     ["byu-religious-studies", "missionary-service"],
     "Randy L. Bott. Serve with Honor."),
    ("Protecting Your Family in an X-Rated World - Randal A Wright.epub",
     "protecting-family-x-rated-wright", "Randal A. Wright",
     25, 60, "opcional", "books", "en",
     ["family-protection", "media-literacy", "parenting"],
     "Randal A. Wright. Protecting Your Family in an X-Rated World."),
    ("Why Say No When the World Says Yes Resisting Temptation in an Immoral World - Randal A Wright.epub",
     "why-say-no-wright", "Randal A. Wright",
     25, 60, "opcional", "books", "en",
     ["youth", "chastity", "resisting-temptation"],
     "Randal A. Wright. Why Say No When the World Says Yes?"),
    ("Millennium, and Other Poems _ To Which is Annexed, d Eternal Duration of Matter, The - Parley P. Pratt.epub",
     "millennium-other-poems-pratt", "Parley P. Pratt",
     45, 75, "importante", "books", "en",
     ["apostle-authored", "19th-century-lds", "poetry", "eternal-matter", "primary-source"],
     "Parley P. Pratt. The Millennium and Other Poems — with essay on Eternal Duration of Matter, 1840."),
    ("ángel de las praderas, El - Parley P. Pratt.epub",
     "angel-de-las-praderas-pratt-es", "Parley P. Pratt",
     45, 70, "importante", "books", "es",
     ["apostle-authored", "19th-century-lds", "angel-of-the-prairies", "vision-narrative", "spanish-translation"],
     "Parley P. Pratt. El ángel de las praderas (ES, traducción del Angel of the Prairies, 1880)."),
    ("Orson Pratt's Works_ A Series of Pamphlets on the Doctrines of the Gospel - Orson Pratt.epub",
     "orson-pratts-works", "Orson Pratt",
     50, 85, "importante", "books", "en",
     ["apostle-authored", "19th-century-lds", "doctrinal-pamphlets", "primary-source"],
     "Orson Pratt (1811-1881), Q12. Orson Pratt's Works — series of doctrinal pamphlets, 1851-1859."),
    ("Saturday Night Thoughts _ A Series of Dissertations istorical, and Philosophic Themes - Orson F. Whitney.epub",
     "saturday-night-thoughts-whitney", "Orson F. Whitney",
     45, 80, "importante", "books", "en",
     ["apostle-authored", "dissertations", "early-20th-century-lds"],
     "Elder Orson F. Whitney (1855-1931), Q12. Saturday Night Thoughts, 1921."),
    ("Strength of the _Mormon_ Position, The - Orson F. Whitney.epub",
     "strength-mormon-position-whitney", "Orson F. Whitney",
     45, 75, "opcional", "books", "en",
     ["apostle-authored", "apologetics", "early-20th-century-lds"],
     "Elder Orson F. Whitney. The Strength of the 'Mormon' Position."),
    ("Operacion Jesucristo - Og Mandino.epub",
     "operacion-jesucristo-mandino-es", "Og Mandino",
     15, 50, "opcional", "reference", "es",
     ["self-help", "popular-christian", "non-lds"],
     "Og Mandino (1923-1996). Operación Jesucristo (ES)."),
    ("secreto más grande del mundo, El - Og Mandino.epub",
     "secreto-mas-grande-mandino-es", "Og Mandino",
     15, 50, "opcional", "reference", "es",
     ["self-help", "popular-christian", "non-lds"],
     "Og Mandino. El secreto más grande del mundo (ES)."),
    ("Tenemos el evangelio en su plenitud - N. Eldon Tanner.epub",
     "tenemos-evangelio-plenitud-tanner-es", "N. Eldon Tanner",
     55, 75, "importante", "discourses", "es",
     ["first-presidency-authored", "fullness-of-gospel", "spanish-discourse"],
     "Pres. N. Eldon Tanner (1898-1982), First Presidency. Tenemos el evangelio en su plenitud."),
    ("papel de la mujer, El - N. Eldon Tanner.epub",
     "papel-de-la-mujer-tanner-es", "N. Eldon Tanner",
     55, 75, "importante", "discourses", "es",
     ["first-presidency-authored", "women", "spanish-discourse"],
     "Pres. N. Eldon Tanner. El papel de la mujer."),
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
        broken.append((fn, r.stderr[-120:] if r.stderr else "?"))
        print(f"  BROKEN {slug}")

print(f"\nPairs batch: {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}")

#!/usr/bin/env python
"""Theme 8: LDS doctrine/apologetics/scripture-studies (40 works + 4 dup archives).

Individually curated. Excludes: JPM works, Pelé works.
"""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

ARCHIVE_DUPS = [
    "En los pasos del Cordero - G. Steinberger (1).epub",
    "Isaías, los tiempos del cumplimiento - Iván D. Sanderson (1).epub",
    "In Perfect Balance - Spencer J Condie.epub",  # keep Condie with dot
    "camino hacia un matrimonio cristiano, El - John Thompson (1).epub",
]

WORKS = [
    # Book of Mormon studies
    ("Book of Mormon Compendium - Sidney B Sperry.epub",
     "book-of-mormon-compendium-sperry", "Sidney B. Sperry", 40, 80, "importante",
     "books", "en", ["book-of-mormon", "byu-academic", "20th-century-lds-scholarship"],
     "Sidney B. Sperry (1895-1977), BYU. Book of Mormon Compendium, 1968."),
    ("Book of Mormon, Message and Evidences - Franklin S Harris.epub",
     "book-of-mormon-message-evidences-harris", "Franklin S. Harris Jr.", 35, 70, "opcional",
     "books", "en", ["book-of-mormon", "apologetics", "mid-20th-century"],
     "Franklin S. Harris Jr. Book of Mormon: Message and Evidences, 1953."),
    ("Book of Mormon, The Keystone Scripture - Paul R Cheesman.epub",
     "book-of-mormon-keystone-cheesman", "Paul R. Cheesman", 35, 70, "opcional",
     "books", "en", ["book-of-mormon", "byu-religious-studies"],
     "Paul R. Cheesman (1921-1991), BYU religion faculty. Book of Mormon: Keystone Scripture, 1988."),
    ("Calendars and Chronology of the Book of Mormon - Jerry D. Grover, Jr_.epub",
     "calendars-chronology-bom-grover", "Jerry D. Grover Jr.", 30, 75, "opcional",
     "books", "en", ["book-of-mormon", "chronology", "mesoamerican-studies"],
     "Jerry D. Grover Jr. Calendars and Chronology of the Book of Mormon."),
    ("Case of the Book of Mormon Witnesses - Eldin Ricks.epub",
     "case-book-mormon-witnesses-ricks", "Eldin Ricks", 35, 70, "opcional",
     "books", "en", ["book-of-mormon", "three-witnesses", "eight-witnesses", "apologetics"],
     "Eldin Ricks (1915-1998), BYU. Case of the Book of Mormon Witnesses."),
    ("Cities of the Sun _ Stories of Ancient America founn the Book of Mormon, The - Elizabeth Cannon Porter.epub",
     "cities-of-the-sun-porter", "Elizabeth Cannon Porter", 25, 55, "opcional",
     "books", "en", ["book-of-mormon", "narrative-retelling", "early-20th-century"],
     "Elizabeth Cannon Porter. Cities of the Sun: BoM stories."),
    ("Conflicting Orders_ Alma and Amulek in Ammonihah - Thomas R. Valletta.epub",
     "conflicting-orders-ammonihah-valletta", "Thomas R. Valletta", 30, 70, "opcional",
     "books", "en", ["book-of-mormon", "alma", "amulek", "ammonihah", "byu-study"],
     "Thomas R. Valletta. Conflicting Orders: Alma and Amulek in Ammonihah."),
    ("Doctrines of the Book of Mormon, 1991 Sperry Symposium on the Book of Mormon - Sperry Symposium.epub",
     "doctrines-of-bom-sperry-1991", "Sperry Symposium (ed.)", 40, 75, "importante",
     "books", "en", ["book-of-mormon", "sperry-symposium", "1991", "byu-academic"],
     "1991 Sperry Symposium on the Book of Mormon. Doctrines of the BoM."),
    ("Encounter in Ammonihah - Francine Bennion.epub",
     "encounter-in-ammonihah-bennion", "Francine Bennion", 25, 60, "opcional",
     "books", "en", ["book-of-mormon", "literary-exegesis", "sister-authored"],
     "Francine Bennion. Encounter in Ammonihah."),
    ("Feasting on the Word, The Literary Testimony of the Book of Mormon - Richard Dilworth Rust.epub",
     "feasting-on-the-word-rust", "Richard Dilworth Rust", 35, 80, "importante",
     "books", "en", ["book-of-mormon", "literary-criticism", "byu-academic"],
     "Richard Dilworth Rust, BYU. Feasting on the Word: Literary Testimony of BoM, 1997."),
    ("En busca de la ruta de Lehi - Lynn M. & Hope A_.epub",
     "en-busca-ruta-lehi", "Lynn M. Hilton & Hope A. Hilton", 35, 75, "importante",
     "books", "es", ["book-of-mormon", "lehi-journey", "arabian-peninsula", "byu-research"],
     "Lynn & Hope Hilton. In Search of Lehi's Trail (Spanish). Classic Arabian-peninsula research."),
    ("En busca del cerro de Cumorah - David A. Palmer.epub",
     "en-busca-cerro-cumorah-palmer", "David A. Palmer", 30, 70, "opcional",
     "books", "es", ["book-of-mormon", "cumorah", "mesoamerican-geography"],
     "David A. Palmer. In Search of Cumorah (Spanish)."),
    ("In the Footsteps of Lehi, New Evidence for Lehi's Joo Bountiful - Warren P. Aston & Michaela Knoth Aston.epub",
     "in-footsteps-of-lehi-aston", "Warren P. Aston & Michaela K. Aston", 35, 80, "importante",
     "books", "en", ["book-of-mormon", "lehi-journey", "bountiful", "arabian-peninsula"],
     "Warren & Michaela Aston. In the Footsteps of Lehi: New Evidence for Lehi's Journey to Bountiful, 1994."),
    ("Lehi in the Desert_The World of the Jaredites_TherNibley & Darrell L. Matthews & Stephen R Callister.epub",
     "lehi-in-the-desert-nibley", "Hugh Nibley", 45, 85, "importante",
     "books", "en", ["book-of-mormon", "hugh-nibley", "jaredites", "ancient-near-east", "byu-academic"],
     "Hugh Nibley (1910-2005). Lehi in the Desert / The World of the Jaredites. Foundational Nibley work."),

    # Doctrine & Covenants
    ("Answers to Your Questions About the Doctrine and Covenants - Richard O. Cowan.epub",
     "answers-questions-dc-cowan", "Richard O. Cowan", 35, 70, "opcional",
     "books", "en", ["doctrine-and-covenants", "byu-academic", "q-and-a"],
     "Richard O. Cowan, BYU. Answers to Your Questions About the D&C."),
    ("Doctrine and Covenants Chronological Reading Checklist - Nathan Richadson.epub",
     "dc-chronological-reading-checklist-richardson", "Nathan Richardson", 20, 55, "opcional",
     "reference", "en", ["doctrine-and-covenants", "study-aid", "chronology"],
     "Nathan Richardson. D&C Chronological Reading Checklist."),
    ("Doctrine and Covenants Commentary - Hyrum M Smith & Janne M Sjodahl.epub",
     "dc-commentary-smith-sjodahl", "Hyrum M. Smith & Janne M. Sjodahl", 45, 80, "importante",
     "books", "en", ["doctrine-and-covenants", "apostle-authored", "classic-commentary", "early-20th-century"],
     "Hyrum M. Smith (Q12) & Janne M. Sjodahl. D&C Commentary, 1919. Classic commentary."),
    ("Doctrine and Covenants, a Book of Answers, The 25tnnis A. Wright & Craig J Ostler & Leon R Hartshorn.epub",
     "dc-book-of-answers-sperry-25th", "Wright, Ostler & Hartshorn (eds.)", 40, 75, "importante",
     "books", "en", ["doctrine-and-covenants", "sperry-symposium-25th", "byu-academic"],
     "Dennis A. Wright, Craig J. Ostler, Leon R. Hartshorn (eds.). D&C: A Book of Answers. 25th Sperry Symposium."),

    # Biblical / Old Testament studies (LDS)
    ("Apocryphal Writings and the Latter-day Saints - C. Wilfred Griggs.epub",
     "apocryphal-writings-lds-griggs", "C. Wilfred Griggs (ed.)", 35, 80, "importante",
     "books", "en", ["apocrypha", "byu-academic", "ancient-texts"],
     "C. Wilfred Griggs (ed.), BYU. Apocryphal Writings and the LDS."),
    ("Baptism for the Dead in Early Christianity - John A. Tvednes.epub",
     "baptism-dead-early-christianity-tvedtnes", "John A. Tvedtnes", 35, 80, "importante",
     "books", "en", ["baptism-for-dead", "patristic-studies", "apologetics", "farms"],
     "John A. Tvedtnes. Baptism for the Dead in Early Christianity. FARMS research."),
    ("Between the Testaments - S Kent Brown & Richard Neitzel Holzapfel.epub",
     "between-the-testaments-brown-holzapfel", "S. Kent Brown & Richard N. Holzapfel", 40, 80, "importante",
     "books", "en", ["intertestamental", "byu-academic", "second-temple"],
     "S. Kent Brown & R. N. Holzapfel, BYU. Between the Testaments."),
    ("Bible Chronology - Ivan Panin.epub",
     "bible-chronology-panin", "Ivan Panin", 15, 50, "opcional",
     "reference", "en", ["bible-chronology", "bible-numerics", "non-lds", "early-20th-century"],
     "Ivan Panin (1855-1942). Bible Chronology. Non-LDS; known for 'Bible numerics'."),
    ("Bible_ a Bible_ - Robert J Matthews.epub",
     "a-bible-a-bible-matthews", "Robert J. Matthews", 40, 75, "importante",
     "books", "en", ["bible", "jst", "byu-academic"],
     "Robert J. Matthews (1926-2009), BYU. A Bible! A Bible! Reply to 2 Nephi 29:3."),
    ("Church of the Old Testament - John A Tvedtnes.epub",
     "church-of-the-ot-tvedtnes", "John A. Tvedtnes", 35, 75, "importante",
     "books", "en", ["old-testament", "apologetics", "farms"],
     "John A. Tvedtnes. Church of the Old Testament."),
    ("From Apostasy to Restoration - Kent P Jackson.epub",
     "from-apostasy-to-restoration-jackson", "Kent P. Jackson", 40, 80, "importante",
     "books", "en", ["apostasy", "restoration", "byu-academic"],
     "Kent P. Jackson, BYU. From Apostasy to Restoration, 1996."),
    ("Isaiah, Prophet, Seer, and Poet - Victor L Ludlow.epub",
     "isaiah-prophet-seer-poet-ludlow", "Victor L. Ludlow", 40, 85, "importante",
     "books", "en", ["isaiah", "byu-academic", "prophetic-literature"],
     "Victor L. Ludlow, BYU. Isaiah: Prophet, Seer, and Poet, 1982."),
    ("Isaías, los tiempos del cumplimiento - Iván D. Sanderson.epub",
     "isaias-tiempos-cumplimiento-sanderson", "Iván D. Sanderson", 25, 60, "opcional",
     "books", "es", ["isaiah", "prophecy", "latin-american-lds"],
     "Iván D. Sanderson. Isaías: los tiempos del cumplimiento."),
    ("Keil and Delitzsch Commentary on the Old Testament - StudyLight.org - Commentary on the Old Testament.epub",
     "keil-delitzsch-ot-commentary", "Carl F. Keil & Franz Delitzsch", 25, 80, "importante",
     "reference", "en", ["bible-commentary", "19th-century", "lutheran", "non-lds", "reference-work"],
     "Keil (1807-1888) & Delitzsch (1813-1890). K&D Commentary on OT. Classic Lutheran commentary."),
    ("Latter-day Saint Commentary on the Old Testament - Ellis T Rasmussen.epub",
     "lds-commentary-ot-rasmussen", "Ellis T. Rasmussen", 40, 80, "importante",
     "books", "en", ["old-testament", "byu-academic", "classic-lds-commentary"],
     "Ellis T. Rasmussen (1915-2009), BYU. LDS Commentary on the Old Testament, 1993."),

    # Abraham / Pearl of Great Price
    ("Abraham - Guía para el Estudio.epub",
     "abraham-guia-para-el-estudio", "Unknown (LDS study guide)", 25, 55, "opcional",
     "study-aids", "es", ["abraham", "pearl-of-great-price", "study-guide", "spanish-lds"],
     "Study guide for the Book of Abraham (Spanish)."),
    ("Abraham - The Encyclopedia of Mormonism - Clark E. Douglas.epub",
     "abraham-encyclopedia-of-mormonism", "Clark E. Douglas", 40, 80, "opcional",
     "reference", "en", ["abraham", "encyclopedia-of-mormonism", "reference-article"],
     "Clark E. Douglas. Abraham article from Encyclopedia of Mormonism, 1992."),
    ("Facsímiles del Libro de Abraham, Figura por Figura, Los - Roberto Vinett Herquiñigo.epub",
     "facsimiles-libro-abraham-vinett", "Roberto Vinett Herquiñigo", 25, 60, "opcional",
     "books", "es", ["book-of-abraham", "facsimiles", "pearl-of-great-price", "latin-american-lds"],
     "Roberto Vinett Herquiñigo. Los Facsímiles del Libro de Abraham figura por figura."),
    ("astronomía y los egipcios_ un enfoque a Abraham 3, La - Kerry Muhlestein.epub",
     "astronomia-egipcios-abraham-3-muhlestein", "Kerry Muhlestein", 35, 80, "importante",
     "books", "es", ["book-of-abraham", "egyptology", "byu-academic"],
     "Kerry Muhlestein, BYU Egyptologist. La astronomía y los egipcios: enfoque a Abraham 3."),
    ("Adán el hombre - Larry E. Dahl.epub",
     "adan-el-hombre-dahl", "Larry E. Dahl", 30, 65, "opcional",
     "books", "es", ["adam", "pearl-of-great-price", "byu-religious-studies"],
     "Larry E. Dahl, BYU. Adán el hombre."),

    # LDS women / family / pastoral (small preview, main in theme 9)
    # (moved to theme 9)

    # Doctrine — general
    ("Compendium of the Doctrines of the Gospel - Franklin D Richards & James A Little.epub",
     "compendium-doctrines-gospel-richards-little", "Franklin D. Richards & James A. Little", 45, 75, "importante",
     "books", "en", ["apostle-authored", "19th-century-lds", "doctrinal-compendium", "primary-source"],
     "Franklin D. Richards (Q12) & James A. Little. Compendium of the Doctrines of the Gospel, 1884."),
    ("Elias, An Epic of the Ages - Orson F Whitney.epub",
     "elias-epic-of-the-ages-whitney", "Orson F. Whitney", 40, 75, "importante",
     "books", "en", ["apostle-authored", "epic-poetry", "prophecy", "primary-source"],
     "Orson F. Whitney (1855-1931), Q12. Elias: An Epic of the Ages, 1904. Book-length doctrinal poem."),
    ("Gospel Standards, Selections from the Sermons and Wrs of Heber J. Grant - Heber J Grant & G Homer Durham.epub",
     "gospel-standards-heber-j-grant", "Heber J. Grant & G. Homer Durham (ed.)", 50, 80, "importante",
     "books", "en", ["prophet-authored", "sermons", "20th-century-lds", "primary-source"],
     "Pres. Heber J. Grant (1856-1945). Gospel Standards, G. Homer Durham ed., 1941."),
    ("Gospel Truth, Discourses and Writings of President George Q_ Cannon - Jerreld L Newquist & George Q Cannon.epub",
     "gospel-truth-george-q-cannon", "George Q. Cannon & Jerreld L. Newquist (ed.)", 45, 80, "importante",
     "books", "en", ["first-presidency-authored", "discourses", "19th-century-lds", "primary-source"],
     "Pres. George Q. Cannon (1827-1901), First Presidency. Gospel Truth, Newquist ed., 1957."),
    ("Gospel, God, Man, and Truth - David H. Yarn.epub",
     "gospel-god-man-truth-yarn", "David H. Yarn Jr.", 30, 70, "opcional",
     "books", "en", ["byu-philosophy", "theology", "mid-20th-century"],
     "David H. Yarn Jr., BYU philosophy. Gospel, God, Man, and Truth."),
    ("Con Que Propósito - Alvin R. Dyer.epub",
     "con-que-proposito-dyer", "Alvin R. Dyer", 40, 70, "importante",
     "books", "es", ["apostle-authored", "purpose-of-life", "spanish-lds"],
     "Elder Alvin R. Dyer (1903-1977), Q12. Con Qué Propósito (Spanish)."),
    ("Leaves from My Journal_ Third Book of the Faith-Pent of Young Latter-Day Saints - Wilford Woodruff.epub",
     "leaves-from-my-journal-woodruff", "Wilford Woodruff", 50, 80, "importante",
     "books", "en", ["prophet-authored", "journal", "faith-promoting-series", "19th-century-lds", "primary-source"],
     "Pres. Wilford Woodruff (1807-1898). Leaves from My Journal, FPS #3, 1882."),
    ("Church in War and Peace - Stephen L Richards.epub",
     "church-in-war-and-peace-richards", "Stephen L. Richards", 45, 75, "importante",
     "books", "en", ["first-presidency-authored", "mid-20th-century", "war", "primary-source"],
     "Pres. Stephen L. Richards (1879-1959), First Counselor. Church in War and Peace, 1943."),
    ("Charter of Liberty, The Inspired Origin and Prophetic Destiny of the Constitution - William O Nelson.epub",
     "charter-of-liberty-nelson", "William O. Nelson", 30, 70, "opcional",
     "books", "en", ["us-constitution", "prophetic-destiny", "political-theology"],
     "William O. Nelson. Charter of Liberty: Inspired Origin and Prophetic Destiny of the Constitution."),
    ("Latter-day Prophets and the United States Constitution - Donald .Q Cannon.epub",
     "latter-day-prophets-us-constitution-cannon", "Donald Q. Cannon (ed.)", 40, 80, "importante",
     "books", "en", ["us-constitution", "prophet-statements", "byu-academic"],
     "Donald Q. Cannon (ed.), BYU. Latter-day Prophets and the U.S. Constitution, 1991."),
    ("Christopher Columbus, A Latter-day Saint Perspective - Arnold K Garr.epub",
     "christopher-columbus-lds-perspective-garr", "Arnold K. Garr", 35, 75, "opcional",
     "books", "en", ["columbus", "1-nephi-13", "byu-academic"],
     "Arnold K. Garr, BYU. Christopher Columbus: An LDS Perspective, 1992."),
    ("C. S. Lewis, The Man and his Message_ An LDS Perspective - Andrew C. Skinner & Robert L. Millet.epub",
     "cs-lewis-lds-perspective-skinner-millet", "Andrew C. Skinner & Robert L. Millet (eds.)", 35, 75, "opcional",
     "books", "en", ["cs-lewis", "comparative-theology", "byu-academic"],
     "Andrew C. Skinner & Robert L. Millet (eds.), BYU. C. S. Lewis: An LDS Perspective, 1999."),
    ("Grand Design, America from Columbus to Zion - E Douglas Clark.epub",
     "grand-design-america-columbus-zion-clark", "E. Douglas Clark", 30, 70, "opcional",
     "books", "en", ["american-providential-history", "restoration-preparation"],
     "E. Douglas Clark. Grand Design: America from Columbus to Zion, 1992."),
    ("Cuarto Milenio, El - W. Cleon Skousen.epub",
     "cuarto-milenio-skousen", "W. Cleon Skousen", 30, 65, "opcional",
     "books", "es", ["millennium", "eschatology", "20th-century-lds"],
     "W. Cleon Skousen (1913-2006). El Cuarto Milenio (Spanish)."),

    # Jewish / Ancient context
    ("Glory of God Is Intelligence, Four Lectures on the Role of Intellect in Judaism - Jacob Neusner.epub",
     "glory-of-god-intelligence-neusner", "Jacob Neusner", 30, 85, "importante",
     "reference", "en", ["judaic-studies", "intellect", "byu-guest-lectures", "non-lds"],
     "Jacob Neusner (1932-2016), Bard College. Glory of God Is Intelligence, BYU Richard L. Evans lectures."),
    ("Inside a Sumerian Temple_ The Ekishnugal at Ur - E. Jan Wilson.epub",
     "inside-sumerian-temple-wilson", "E. Jan Wilson", 30, 80, "opcional",
     "reference", "en", ["ancient-near-east", "sumer", "temple-studies"],
     "E. Jan Wilson. Inside a Sumerian Temple: The Ekishnugal at Ur."),
    ("Escritos de Josefo y su relación con el Nuevo Testamento, Los - Greg Herrick.epub",
     "escritos-josefo-nt-herrick", "Greg Herrick", 25, 70, "opcional",
     "reference", "es", ["josephus", "nt-context", "biblical-studies"],
     "Greg Herrick. Los escritos de Josefo y su relación con el NT (Spanish)."),
]

# Archive dups first
for fn in ARCHIVE_DUPS:
    src = READY / fn
    if src.exists():
        src.rename(DONE / fn)
        print(f"  archived dup: {fn[:70]}")

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

print(f"\nTheme 8 (LDS doctrine): {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

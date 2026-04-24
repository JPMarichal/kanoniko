#!/usr/bin/env python
"""Theme 10+11 final: bible-study resources, discourses, misc LDS (combined).

Individually curated. Excludes JPM (23), Pelé (5), JPM-family (1).
Archives: technical, fiction, broken, unclear.
"""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

# Archive (non-corpus / broken / literary / technical / unclear)
ARCHIVE = [
    "Basic Teradata Query Reference - Teradata Information Engineering.epub",  # technical manual
    "Index of the Project Gutenberg Works of Alfred Henry Lewis - Alfred Henry Lewis.epub",  # bibliographic index
    "guerrero de Zarahemla, El - Chris Heimerdinger.epub",  # fiction (LDS novel)
    "John Stevens' Courtship_ A Story of the Echo Canyon War - Susa Young Gates.epub",  # historical novel
    "Chronicle of the Cid - Robert Southey.epub",  # medieval literature
    "Avoiding the 23 pitfalls to recovery - Jeff Robinson.epub",  # broken (empty)
    "In Perfect Balance - Spencer J. Condie.epub",  # broken (empty)
    "Epistle to the Philippians - Polycarp.epub",  # broken (empty) - Polycarp
    "Cristianismo y nada mas - C. S. Lewis.epub",  # broken (empty)
    "40 Principios SP.qxd - lared.epub",  # slide-deck fragment, unclear
    "DIÁLOGO PARA LA EXPOSICIÓN - edgar eduardo miranda estrada.epub",  # unclear
    "LDS Church News - Leaders on social media sites_ Proebook, Google_ pages - Leaders on social media sites.epub",  # news clip
]

WORKS = [
    # === DISCOURSES (apostolic talks, singles) ===
    ("Be of Good Cheer - Marvin J. Ashton.epub",  # double-check not already done
     None, None, None, None, None, None, None, None, None),  # skip-marker - already in theme 9
    ("Cómo encontrar el camino de regreso - Richard G. Scott.epub",
     "como-encontrar-el-camino-de-regreso-scott", "Richard G. Scott", 50, 70, "importante",
     "discourses", "es", ["apostle-authored", "repentance", "spanish-talk"],
     "Elder Richard G. Scott (1928-2015), Q12. Cómo encontrar el camino de regreso (conference talk)."),
    ("Dones de paz - Henry B. Eyring.epub",
     "dones-de-paz-eyring", "Henry B. Eyring", 55, 75, "importante",
     "discourses", "es", ["first-presidency-authored", "peace", "spanish-talk"],
     "Pres. Henry B. Eyring, First Counselor. Dones de paz (conference talk)."),
    ("Este es el tiempo de Mexico - Gerrit W. Gong.epub",
     "este-es-el-tiempo-de-mexico-gong", "Gerrit W. Gong", 50, 70, "importante",
     "discourses", "es", ["apostle-authored", "mexico", "spanish-talk"],
     "Elder Gerrit W. Gong, Q12. Este es el tiempo de México."),
    ("For unto whomsoever much is given, of him shall bted much, of him they will ask th - Neal A Maxwel.epub",
     "whomsoever-much-is-given-maxwell", "Neal A. Maxwell", 50, 75, "importante",
     "discourses", "en", ["apostle-authored", "stewardship", "talk"],
     "Elder Neal A. Maxwell (1926-2004), Q12. For Unto Whomsoever Much Is Given."),
    ("Generoso, El - Dieter F. Uchtdorf.epub",
     "el-generoso-uchtdorf", "Dieter F. Uchtdorf", 55, 75, "importante",
     "discourses", "es", ["apostle-authored", "generosity", "spanish-talk"],
     "Elder Dieter F. Uchtdorf, Q12 (former FP Counselor). El Generoso."),
    ("Joseph B. Wirthlin_ Una selección de discursos - Joseph B. Wirthlin.epub",
     "joseph-b-wirthlin-seleccion-discursos", "Joseph B. Wirthlin", 50, 75, "importante",
     "discourses", "es", ["apostle-authored", "discourses-compilation", "spanish"],
     "Elder Joseph B. Wirthlin (1917-2008), Q12. Una selección de discursos."),
    ("condescendencia de Dios y del hombre, La - D. Todd Christofferson.epub",
     "condescendencia-de-dios-christofferson", "D. Todd Christofferson", 55, 75, "importante",
     "discourses", "es", ["apostle-authored", "condescension-of-god", "spanish-talk"],
     "Elder D. Todd Christofferson, Q12. La condescendencia de Dios y del hombre."),
    ("don del Espíritu Santo, El - Douglas D. Holmes.epub",
     "don-del-espiritu-santo-holmes", "Douglas D. Holmes", 40, 65, "opcional",
     "discourses", "es", ["seventy-authored", "holy-ghost", "spanish-talk"],
     "Elder Douglas D. Holmes, Seventy. El don del Espíritu Santo."),
    ("día de la defensa, El - A. Melvin McDonald.epub",
     "dia-de-la-defensa-mcdonald", "A. Melvin McDonald", 25, 55, "opcional",
     "discourses", "es", ["defense", "legal-perspective", "spanish-lds"],
     "A. Melvin McDonald. El día de la defensa."),
    ("Carta -14OCT2022 Clase de quinto domingo - David J. Davis.epub",
     "carta-14oct2022-davis", "David J. Davis", 20, 50, "opcional",
     "discourses", "es", ["fifth-sunday", "local-leader", "letter"],
     "David J. Davis. Carta 14-oct-2022 para clase de quinto domingo."),

    # === BIBLE-STUDY REFERENCES ===
    ("Diccionario Biblico Arqueologico - Charles Pfeiffer.epub",
     "diccionario-biblico-arqueologico-pfeiffer", "Charles F. Pfeiffer", 25, 80, "importante",
     "reference", "es", ["bible-archaeology", "reference-work", "non-lds", "evangelical"],
     "Charles F. Pfeiffer. Diccionario Bíblico Arqueológico. Non-LDS evangelical reference."),
    ("Diccionario Biblico Mundo Hispano - J.D. Douglas, Merrill C. Tenney.epub",
     "diccionario-biblico-mundo-hispano", "J. D. Douglas & Merrill C. Tenney", 25, 80, "importante",
     "reference", "es", ["bible-dictionary", "reference-work", "non-lds", "evangelical"],
     "J. D. Douglas & Merrill C. Tenney. Diccionario Bíblico Mundo Hispano."),
    ("Diccionario Strong de palabras originales del Antiguo y Nuevo Testamento - James Strong.epub",
     "diccionario-strong", "James Strong", 30, 85, "importante",
     "reference", "es", ["strong-concordance", "hebrew-greek", "reference-work", "19th-century"],
     "James Strong (1822-1894). Strong's Hebrew & Greek Dictionary (Spanish)."),
    ("Dónde se encuentra en la Biblia - José L. Rizo Martínez.epub",
     "donde-se-encuentra-en-la-biblia-rizo", "José L. Rizo Martínez", 20, 60, "opcional",
     "reference", "es", ["bible-topical-index", "spanish-evangelical", "non-lds"],
     "José L. Rizo Martínez. Dónde se encuentra en la Biblia."),
    ("How We Got the Bible - Lenet Hadley Read.epub",
     "how-we-got-the-bible-read", "Lenet Hadley Read", 35, 70, "importante",
     "books", "en", ["bible-transmission", "canon-history", "lds-perspective"],
     "Lenet Hadley Read. How We Got the Bible (LDS perspective)."),
    ("jornada semanal_ la Biblia de Lutero, La - Carlos Martínez García & Leopoldo Cervantes Ortiz.epub",
     "jornada-semanal-biblia-lutero", "Carlos Martínez García & Leopoldo Cervantes Ortiz", 20, 65, "opcional",
     "reference", "es", ["luther-bible", "reformation-history", "protestant", "non-lds"],
     "Martínez García & Cervantes Ortiz. La jornada semanal: la Biblia de Lutero."),
    ("GospeLink - The House of Israel_ from Everlasting to Everlasting - Richard D. Dagger.epub",
     "gospelink-house-of-israel-dagger", "Richard D. Dagger", 30, 65, "opcional",
     "reference", "en", ["house-of-israel", "scattering-and-gathering", "gospelink"],
     "Richard D. Dagger (GospeLink). The House of Israel: From Everlasting to Everlasting."),

    # === INTER-RELIGIOUS / CONTEXT ===
    ("Corán, El - Mahoma.epub",
     "coran-el", "Muhammad (attrib.) / Qur'an", 20, 85, "importante",
     "reference", "es", ["quran", "islam", "primary-source", "interreligious", "non-lds"],
     "El Corán (Qur'an, Spanish translation). Islamic scripture, primary source."),
    ("Enciclopedia de la mitología - J. C. Escobedo.epub",
     "enciclopedia-mitologia-escobedo", "J. C. Escobedo", 20, 60, "opcional",
     "reference", "es", ["mythology", "encyclopedia", "non-lds", "reference-work"],
     "J. C. Escobedo. Enciclopedia de la mitología."),
    ("Historia de los judíos en España - Adolfo de Castro.epub",
     "historia-judios-espana-castro", "Adolfo de Castro", 25, 70, "opcional",
     "history", "es", ["jewish-history", "spanish-jews", "sephardic", "19th-century"],
     "Adolfo de Castro (1823-1898). Historia de los judíos en España, 1847."),
    ("Es Dios un Matematico - Mario Livio.epub",
     "es-dios-matematico-livio", "Mario Livio", 20, 80, "opcional",
     "reference", "es", ["mathematics", "science-religion", "non-lds", "popular-science"],
     "Mario Livio. Is God a Mathematician? (Spanish). Astrophysicist on math and cosmos."),
    ("Divine Comedy - Dante Alighieri.epub",
     "divine-comedy-dante", "Dante Alighieri", 30, 85, "importante",
     "reference", "en", ["medieval", "13th-14th-century", "christian-allegory", "primary-source"],
     "Dante Alighieri (1265-1321). Divina Commedia. Medieval Christian theological allegory."),

    # === LDS MISC ===
    ("Believing People, Literature of the Latter-day Saints - Neal A Lambert & Richard E Cracr.epub",
     "believing-people-literature-lds-lambert", "Neal A. Lambert & Richard H. Cracroft (eds.)", 35, 75, "importante",
     "books", "en", ["lds-literature", "anthology", "byu-academic"],
     "Neal A. Lambert & Richard H. Cracroft (eds.), BYU. A Believing People: Literature of the LDS, 1974."),
    ("Best-Loved Stories of the LDS People, Vol_ 1 - Jack M. Lyon & Linda Ririe Gundry & Jay A. Parry.epub",
     "best-loved-stories-lds-vol-1", "Jack M. Lyon, Linda R. Gundry, Jay A. Parry (eds.)", 30, 60, "opcional",
     "books", "en", ["lds-stories", "anthology", "deseret-book"],
     "Lyon, Gundry, Parry (eds.), Deseret Book. Best-Loved Stories of the LDS People, Vol. 1."),
    ("Best-Loved Stories of the LDS People, Vol_ 2 - Jay A Parry & Jack M Lyon & Linda Ririe Gundry.epub",
     "best-loved-stories-lds-vol-2", "Parry, Lyon, Gundry (eds.)", 30, 60, "opcional",
     "books", "en", ["lds-stories", "anthology", "deseret-book"],
     "Parry, Lyon, Gundry (eds.), Deseret Book. Best-Loved Stories of the LDS People, Vol. 2."),
    ("Blessed by the Hymns - LaVonne VanOrden.epub",
     "blessed-by-the-hymns-vanorden", "LaVonne VanOrden", 25, 55, "opcional",
     "books", "en", ["hymns", "women-authored"],
     "LaVonne VanOrden. Blessed by the Hymns."),
    ("Child of the Sea; and Life Among the Mormons, A - Elizabeth Whitney Williams.epub",
     "child-of-the-sea-whitney-williams", "Elizabeth Whitney Williams", 25, 60, "opcional",
     "history", "en", ["19th-century-lds", "women-authored", "memoir", "primary-source"],
     "Elizabeth Whitney Williams. A Child of the Sea and Life Among the Mormons, 1905."),
    ("Collection of Sacred Hymns, A - Emma Smith.epub",
     "collection-of-sacred-hymns-emma-smith", "Emma Smith (compiler)", 55, 85, "importante",
     "books", "en", ["hymnal", "19th-century-lds", "emma-smith", "primary-source", "revelation-d&c-25"],
     "Emma Smith (compiler, 1804-1879). A Collection of Sacred Hymns, 1835. First LDS hymnal (D&C 25 fulfillment)."),
    ("Creation - Frank B Salisbury.epub",
     "creation-salisbury", "Frank B. Salisbury", 30, 75, "importante",
     "books", "en", ["creation", "science-religion", "byu-botanist"],
     "Frank B. Salisbury (1926-2015), BYU botanist. Creation (LDS science-religion)."),
    ("Great Stories from Mormon History - Tom Hughes & Dean Hughes.epub",
     "great-stories-from-mormon-history-hughes", "Tom Hughes & Dean Hughes", 30, 60, "opcional",
     "history", "en", ["lds-history", "anthology", "stories"],
     "Tom & Dean Hughes. Great Stories from Mormon History."),
    ("Iglesia restaurada, La - William Edwin Berret.epub",
     "iglesia-restaurada-berret", "William E. Berret", 35, 75, "importante",
     "history", "es", ["church-history", "classic-textbook", "mid-20th-century"],
     "William E. Berret. The Restored Church (Spanish: La Iglesia restaurada). Classic LDS history."),
    ("Israel_ Do You Know - LeGrand Richards.epub",
     "israel-do-you-know-richards", "LeGrand Richards", 50, 75, "importante",
     "books", "en", ["apostle-authored", "israel", "gathering", "20th-century-lds"],
     "Elder LeGrand Richards (1886-1983), Q12. Israel! Do You Know?"),
    ("Jeremiah's crisis of faith (Jeremiah 15_20) - Kent S. Brown.epub",
     "jeremiahs-crisis-of-faith-brown", "S. Kent Brown", 35, 75, "opcional",
     "books", "en", ["jeremiah", "faith-crisis", "byu-academic", "essay"],
     "S. Kent Brown, BYU. Jeremiah's crisis of faith (Jeremiah 15:20) essay."),
    ("Jesus Was Married - Ogden Kraut.epub",
     "jesus-was-married-kraut", "Ogden Kraut", 15, 45, "opcional",
     "books", "en", ["controversial", "speculative", "fundamentalist-lds", "non-mainstream"],
     "Ogden Kraut (1927-2002), fundamentalist LDS. Jesus Was Married. Speculative, non-mainstream."),
    ("Journal of Travels From St. Josephs to Oregon _ Wia Full Description of Its Gold Mines. - Riley Root.epub",
     "journal-st-joseph-to-oregon-root", "Riley Root", 20, 65, "opcional",
     "history", "en", ["19th-century-travel", "overland-trail", "primary-source"],
     "Riley Root. Journal of Travels from St. Joseph's to Oregon, 1850."),
    ("camino hacia un matrimonio cristiano, El - John Thompson.epub",
     "camino-hacia-matrimonio-cristiano-thompson", "John Thompson", 15, 55, "opcional",
     "reference", "es", ["marriage", "evangelical", "non-lds"],
     "John Thompson. El camino hacia un matrimonio cristiano (evangelical)."),
    ("En los pasos del Cordero - G. Steinberger.epub",
     "en-los-pasos-del-cordero-steinberger", "G. Steinberger", 15, 55, "opcional",
     "reference", "es", ["life-of-christ", "devotional", "non-lds"],
     "G. Steinberger. En los pasos del Cordero."),
    ("juicio del palo de José, El - Jack H. West.epub",
     "juicio-del-palo-de-jose-west", "Jack H. West", 30, 65, "opcional",
     "books", "es", ["stick-of-joseph", "book-of-mormon", "apologetics"],
     "Jack H. West. El juicio del palo de José (Stick of Joseph apologetics)."),
    ("lamanita mestizo, El - Arturo de Hoyos.epub",
     "lamanita-mestizo-hoyos", "Arturo de Hoyos", 30, 65, "opcional",
     "books", "es", ["lamanites", "mesoamerica", "latin-american-lds"],
     "Arturo de Hoyos. El lamanita mestizo."),
    ("Indian Why Stories - Frank Linderman.epub",
     "indian-why-stories-linderman", "Frank B. Linderman", 20, 65, "opcional",
     "reference", "en", ["native-american", "folklore", "early-20th-century", "primary-source"],
     "Frank B. Linderman (1869-1938). Indian Why Stories, 1915. Blackfoot/Chippewa folklore."),
    ("2018.estacatacubaya - María Fernanda Lira Arzaluz.epub",
     "estacatacubaya-2018-lira", "María Fernanda Lira Arzaluz", 15, 50, "opcional",
     "books", "es", ["mexican-lds", "local-history", "contemporary"],
     "María Fernanda Lira Arzaluz. Estaca Tacubaya 2018 (Mexican local LDS history)."),
    ("consejo latinoamericano de iglesias - La distribución de la tierra.epub",
     "consejo-latinoamericano-distribucion-tierra", "Consejo Latinoamericano de Iglesias", 15, 55, "opcional",
     "reference", "es", ["ecumenical", "social-justice", "land-distribution", "non-lds"],
     "CLAI. La distribución de la tierra (ecumenical social-justice document)."),

    # === SECULAR SELF-HELP ===
    ("7 hábitos de la gente altamente efectiva, Los - Stephen R. Covey.epub",
     "7-habitos-gente-efectiva-covey", "Stephen R. Covey", 25, 75, "opcional",
     "reference", "es", ["self-help", "lds-author", "bestseller", "leadership"],
     "Stephen R. Covey (1932-2012), LDS author. 7 Hábitos de la gente altamente efectiva, 1989."),
    ("How to Succeed with People - Stephen R Covey.epub",
     "how-to-succeed-with-people-covey", "Stephen R. Covey", 25, 65, "opcional",
     "reference", "en", ["self-help", "lds-author", "interpersonal"],
     "Stephen R. Covey. How to Succeed with People, 1971."),
]

# Archive first
for fn in ARCHIVE:
    src = READY / fn
    if src.exists():
        src.rename(DONE / fn)
        print(f"  archived: {fn[:70]}")

ok = 0
broken = []
for entry in WORKS:
    fn = entry[0]
    if entry[1] is None:  # skip marker
        continue
    slug, author, auth, rigor, imp, cat, lang, tags, note = entry[1:]
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

print(f"\nTheme 10+11 final: {ok} OK, {len(broken)} broken, {len(ARCHIVE)} archived")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

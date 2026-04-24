"""Sub-batch 3: bulk processing ~67 works across 34 LDS authors (2+ works each)."""
import json, re, shutil, subprocess, sys, unicodedata, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
FASE0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0"


def slugify(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:75]


# Intra-batch dups to archive
dups = [
    'Feasting upon the Word - Sandra Packard & Dennis Packard.epub',  # variant spelling dup
    'Howard W_ Hunter - Eleanor Knowles.epub',  # ES has same content via "Biografía" variant
]

# 1844 Holzapfel was already extracted to corpus during earlier smoke-test sequence.
# Check if already exists and skip or re-extract.
existing_1844 = (ROOT / "corpus" / "es" / "history" / "1844-la-ultima-asignacion-del-profeta-a-los-doce").exists() or \
                any((ROOT / "corpus").rglob("1844*"))

# (fname, slug, lang, cat, author, title, note, tags, authority, rigor, importance)
works = [
    # Robinson (4)
    ('Believing Christ - Stephen E Robinson.epub', 'believing-christ-robinson', 'en', 'books',
     'Stephen E. Robinson', 'Believing Christ',
     "Robinson (BYU religion dean) classic on the Atonement — believing IN Christ vs believing Christ. Pre-1990.",
     ['atonement', 'christology', 'robinson-se', 'byu-scholarship'], 30, 70, 'importante'),
    ('Following Christ, The Parable of the Divers and More Good News - Stephen E Robin.epub',
     'following-christ-divers-robinson', 'en', 'books', 'Stephen E. Robinson', 'Following Christ',
     "Robinson sequel to Believing Christ.",
     ['atonement', 'discipleship', 'robinson-se', 'byu-scholarship'], 30, 70, 'importante'),
    ('Are Mormons Christians - Stephen E. Robinson.epub', 'are-mormons-christians',
     'en', 'books', 'Stephen E. Robinson', 'Are Mormons Christians?',
     "Robinson 1991 apologetic addressing evangelical criticisms.",
     ['apologetics', 'evangelical-dialogue', 'robinson-se', 'byu-scholarship'], 30, 70, 'importante'),
    ('Creámosle a Cristo - Stephen E. Robinson.epub', 'creamosle-a-cristo-robinson-es',
     'es', 'books', 'Stephen E. Robinson', 'Creámosle a Cristo',
     "Traducción ES de Believing Christ. Par de traducción.",
     ['atonement', 'christology', 'robinson-se', 'byu-scholarship', 'spanish-translation'], 30, 70, 'importante'),
    # Ricks (2)
    ('By Study and Also by Faith, vol_ 1 - Stephen D Ricks & John M Lundquist.epub',
     'by-study-and-also-by-faith-vol-1', 'en', 'books', 'Stephen D. Ricks & John M. Lundquist',
     'By Study and Also by Faith, vol. 1', "FARMS festschrift for Hugh Nibley vol 1.",
     ['festschrift', 'nibley', 'farms', 'byu-scholarship', 'ricks-sd'], 30, 75, 'importante'),
    ('By Study and Also by Faith, vol_ 2 - Stephen D Ricks & John M Lundquist.epub',
     'by-study-and-also-by-faith-vol-2', 'en', 'books', 'Stephen D. Ricks & John M. Lundquist',
     'By Study and Also by Faith, vol. 2', "FARMS festschrift vol 2.",
     ['festschrift', 'nibley', 'farms', 'byu-scholarship', 'ricks-sd'], 30, 75, 'importante'),
    # Lund (2)
    ('Coming of the Lord - Gerald N Lund.epub', 'coming-of-the-lord-lund', 'en', 'books',
     'Gerald N. Lund', 'The Coming of the Lord', "Lund (Seventy 2002-2008) on Second Coming/millennial eschatology.",
     ['second-coming', 'millennialism', 'lund', 'seventy'], 40, 70, 'importante'),
    ('Jesus Christ, Key to the Plan of Salvation - Gerald N Lund.epub',
     'jesus-christ-key-plan-salvation-lund', 'en', 'books', 'Gerald N. Lund',
     'Jesus Christ: Key to the Plan of Salvation', "Lund christology.",
     ['christology', 'plan-of-salvation', 'lund', 'seventy'], 40, 70, 'importante'),
    # Gene R. Cook (2)
    ('Cómo criar una familia celestial - Gene R. Cook.epub', 'como-criar-familia-celestial-cook',
     'es', 'books', 'Gene R. Cook', 'Cómo criar una familia celestial',
     "Cook (Seventy 1975-2008) sobre familia. ES.",
     ['family', 'cook-gr', 'seventy', 'spanish-translation'], 40, 65, 'importante'),
    ('Cómo obtener respuestas a nuestras oraciones - Gene R. Cook.epub',
     'como-obtener-respuestas-oraciones-cook', 'es', 'books', 'Gene R. Cook',
     'Cómo obtener respuestas a nuestras oraciones', "Cook sobre oración. ES.",
     ['prayer', 'cook-gr', 'seventy', 'spanish-translation'], 40, 65, 'importante'),
    # Faust (2)
    ('Finding Light in a Dark World - James E Faust.epub', 'finding-light-in-a-dark-world',
     'en', 'books', 'James E. Faust', 'Finding Light in a Dark World',
     "Faust (Second Counselor in FP 1995-2007). 1995 Deseret Book.",
     ['faust', 'second-counselor', 'discipleship', 'deseret-book'], 45, 70, 'importante'),
    ('In the Strength of the Lord, The Life and Teachings of James E_ Faust - James E Faust.epub',
     'in-the-strength-of-the-lord-faust', 'en', 'books', 'James E. Faust',
     'In the Strength of the Lord', "Faust life+teachings compilation.",
     ['faust', 'compilation', 'second-counselor'], 45, 70, 'importante'),
    # Pearson (2)
    ('Book of Mormon, Key to Conversion - Glenn L Pearson.epub',
     'book-of-mormon-key-to-conversion-pearson', 'en', 'books', 'Glenn L. Pearson',
     'The Book of Mormon: Key to Conversion', "Pearson (BYU religion) on BoM conversion.",
     ['book-of-mormon', 'conversion', 'pearson-gl', 'byu-scholarship'], 30, 65, 'importante'),
    ('Building Faith with the Book of Mormon - Glenn L Pearson & Reid E Bankhead.epub',
     'building-faith-with-the-bom-pearson', 'en', 'books', 'Glenn L. Pearson & Reid E. Bankhead',
     'Building Faith with the Book of Mormon', "Pearson & Bankhead, BYU BoM study.",
     ['book-of-mormon', 'pearson-gl', 'bankhead', 'byu-scholarship'], 30, 65, 'importante'),
    # Anderson (2)
    ('Investigating the Book of Mormon Witnesses - Richard Lloyd Anderson.epub',
     'investigating-book-of-mormon-witnesses', 'en', 'books', 'Richard Lloyd Anderson',
     'Investigating the Book of Mormon Witnesses',
     "Anderson (BYU historian). Classic scholarly apologetic for the BoM witnesses.",
     ['book-of-mormon', 'witnesses', 'three-witnesses', 'eight-witnesses', 'anderson-rl', 'byu-scholarship'],
     30, 80, 'importante'),
    ('Joseph Smith_s New England Heritage, Influences of Golomon Mack and Asael Smith - Richard Lloyd Anderson.epub',
     'joseph-smiths-new-england-heritage', 'en', 'biographies', 'Richard Lloyd Anderson',
     "Joseph Smith's New England Heritage", "Anderson on Solomon Mack/Asael Smith influences on JS.",
     ['joseph-smith', 'new-england', 'solomon-mack', 'asael-smith', 'anderson-rl', 'genealogy'],
     30, 80, 'importante'),
    # Holzapfel (2) — 1844 already in corpus
    ('Every Stone a Sermon - Richard Neitzel Holzapfel.epub', 'every-stone-a-sermon-holzapfel',
     'en', 'books', 'Richard Neitzel Holzapfel', 'Every Stone a Sermon',
     "Holzapfel (BYU religion, historian) — possibly on temples. Deseret Book.",
     ['temple', 'symbolism', 'holzapfel', 'byu-scholarship'], 30, 70, 'importante'),
    # Ballard (2)
    ('Counseling with Our Councils_ Learning to Minister Tin the Church and in the Fam.epub',
     'counseling-with-our-councils-ballard', 'en', 'books', 'M. Russell Ballard',
     'Counseling with Our Councils',
     "Ballard (Q12 1985-present) on using councils in Church and family governance.",
     ['councils', 'leadership', 'ballard', 'q12'], 40, 70, 'importante'),
    ('divino sistema de consejos, El - M. Russell Ballard.epub', 'el-divino-sistema-de-consejos',
     'es', 'books', 'M. Russell Ballard', 'El divino sistema de consejos',
     "Traducción ES de Counseling with Our Councils.",
     ['councils', 'leadership', 'ballard', 'q12', 'spanish-translation'], 40, 70, 'importante'),
    # Hugh B Brown (3 — 2 under "Hugh B Brown" + 1 under "Hugh B. Brown")
    ('Continuing the Quest - Hugh B Brown.epub', 'continuing-the-quest-brown', 'en', 'books',
     'Hugh B. Brown', 'Continuing the Quest',
     "Hugh B. Brown (FP Counselor 1961-1970). Collection of essays.",
     ['brown-hb', 'first-presidency', 'essays'], 45, 70, 'importante'),
    ('Eternal Quest - Hugh B Brown.epub', 'eternal-quest-brown', 'en', 'books',
     'Hugh B. Brown', 'Eternal Quest', "Brown addresses/writings.",
     ['brown-hb', 'first-presidency', 'essays'], 45, 70, 'importante'),
    ('Abundant Life - Hugh B. Brown.epub', 'abundant-life-brown', 'en', 'books',
     'Hugh B. Brown', 'The Abundant Life', "Brown classic on abundant Christian life.",
     ['brown-hb', 'first-presidency', 'abundant-life'], 45, 70, 'importante'),
    # Parry Jay A (2)
    ('Best-Loved Humor of the LDS People - Jay A. Parry & Jack M. Lyon & Linda Ririe Gundry.epub',
     'best-loved-humor-of-the-lds-people', 'en', 'books', 'Jay A. Parry & Jack M. Lyon & Linda Ririe Gundry',
     'Best-Loved Humor of the LDS People', "Parry/Lyon/Gundry compilation of LDS humor.",
     ['humor', 'compilation', 'parry-j', 'deseret-book'], 20, 50, 'complementario'),
    ('Best-Loved Poems of the LDS People - Jay A. Parry & Linda Ririe Gundry & Jack M. Lyon.epub',
     'best-loved-poems-of-the-lds-people', 'en', 'books', 'Jay A. Parry & Linda Ririe Gundry & Jack M. Lyon',
     'Best-Loved Poems of the LDS People', "Parry/Gundry/Lyon LDS poetry compilation.",
     ['poetry', 'compilation', 'parry-j'], 20, 55, 'complementario'),
    # Merrill (2)
    ('Elijah, Yesterday, Today, and Tomorrow - Byron R. Merrill.epub',
     'elijah-yesterday-today-tomorrow-merrill', 'en', 'books', 'Byron R. Merrill',
     'Elijah: Yesterday, Today, and Tomorrow', "Merrill (BYU religion) on Elijah.",
     ['elijah', 'prophets', 'merrill', 'byu-scholarship'], 30, 70, 'importante'),
    ('Heavens Are Open, The 1992 Sperry Symposium on the D and Covenants and Church Hi.epub',
     'heavens-are-open-sperry-1992', 'en', 'books', 'Byron R. Merrill',
     'The Heavens Are Open: 1992 Sperry Symposium',
     "1992 Sperry Symposium volume (BYU religion). Edited by Merrill.",
     ['sperry-symposium', 'd-and-c', 'church-history', 'merrill', 'byu-scholarship'],
     30, 75, 'importante'),
    # Asay (2)
    ('Family Pecan Trees, Planting a Legacy of Faith at Home - Carlos E. Asay.epub',
     'family-pecan-trees-asay', 'en', 'books', 'Carlos E. Asay',
     'Family Pecan Trees', "Asay (Seventy) on family.",
     ['family', 'asay', 'seventy'], 40, 65, 'importante'),
    ("In the Lord's Service - Carlos E. Asay.epub", 'in-the-lords-service-asay', 'en', 'books',
     'Carlos E. Asay', "In the Lord's Service", "Asay on service.",
     ['service', 'asay', 'seventy'], 40, 65, 'importante'),
    # Bennion (2)
    ('Introduction to the Gospel - Lowell L Bennion.epub', 'introduction-to-the-gospel-bennion',
     'en', 'books', 'Lowell L. Bennion', 'Introduction to the Gospel',
     "Bennion (CES director, LDS intellectual) intro to gospel.",
     ['gospel', 'ces', 'bennion', 'introduction'], 30, 65, 'importante'),
    ('Legacies of Jesus - Lowell L Bennion.epub', 'legacies-of-jesus-bennion', 'en', 'books',
     'Lowell L. Bennion', 'Legacies of Jesus', "Bennion on christology/ethics.",
     ['christology', 'ethics', 'bennion'], 30, 65, 'importante'),
    # Reynolds (2)
    ('Book of Mormon Authorship Revisited, The Evidence for Ancient Origins - Noel B Reynolds.epub',
     'bom-authorship-revisited-reynolds', 'en', 'books', 'Noel B. Reynolds',
     'Book of Mormon Authorship Revisited',
     "Reynolds (BYU, FARMS director) on BoM ancient origins apologetics. 1997.",
     ['book-of-mormon', 'authorship', 'apologetics', 'reynolds-nb', 'farms'], 30, 80, 'importante'),
    ('Book of Mormon Authorship, New Light on Ancient Origins - Noel B Reynolds.epub',
     'bom-authorship-reynolds', 'en', 'books', 'Noel B. Reynolds',
     'Book of Mormon Authorship: New Light on Ancient Origins',
     "Reynolds earlier (1982) BYU Symposium on BoM authorship.",
     ['book-of-mormon', 'authorship', 'apologetics', 'reynolds-nb', 'farms'], 30, 80, 'importante'),
    # Crowther (2)
    ('Amonestaciones proféticas inspiradas - Duane S. Crowther.epub',
     'amonestaciones-profeticas-crowther-es', 'es', 'books', 'Duane S. Crowther',
     'Amonestaciones proféticas inspiradas',
     "Crowther (LDS popular author) on prophetic warnings. ES.",
     ['prophecy', 'warnings', 'crowther', 'spanish-translation'], 25, 60, 'complementario'),
    ('José Smith_ Un verdadero profeta de Dios - Duane S. Crowther.epub',
     'jose-smith-verdadero-profeta-crowther-es', 'es', 'books', 'Duane S. Crowther',
     'José Smith: Un verdadero profeta de Dios',
     "Crowther's apologetic on Joseph Smith. ES.",
     ['joseph-smith', 'apologetics', 'crowther', 'spanish-translation'], 25, 60, 'complementario'),
    # Carol Cornwall Madsen (2)
    ('In Their Own Words, Women and the Story of Nauvoo - Carol Cornwall Madsen.epub',
     'in-their-own-words-nauvoo-women-madsen', 'en', 'history', 'Carol Cornwall Madsen',
     'In Their Own Words: Women and the Story of Nauvoo',
     "Madsen (BYU historian) on Nauvoo women primary sources.",
     ['nauvoo', 'women-history', 'primary-source', 'madsen-cc', 'byu-scholarship'],
     30, 80, 'importante'),
    ('Journey to Zion - Carol Cornwall Madsen.epub', 'journey-to-zion-madsen', 'en', 'history',
     'Carol Cornwall Madsen', 'Journey to Zion', "Madsen on pioneer migration.",
     ['pioneers', 'migration', 'madsen-cc', 'byu-scholarship'], 30, 75, 'importante'),
    # Susan Arrington Madsen (2)
    ('Growing Up in Zion, True Stories of Young Pioneers Building the Kingdom - Susan Arrington Madsen.epub',
     'growing-up-in-zion-madsen-sa', 'en', 'history', 'Susan Arrington Madsen',
     'Growing Up in Zion', "Madsen on young pioneers building Utah.",
     ['pioneers', 'youth-history', 'madsen-sa', 'arrington-family'], 30, 70, 'importante'),
    ('I Walked to Zion, True Stories of Young Pioneers on the Mormon Trail - Susan Arrington Madsen.epub',
     'i-walked-to-zion-madsen-sa', 'en', 'history', 'Susan Arrington Madsen',
     'I Walked to Zion', "Madsen on pioneer children on Mormon Trail.",
     ['pioneers', 'mormon-trail', 'youth-history', 'madsen-sa'], 30, 70, 'importante'),
    # Susan Easton Black (2)
    ('Doctrines for Exaltation, The 1989 Sperry Symposium on the Doctrine and Covenant.epub',
     'doctrines-for-exaltation-sperry-1989', 'en', 'books', 'Susan Easton Black',
     'Doctrines for Exaltation: 1989 Sperry Symposium',
     "1989 Sperry Symposium on D&C. Edited Black.",
     ['sperry-symposium', 'd-and-c', 'exaltation', 'black-se', 'byu-scholarship'], 30, 75, 'importante'),
    ('Expressions of Faith, Testimonies of Latter-day Saint Scholars - Susan Easton Black.epub',
     'expressions-of-faith-black', 'en', 'books', 'Susan Easton Black',
     'Expressions of Faith: Testimonies of Latter-day Saint Scholars',
     "Black (BYU religion) compilation of LDS scholar testimonies.",
     ['testimonies', 'lds-scholars', 'black-se', 'byu-scholarship'], 30, 70, 'importante'),
    # Eleanor Knowles (1 after dup archive — 1 Howard W Hunter variant)
    ('Howard W. Hunter_ Biografía de un profeta - Eleanor Knowles.epub',
     'howard-w-hunter-biografia-knowles-es', 'es', 'biographies', 'Eleanor Knowles',
     'Howard W. Hunter: Biografía de un profeta',
     "Knowles's biography of President Howard W. Hunter (14th President 1994-1995). ES translation.",
     ['biography', 'howard-w-hunter', 'church-president', 'knowles', 'spanish-translation'], 25, 70, 'importante'),
    # Janet Peterson (2)
    ('Elect Ladies - Janet Peterson & LaRene Gaunt.epub', 'elect-ladies-peterson',
     'en', 'biographies', 'Janet Peterson & LaRene Gaunt', 'Elect Ladies',
     "Peterson/Gaunt biographies of Relief Society General Presidents.",
     ['relief-society', 'women-leaders', 'biography', 'peterson', 'gaunt'], 30, 70, 'importante'),
    ('Keepers of the Flame - Janet Peterson & LaRene Gaunt.epub', 'keepers-of-the-flame-peterson',
     'en', 'biographies', 'Janet Peterson & LaRene Gaunt', 'Keepers of the Flame',
     "Peterson/Gaunt biographies of Primary General Presidents.",
     ['primary', 'women-leaders', 'biography', 'peterson', 'gaunt'], 30, 70, 'importante'),
    # Featherstone (2)
    ('Commitment - Vaughn J Featherstone.epub', 'commitment-featherstone', 'en', 'books',
     'Vaughn J. Featherstone', 'Commitment', "Featherstone (Seventy 1976-2006) on commitment.",
     ['commitment', 'discipleship', 'featherstone', 'seventy'], 40, 65, 'importante'),
    ('Incomparable Christ, Our Master and Model - Vaughn J Featherstone.epub',
     'incomparable-christ-featherstone', 'en', 'books', 'Vaughn J. Featherstone',
     'The Incomparable Christ', "Featherstone christology.",
     ['christology', 'featherstone', 'seventy'], 40, 65, 'importante'),
    # Olson (2)
    ('Counseling, A Guide to Helping Others, vol_ 1 - Terrance D Olson & R Lanier Britsch.epub',
     'counseling-a-guide-to-helping-others-vol-1', 'en', 'books',
     'Terrance D. Olson & R. Lanier Britsch', 'Counseling: A Guide to Helping Others vol 1',
     "BYU pastoral counseling handbook vol 1.",
     ['counseling', 'pastoral-care', 'olson', 'britsch', 'byu-scholarship'], 30, 65, 'importante'),
    ('Counseling, A Guide to Helping Others, vol_ 2 - Terrance D Olson & R Lanier Britsch.epub',
     'counseling-a-guide-to-helping-others-vol-2', 'en', 'books',
     'Terrance D. Olson & R. Lanier Britsch', 'Counseling vol 2', "vol 2.",
     ['counseling', 'pastoral-care', 'olson', 'britsch', 'byu-scholarship'], 30, 65, 'importante'),
    # Packard (1 after dup)
    ('Feasting upon the Word - Sandra Packard & Denisse Packard.epub',
     'feasting-upon-the-word-packard', 'en', 'books', 'Sandra Packard & Dennis Packard',
     'Feasting upon the Word',
     "Packard on scripture study methods. (Coauthor name variant 'Denisse'/'Dennis' — archived second variant as dup.)",
     ['scripture-study', 'packard', 'byu-scholarship'], 30, 65, 'importante'),
    # Scoresby (2)
    ('Bringing Up Moral Children - A. Lynn Scoresby.epub', 'bringing-up-moral-children-scoresby',
     'en', 'books', 'A. Lynn Scoresby', 'Bringing Up Moral Children',
     "Scoresby (BYU family studies) on moral child-rearing.",
     ['parenting', 'family', 'moral-development', 'scoresby'], 25, 60, 'complementario'),
    ('Foundations for a Happier Marriage - A. Lynn Scoresby.epub',
     'foundations-for-a-happier-marriage-scoresby', 'en', 'books', 'A. Lynn Scoresby',
     'Foundations for a Happier Marriage', "Scoresby on marriage.",
     ['marriage', 'family', 'scoresby'], 25, 60, 'complementario'),
    # Eugene England (2)
    ('Best of Lowell L_ Bennion, Selected Writings 1928-1988 - Eugene England & Lowell L Bennion.epub',
     'best-of-lowell-bennion-england', 'en', 'books', 'Eugene England & Lowell L. Bennion',
     'The Best of Lowell L. Bennion: Selected Writings 1928-1988',
     "Eugene England's edited selection of Bennion's writings.",
     ['bennion', 'compilation', 'england', 'ces', 'lds-intellectual'], 30, 70, 'importante'),
    ('Converted to Christ through the Book of Mormon - Eugene England.epub',
     'converted-to-christ-through-bom-england', 'en', 'books', 'Eugene England',
     'Converted to Christ Through the Book of Mormon',
     "England on BoM conversion narratives.",
     ['book-of-mormon', 'conversion', 'england', 'lds-intellectual'], 30, 70, 'importante'),
    # George Q. Cannon (2)
    ('Book of Mormon Stories. No. 1. _ Adapted to the Cciations, and for Home Reading - George Q. Cannon.epub',
     'book-of-mormon-stories-cannon', 'en', 'books', 'George Q. Cannon',
     'Book of Mormon Stories, No. 1',
     "Cannon (FP Counselor 1873-1901) BoM adaptation for youth/family reading.",
     ['book-of-mormon', 'cannon', 'youth', 'first-presidency', '19th-century-lds'], 45, 65, 'importante'),
    ('Latter-Day Prophet_ History of Joseph Smith Written for Young People, The - George Q. Cannon.epub',
     'latter-day-prophet-cannon', 'en', 'biographies', 'George Q. Cannon',
     'The Latter-Day Prophet: History of Joseph Smith Written for Young People',
     "Cannon biography of Joseph Smith for youth readers.",
     ['joseph-smith', 'biography', 'youth', 'cannon', 'first-presidency'], 45, 70, 'importante'),
    # Gordon B. Hinckley (2 more)
    ('Be Thou an Example - Gordon B Hinckley.epub', 'be-thou-an-example-hinckley',
     'en', 'books', 'Gordon B. Hinckley', 'Be Thou an Example',
     "Hinckley (15th Pres 1995-2008). Pre-presidency discourses.",
     ['hinckley', 'church-president', 'discipleship'], 50, 70, 'importante'),
    ('Faith, The Essence of True Religion - Gordon B Hinckley.epub',
     'faith-essence-of-true-religion-hinckley', 'en', 'books', 'Gordon B. Hinckley',
     'Faith, the Essence of True Religion', "Hinckley on faith.",
     ['faith', 'hinckley', 'church-president'], 50, 70, 'importante'),
    # Orson F. Whitney (2)
    ('Elias_ An Epic of the Ages - Orson F. Whitney.epub', 'elias-epic-of-the-ages-whitney',
     'en', 'books', 'Orson F. Whitney', 'Elias: An Epic of the Ages',
     "Whitney (Q12 1906-1931) — his epic poem on LDS theology/history.",
     ['poetry', 'epic', 'whitney', 'q12', 'theological-verse'], 45, 70, 'importante'),
    ('Gospel Themes_ A Treatise on Salient Features of _Mormonism_ - Orson F. Whitney.epub',
     'gospel-themes-whitney', 'en', 'books', 'Orson F. Whitney', 'Gospel Themes',
     "Whitney's doctrinal treatise. corpus already has gospel-themes — verify.",
     ['doctrine', 'whitney', 'q12'], 45, 70, 'importante'),
    # Donald W. Parry (2)
    ('Guide to Scriptural Symbols - Donald W. Parry.epub', 'guide-to-scriptural-symbols-parry',
     'en', 'reference', 'Donald W. Parry', 'Guide to Scriptural Symbols',
     "Parry (BYU, Dead Sea Scrolls) on biblical symbolism.",
     ['symbolism', 'biblical', 'parry-dw', 'byu-scholarship'], 30, 70, 'importante'),
    ('LDS Perspectives on the Dead Sea Scrolls - Donald W. Parry.epub',
     'lds-perspectives-dead-sea-scrolls-parry', 'en', 'reference', 'Donald W. Parry',
     'LDS Perspectives on the Dead Sea Scrolls',
     "Parry on DSS from LDS scholarly perspective.",
     ['dead-sea-scrolls', 'parry-dw', 'byu-scholarship'], 30, 75, 'importante'),
    # Oscar W. McConkie (2 — father of Bruce R.)
    ('Aaronic Priesthood - Oscar W. McConkie.epub', 'aaronic-priesthood-mcconkie-ow',
     'en', 'books', 'Oscar W. McConkie', 'The Aaronic Priesthood',
     "Oscar W. McConkie (father of Bruce R., Assistant to Q12 1946-1950s era) on the Aaronic Priesthood.",
     ['aaronic-priesthood', 'mcconkie-ow', 'priesthood'], 40, 65, 'importante'),
    ('Angels - Oscar W. McConkie.epub', 'angels-mcconkie-ow',
     'en', 'books', 'Oscar W. McConkie', 'Angels',
     "Oscar W. McConkie's doctrinal study of angels.",
     ['angels', 'mcconkie-ow', 'doctrine'], 40, 65, 'importante'),
    # Skanchy (2) — 19th c missionary autobiography
    ('A Brief Autobiographical Sketch of the Missionary La of a Valiant Soldier for Ch.epub',
     'skanchy-missionary-autobiography', 'en', 'biographies', 'Anthon L. Skanchy',
     'A Brief Autobiographical Sketch of the Missionary Labors of a Valiant Soldier for Christ',
     "Skanchy's autobiographical sketch — 19th-c Scandinavian mission primary source.",
     ['biography', 'missionary', 'skanchy', 'scandinavian', 'primary-source', '19th-century-lds'],
     25, 75, 'importante'),
    ('Anthon L. Skanchy - Anthon L. Skanchy.epub', 'anthon-l-skanchy-autobiography',
     'en', 'biographies', 'Anthon L. Skanchy', 'Anthon L. Skanchy (autobiography)',
     "Skanchy autobiography.",
     ['biography', 'skanchy', 'scandinavian', 'primary-source'], 25, 75, 'importante'),
    # Emily Wilson (3) — evangelical Bible study
    ('Book of John Study - 12 weeks - Emily Wilson.epub', 'book-of-john-study-12-weeks-wilson',
     'en', 'reference', 'Emily Wilson', 'Book of John Study (12 weeks)',
     "Wilson evangelical Bible study guide on John's Gospel, 12-week version. Non-LDS.",
     ['bible-study', 'john-gospel', 'evangelical', 'wilson'], 15, 50, 'complementario'),
    ('Book of John Study - 21 days - Emily Wilson.epub', 'book-of-john-study-21-days-wilson',
     'en', 'reference', 'Emily Wilson', 'Book of John Study (21 days)',
     "Wilson evangelical Bible study 21-day version.",
     ['bible-study', 'john-gospel', 'evangelical', 'wilson'], 15, 50, 'complementario'),
    ('Investigative Bible Study Leaders Guide - Emily Wilson.epub',
     'investigative-bible-study-leaders-guide-wilson', 'en', 'reference', 'Emily Wilson',
     'Investigative Bible Study Leaders Guide',
     "Wilson evangelical study leader guide.",
     ['bible-study', 'leaders-guide', 'evangelical', 'wilson'], 15, 50, 'complementario'),
    # Mary E. Stovall (2)
    ('As Women of Faith, Talks Selected from the BYU WomenConferences - Mary E Stovall.epub',
     'as-women-of-faith-stovall', 'en', 'books', 'Mary E. Stovall',
     'As Women of Faith: Talks from BYU Women\'s Conferences',
     "Stovall edited compilation of BYU Women's Conf talks.",
     ['women-conference', 'compilation', 'byu-scholarship', 'stovall'], 30, 65, 'importante'),
    ('Heritage of Faith, Talks Selected from the BYU WomenConferences - Mary E Stovall.epub',
     'heritage-of-faith-stovall', 'en', 'books', 'Mary E. Stovall',
     'Heritage of Faith', "Stovall second BYU Women's Conf volume.",
     ['women-conference', 'compilation', 'byu-scholarship', 'stovall'], 30, 65, 'importante'),
]

print(f"\n=== archiving intra-dups ({len(dups)}) ===")
for n in dups:
    src = READY / n
    if src.exists():
        shutil.move(str(src), str(DONE / n))
        print(f"  archived: {n[:60]}")

print(f"\n=== extracting {len(works)} works ===")
results = []
broken = []
for row in works:
    fname, slug, lang, cat, author, title, note, tags, auth, rigor, imp = row
    src = READY / fname
    if not src.exists():
        broken.append((fname, "MISSING source"))
        continue
    meta = {
        "authority": auth, "rigor": rigor, "importance": imp,
        "official": False, "current": True,
        "context": "scholarly" if cat == "reference" else "book-private",
        "audience": "adult", "tags": tags,
        "category": cat, "author": author, "source_url": None, "note": note,
    }
    (FASE0 / f"{slug}.fase0.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    (FASE0 / f"{slug}.md").write_text(
        f"# Fase 0 --- {title} ({author})\n\n> Fecha: 2026-04-23. Sub-batch 3.\n\n## Que es\n\n{note}\n\n## Evaluacion\n\nauthority={auth}; rigor={rigor}; importance={imp}; category={cat}; tags: {', '.join(tags)}.\n",
        encoding="utf-8")
    r = subprocess.run(["python","scripts/epub_extract.py", str(src),
                        "--lang", lang, "--category", cat, "--slug", slug],
                       capture_output=True, text=True, timeout=300)
    if r.returncode == 0:
        results.append((str(src), slug, lang, cat))
    else:
        broken.append((fname, (r.stderr or '')[-200:]))

print(f"\nExtract: {len(results)} OK, {len(broken)} broken")
for n, e in broken[:10]:
    print(f"  BROKEN {n[:50]}: {e[:100]}")

for src_str, slug, lang, cat in results:
    r = subprocess.run(['python','scripts/epub_extract.py','--promote', f'epub/_preview/{lang}/{cat}/{slug}'],
                       capture_output=True, text=True, timeout=60)

for src_str, _, _, _ in results:
    p = Path(src_str)
    if p.exists():
        shutil.move(str(p), str(DONE / p.name))
for fname, _ in broken:
    src = READY / fname
    if src.exists():
        shutil.move(str(src), str(DONE / fname))
# Also archive 1844 Holzapfel (it's in corpus already from smoke test, archived earlier — check)
h = READY / '1844, la última asignación del profeta a los doce - Richard Neitzel Holzapfel.epub'
if h.exists():
    shutil.move(str(h), str(DONE / h.name))
    print(f"  archived 1844 Holzapfel (already in corpus)")

print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

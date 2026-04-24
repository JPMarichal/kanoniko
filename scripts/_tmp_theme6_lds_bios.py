#!/usr/bin/env python
"""Theme 6: LDS biographies (25 works + 1 intra-dup archive, individually curated)."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

# Archive the shorter Lorenzo Snow variant (keep the longer one)
ARCHIVE_DUPS = [
    "Biography and Family Record of Lorenzo Snow - Eliza R Snow.epub",  # shorter variant
]

WORKS = [
    ("Autobiography of Parley Parker Pratt _ One of theife, Ministry, and Travels, The - Parley P. Pratt.epub",
     "autobiography-parley-p-pratt", "Parley P. Pratt", 45, 75, "importante",
     "biographies", "en", ["apostle-authored", "autobiography", "19th-century-lds", "early-apostle", "primary-source"],
     "Parley P. Pratt (1807-1857), Q12. Autobiography, published posthumously 1874."),
    ("Biografía Elder Montoya Oficial - Marina Triana.epub",
     "biografia-elder-montoya", "Marina Triana", 25, 55, "opcional",
     "biographies", "es", ["latin-american", "general-authority", "modern", "biography"],
     "Marina Triana. Official biography of Elder Montoya, Latin American GA."),
    ("Biography and Family Record of Lorenzo Snow _ One  Jesus Christ of Latter-day Saints - Eliza R. Snow.epub",
     "biography-lorenzo-snow-eliza", "Eliza R. Snow", 40, 70, "importante",
     "biographies", "en", ["19th-century-lds", "prophet-biography", "sister-authored", "primary-source"],
     "Eliza R. Snow (1804-1887), sister of Lorenzo. Biography of her brother, 1884."),
    ("Book of John Whitmer - John Whitmer.epub",
     "book-of-john-whitmer", "John Whitmer", 40, 75, "importante",
     "biographies", "en", ["19th-century-lds", "early-church", "church-historian", "primary-source", "journal"],
     "John Whitmer (1802-1878), first Church Historian. Historical record, 1831-1847."),
    ("Brigham Young at Home - Clarissa Young Spencer.epub",
     "brigham-young-at-home", "Clarissa Young Spencer", 35, 65, "opcional",
     "biographies", "en", ["19th-century-lds", "prophet-biography", "daughter-authored", "family-memoir"],
     "Clarissa Young Spencer, daughter of Brigham Young. Intimate family memoir."),
    ("Brigham Young, The Man and His Work - Preston Nibley.epub",
     "brigham-young-nibley", "Preston Nibley", 35, 70, "importante",
     "biographies", "en", ["19th-century-lds", "prophet-biography", "early-20th-century-lds-scholar"],
     "Preston Nibley (1884-1966), Assistant Church Historian. Biography of Brigham Young."),
    ("Camilla, a Biography of Camilla Eyring Kimball - Caroline Eyring Miner & Edward L Kimball.epub",
     "camilla-eyring-kimball", "Caroline Eyring Miner & Edward L. Kimball", 35, 70, "opcional",
     "biographies", "en", ["20th-century-lds", "prophet-spouse", "family-authored"],
     "Biography of Camilla Eyring Kimball (1894-1987), wife of Pres. Spencer W. Kimball."),
    ("Father of the Prophet, Stories and Insights from the Life of Joseph Smith, Sr_ - Mark L McConkie.epub",
     "father-of-the-prophet-joseph-smith-sr", "Mark L. McConkie", 40, 70, "importante",
     "biographies", "en", ["19th-century-lds", "patriarch", "joseph-smith-family"],
     "Mark L. McConkie. Biography of Joseph Smith Sr. (1771-1840), Presiding Patriarch."),
    ("Glimpses into the Life and Heart of Marjorie Pay Hinckley - Virginia H Pearce.epub",
     "glimpses-marjorie-pay-hinckley", "Virginia H. Pearce", 40, 65, "importante",
     "biographies", "en", ["20th-century-lds", "prophet-spouse", "daughter-authored"],
     "Virginia H. Pearce, daughter. Glimpses of Marjorie Pay Hinckley (1911-2004)."),
    ("Go Forward with Faith, The Biography of Gordon B_ Hinckley - Sheri Dew.epub",
     "go-forward-with-faith-hinckley-dew", "Sheri Dew", 45, 80, "importante",
     "biographies", "en", ["20th-century-lds", "prophet-biography", "authorized"],
     "Sheri Dew. Authorized biography of Pres. Gordon B. Hinckley (1910-2008), pub. 1996."),
    ("Harold B_ Lee, Prophet and Seer - Brent L. Goates.epub",
     "harold-b-lee-goates", "Brent L. Goates", 40, 75, "importante",
     "biographies", "en", ["20th-century-lds", "prophet-biography", "son-in-law-authored"],
     "Brent L. Goates, son-in-law. Biography of Pres. Harold B. Lee (1899-1973)."),
    ("Heber J_ Grant, Highlights in the Life of a Great Leader - Bryant S. Hinckley.epub",
     "heber-j-grant-highlights-hinckley", "Bryant S. Hinckley", 35, 70, "opcional",
     "biographies", "en", ["20th-century-lds", "prophet-biography", "contemporary-author"],
     "Bryant S. Hinckley (father of Gordon B.). Biography of Pres. Heber J. Grant (1856-1945)."),
    ("Henry Ballard, The Story of a Courageous Pioneer, 1832-1908 - Douglas O. Crookston.epub",
     "henry-ballard-crookston", "Douglas O. Crookston", 30, 65, "opcional",
     "biographies", "en", ["19th-century-lds", "pioneer", "ballard-family"],
     "Douglas O. Crookston. Biography of Henry Ballard (1832-1908), pioneer, grandfather of Pres. M. Russell Ballard."),
    ("Here Is Brigham _ _ _ Brigham Young, The Years to 1844 - S Dilworth Young.epub",
     "here-is-brigham-young-1844", "S. Dilworth Young", 35, 70, "opcional",
     "biographies", "en", ["19th-century-lds", "prophet-biography", "pre-exodus"],
     "S. Dilworth Young, Seventy. Brigham Young: the years to 1844."),
    ("Highlights in the Life of President David O_ McKay - Jeanette McKay Morrell.epub",
     "highlights-david-o-mckay", "Jeanette McKay Morrell", 35, 65, "opcional",
     "biographies", "en", ["20th-century-lds", "prophet-biography", "family-authored"],
     "Jeanette McKay Morrell, daughter. Highlights of Pres. David O. McKay (1873-1970)."),
    ("History of Joseph Smith by His Mother - Lucy Mack Smith & Preston Nibley.epub",
     "history-joseph-smith-his-mother", "Lucy Mack Smith", 45, 75, "importante",
     "biographies", "en", ["19th-century-lds", "prophet-biography", "mother-authored", "primary-source"],
     "Lucy Mack Smith (1775-1856), Preston Nibley ed. Foundational biographical record, first pub. 1853."),
    ("Hyrum Smith, Patriarch - Pearson H Corbett.epub",
     "hyrum-smith-patriarch-corbett", "Pearson H. Corbett", 40, 75, "importante",
     "biographies", "en", ["19th-century-lds", "prophet-brother", "patriarch", "martyr"],
     "Pearson H. Corbett. Biography of Hyrum Smith (1800-1844)."),
    ("J_ Golden Kimball, The Story of a Unique Personality - Claude Richards.epub",
     "j-golden-kimball-richards", "Claude Richards", 30, 65, "opcional",
     "biographies", "en", ["20th-century-lds", "seventy", "folk-hero"],
     "Claude Richards. Biography of J. Golden Kimball (1853-1938), beloved Seventy."),
    ("Jacob Hamblin_ A Narrative of His Personal Experigement of Young Latter-day Saints - Jacob Hamblin.epub",
     "jacob-hamblin-narrative", "Jacob Hamblin", 40, 70, "importante",
     "biographies", "en", ["19th-century-lds", "autobiography", "missionary-to-natives", "pioneer", "primary-source"],
     "Jacob Hamblin (1819-1886), 'Apostle to the Lamanites'. Personal narrative, 1881."),
    ("John Lyon, The Life of a Pioneer Poet - T Edgar Lyon.epub",
     "john-lyon-pioneer-poet", "T. Edgar Lyon", 30, 65, "opcional",
     "biographies", "en", ["19th-century-lds", "poet", "scottish-mission", "family-authored"],
     "T. Edgar Lyon, descendant. Biography of John Lyon (1803-1889), Scottish pioneer poet."),
    ("Joseph Smith, an American Prophet - John Henry Evans.epub",
     "joseph-smith-american-prophet-evans", "John Henry Evans", 35, 75, "importante",
     "biographies", "en", ["19th-century-lds", "prophet-biography", "early-20th-century-scholarship"],
     "John Henry Evans (1872-1947). Joseph Smith: An American Prophet, 1933."),
    ("Joseph Smith_s Kirtland, Eyewitness Accounts - Karl Ricks Anderson.epub",
     "joseph-smiths-kirtland-anderson", "Karl Ricks Anderson", 35, 75, "importante",
     "biographies", "en", ["19th-century-lds", "kirtland-era", "eyewitness-accounts", "primary-source-anthology"],
     "Karl Ricks Anderson. Eyewitness accounts of Joseph Smith's Kirtland ministry."),
    ("Journal of Heber C. Kimball - Heber C Kimball.epub",
     "journal-heber-c-kimball", "Heber C. Kimball", 45, 75, "importante",
     "biographies", "en", ["apostle-authored", "journal", "19th-century-lds", "british-mission", "primary-source"],
     "Heber C. Kimball (1801-1868), First Counselor to Brigham Young. Journal."),
    ("José Smith, el profeta y vidente - Kent P. Jackson & Richard Neitzel Holzapfel.epub",
     "jose-smith-profeta-y-vidente", "Kent P. Jackson & Richard Neitzel Holzapfel", 35, 75, "importante",
     "biographies", "es", ["20th-century-lds-scholarship", "prophet-biography", "byu-academic"],
     "Kent P. Jackson & R. N. Holzapfel. Joseph Smith: Prophet and Seer (Spanish)."),
    ("LeGrand Richards, Beloved Apostle - Lucile C Tate.epub",
     "legrand-richards-beloved-apostle-tate", "Lucile C. Tate", 35, 70, "opcional",
     "biographies", "en", ["apostle-biography", "20th-century-lds"],
     "Lucile C. Tate. Biography of Elder LeGrand Richards (1886-1983)."),
]

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

print(f"\nTheme 6 (LDS bios): {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

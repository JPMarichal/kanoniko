#!/usr/bin/env python
"""Theme 7: LDS history (30 works, individually curated). Excludes Pelé (final)."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

WORKS = [
    ("American Religions and the Rise of Mormonism - Milton V. Backman.epub",
     "american-religions-rise-mormonism-backman", "Milton V. Backman Jr.", 40, 80, "importante",
     "history", "en", ["byu-academic", "religious-history", "restoration-context", "19th-century-america"],
     "Milton V. Backman Jr., BYU. American Religions and the Rise of Mormonism, 1965/1970."),
    ("Are We of Israel_ - George Reynolds.epub",
     "are-we-of-israel-reynolds", "George Reynolds", 35, 65, "opcional",
     "history", "en", ["19th-century-lds", "israelite-lineage", "first-council-seventy", "primary-source"],
     "George Reynolds (1842-1909), First Council of Seventy. Are We of Israel?, 1883."),
    ("Being a summary statement of the investigation madethe _Mormon_ question in England - Arthur L. Beeley.epub",
     "mormon-question-england-beeley", "Arthur L. Beeley", 25, 60, "opcional",
     "history", "en", ["lds-in-britain", "early-20th-century", "apologetics"],
     "Arthur L. Beeley. Summary of investigation of the 'Mormon question' in England."),
    ("Call of Zion, The Story of the First Welsh Mormon Migration - Ronald D Dennis.epub",
     "call-of-zion-welsh-migration-dennis", "Ronald D. Dennis", 35, 75, "importante",
     "history", "en", ["welsh-mission", "gathering", "byu-academic", "19th-century-lds"],
     "Ronald D. Dennis, BYU. Call of Zion: First Welsh Mormon Migration, 1987."),
    ("Century of Mormonism in Great Britain - Richard L Evans.epub",
     "century-of-mormonism-britain-evans", "Richard L. Evans", 40, 70, "importante",
     "history", "en", ["apostle-authored", "british-mission", "centennial-history"],
     "Richard L. Evans (1906-1971), Q12. Century of Mormonism in Great Britain, 1937."),
    ("City of the Mormons; or, Three Days at Nauvoo, in 1842, The - Henry Caswall.epub",
     "city-of-mormons-caswall", "Henry Caswall", 20, 55, "opcional",
     "history", "en", ["anglican-observer", "nauvoo", "1842", "external-account", "primary-source"],
     "Henry Caswall, Anglican cleric. Three Days at Nauvoo, 1842. Hostile external eyewitness."),
    ("City of the Saints, and Across the Rocky Mountains to California, The - Sir Richard Francis Burton.epub",
     "city-of-the-saints-burton", "Richard F. Burton", 25, 70, "importante",
     "history", "en", ["external-observer", "utah", "19th-century", "primary-source"],
     "Sir Richard F. Burton (1821-1890). City of the Saints, 1861. British explorer's Utah account."),
    ("Collection of Facts Relative to Sidney Rigdon - Jedediah M Grant.epub",
     "facts-sidney-rigdon-grant", "Jedediah M. Grant", 40, 70, "opcional",
     "history", "en", ["apostle-authored", "rigdon-controversy", "succession", "primary-source"],
     "Jedediah M. Grant (1816-1856), Q12 later First Presidency. Collection of Facts re Sidney Rigdon, 1844."),
    ("Colonia Juarez_ An Intimate Account of a Mormon Village - Nelle Hatch.epub",
     "colonia-juarez-hatch", "Nelle Spilsbury Hatch", 30, 65, "opcional",
     "history", "es", ["mexican-colonies", "chihuahua", "20th-century-lds", "family-memoir"],
     "Nelle Spilsbury Hatch. Colonia Juárez: Intimate Account, 1954."),
    ("Concise History of the Mormon Battalion - Daniel Tyler.epub",
     "concise-history-mormon-battalion-tyler", "Daniel Tyler", 40, 75, "importante",
     "history", "en", ["mormon-battalion", "mexican-war", "19th-century", "primary-source", "veteran-authored"],
     "Daniel Tyler, Battalion veteran. Concise History of the Mormon Battalion, 1881."),
    ("Conditions in Utah _ Speech of Hon. Thomas Kearns of, in the Senate of the United States - Thomas Kearns.epub",
     "conditions-in-utah-kearns", "Thomas Kearns", 15, 55, "opcional",
     "history", "en", ["senate-speech", "early-20th-century", "external-criticism", "primary-source"],
     "Sen. Thomas Kearns (UT). 1905 Senate speech attacking LDS leadership. External critique."),
    ("Dawning of a Brighter Day, The - Derin Head Rodriguez.epub",
     "dawning-of-a-brighter-day-rodriguez", "Derin Head Rodriguez", 30, 60, "opcional",
     "history", "en", ["modern-lds", "women-history", "20th-century"],
     "Derin Head Rodriguez. Dawning of a Brighter Day."),
    ("Dawning of a Brighter Day, The Church in Black Africa - Alexander B Morrison.epub",
     "dawning-church-black-africa-morrison", "Alexander B. Morrison", 45, 75, "importante",
     "history", "en", ["seventy-authored", "africa", "modern-lds", "missionary-work"],
     "Elder Alexander B. Morrison, Seventy. Dawning of a Brighter Day: the Church in Black Africa, 1990."),
    ("Death of Orson Spencer's Wife - John R. Young.epub",
     "death-orson-spencer-wife-young", "John R. Young", 25, 55, "opcional",
     "history", "en", ["19th-century-lds", "missouri-persecution", "martyrdom-account", "primary-source"],
     "John R. Young. Account of the death of Orson Spencer's wife during Missouri persecutions."),
    ("Englishwoman in Utah_ The Story of a Life's Experience in Mormonism, An - Mrs. T. B. H. Stenhouse.epub",
     "englishwoman-in-utah-stenhouse", "Mrs. T. B. H. Stenhouse", 20, 60, "opcional",
     "history", "en", ["ex-lds", "19th-century", "polygamy-critique", "primary-source"],
     "Fanny Stenhouse (1829-1904). Englishwoman in Utah, 1880. Ex-LDS exposé, polygamy critique."),
    ("Eventful Narratives _ The Thirteenth Book of- Robert Aveson & Oliver Boardman Huntington.epub",
     "eventful-narratives-fps-13", "Robert Aveson & O. B. Huntington", 30, 60, "opcional",
     "history", "en", ["faith-promoting-series", "19th-century-lds", "anthology"],
     "Faith-Promoting Series #13. Eventful Narratives."),
    ("Expulsion of the Mormons - John P Greene.epub",
     "expulsion-of-the-mormons-greene", "John P. Greene", 40, 70, "importante",
     "history", "en", ["19th-century-lds", "missouri-expulsion", "primary-source"],
     "John P. Greene (1793-1844). Facts Relative to the Expulsion of the Mormons from Missouri, 1839."),
    ("Far West Record, Minutes of the Church of Jesus ChriSaints, 1830-1844 - Lyndon W Cook & Donald .Q Cannon.epub",
     "far-west-record-cook-cannon", "Lyndon W. Cook & Donald Q. Cannon (eds.)", 45, 85, "importante",
     "history", "en", ["byu-academic", "early-church-minutes", "primary-source", "1830-1844"],
     "Cook & Cannon eds. Far West Record: Minutes 1830-1844, 1983. Critical primary source."),
    ("Foot-prints of Travel; Or, Journeyings in Many Lands - Maturin M. Ballou.epub",
     "foot-prints-of-travel-ballou", "Maturin M. Ballou", 15, 50, "opcional",
     "history", "en", ["19th-century-travel", "external-observer", "primary-source"],
     "Maturin M. Ballou (1820-1895). Foot-prints of Travel, 1889. Includes Mormon observations."),
    ("Forty Years Among the Indians _ A true yet thrillingor's experiences among the natives - Daniel W. Jones.epub",
     "forty-years-among-indians-jones", "Daniel W. Jones", 40, 75, "importante",
     "history", "en", ["19th-century-lds", "native-american-mission", "pioneer", "primary-source"],
     "Daniel W. Jones (1830-1915). Forty Years Among the Indians, 1890. Autobiographical primary source."),
    ("From Kirtland to Salt Lake City - James A Little.epub",
     "from-kirtland-to-salt-lake-little", "James A. Little", 30, 65, "opcional",
     "history", "en", ["19th-century-lds", "church-history-narrative"],
     "James A. Little. From Kirtland to Salt Lake City."),
    ("From the East, The History of the Latter-day Saints in Asia, 1851-1996 - R Lanier Britsch.epub",
     "from-the-east-britsch", "R. Lanier Britsch", 40, 80, "importante",
     "history", "en", ["byu-academic", "asia", "modern-lds", "missionary-history"],
     "R. Lanier Britsch, BYU. From the East: LDS in Asia 1851-1996, 1998."),
    ("Gems of Reminiscence, Faith-Promoting Series, no_ 17 - George C Lambert & George Q Cannon.epub",
     "gems-of-reminiscence-fps-17", "George C. Lambert", 30, 55, "opcional",
     "history", "en", ["faith-promoting-series", "19th-century-lds", "anthology"],
     "Faith-Promoting Series #17. Gems of Reminiscence."),
    ("General Smith's Views of the Powers and Policy of the Government of the United States - Jr. Joseph Smith.epub",
     "general-smith-views-powers-policy", "Joseph Smith Jr.", 55, 85, "importante",
     "history", "en", ["prophet-authored", "political", "1844-presidential-campaign", "primary-source"],
     "Joseph Smith Jr. General Smith's Views, 1844. Presidential campaign platform."),
    ("Great Salt Lake Trail, The - Henry Inman & Buffalo Bill.epub",
     "great-salt-lake-trail-inman", "Henry Inman & William F. Cody", 20, 60, "opcional",
     "history", "en", ["western-history", "19th-century", "mormon-trail", "external-observer"],
     "Henry Inman & Buffalo Bill Cody. Great Salt Lake Trail, 1898."),
    ("Historical Atlas of Mormonism - Richard H Jackson & Donald .Q Cannon & S Kent Brown.epub",
     "historical-atlas-mormonism", "S. Kent Brown, D. Q. Cannon & R. H. Jackson", 40, 85, "importante",
     "history", "en", ["byu-academic", "reference-work", "atlas", "modern-lds-scholarship"],
     "Brown, Cannon & Jackson, BYU. Historical Atlas of Mormonism, 1994."),
    ("History of Southern Utah and Its National Parks (Revised), A - Angus M. Woodbury.epub",
     "history-southern-utah-woodbury", "Angus M. Woodbury", 25, 70, "opcional",
     "history", "en", ["regional-history", "southern-utah", "20th-century"],
     "Angus M. Woodbury. History of Southern Utah and Its National Parks."),
    ("History of the Late Persecution Inflicted by the State of Missouri upon the Mormons - Parley P Pratt.epub",
     "history-persecution-missouri-pratt", "Parley P. Pratt", 45, 75, "importante",
     "history", "en", ["apostle-authored", "missouri-persecution", "primary-source"],
     "Parley P. Pratt. History of the Late Persecution, 1839. Written from Missouri jail."),
    ("In Old Nauvoo, Everyday Life in the City of Joseph - George W Givens.epub",
     "in-old-nauvoo-givens", "George W. Givens", 35, 70, "importante",
     "history", "en", ["nauvoo", "social-history", "19th-century-lds"],
     "George W. Givens. In Old Nauvoo: Everyday Life in the City of Joseph, 1990."),
    ("Italian Mission - Lorenzo Snow.epub",
     "italian-mission-snow", "Lorenzo Snow", 45, 75, "importante",
     "history", "en", ["apostle-authored", "italian-mission", "19th-century-lds", "primary-source"],
     "Lorenzo Snow (1814-1901). Italian Mission, 1851. Pre-apostolic missionary report."),
    ("Joseph Smith Chronology - J Christopher Conkling.epub",
     "joseph-smith-chronology-conkling", "J. Christopher Conkling", 30, 75, "importante",
     "history", "en", ["prophet-chronology", "reference", "byu-adjacent"],
     "J. Christopher Conkling. Joseph Smith Chronology, 1979. Reference timeline."),
    ("Last American Frontier, The - Frederic L. Paxson.epub",
     "last-american-frontier-paxson", "Frederic L. Paxson", 20, 65, "opcional",
     "history", "en", ["western-history", "early-20th-century-scholarship", "general-us-history"],
     "Frederic L. Paxson (1877-1948), Pulitzer-winning historian. Last American Frontier, 1910."),
    ("Letters Exhibiting the Most Prominent Doctrines of Tof Jesus Christ of Latter-day Saints - Orson Spencer.epub",
     "letters-exhibiting-doctrines-spencer", "Orson Spencer", 40, 70, "importante",
     "history", "en", ["19th-century-lds", "apologetics", "early-apostles-associate", "primary-source"],
     "Orson Spencer (1802-1855), BYU founding chancellor. Letters Exhibiting... 1848."),
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

print(f"\nTheme 7 (LDS history): {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

#!/usr/bin/env python
"""Theme 1: Patristic / early Christian writings (22 works, individually curated)."""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

# Each entry individually curated: (file, slug, author, auth, rigor, imp, cat, lang, tags, note)
WORKS = [
    ("Address to the Greeks - Tatiano.epub",
     "address-to-the-greeks-tatian", "Tatian the Assyrian", 30, 75, "opcional",
     "reference", "en", ["patristic", "2nd-century", "apologetics", "primary-source", "ante-nicene"],
     "Tatian (c. 120-180), Syrian Christian apologist. Oratio ad Graecos, c. 165-175."),
    ("Against Heresies - Irenaeus of Lyons.epub",
     "against-heresies-irenaeus", "Irenaeus of Lyons", 40, 85, "importante",
     "reference", "en", ["patristic", "2nd-century", "anti-gnostic", "apostolic-succession", "primary-source", "ante-nicene"],
     "Irenaeus (c. 130-202), bishop of Lyons. Adversus Haereses, c. 180. Key source for early Christian doctrine."),
    ("Against the Pelagians - Jerome.epub",
     "against-the-pelagians-jerome", "Jerome", 35, 80, "opcional",
     "reference", "en", ["patristic", "5th-century", "anti-pelagian", "primary-source", "nicene-post-nicene"],
     "Jerome (c. 347-420), Vulgate translator. Dialogus adversus Pelagianos, c. 415."),
    ("Barlaam and Ioasaph - John Damascene.epub",
     "barlaam-and-ioasaph-john-damascene", "John Damascene (attrib.)", 25, 60, "opcional",
     "reference", "en", ["patristic", "8th-century", "hagiography", "christian-novel", "buddhist-christian"],
     "Attributed to John Damascene (c. 675-749). Christianized version of Buddha legend."),
    ("Catechetical Lectures - Cyril.epub",
     "catechetical-lectures-cyril", "Cyril of Jerusalem", 40, 85, "importante",
     "reference", "en", ["patristic", "4th-century", "catechesis", "baptism", "eucharist", "primary-source", "nicene"],
     "Cyril of Jerusalem (c. 313-386). Catecheses, c. 350. Key witness to 4th-c liturgy and doctrine."),
    ("De Spiritu Sancto - Basil the Great.epub",
     "de-spiritu-sancto-basil", "Basil the Great", 40, 85, "importante",
     "reference", "en", ["patristic", "4th-century", "pneumatology", "cappadocian", "trinity", "primary-source", "nicene"],
     "Basil of Caesarea (c. 330-379), Cappadocian Father. De Spiritu Sancto, c. 375. Foundational on the Holy Spirit."),
    ("Divine Institutes - Lactantius.epub",
     "divine-institutes-lactantius", "Lactantius", 35, 80, "importante",
     "reference", "en", ["patristic", "4th-century", "apologetics", "latin-fathers", "primary-source", "ante-nicene"],
     "Lactantius (c. 250-325), tutor of Constantine's son. Divinae Institutiones, c. 303-311."),
    ("Ecclesiastical History - Eusebio de Cesárea.epub",
     "ecclesiastical-history-eusebius", "Eusebius of Caesarea", 40, 85, "importante",
     "history", "en", ["patristic", "4th-century", "church-history", "apostolic-era", "primary-source", "nicene"],
     "Eusebius (c. 260-339), 'Father of Church History'. Historia Ecclesiastica, c. 324. Essential primary source."),
    ("Ecclesiastical History - Socrates Scholasticus.epub",
     "ecclesiastical-history-socrates-scholasticus", "Socrates Scholasticus", 35, 80, "importante",
     "history", "en", ["patristic", "5th-century", "church-history", "post-nicene", "primary-source"],
     "Socrates Scholasticus (c. 380-439). Historia Ecclesiastica c. 439. Continues Eusebius."),
    ("Ecclesiastical History - Sozomen.epub",
     "ecclesiastical-history-sozomen", "Sozomen", 35, 80, "opcional",
     "history", "en", ["patristic", "5th-century", "church-history", "post-nicene", "primary-source"],
     "Sozomen (c. 400-450). Historia Ecclesiastica c. 443. Parallel to Socrates Scholasticus."),
    ("Epistle of Barnabas - Barnabas.epub",
     "epistle-of-barnabas", "Pseudo-Barnabas", 30, 75, "importante",
     "reference", "en", ["patristic", "2nd-century", "apostolic-fathers", "typology", "primary-source", "ante-nicene"],
     "Epistle of Barnabas (c. 70-132), anonymous. Counted among Apostolic Fathers."),
    ("Epistle to Diognetus - Mathetes.epub",
     "epistle-to-diognetus", "Mathetes (anonymous)", 30, 75, "importante",
     "reference", "en", ["patristic", "2nd-century", "apologetics", "apostolic-fathers", "primary-source", "ante-nicene"],
     "Epistle to Diognetus (c. 130-200). Early Christian apology, anonymous."),
    ("Epistle to the Philippians - Polycarp.epub",
     "epistle-to-the-philippians-polycarp", "Polycarp of Smyrna", 40, 85, "importante",
     "reference", "en", ["patristic", "2nd-century", "apostolic-fathers", "martyr", "primary-source", "ante-nicene"],
     "Polycarp (c. 69-155), disciple of John. Epistle to the Philippians, c. 110-140."),
    ("Epistles of Apostle Paul - Alexander Mileant.epub",
     "epistles-of-apostle-paul-mileant", "Alexander Mileant", 20, 55, "opcional",
     "reference", "en", ["orthodox", "pauline-studies", "modern-commentary", "non-lds"],
     "Bp. Alexander Mileant (1938-2005), Russian Orthodox. Study guide on Pauline epistles."),
    ("Epistles of Clement of Rome - Clement of Rome.epub",
     "epistles-of-clement-of-rome", "Clement of Rome", 40, 85, "importante",
     "reference", "en", ["patristic", "1st-century", "apostolic-fathers", "roman-church", "primary-source", "ante-nicene"],
     "Clement of Rome (d. c. 99). 1 Clement (c. 95-96). Earliest non-NT Christian letter."),
    ("Epistles of Cyprian - Cyprian.epub",
     "epistles-of-cyprian", "Cyprian of Carthage", 40, 85, "importante",
     "reference", "en", ["patristic", "3rd-century", "ecclesiology", "martyr", "primary-source", "ante-nicene"],
     "Cyprian of Carthage (c. 200-258). Epistles and treatises, pre-martyrdom."),
    ("Epistles of Ignatius - Ignatius.epub",
     "epistles-of-ignatius", "Ignatius of Antioch", 40, 85, "importante",
     "reference", "en", ["patristic", "2nd-century", "apostolic-fathers", "martyr", "episcopacy", "primary-source", "ante-nicene"],
     "Ignatius of Antioch (c. 35-108). Seven epistles written en route to martyrdom, c. 107-108."),
    ("Extant Fragments - Dionysus.epub",
     "extant-fragments-dionysius-alexandria", "Dionysius of Alexandria", 35, 75, "opcional",
     "reference", "en", ["patristic", "3rd-century", "fragments", "primary-source", "ante-nicene"],
     "Dionysius of Alexandria (d. 265), disciple of Origen. Extant fragments."),
    ("First Epistle of Clement to the Corinthians - Clemente de Alejandría.epub",
     "first-epistle-of-clement-to-corinthians", "Clement of Rome", 40, 85, "importante",
     "reference", "en", ["patristic", "1st-century", "apostolic-fathers", "primary-source", "ante-nicene"],
     "1 Clement (c. 95-96). Author is Clement of Rome (OPF attribution to 'Clemente de Alejandría' is an error)."),
    ("Five Books against Marcion - Tertullian.epub",
     "five-books-against-marcion-tertullian", "Tertullian", 40, 85, "importante",
     "reference", "en", ["patristic", "3rd-century", "anti-marcion", "latin-fathers", "primary-source", "ante-nicene"],
     "Tertullian (c. 155-220). Adversus Marcionem, c. 207-212. Key refutation of Marcion's heresy."),
    ("Fragments - Papias.epub",
     "fragments-papias", "Papias of Hierapolis", 40, 80, "importante",
     "reference", "en", ["patristic", "2nd-century", "apostolic-fathers", "gospel-origins", "primary-source", "ante-nicene"],
     "Papias of Hierapolis (c. 60-130), hearer of John. Fragments preserved by Eusebius and Irenaeus."),
    ("Fragments from the Acts of the Church - Hegesippus.epub",
     "fragments-hegesippus", "Hegesippus", 40, 80, "importante",
     "reference", "en", ["patristic", "2nd-century", "church-history", "jewish-christian", "primary-source", "ante-nicene"],
     "Hegesippus (c. 110-180), Jewish-Christian historian. Fragments on apostolic succession."),
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

print(f"\nTheme 1 (Patristic): {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

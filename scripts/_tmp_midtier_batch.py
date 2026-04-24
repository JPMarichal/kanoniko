#!/usr/bin/env python
"""Mid-tier authors: Nibley (8), Petersen (5), Skousen (5), J.R. Clark (5 FP vols).

Individual Fase 0.
"""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

WORKS = [
    # Hugh Nibley (8)
    ("Mormonism and Early Christianity - Stephen D Ricks & Hugh Nibley.epub",
     "mormonism-and-early-christianity-nibley", "Hugh Nibley (ed. Stephen D. Ricks)",
     45, 85, "importante", "books", "en",
     ["hugh-nibley", "early-christianity", "farms", "collected-works"],
     "Hugh Nibley. Mormonism and Early Christianity. Vol. 4 of Collected Works (ed. Stephen D. Ricks)."),
    ("Nibley on the Timely and the Timeless - Hugh Nibley.epub",
     "nibley-timely-and-timeless", "Hugh Nibley",
     45, 80, "importante", "books", "en",
     ["hugh-nibley", "essays", "byu-collected"],
     "Hugh Nibley. Nibley on the Timely and the Timeless, 1978."),
    ("Of All Things_ Classic Quotations from Hugh Nibley - Hugh Nibley & Gary P Gillum.epub",
     "of-all-things-nibley-quotations", "Hugh Nibley (ed. Gary P. Gillum)",
     45, 70, "opcional", "reference", "en",
     ["hugh-nibley", "quotations", "compilation"],
     "Hugh Nibley. Of All Things: Classic Quotations from Hugh Nibley (ed. Gillum)."),
    ("Old Testament and Related Studies - John W Welch & Hugh Nibley & Gary P Gillum.epub",
     "ot-and-related-studies-nibley", "Hugh Nibley (eds. Welch & Gillum)",
     45, 85, "importante", "books", "en",
     ["hugh-nibley", "old-testament", "farms", "collected-works"],
     "Hugh Nibley. Old Testament and Related Studies. Vol. 1 of Collected Works (eds. Welch & Gillum)."),
    ("Since Cumorah - Hugh Nibley.epub",
     "since-cumorah-nibley", "Hugh Nibley",
     45, 85, "importante", "books", "en",
     ["hugh-nibley", "book-of-mormon", "classic-apologetics"],
     "Hugh Nibley. Since Cumorah, 1967. Classic Book of Mormon apologetics."),
    ("Temple and Cosmos, Beyond This Ignorant Present - Hugh Nibley.epub",
     "temple-and-cosmos-nibley", "Hugh Nibley",
     45, 85, "importante", "books", "en",
     ["hugh-nibley", "temple", "ancient-near-east", "farms", "collected-works"],
     "Hugh Nibley. Temple and Cosmos, 1992. Vol. 12 of Collected Works."),
    ("Templo y Cosmos - Hugh Nibley.epub",
     "templo-y-cosmos-nibley-es", "Hugh Nibley",
     45, 85, "importante", "books", "es",
     ["hugh-nibley", "temple", "spanish-translation"],
     "Hugh Nibley. Templo y Cosmos (ES translation of Temple and Cosmos)."),
    ("World and the Prophets - Hugh Nibley.epub",
     "world-and-the-prophets-nibley", "Hugh Nibley",
     45, 85, "importante", "books", "en",
     ["hugh-nibley", "apostasy", "classical-studies", "farms", "collected-works"],
     "Hugh Nibley. The World and the Prophets, 1954/1987. Vol. 3 of Collected Works."),

    # Mark E. Petersen (5)
    ("Moses, Man of Miracles - Mark E Petersen.epub",
     "moses-man-of-miracles-petersen", "Mark E. Petersen",
     50, 75, "importante", "biographies", "en",
     ["apostle-authored", "moses", "old-testament-prophet", "petersen-prophet-series"],
     "Elder Mark E. Petersen (1900-1984), Q12. Moses, Man of Miracles. Part of his biblical-prophet series."),
    ("Noah and the Flood - Mark E Petersen.epub",
     "noah-and-the-flood-petersen", "Mark E. Petersen",
     50, 75, "importante", "biographies", "en",
     ["apostle-authored", "noah", "flood", "petersen-prophet-series"],
     "Elder Mark E. Petersen. Noah and the Flood, 1982."),
    ("Sons of Mosiah - Mark E Petersen.epub",
     "sons-of-mosiah-petersen", "Mark E. Petersen",
     50, 75, "importante", "books", "en",
     ["apostle-authored", "sons-of-mosiah", "book-of-mormon", "missionary"],
     "Elder Mark E. Petersen. Sons of Mosiah, 1978."),
    ("Three Kings of Israel - Mark E Petersen.epub",
     "three-kings-of-israel-petersen", "Mark E. Petersen",
     50, 75, "importante", "biographies", "en",
     ["apostle-authored", "saul", "david", "solomon", "petersen-prophet-series"],
     "Elder Mark E. Petersen. Three Kings of Israel (Saul, David, Solomon), 1980."),
    ("Way to Peace - Mark E Petersen.epub",
     "way-to-peace-petersen", "Mark E. Petersen",
     50, 75, "importante", "books", "en",
     ["apostle-authored", "peace", "gospel-living"],
     "Elder Mark E. Petersen. The Way to Peace, 1969."),

    # W. Cleon Skousen (5) — series Mormonism through millennia
    ("primeros 2000 años, Los - W. Cleon Skousen.epub",
     "primeros-2000-anos-skousen-es", "W. Cleon Skousen",
     30, 65, "opcional", "books", "es",
     ["skousen", "old-testament", "adam-to-abraham", "popular-lds-history"],
     "W. Cleon Skousen. Los primeros 2000 años (ES). First Two Thousand Years (Adam to Abraham)."),
    ("primeros 2000 años_ De Adán a Abraham, Los - W. Cleon Skousen.epub",
     "primeros-2000-anos-adan-abraham-skousen-es", "W. Cleon Skousen",
     30, 65, "opcional", "books", "es",
     ["skousen", "old-testament", "adam-to-abraham", "alternate-edition"],
     "W. Cleon Skousen. Los primeros 2000 años: De Adán a Abraham (edición con subtítulo)."),
    ("segundo milenio, El - W. Cleon Skousen.epub",
     "segundo-milenio-skousen-es", "W. Cleon Skousen",
     30, 65, "opcional", "books", "es",
     ["skousen", "second-millennium", "abraham-to-david", "popular-lds-history"],
     "W. Cleon Skousen. El segundo milenio (ES). Posible edición alternativa o extensión de su serie de millennia."),
    ("tercer milenio, El - W. Cleon Skousen.epub",
     "tercer-milenio-skousen-es", "W. Cleon Skousen",
     30, 65, "opcional", "books", "es",
     ["skousen", "third-thousand-years", "abraham-to-david", "popular-lds-history"],
     "W. Cleon Skousen. El tercer milenio (ES). The Third Thousand Years (Abraham to David)."),
    ("Tercer Milenio_ De Abraham hasta David, El - W. Cleon Skousen.epub",
     "tercer-milenio-abraham-david-skousen-es", "W. Cleon Skousen",
     30, 65, "opcional", "books", "es",
     ["skousen", "third-thousand-years", "alternate-edition"],
     "W. Cleon Skousen. El Tercer Milenio: De Abraham hasta David (edición con subtítulo)."),

    # James R. Clark Messages of FP (vols 2-6; vol 1 not in !Ready, presumed already)
    ("Messages of the First Presidency, vol. 2 - James R Clark.epub",
     "messages-first-presidency-vol-2-clark", "James R. Clark (ed.)",
     55, 85, "importante", "books", "en",
     ["first-presidency-messages", "primary-source-compilation", "1833-1964"],
     "James R. Clark (ed.), BYU. Messages of the First Presidency, vol. 2. Compilación oficial de mensajes de la PP."),
    ("Messages of the First Presidency, vol. 3 - James R Clark.epub",
     "messages-first-presidency-vol-3-clark", "James R. Clark (ed.)",
     55, 85, "importante", "books", "en",
     ["first-presidency-messages", "primary-source-compilation"],
     "James R. Clark (ed.). Messages of the First Presidency, vol. 3."),
    ("Messages of the First Presidency, vol. 4 - James R Clark.epub",
     "messages-first-presidency-vol-4-clark", "James R. Clark (ed.)",
     55, 85, "importante", "books", "en",
     ["first-presidency-messages", "primary-source-compilation"],
     "James R. Clark (ed.). Messages of the First Presidency, vol. 4."),
    ("Messages of the First Presidency, vol. 5 - James R Clark.epub",
     "messages-first-presidency-vol-5-clark", "James R. Clark (ed.)",
     55, 85, "importante", "books", "en",
     ["first-presidency-messages", "primary-source-compilation"],
     "James R. Clark (ed.). Messages of the First Presidency, vol. 5."),
    ("Messages of the First Presidency, vol. 6 - James R Clark.epub",
     "messages-first-presidency-vol-6-clark", "James R. Clark (ed.)",
     55, 85, "importante", "books", "en",
     ["first-presidency-messages", "primary-source-compilation"],
     "James R. Clark (ed.). Messages of the First Presidency, vol. 6."),
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

print(f"\nMid-tier batch: {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}")

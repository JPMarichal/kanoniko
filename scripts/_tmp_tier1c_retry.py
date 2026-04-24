#!/usr/bin/env python
"""Retry the 9 broken sources from sub-batch 3 with correct filenames."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"

RETRIES = [
    # (filename, slug, author, title, authority, rigor, importance, category, lang, tags, note)
    ("Following Christ, The Parable of the Divers and More Good News - Stephen E Robinson.epub",
     "following-christ-divers-robinson", "Stephen E. Robinson",
     "Following Christ: The Parable of the Divers and More Good News",
     35, 60, "importante", "books", "en",
     ["atonement", "grace", "discipleship", "byu-professor"],
     "Deseret Book. Sequel to Believing Christ by BYU religion professor."),
    ("In the Strength of the Lord, The Life and Teachings of James E_ Faust - James E Faust & James P Bell.epub",
     "in-the-strength-of-the-lord-faust", "James E. Faust",
     "In the Strength of the Lord: The Life and Teachings of James E. Faust",
     45, 65, "importante", "biographies", "en",
     ["apostle-authored", "biography", "teachings-compilation"],
     "Deseret Book. Compilation of Faust's life and teachings (with James P. Bell)."),
    ("Counseling with Our Councils_ Learning to Minister Tin the Church and in the Family - M. Russell Ballard.epub",
     "counseling-with-our-councils-ballard", "M. Russell Ballard",
     "Counseling with Our Councils: Learning to Minister Together in the Church and in the Family",
     45, 65, "importante", "books", "en",
     ["apostle-authored", "councils", "church-administration"],
     "Deseret Book. Ballard's treatise on council governance."),
    ("Best-Loved Poems of the LDS People - Jay A. Parry & Linda Ririe Gundry & Jack M. Lyon & Devan Jensen.epub",
     "best-loved-poems-lds", "Jay A. Parry, Linda Ririe Gundry, Jack M. Lyon, Devan Jensen (eds.)",
     "Best-Loved Poems of the LDS People",
     30, 55, "opcional", "reference", "en",
     ["poetry", "anthology", "lds-culture"],
     "Deseret Book anthology of LDS-beloved poetry."),
    ("Heavens Are Open, The 1992 Sperry Symposium on the D and Covenants and Church History - Byron R. Merrill.epub",
     "heavens-are-open-sperry-1992", "Byron R. Merrill (ed.)",
     "The Heavens Are Open: The 1992 Sperry Symposium on the Doctrine and Covenants and Church History",
     35, 70, "importante", "books", "en",
     ["sperry-symposium", "doctrine-and-covenants", "church-history", "byu-academic"],
     "BYU Religious Studies Center. 1992 Sperry Symposium proceedings."),
    ("Doctrines for Exaltation, The 1989 Sperry Symposium on the Doctrine and Covenants - Susan Easton Black.epub",
     "doctrines-for-exaltation-sperry-1989", "Susan Easton Black (ed.)",
     "Doctrines for Exaltation: The 1989 Sperry Symposium on the Doctrine and Covenants",
     35, 70, "importante", "books", "en",
     ["sperry-symposium", "doctrine-and-covenants", "exaltation", "byu-academic"],
     "Deseret Book. 1989 Sperry Symposium proceedings."),
    ("A Brief Autobiographical Sketch of the Missionary La of a Valiant Soldier for Christ - Anthon L. Skanchy.epub",
     "skanchy-autobiographical-sketch", "Anthon L. Skanchy",
     "A Brief Autobiographical Sketch of the Missionary Labors of a Valiant Soldier for Christ",
     30, 55, "opcional", "biographies", "en",
     ["missionary", "autobiography", "19th-century", "scandinavian-mission"],
     "Autobiographical account of Norwegian LDS missionary."),
    ("As Women of Faith, Talks Selected from the BYU WomenConferences - Mary E Stovall & Carol Cornwall Madsen.epub",
     "as-women-of-faith-byu", "Mary E. Stovall, Carol Cornwall Madsen (eds.)",
     "As Women of Faith: Talks Selected from the BYU Women's Conferences",
     30, 60, "opcional", "books", "en",
     ["women", "byu-womens-conference", "anthology"],
     "Deseret Book. BYU Women's Conference talks anthology."),
    ("Heritage of Faith, Talks Selected from the BYU WomenConferences - Mary E Stovall & Carol Cornwall Madsen.epub",
     "heritage-of-faith-byu", "Mary E. Stovall, Carol Cornwall Madsen (eds.)",
     "Heritage of Faith: Talks Selected from the BYU Women's Conferences",
     30, 60, "opcional", "books", "en",
     ["women", "byu-womens-conference", "anthology"],
     "Deseret Book. BYU Women's Conference talks anthology."),
]

import json, tempfile, os
EXTRACT = ROOT / "scripts" / "epub_extract.py"

ok = 0
broken = []
for fn, slug, author, title, authority, rigor, importance, category, lang, tags, note in RETRIES:
    src = READY / fn
    if not src.exists():
        broken.append((fn, "MISSING"))
        continue
    # write sidecar
    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    fase0.parent.mkdir(parents=True, exist_ok=True)
    fase0.write_text(json.dumps({
        "authority": authority, "rigor": rigor, "importance": importance,
        "official": False, "current": True, "context": "book-private",
        "audience": "adult", "tags": tags, "category": category,
        "author": author, "source_url": None, "note": note,
    }, indent=2), encoding="utf-8")
    cmd = [sys.executable, str(EXTRACT), str(src),
           "--lang", lang, "--category", category, "--apply",
           "--slug", slug, "--author", author,
           "--fase0", str(fase0)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        # archive source
        (DONE / fn).parent.mkdir(parents=True, exist_ok=True)
        src.rename(DONE / fn)
        print(f"  OK {slug}")
    else:
        broken.append((fn, r.stderr[-200:] if r.stderr else "?"))
        print(f"  BROKEN {slug}: {r.stderr[-200:]}")

print(f"\nRetry: {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

#!/usr/bin/env python
"""Theme 4: Non-LDS Christian theology / devotional (22 works, individually curated).

Excludes:
  - Skinner/Millet (LDS-on-Lewis) — goes to theme 8
  - Dymer (Lewis poem) — goes to theme 5 literature
"""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

WORKS = [
    ("A Brief Bible History_ A Surve of the Old and New Testaments - James Oscar Boyd & John Gresham Machen.epub",
     "brief-bible-history-boyd-machen", "James Oscar Boyd & J. Gresham Machen", 25, 70, "opcional",
     "reference", "en", ["evangelical", "reformed", "bible-survey", "early-20th-century", "non-lds"],
     "Boyd & Machen. Brief Bible History, 1922. Princeton Seminary context."),
    ("A Modern Translation of Genesis 1–11 in the Traditional Sense - Dominic Kent.epub",
     "modern-translation-genesis-1-11-kent", "Dominic Kent", 15, 55, "opcional",
     "reference", "en", ["bible-translation", "genesis", "modern", "non-lds"],
     "Dominic Kent's modern translation of Genesis 1–11 in traditional sense."),
    ("Abandonment to Divine Providence - Jean-Pierre de Caussade.epub",
     "abandonment-to-divine-providence-caussade", "Jean-Pierre de Caussade", 25, 75, "opcional",
     "reference", "en", ["catholic", "18th-century", "jesuit", "mystical-theology", "non-lds"],
     "Caussade (1675-1751), Jesuit. Abandonment to Divine Providence, posthumous 1861."),
    ("Absolute Surrender - Andrew Murray.epub",
     "absolute-surrender-murray", "Andrew Murray", 20, 60, "opcional",
     "reference", "en", ["evangelical", "dutch-reformed", "devotional", "19th-century", "non-lds"],
     "Andrew Murray (1828-1917), South African Dutch Reformed. Devotional classic."),
    ("Abstract of Systematic Theology - James P. Boyce.epub",
     "abstract-systematic-theology-boyce", "James P. Boyce", 20, 75, "opcional",
     "reference", "en", ["baptist", "systematic-theology", "19th-century", "southern-baptist", "non-lds"],
     "James P. Boyce (1827-1888). Abstract of Systematic Theology, 1887. Southern Baptist Seminary founder."),
    ("Avoiding the 23 pitfalls to recovery - Jeff Robinson.epub",
     "avoiding-23-pitfalls-to-recovery-robinson", "Jeff Robinson", 15, 45, "opcional",
     "reference", "en", ["addiction-recovery", "12-step", "non-lds"],
     "Jeff Robinson. Recovery pitfalls guide (non-LDS context)."),
    ("Bible Summary - Justin S. Holcomb.epub",
     "bible-summary-holcomb", "Justin S. Holcomb", 15, 55, "opcional",
     "reference", "en", ["evangelical", "anglican", "bible-overview", "modern", "non-lds"],
     "Justin Holcomb, Anglican theologian. Bible book-by-book summary."),
    ("Cristianismo y nada mas - C. S. Lewis.epub",
     "mero-cristianismo-lewis", "C. S. Lewis", 30, 75, "importante",
     "reference", "es", ["anglican", "apologetics", "20th-century", "non-lds"],
     "C. S. Lewis (1898-1963). Mere Christianity, 1952. Spanish translation."),
    ("Cuando el cristianismo era nuevo - David W. Bercot.epub",
     "cuando-el-cristianismo-era-nuevo-bercot", "David W. Bercot", 25, 70, "opcional",
     "reference", "es", ["patristic-studies", "primitive-christianity", "anabaptist-leaning", "non-lds"],
     "David Bercot. When the Church was Young (Spanish). Patristic primer."),
    ("De la tradición a la verdad - Richard Bennett.epub",
     "de-la-tradicion-a-la-verdad-bennett", "Richard Bennett", 15, 55, "opcional",
     "reference", "es", ["ex-catholic", "evangelical", "anti-catholic", "non-lds"],
     "Richard Bennett, former Catholic priest turned evangelical. Autobiographical critique of Catholicism."),
    ("Death of Christ, The - James Denney.epub",
     "death-of-christ-denney", "James Denney", 25, 75, "opcional",
     "reference", "en", ["presbyterian", "atonement", "early-20th-century", "scottish-theology", "non-lds"],
     "James Denney (1856-1917), Scottish Presbyterian. The Death of Christ, 1902."),
    ("Foxe's Book of Martyrs - John Foxe.epub",
     "foxes-book-of-martyrs", "John Foxe", 30, 70, "importante",
     "history", "en", ["protestant", "16th-century", "martyrology", "reformation", "primary-source", "non-lds"],
     "John Foxe (1516-1587). Acts and Monuments, 1563. Protestant martyrology."),
    ("Grace Abounding on the Chief of Sinners - John Bunyan.epub",
     "grace-abounding-bunyan", "John Bunyan", 25, 75, "opcional",
     "reference", "en", ["puritan", "baptist", "17th-century", "spiritual-autobiography", "non-lds"],
     "John Bunyan (1628-1688). Grace Abounding to the Chief of Sinners, 1666. Spiritual autobiography."),
    ("Heretics - G K Chesterton.epub",
     "heretics-chesterton", "G. K. Chesterton", 25, 75, "opcional",
     "reference", "en", ["catholic", "early-20th-century", "cultural-criticism", "non-lds"],
     "G. K. Chesterton (1874-1936). Heretics, 1905. Cultural and religious criticism."),
    ("Hermanos de Jesús, ¿hijos de María_ - Pablo Blanco.epub",
     "hermanos-de-jesus-blanco", "Pablo Blanco", 15, 60, "opcional",
     "reference", "es", ["catholic", "mariology", "biblical-studies", "modern", "non-lds"],
     "Pablo Blanco Sarto, Spanish Catholic theologian. On the 'brothers of Jesus' question."),
    ("How to Study and Teach the Bible - Elmer L. Towns.epub",
     "how-to-study-and-teach-the-bible-towns", "Elmer L. Towns", 15, 50, "opcional",
     "reference", "en", ["evangelical", "baptist", "bible-pedagogy", "non-lds"],
     "Elmer Towns, Liberty University. Evangelical Bible-teaching guide."),
    ("Imitation of Christ - Thomas Kempis.epub",
     "imitation-of-christ-kempis", "Thomas à Kempis", 35, 80, "importante",
     "reference", "en", ["catholic", "15th-century", "devotional-classic", "devotio-moderna", "primary-source"],
     "Thomas à Kempis (c. 1380-1471). De Imitatione Christi, c. 1418-1427. Most-read devotional after the Bible."),
    ("In His Steps - Charles Sheldon.epub",
     "in-his-steps-sheldon", "Charles M. Sheldon", 20, 65, "opcional",
     "reference", "en", ["social-gospel", "19th-century", "wwjd", "protestant", "non-lds"],
     "Charles Sheldon (1857-1946). In His Steps, 1896. Origin of 'What Would Jesus Do'."),
    ("Institutes of the Christian Religion - John Calvin.epub",
     "institutes-christian-religion-calvin", "John Calvin", 30, 85, "importante",
     "reference", "en", ["reformed", "reformation", "16th-century", "systematic-theology", "primary-source", "non-lds"],
     "John Calvin (1509-1564). Institutio Christianae Religionis, 1536/1559. Foundation of Reformed theology."),
    ("Jerusalem in the New Testament - Tom Wright.epub",
     "jerusalem-in-the-nt-wright", "N. T. Wright", 30, 80, "importante",
     "reference", "en", ["anglican", "nt-scholarship", "modern", "biblical-studies", "non-lds"],
     "N. T. Wright, Anglican bishop and NT scholar. Essay on Jerusalem's NT significance."),
    ("Jesus no Dijo Eso - Bart D. Ehrman.epub",
     "jesus-no-dijo-eso-ehrman", "Bart D. Ehrman", 25, 75, "opcional",
     "reference", "es", ["secular-nt-scholarship", "textual-criticism", "modern", "non-lds", "critical"],
     "Bart Ehrman (UNC). Misquoting Jesus (Spanish). Textual criticism bestseller."),
    ("Large Catechism - Martin Luther.epub",
     "large-catechism-luther", "Martin Luther", 30, 85, "importante",
     "reference", "en", ["lutheran", "reformation", "16th-century", "catechism", "primary-source", "non-lds"],
     "Martin Luther (1483-1546). Der Große Katechismus, 1529. Foundational Lutheran confession."),
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

print(f"\nTheme 4 (Non-LDS theology): {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

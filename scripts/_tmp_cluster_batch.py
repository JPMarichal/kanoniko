#!/usr/bin/env python
"""Clusters batch: philosophy, patristic, Edersheim scholarship, LDS authors.

Archives: literature (Austen, Macdonald, Stevenson, Burnett).
Incorporates: Aristotle (5), Plato (4), Aquinas (6), Tertullian (4),
  Edersheim (4), Millet (6), Barlow (6), Cook (4), Crowther (4),
  Widtsoe (4), Andrus (4), SW Kimball (3), Preston Nibley (3),
  Crowder (4), Hartshorn (3), D.W. Parry (3), Shelton (3 evangelical).
"""
import subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

ARCHIVE_LIT = [
    "Mansfield Park - Jane Austen.epub",
    "Orgullo y prejuicio - Jane Austen.epub",
    "Persuasion - Jane Austen.epub",
    "Sense and Sensibility - Jane Austen.epub",
    "Lilith - George Macdonald.epub",
    "Phantastes - George Macdonald.epub",
    "Princess and Curdie - George Macdonald.epub",
    "Princess and the Goblin - George Macdonald.epub",
    "Moral Emblems - Robert Louis Stevenson.epub",
    "Strange Case of Dr. Jekyll and Mr. Hyde, The - Robert Louis Stevenson.epub",
    "Treasure Island - Robert Louis Stevenson.epub",
    "Little Lord Fauntleroy - Francis H Burnett.epub",
    "Lost Prince - Francis H Burnett.epub",
    "Secret Garden - Francis H Burnett.epub",
]

WORKS = [
    # Aristotle (5) — philosophy
    ("Nicomachean Ethics - Aristóteles.epub",
     "nicomachean-ethics-aristotle", "Aristotle",
     35, 90, "importante", "reference", "en",
     ["classical", "greek", "ethics", "aristotle", "primary-source", "virtue-ethics"],
     "Aristotle (384-322 BC). Nicomachean Ethics. Foundational virtue-ethics treatise."),
    ("On the Soul - Aristóteles.epub",
     "on-the-soul-aristotle", "Aristotle",
     30, 85, "importante", "reference", "en",
     ["classical", "greek", "psychology", "soul", "aristotle", "primary-source"],
     "Aristotle. De Anima (On the Soul). Foundational work on psychology and the soul."),
    ("Physics - Aristóteles.epub",
     "physics-aristotle", "Aristotle",
     30, 85, "opcional", "reference", "en",
     ["classical", "greek", "natural-philosophy", "aristotle", "primary-source"],
     "Aristotle. Physics. Natural philosophy foundational text."),
    ("Poetics - Aristóteles.epub",
     "poetics-aristotle", "Aristotle",
     30, 80, "opcional", "reference", "en",
     ["classical", "greek", "aesthetics", "literary-theory", "aristotle", "primary-source"],
     "Aristotle. Poetics. Foundational literary/aesthetic theory."),
    ("Sobre la generación y la corrupción - Aristóteles.epub",
     "generacion-corrupcion-aristotle-es", "Aristotle",
     25, 80, "opcional", "reference", "es",
     ["classical", "greek", "natural-philosophy", "aristotle", "primary-source"],
     "Aristóteles. Sobre la generación y la corrupción (De Generatione et Corruptione)."),

    # Plato (4) — philosophy
    ("Meno - Plato.epub",
     "meno-plato", "Plato",
     30, 85, "importante", "reference", "en",
     ["classical", "greek", "epistemology", "virtue", "plato", "primary-source"],
     "Plato (c. 428-348 BC). Meno. On virtue and knowledge as recollection."),
    ("Sophist - Plato.epub",
     "sophist-plato", "Plato",
     30, 85, "opcional", "reference", "en",
     ["classical", "greek", "being", "epistemology", "plato", "primary-source"],
     "Plato. Sophist. On being and non-being."),
    ("Symposium - Plato.epub",
     "symposium-plato", "Plato",
     30, 85, "importante", "reference", "en",
     ["classical", "greek", "love", "eros", "plato", "primary-source"],
     "Plato. Symposium. Philosophical dialogue on love."),
    ("Timaeus - Plato.epub",
     "timaeus-plato", "Plato",
     30, 85, "importante", "reference", "en",
     ["classical", "greek", "cosmology", "creation", "plato", "primary-source"],
     "Plato. Timaeus. Cosmology, creation of the universe — influential on early Christian thought."),

    # Aquinas (6) - scholastic theology
    ("Summa Teológica - Tomas de Aquino.epub",
     "summa-teologica-aquino-es", "Thomas Aquinas",
     40, 90, "importante", "reference", "es",
     ["scholastic", "catholic", "13th-century", "systematic-theology", "aquinas", "primary-source"],
     "Santo Tomás de Aquino (1225-1274). Summa Teológica (ES). Magnum opus del tomismo escolástico."),
    ("Summa Theologica, part 1 - Tomas de Aquino.epub",
     "summa-theologica-part-1-aquinas", "Thomas Aquinas",
     40, 90, "importante", "reference", "en",
     ["scholastic", "catholic", "13th-century", "systematic-theology", "aquinas", "primary-source"],
     "Aquinas. Summa Theologica, Pars Prima (God, creation)."),
    ("Summa Theologica, part 2, section 1 - Tomas de Aquino.epub",
     "summa-theologica-part-2-1-aquinas", "Thomas Aquinas",
     40, 90, "importante", "reference", "en",
     ["scholastic", "catholic", "ethics", "aquinas", "primary-source"],
     "Aquinas. Summa Theologica, Prima Secundae (ethics, beatitude, law, grace)."),
    ("Summa Theologica, part 2, section 2 - Tomas de Aquino.epub",
     "summa-theologica-part-2-2-aquinas", "Thomas Aquinas",
     40, 90, "importante", "reference", "en",
     ["scholastic", "catholic", "virtues", "aquinas", "primary-source"],
     "Aquinas. Summa Theologica, Secunda Secundae (theological and cardinal virtues)."),
    ("Summa Theologica, part 3 - Tomas de Aquino.epub",
     "summa-theologica-part-3-aquinas", "Thomas Aquinas",
     40, 90, "importante", "reference", "en",
     ["scholastic", "catholic", "christology", "sacraments", "aquinas", "primary-source"],
     "Aquinas. Summa Theologica, Tertia Pars (Christ, sacraments)."),
    ("Summa Theologica, part 3, supplement and appendices - Tomas de Aquino.epub",
     "summa-theologica-supplement-aquinas", "Thomas Aquinas",
     35, 85, "opcional", "reference", "en",
     ["scholastic", "catholic", "supplement", "aquinas", "primary-source"],
     "Aquinas. Summa Theologica, Supplement (compiled posthumously from Commentary on the Sentences)."),

    # Tertullian (4)
    ("On Modesty - Tertullian.epub",
     "on-modesty-tertullian", "Tertullian",
     40, 80, "opcional", "reference", "en",
     ["patristic", "3rd-century", "ante-nicene", "tertullian", "primary-source"],
     "Tertullian (c. 155-220). De Pudicitia (On Modesty)."),
    ("On Monogamy - Tertullian.epub",
     "on-monogamy-tertullian", "Tertullian",
     40, 80, "opcional", "reference", "en",
     ["patristic", "3rd-century", "ante-nicene", "marriage", "tertullian", "primary-source"],
     "Tertullian. De Monogamia (On Monogamy)."),
    ("On the Resurrection - Tertullian.epub",
     "on-the-resurrection-tertullian", "Tertullian",
     40, 85, "importante", "reference", "en",
     ["patristic", "3rd-century", "ante-nicene", "resurrection", "tertullian", "primary-source"],
     "Tertullian. De Resurrectione Carnis (On the Resurrection of the Flesh)."),
    ("Scorpiace - Tertullian.epub",
     "scorpiace-tertullian", "Tertullian",
     40, 80, "opcional", "reference", "en",
     ["patristic", "3rd-century", "ante-nicene", "martyrdom", "tertullian", "primary-source"],
     "Tertullian. Scorpiace (Antidote against the Scorpion — on martyrdom)."),

    # Alfred Edersheim (4) — Jewish-Christian scholar
    ("Old Testament Bible History - Alfred Edersheim.epub",
     "ot-bible-history-edersheim", "Alfred Edersheim",
     30, 85, "importante", "reference", "en",
     ["biblical-studies", "jewish-christian", "19th-century", "ot-history", "non-lds"],
     "Alfred Edersheim (1825-1889). Old Testament Bible History, 1876-1887."),
    ("Sketches of Jewish Social Life - Alfred Edersheim.epub",
     "sketches-jewish-social-life-edersheim", "Alfred Edersheim",
     30, 85, "importante", "reference", "en",
     ["biblical-studies", "jewish-social-history", "nt-context", "19th-century", "non-lds"],
     "Alfred Edersheim. Sketches of Jewish Social Life in the Days of Christ, 1876."),
    ("Templo_ Su ministerio y servicios en tiempos de Jesucristo, El - Alfred Edersheim.epub",
     "templo-ministerio-edersheim-es", "Alfred Edersheim",
     30, 85, "importante", "reference", "es",
     ["biblical-studies", "jewish-temple", "second-temple", "nt-context", "non-lds"],
     "Alfred Edersheim. El Templo: Su ministerio y servicios en tiempos de Jesucristo (ES)."),
    ("Vida Y Los Tiempos De Jesus El Mesias, tomo 1, La - Alfred Edersheim.epub",
     "vida-tiempos-jesus-mesias-edersheim-es", "Alfred Edersheim",
     30, 85, "importante", "reference", "es",
     ["biblical-studies", "life-of-christ", "jewish-context", "19th-century", "non-lds"],
     "Alfred Edersheim. La Vida y los Tiempos de Jesús el Mesías, tomo 1 (ES)."),
]

# Archive literature first
archived = 0
for fn in ARCHIVE_LIT:
    p = READY / fn
    if p.exists():
        p.rename(DONE / fn)
        archived += 1
print(f"Literature archived: {archived}")

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

print(f"\nCluster batch: {ok} OK, {len(broken)} broken, {archived} literature archived")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={sum(1 for _ in READY.iterdir() if _.is_file())}")

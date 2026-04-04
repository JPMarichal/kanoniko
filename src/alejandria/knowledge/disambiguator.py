"""Rule-based disambiguation resolver for ambiguous entity mentions.

Approach
--------
Three levels of disambiguation, each progressively more nuanced:

**Level 1 — Person identity:** Which Judas? Which Mary? Which Nephi?
Resolves ~20 ambiguous names to their specific referent using modifier
detection (regex within ~200-char window) and source-file path matching.
Also handles alternate names for the same person (Peter/Cephas/Simon,
Matthew/Levi, Saul/Paul, Jacob/Israel).

**Level 2 — Entity type:** Judah = patriarch (person), tribe (people),
kingdom (polity), territory (place).  Israel = person, nation, covenant
people, scattered remnant.  Bethlehem = Bethlehem of Judah vs Bethlehem
of Zebulun.  These require type-aware matching and may change the entity
type itself.  Bilingual asymmetry is handled: EN "Judah" covers patriarch
through territory; ES "Judá" is patriarch/tribe/kingdom/territory while
"Judas" only covers NT persons.

**Level 3 — Temporal/dispensational meaning:** Terms whose meaning shifts
across covenant eras.  Gentiles: non-Hebrews (Abraham) → non-Israelites
(Moses) → non-Jews (post-exile) → non-members (Restoration) → European
peoples (BofM 1 Nephi 13).  Zion: City of David → Enoch's city → pure
in heart (D&C 97:21) → New Jerusalem/Missouri → the Church.

No NLP models are required.  Every rule returns an explicit confidence tier
(high / medium / low) and a human-readable evidence string so downstream
consumers can decide whether to trust the resolution.

Integration
-----------
The extractor pipeline calls ``Disambiguator.resolve()`` after gazetteer
matching to upgrade a bare "Alma" mention into "Alma the Elder" or
"Alma the Younger" before the entity is written to the knowledge graph.

When ``resolve()`` returns ``None``, the mention is either unambiguous already
or cannot be resolved with the available signals -- the caller should keep the
original name as-is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional, Tuple


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class DisambiguatedMention:
    """Result of a successful disambiguation."""

    original_name: str      # "Judas"
    resolved_name: str      # "Judas Iscariot"
    confidence: str         # "high", "medium", "low"
    evidence: str           # "modifier: one of the twelve"
    entity_type_resolved: str | None = None  # Level 2: overrides entity type
                                             # e.g. "Judah" as person→"people"


# Type alias for individual rule functions.
# Each takes (text_window, source_file) and returns a resolution tuple or None.
# 3-tuple: (resolved_name, confidence, evidence)
# 4-tuple: (resolved_name, confidence, evidence, entity_type_resolved)
_RuleFn = Callable[[str, str], Optional[Tuple[str, str, str] | Tuple[str, str, str, str | None]]]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WINDOW = 200  # chars before and after the mention to inspect

# Noise patterns common in scraped/converted corpus files.
# Stripped before regex matching to avoid false negatives.
_NOISE_RE = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f]"  # control chars (except \n \r \t)
    r"|<[^>]{0,80}>"                    # HTML tags
    r"|\{[^}]{0,80}\}"                  # stray JSON/template braces
    r"|\[(?:footnote|fn|note)\s*\d*\]"  # footnote markers
    r"|&[a-z]{2,8};"                    # HTML entities
    r"|<!--.*?-->"                       # HTML comments
    r"|\u200b|\u00a0|\ufeff",           # zero-width / nbsp / BOM
    re.IGNORECASE | re.DOTALL,
)


def _clean_window(text: str) -> str:
    """Remove noise that could interfere with regex disambiguation."""
    return _NOISE_RE.sub(" ", text)


def _window_around(text: str, name: str, size: int = _WINDOW) -> str:
    """Return a cleaned, lowercase text window of *size* chars around the first
    occurrence of *name* (case-insensitive).  Falls back to the full text
    (lowered) if the name is not found.  Noise (HTML, control chars, footnote
    markers) is stripped before matching."""
    idx = text.lower().find(name.lower())
    if idx == -1:
        return _clean_window(text.lower())
    start = max(0, idx - size)
    end = min(len(text), idx + len(name) + size)
    return _clean_window(text[start:end].lower())


def _src(path: str) -> str:
    """Normalise a source-file path to forward-slash lowercase for matching."""
    return path.replace("\\", "/").lower()


def _chapter_num(path: str) -> int | None:
    """Try to extract a chapter number from a corpus file path.

    Expected patterns:
        .../alma/42.txt  -> 42
        .../alma/chapter-42.txt -> 42
    """
    m = re.search(r"(\d+)\.(?:txt|md|html|json)$", _src(path))
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Rule sets per ambiguous entity name
# ---------------------------------------------------------------------------

def _rules_judas(window: str, source: str) -> tuple[str, str, str] | None:
    # Judas Maccabeus
    if re.search(r"judas\s+maccab(?:eus|ee)", window):
        return ("Judas Maccabeus", "high", "modifier: Maccabeus/Maccabee")
    if re.search(r"judas\s+macabeo", window):
        return ("Judas Maccabeus", "high", "modifier: Macabeo (ES)")

    # Judas (not Iscariot) -- the other apostle
    if re.search(r"judas\s*\(?not\s+iscariot\)?", window):
        return ("Judas (not Iscariot)", "high", "modifier: not Iscariot")
    if re.search(r"judas\s*\(?\s*son of james\s*\)?", window):
        return ("Judas (not Iscariot)", "high", "modifier: son of James")
    if re.search(r"judas\s*\(?\s*hijo de (?:santiago|jacobo)\s*\)?", window):
        return ("Judas (not Iscariot)", "high", "modifier: hijo de Santiago/Jacobo (ES)")

    # Judas Iscariot
    if re.search(r"judas\s+iscariote?", window):
        return ("Judas Iscariot", "high", "modifier: Iscariot/Iscariote")
    if re.search(r"judas.{0,60}(?:betray|traicion|treach|thirty\s+pieces|treinta\s+piezas"
                 r"|silver|plata|hanged|ahorc[oó])", window):
        return ("Judas Iscariot", "high", "contextual: betrayal/silver/hanging language")

    return None


def _rules_james(window: str, source: str) -> tuple[str, str, str] | None:
    # Son of Zebedee
    if re.search(r"james.{0,30}son\s+of\s+zebedee", window):
        return ("James (son of Zebedee)", "high", "modifier: son of Zebedee")
    if re.search(r"santiago.{0,30}hijo\s+de\s+zebedeo", window):
        return ("James (son of Zebedee)", "high", "modifier: hijo de Zebedeo (ES)")
    # "James and John" as apostolic pair
    if re.search(r"james\s+and\s+john(?!\s+the\s+baptist)", window):
        return ("James (son of Zebedee)", "high", "paired with John (apostolic pair)")
    if re.search(r"santiago\s+y\s+juan(?!\s+(?:el\s+)?bautista)", window):
        return ("James (son of Zebedee)", "high", "paired with Juan (apostolic pair, ES)")

    # Son of Alphaeus
    if re.search(r"james.{0,30}son\s+of\s+alphaeus", window):
        return ("James (son of Alphaeus)", "high", "modifier: son of Alphaeus")
    if re.search(r"santiago.{0,30}hijo\s+de\s+alfeo", window):
        return ("James (son of Alphaeus)", "high", "modifier: hijo de Alfeo (ES)")

    # Brother of the Lord
    if re.search(r"james.{0,30}brother\s+of\s+(?:the\s+)?lord", window):
        return ("James (brother of Jesus)", "high", "modifier: brother of the Lord")
    if re.search(r"santiago.{0,30}hermano\s+del?\s+señor", window):
        return ("James (brother of Jesus)", "high", "modifier: hermano del Señor (ES)")

    # Epistle of James / Santiago -- likely the brother of Jesus
    src = _src(source)
    if "/james/" in src or "/santiago/" in src:
        return ("James (brother of Jesus)", "medium",
                "source file: epistle of James/Santiago")

    return None


def _rules_mary(window: str, source: str) -> tuple[str, str, str] | None:
    # Mary Magdalene
    if re.search(r"mary\s+magdalen[ea]?", window):
        return ("Mary Magdalene", "high", "modifier: Magdalene/Magdalena")
    if re.search(r"mar[ií]a\s+magdalena", window):
        return ("Mary Magdalene", "high", "modifier: Magdalena (ES)")
    if re.search(r"mary.{0,40}(?:of\s+)?magdala", window):
        return ("Mary Magdalene", "high", "modifier: of Magdala")

    # Mary wife of Cleophas
    if re.search(r"mary.{0,30}wife\s+of\s+cleophas", window):
        return ("Mary (wife of Cleophas)", "high", "modifier: wife of Cleophas")
    if re.search(r"mar[ií]a.{0,30}(?:mujer|esposa)\s+de\s+cleofas", window):
        return ("Mary (wife of Cleophas)", "high", "modifier: mujer de Cleofas (ES)")

    # Mary sister of Martha / Mary of Bethany
    if re.search(r"mary.{0,30}sister\s+of\s+martha", window):
        return ("Mary (sister of Martha)", "high", "modifier: sister of Martha")
    if re.search(r"mar[ií]a.{0,30}hermana\s+de\s+marta", window):
        return ("Mary (sister of Martha)", "high", "modifier: hermana de Marta (ES)")
    if re.search(r"mary.{0,40}bethany", window):
        return ("Mary (sister of Martha)", "high", "location: Bethany")
    if re.search(r"mar[ií]a.{0,40}betania", window):
        return ("Mary (sister of Martha)", "high", "location: Betania (ES)")
    # Martha paired
    if re.search(r"(?:martha\s+and\s+mary|mary\s+and\s+martha)", window):
        return ("Mary (sister of Martha)", "high", "paired with Martha")
    if re.search(r"(?:marta\s+y\s+mar[ií]a|mar[ií]a\s+y\s+marta)", window):
        return ("Mary (sister of Martha)", "high", "paired with Marta (ES)")

    # Mary mother of Jesus
    if re.search(r"mary.{0,30}mother\s+of\s+(?:jesus|the\s+lord)", window):
        return ("Mary (mother of Jesus)", "high", "modifier: mother of Jesus")
    if re.search(r"mar[ií]a.{0,30}madre\s+de\s+jes[uú]s", window):
        return ("Mary (mother of Jesus)", "high", "modifier: madre de Jesus (ES)")
    if re.search(r"virgin\s+mary", window):
        return ("Mary (mother of Jesus)", "high", "modifier: Virgin Mary")
    if re.search(r"virgen\s+mar[ií]a", window):
        return ("Mary (mother of Jesus)", "high", "modifier: Virgen Maria (ES)")
    # Nativity context
    if re.search(r"mary.{0,60}(?:joseph.{0,40}(?:birth|born|manger|nazareth|bel[eé]n|pesebre"
                 r"|naci[oó])|conceived\s+of\s+the\s+holy)", window):
        return ("Mary (mother of Jesus)", "high",
                "contextual: nativity (Joseph + birth/manger/Nazareth)")
    if re.search(r"(?:joseph|jos[eé]).{0,40}(?:mary|mar[ií]a).{0,40}"
                 r"(?:birth|born|child|ni[nñ]o|bel[eé]n|nazaret)", window):
        return ("Mary (mother of Jesus)", "medium",
                "contextual: Joseph + Mary + birth context")

    return None


def _rules_john(window: str, source: str) -> tuple[str, str, str] | None:
    # John the Baptist
    if re.search(r"john\s+the\s+baptist", window):
        return ("John the Baptist", "high", "modifier: the Baptist")
    if re.search(r"juan\s+el\s+bautista", window):
        return ("John the Baptist", "high", "modifier: el Bautista (ES)")
    if re.search(r"john.{0,60}(?:baptiz|wilderness|wild\s+honey|locusts"
                 r"|beheaded|herod|jordan)", window):
        return ("John the Baptist", "high",
                "contextual: baptize/wilderness/beheaded/Jordan")
    if re.search(r"juan.{0,60}(?:bautiz|desierto|miel\s+silvestre|langostas"
                 r"|decapitad|herodes|jord[aá]n)", window):
        return ("John the Baptist", "high",
                "contextual: bautizar/desierto/decapitado/Jordan (ES)")

    # John the Beloved / Revelator
    if re.search(r"john.{0,30}(?:beloved|revelator)", window):
        return ("John the Beloved", "high", "modifier: beloved/revelator")
    if re.search(r"juan.{0,30}(?:amado|revelador)", window):
        return ("John the Beloved", "high", "modifier: amado/revelador (ES)")
    if re.search(r"john.{0,60}revelation", window):
        return ("John the Beloved", "high", "contextual: Revelation")
    if re.search(r"juan.{0,60}apocalipsis", window):
        return ("John the Beloved", "high", "contextual: Apocalipsis (ES)")
    # "Peter and John" or "John and Peter" -- apostolic pair
    if re.search(r"(?:peter\s+and\s+john|john\s+and\s+peter)", window):
        return ("John the Beloved", "high", "paired with Peter (apostolic pair)")
    if re.search(r"(?:pedro\s+y\s+juan|juan\s+y\s+pedro)", window):
        return ("John the Beloved", "high", "paired with Pedro (apostolic pair, ES)")

    # Source file: Gospel of John, Epistles of John, Revelation
    src = _src(source)
    if re.search(r"/(?:john|juan)/(?!the.baptist)", src):
        return ("John the Beloved", "medium",
                "source file: Gospel/Epistles of John")
    if re.search(r"/(?:revelation|apocalipsis)/", src):
        return ("John the Beloved", "medium",
                "source file: Revelation/Apocalipsis")

    return None


def _rules_joseph(window: str, source: str) -> tuple[str, str, str] | None:
    # Joseph Smith
    if re.search(r"joseph\s+smith", window):
        return ("Joseph Smith", "high", "modifier: Smith")
    if re.search(r"jos[eé]\s+smith", window):
        return ("Joseph Smith", "high", "modifier: Smith (ES)")
    if re.search(r"(?:the\s+)?prophet\s+joseph", window):
        return ("Joseph Smith", "high", "modifier: Prophet Joseph")
    if re.search(r"(?:el\s+)?profeta\s+jos[eé]", window):
        return ("Joseph Smith", "high", "modifier: Profeta Jose (ES)")

    # Joseph of Arimathea
    if re.search(r"joseph\s+of\s+arimathea", window):
        return ("Joseph of Arimathea", "high", "modifier: of Arimathea")
    if re.search(r"jos[eé]\s+de\s+arimatea", window):
        return ("Joseph of Arimathea", "high", "modifier: de Arimatea (ES)")

    # Joseph husband of Mary (NT)
    if re.search(r"joseph.{0,40}(?:husband\s+of\s+mary|mary.{0,20}(?:nazareth|bel[eé]n"
                 r"|manger|pesebre|birth|naci))", window):
        return ("Joseph (husband of Mary)", "high",
                "contextual: husband of Mary / nativity")
    if re.search(r"jos[eé].{0,40}(?:esposo\s+de\s+mar[ií]a|mar[ií]a.{0,20}"
                 r"(?:nazaret|bel[eé]n|pesebre|naci))", window):
        return ("Joseph (husband of Mary)", "high",
                "contextual: esposo de Maria / natividad (ES)")

    # Joseph son of Jacob (OT) -- sold into Egypt
    if re.search(r"joseph.{0,60}(?:egypt|sold|dream|pharaoh|coat.{0,15}colours"
                 r"|potiphar|prison)", window):
        return ("Joseph (son of Jacob)", "high",
                "contextual: Egypt/sold/dreams/Pharaoh")
    if re.search(r"jos[eé].{0,60}(?:egipto|vendid|sue[nñ]o|fara[oó]n"
                 r"|t[uú]nica|potifar|c[aá]rcel|prisi[oó]n)", window):
        return ("Joseph (son of Jacob)", "high",
                "contextual: Egipto/vendido/suenos/Faraon (ES)")

    return None


def _rules_nephi(window: str, source: str) -> tuple[str, str, str] | None:
    src = _src(source)

    # 1 Nephi / 2 Nephi -> son of Lehi
    if re.search(r"/(?:1|2)-?nephi/", src) or re.search(r"/(?:1|2)-?nefi/", src):
        return ("Nephi (son of Lehi)", "high",
                "source file: 1-Nephi or 2-Nephi")

    # Helaman -> son of Helaman
    if "/helaman/" in src or "/helaman/" in src:
        return ("Nephi (son of Helaman)", "high",
                "source file: Helaman")

    # 3 Nephi -> could be Nephi son of Helaman or Nephi the disciple
    if re.search(r"/3-?nephi/", src) or re.search(r"/3-?nefi/", src):
        return ("Nephi (disciple)", "medium",
                "source file: 3-Nephi (likely the disciple of Christ)")

    # 4 Nephi -> Nephi the disciple
    if re.search(r"/4-?nephi/", src) or re.search(r"/4-?nefi/", src):
        return ("Nephi (disciple)", "medium",
                "source file: 4-Nephi")

    # Textual modifiers
    if re.search(r"nephi.{0,30}son\s+of\s+lehi", window):
        return ("Nephi (son of Lehi)", "high", "modifier: son of Lehi")
    if re.search(r"nefi.{0,30}hijo\s+de\s+leh[ií]", window):
        return ("Nephi (son of Lehi)", "high", "modifier: hijo de Lehi (ES)")
    if re.search(r"nephi.{0,30}son\s+of\s+helaman", window):
        return ("Nephi (son of Helaman)", "high", "modifier: son of Helaman")
    if re.search(r"nefi.{0,30}hijo\s+de\s+helam[aá]n", window):
        return ("Nephi (son of Helaman)", "high", "modifier: hijo de Helaman (ES)")

    return None


def _rules_alma(window: str, source: str) -> tuple[str, str, str] | None:
    src = _src(source)

    # Textual modifiers (check first -- they override source-file heuristics)
    if re.search(r"alma\s+(?:the\s+)?elder", window):
        return ("Alma the Elder", "high", "modifier: the Elder")
    if re.search(r"alma\s+padre", window):
        return ("Alma the Elder", "high", "modifier: padre (ES)")
    if re.search(r"alma\s+(?:the\s+)?younger", window):
        return ("Alma the Younger", "high", "modifier: the Younger")
    if re.search(r"alma\s+hijo", window):
        return ("Alma the Younger", "high", "modifier: hijo (ES)")

    # "baptize at the waters of Mormon" -> Alma the Elder
    if re.search(r"alma.{0,80}(?:waters?\s+of\s+mormon|aguas?\s+de\s+morm[oó]n"
                 r"|baptiz.{0,20}(?:helam|mormon))", window):
        return ("Alma the Elder", "high",
                "contextual: waters of Mormon / baptism at Helam")

    # Source-file: Mosiah -> Alma the Elder (his conversion story)
    if "/mosiah/" in src or "/mosíah/" in src or "/mosiah/" in src:
        return ("Alma the Elder", "high",
                "source file: Mosiah (Alma the Elder narrative)")

    # Source-file: Alma chapters
    ch = _chapter_num(source)
    if "/alma/" in src and ch is not None:
        if ch <= 16:
            # Chapters 1-16 cover both Alma as chief judge (Younger) and
            # references to his father.  Low confidence.
            return ("Alma the Younger", "low",
                    f"source file: Alma chapter {ch} (ambiguous zone, defaulting to Younger)")
        else:
            return ("Alma the Younger", "high",
                    f"source file: Alma chapter {ch} (mission/war narratives)")

    if "/alma/" in src:
        # Alma book but no chapter number extractable
        return ("Alma the Younger", "medium",
                "source file: book of Alma (likely the Younger)")

    return None


def _rules_moroni(window: str, source: str) -> tuple[str, str, str] | None:
    src = _src(source)

    # Captain Moroni
    if re.search(r"captain\s+moroni", window):
        return ("Captain Moroni", "high", "modifier: Captain")
    if re.search(r"capit[aá]n\s+moroni", window):
        return ("Captain Moroni", "high", "modifier: Capitan (ES)")
    if re.search(r"moroni.{0,60}(?:title\s+of\s+liberty|t[ií]tulo\s+de\s+(?:la\s+)?libertad"
                 r"|standard|estandarte)", window):
        return ("Captain Moroni", "high",
                "contextual: title of liberty / standard")

    # Source-file: Alma war chapters (43-63)
    ch = _chapter_num(source)
    if "/alma/" in src and ch is not None and 43 <= ch <= 63:
        return ("Captain Moroni", "high",
                f"source file: Alma chapter {ch} (war chapters)")

    # Angel Moroni / latter-day context
    if re.search(r"(?:angel|[aá]ngel)\s+moroni", window):
        return ("Moroni (son of Mormon)", "high",
                "modifier: angel Moroni")
    if re.search(r"moroni.{0,60}(?:appeared?\s+to\s+joseph|apareci[oó].{0,20}jos[eé]"
                 r"|gold\s*en?\s+plates?|planchas|hill\s+cumorah|cerro\s+cumorah)", window):
        return ("Moroni (son of Mormon)", "high",
                "contextual: appeared to Joseph / golden plates / Cumorah")

    # Source-file: book of Moroni or Mormon 8+
    if re.search(r"/moroni/", src) or re.search(r"/moron[ií]/", src):
        return ("Moroni (son of Mormon)", "high",
                "source file: book of Moroni")
    if "/mormon/" in src or "/mormón/" in src or "/mormon/" in src:
        if ch is not None and ch >= 8:
            return ("Moroni (son of Mormon)", "high",
                    f"source file: Mormon chapter {ch} (Moroni writing)")

    return None


# ---------------------------------------------------------------------------
# Level 1 additions: alternate names for the same person
# ---------------------------------------------------------------------------

def _rules_peter(window: str, source: str) -> tuple[str, str, str] | None:
    """Peter / Cephas / Simon Peter — all the same apostle."""
    # "Simon called Peter" or "Simon Peter"
    if re.search(r"simon\s+(?:called\s+)?peter", window):
        return ("Peter", "high", "modifier: Simon Peter")
    if re.search(r"sim[oó]n\s+(?:llamado\s+)?pedro", window):
        return ("Peter", "high", "modifier: Simón Pedro (ES)")

    # Cephas is always Peter
    if re.search(r"cephas|cefas", window):
        return ("Peter", "high", "alias: Cephas/Cefas = Peter")

    # "Peter" alone in apostolic context
    if re.search(r"peter.{0,60}(?:apostle|keys?|denied|denied\s+three|rock"
                 r"|feed\s+my\s+sheep|transfigur)", window):
        return ("Peter", "high", "contextual: apostolic role")
    if re.search(r"pedro.{0,60}(?:ap[oó]stol|llaves?|neg[oó]|roca"
                 r"|apacienta\s+mis\s+ovejas|transfigur)", window):
        return ("Peter", "high", "contextual: apostolic role (ES)")

    # Source: epistles of Peter
    src = _src(source)
    if re.search(r"/(?:1|2)-?peter/", src) or re.search(r"/(?:1|2)-?pedro/", src):
        return ("Peter", "medium", "source file: epistles of Peter")

    return None


def _rules_matthew(window: str, source: str) -> tuple[str, str, str] | None:
    """Matthew / Levi — the apostle and tax collector."""
    # "Matthew the publican" or "Matthew called Levi"
    if re.search(r"matthew.{0,30}(?:publican|tax|custom)", window):
        return ("Matthew (Apostle)", "high", "modifier: publican/tax collector")
    if re.search(r"mateo.{0,30}(?:publicano|impuestos|aduana)", window):
        return ("Matthew (Apostle)", "high", "modifier: publicano (ES)")

    # Source: Gospel of Matthew
    src = _src(source)
    if re.search(r"/matthew/", src) or re.search(r"/mateo/", src):
        return ("Matthew (Apostle)", "medium", "source file: Gospel of Matthew")

    return None


def _rules_levi(window: str, source: str) -> tuple[str, str, str] | None:
    """Levi — could be Levi son of Jacob (OT patriarch) or Matthew/Levi (NT)."""
    src = _src(source)

    # NT context: "Levi sitting at the receipt of custom" = Matthew
    if re.search(r"levi.{0,60}(?:receipt\s+of\s+custom|tax|publican|follow\s+me"
                 r"|sitting\s+at\s+the)", window):
        return ("Matthew (Apostle)", "high",
                "contextual: Levi the tax collector = Matthew")
    if re.search(r"lev[ií].{0,60}(?:cobro\s+de\s+impuestos|publicano|s[ií]gueme"
                 r"|sentado\s+(?:en|al))", window):
        return ("Matthew (Apostle)", "high",
                "contextual: Leví el publicano = Mateo (ES)")

    # Source in Mark/Luke calling narrative
    if re.search(r"/(?:mark|marcos)/(?:2|2\.txt)", src):
        return ("Matthew (Apostle)", "medium",
                "source file: Mark 2 (Levi's calling)")
    if re.search(r"/(?:luke|lucas)/(?:5|5\.txt)", src):
        return ("Matthew (Apostle)", "medium",
                "source file: Luke 5 (Levi's calling)")

    # OT: Levi son of Jacob — tribe patriarch
    if re.search(r"levi.{0,60}(?:son\s+of\s+jacob|simeon\s+and\s+levi"
                 r"|tribe|priesthood|levit)", window):
        return ("Levi (son of Jacob)", "high",
                "contextual: OT patriarch / tribal context")
    if re.search(r"lev[ií].{0,60}(?:hijo\s+de\s+jacob|sime[oó]n\s+y\s+lev[ií]"
                 r"|tribu|sacerdocio|levit)", window):
        return ("Levi (son of Jacob)", "high",
                "contextual: patriarca AT / tribu (ES)")

    # Source: Genesis, Exodus, Numbers, Deuteronomy
    if re.search(r"/(?:genesis|g[eé]nesis|exodus|[eé]xodo|numbers|n[uú]meros"
                 r"|deuteronomy|deuteronomio)/", src):
        return ("Levi (son of Jacob)", "medium",
                "source file: Pentateuch (OT Levi)")

    return None


def _rules_saul(window: str, source: str) -> tuple[str, str, str] | None:
    """Saul — King Saul (OT) or Saul of Tarsus / Paul (NT)."""
    src = _src(source)

    # "Saul of Tarsus" or "Saul who is also called Paul"
    if re.search(r"saul.{0,30}(?:of\s+tarsus|tarsus|also\s+called\s+paul)", window):
        return ("Paul the Apostle", "high", "modifier: Saul of Tarsus = Paul")
    if re.search(r"saulo.{0,30}(?:de\s+tarso|tarso|tambi[eé]n\s+llamado\s+pablo)", window):
        return ("Paul the Apostle", "high", "modifier: Saulo de Tarso = Pablo (ES)")

    # Damascus road, Ananias vision — Saul/Paul
    if re.search(r"saul.{0,80}(?:damascus|damas[ck]o|ananias|anan[ií]as"
                 r"|scales?.{0,10}eyes?|persecuti|perse[cg]u)", window):
        return ("Paul the Apostle", "high",
                "contextual: Damascus/Ananias/persecution (Saul→Paul)")

    # Source: Acts (after chapter 7), any epistle
    if re.search(r"/(?:acts|hechos)/", src):
        ch = _chapter_num(source)
        if ch is not None and ch >= 7:
            return ("Paul the Apostle", "high",
                    f"source file: Acts {ch} (Saul of Tarsus)")

    # OT King Saul context
    if re.search(r"saul.{0,60}(?:king|reign|jonathan|david.{0,30}spear"
                 r"|philistin|gilboa|samuel.{0,30}anoint)", window):
        return ("King Saul", "high", "contextual: OT king narrative")
    if re.search(r"sa[uú]l.{0,60}(?:rey|rein[oó]|jonat[aá]n|david.{0,30}lanza"
                 r"|filisteo|gilboa|samuel.{0,30}ungi)", window):
        return ("King Saul", "high", "contextual: OT king narrative (ES)")

    # Source: 1 Samuel, 2 Samuel
    if re.search(r"/(?:1|2)-?samuel/", src):
        return ("King Saul", "medium", "source file: Samuel (OT)")

    return None


def _rules_paul(window: str, source: str) -> tuple[str, str, str] | None:
    """Paul — always the apostle (no ambiguity, but alias-canonicalizes)."""
    return ("Paul the Apostle", "high", "canonical: Paul the Apostle")


def _rules_jacob_patriarch(window: str, source: str) -> tuple[str, str, str] | None:
    """Jacob — patriarch (Israel), or Jacob son of Lehi (BofM), or Jacob son of
    Matthan (NT genealogy), or Jacobo (ES).  Handles Jacob/Israel identity."""
    src = _src(source)

    # BofM Jacob — son of Lehi
    if re.search(r"/(?:jacob|jacobo)/", src):
        return ("Jacob (son of Lehi)", "high", "source file: book of Jacob")
    if re.search(r"/(?:1|2)-?nephi/", src) or re.search(r"/(?:1|2)-?nefi/", src):
        return ("Jacob (son of Lehi)", "medium",
                "source file: 1-2 Nephi (likely son of Lehi)")

    # "Jacob/Israel" or "whose name was changed to Israel"
    if re.search(r"jacob.{0,30}(?:whose\s+name|called\s+israel|surnamed\s+israel"
                 r"|who\s+is\s+israel)", window):
        return ("Jacob (patriarch/Israel)", "high",
                "modifier: name changed to Israel")
    if re.search(r"jacob.{0,30}(?:cuyo\s+nombre|llamado\s+israel"
                 r"|que\s+es\s+israel)", window):
        return ("Jacob (patriarch/Israel)", "high",
                "modifier: nombre cambiado a Israel (ES)")

    # Twelve sons, Esau, Laban (OT)
    if re.search(r"jacob.{0,80}(?:esau|esa[uú]|laban|lab[aá]n|twelve\s+(?:sons|tribes)"
                 r"|doce\s+(?:hijos|tribus)|birthright|primogenitura"
                 r"|rachel|raquel|leah|lea\b|rebekah|rebeca)", window):
        return ("Jacob (patriarch/Israel)", "high",
                "contextual: patriarchal narrative (Esau/Laban/Rachel/tribes)")

    # Source: Genesis
    if re.search(r"/(?:genesis|g[eé]nesis)/", src):
        return ("Jacob (patriarch/Israel)", "medium",
                "source file: Genesis")

    return None


# ---------------------------------------------------------------------------
# Level 2: entity-type disambiguation (same name → different entity types)
# ---------------------------------------------------------------------------

def _rules_judah(window: str, source: str) -> tuple[str, str, str, str | None] | None:
    """Judah / Judá — patriarch (person), tribe (people), kingdom (polity),
    territory (place).

    Bilingual mapping:
    - EN: "Judah" covers all four.  KJV also uses "Judas" for the patriarch
      in NT genealogies (Matt 1:2-3).
    - ES: "Judá" covers patriarch/tribe/kingdom/territory.
      "Judas" is reserved for NT individuals (Iscariot, etc.).
    """
    src = _src(source)
    ch = _chapter_num(source)

    # --- Person: Judah the patriarch (son of Jacob) ---
    if re.search(r"jud(?:ah|á).{0,60}(?:son\s+of\s+jacob|hijo\s+de\s+jacob"
                 r"|tamar|thamar|er\s+and\s+onan|shechem|siquem"
                 r"|perez|fares|zerah|zara)", window):
        return ("Judah (patriarch)", "high",
                "contextual: son of Jacob / Tamar / Er & Onan", "person")

    # NT genealogy: "Judas" in Matt 1:2-3 = the patriarch (KJV English quirk)
    if re.search(r"/(?:matthew|mateo)/", src) and ch is not None and ch <= 2:
        if re.search(r"jud(?:as|ah|á).{0,40}(?:begat|beg[eo]t|engendr[oó]"
                     r"|phares|fares|thamar|tamar)", window):
            return ("Judah (patriarch)", "high",
                    "contextual: genealogy of Jesus (Matt 1)", "person")

    # Luke genealogy
    if re.search(r"/(?:luke|lucas)/", src) and ch is not None and ch == 3:
        if re.search(r"jud(?:as|ah|á)", window):
            return ("Judah (patriarch)", "medium",
                    "contextual: genealogy (Luke 3)", "person")

    # Genesis source + patriarch context
    if re.search(r"/(?:genesis|g[eé]nesis)/", src):
        if ch is not None and 37 <= ch <= 50:
            return ("Judah (patriarch)", "high",
                    f"source file: Genesis {ch} (Joseph/Judah narrative)", "person")
        if ch is not None and ch <= 36:
            return ("Judah (patriarch)", "medium",
                    f"source file: Genesis {ch}", "person")

    # --- Place: territory / land of Judah ---
    if re.search(r"(?:land|territory|wilderness|desert|hills?|mountains?)\s+of\s+jud(?:ah|á"
                 r"|ea)", window):
        return ("Judah (territory)", "high",
                "modifier: land/territory/wilderness of Judah", "place")
    if re.search(r"(?:tierra|territorio|desierto|montes?|monta[nñ]as?)\s+de\s+jud[aá]", window):
        return ("Judah (territory)", "high",
                "modifier: tierra/desierto de Judá (ES)", "place")
    if re.search(r"(?:bethlehem|bel[eé]n).{0,30}(?:of\s+)?jud(?:ah|á)", window):
        return ("Judah (territory)", "high",
                "contextual: Bethlehem of Judah (geographic)", "place")

    # --- Polity: Kingdom of Judah ---
    if re.search(r"(?:kingdom|king(?:s)?\s+of)\s+jud(?:ah|á)", window):
        return ("Judah (kingdom)", "high",
                "modifier: kingdom/kings of Judah", "polity")
    if re.search(r"(?:reino|rey(?:es)?\s+de)\s+jud[aá]", window):
        return ("Judah (kingdom)", "high",
                "modifier: reino/reyes de Judá (ES)", "polity")
    if re.search(r"jud(?:ah|á).{0,60}(?:rehoboam|robo[aá]m|hezekiah|ezequ[ií]as"
                 r"|josiah|jos[ií]as|captiv|cautiv|babylon|babilon"
                 r"|assyria|asiria|divided\s+kingdom|reino\s+dividido)", window):
        return ("Judah (kingdom)", "high",
                "contextual: monarchy/exile narrative", "polity")

    # --- People: Tribe of Judah ---
    if re.search(r"tribe\s+of\s+jud(?:ah|á)", window):
        return ("Judah (tribe)", "high", "modifier: tribe of Judah", "people")
    if re.search(r"tribu\s+de\s+jud[aá]", window):
        return ("Judah (tribe)", "high", "modifier: tribu de Judá (ES)", "people")
    if re.search(r"jud(?:ah|á).{0,40}(?:lion|le[oó]n|scepter|cetro)", window):
        return ("Judah (tribe)", "high",
                "contextual: lion/scepter of Judah (tribal blessing)", "people")

    # Source: prophets (Isaiah, Jeremiah, etc.) — usually the kingdom
    if re.search(r"/(?:isaiah|isa[ií]as|jeremiah|jerem[ií]as|ezekiel|ezequiel"
                 r"|hosea|oseas|amos|am[oó]s|micah|miqueas)/", src):
        return ("Judah (kingdom)", "medium",
                "source file: prophetic book (likely kingdom context)", "polity")

    return None


def _rules_israel_entity(window: str, source: str) -> tuple[str, str, str, str | None] | None:
    """Israel — person (patriarch Jacob), nation (people), covenant concept,
    land / place, scattered remnant."""
    src = _src(source)

    # --- Person: Jacob renamed Israel ---
    if re.search(r"israel.{0,40}(?:who\s+(?:is|was)\s+jacob|formerly\s+jacob"
                 r"|whose\s+name\s+was\s+jacob)", window):
        return ("Jacob (patriarch/Israel)", "high",
                "modifier: Israel = Jacob", "person")
    if re.search(r"israel.{0,40}(?:que\s+(?:es|era)\s+jacob|antes\s+jacob"
                 r"|cuyo\s+nombre\s+era\s+jacob)", window):
        return ("Jacob (patriarch/Israel)", "high",
                "modifier: Israel = Jacob (ES)", "person")

    # "sons of Israel" / "children of Israel" = the people
    if re.search(r"(?:children|sons|people|house|congregation)\s+of\s+israel", window):
        return ("Israel (nation)", "high",
                "modifier: children/house of Israel", "people")
    if re.search(r"(?:hijos|pueblo|casa|congregaci[oó]n)\s+de\s+israel", window):
        return ("Israel (nation)", "high",
                "modifier: hijos/pueblo/casa de Israel (ES)", "people")

    # "land of Israel"
    if re.search(r"(?:land|territory)\s+of\s+israel", window):
        return ("Israel (land)", "high",
                "modifier: land of Israel", "place")
    if re.search(r"(?:tierra|territorio)\s+de\s+israel", window):
        return ("Israel (land)", "high",
                "modifier: tierra de Israel (ES)", "place")

    # Gathering / scattering language = covenant people / remnant
    if re.search(r"(?:gather(?:ing)?|scatter(?:ed|ing)?|remnant|lost\s+(?:tribes?"
                 r"|ten))\s+(?:of\s+)?israel", window):
        return ("Israel (covenant people)", "high",
                "contextual: gathering/scattering/remnant", "concept")
    if re.search(r"(?:recog(?:er|idos?)|esparci(?:dos?|miento)|remanente"
                 r"|(?:tribus?\s+)?perdidas?)\s+(?:de\s+)?israel", window):
        return ("Israel (covenant people)", "high",
                "contextual: recogimiento/esparcimiento/remanente (ES)", "concept")

    # Kingdom: "kingdom of Israel" or "king of Israel"
    if re.search(r"(?:kingdom|king(?:s)?)\s+of\s+israel", window):
        return ("Israel (kingdom)", "high",
                "modifier: kingdom/king of Israel", "polity")
    if re.search(r"(?:reino|rey(?:es)?)\s+de\s+israel", window):
        return ("Israel (kingdom)", "high",
                "modifier: reino/rey de Israel (ES)", "polity")

    # BofM context: almost always covenant people
    if re.search(r"/(?:book-of-mormon|libro-de-morm[oó]n|1-nephi|2-nephi|jacob"
                 r"|enos|jarom|omni|mosiah|alma|helaman|3-nephi|4-nephi"
                 r"|mormon|ether|moroni)/", src):
        return ("Israel (covenant people)", "medium",
                "source file: Book of Mormon (covenant Israel)", "concept")

    # D&C / Restoration: covenant people
    if re.search(r"/(?:doctrine-and-covenants|d&c|d-and-c"
                 r"|doctrina-y-convenios)/", src):
        return ("Israel (covenant people)", "medium",
                "source file: D&C (covenant/gathering context)", "concept")

    return None


def _rules_bethlehem(window: str, source: str) -> tuple[str, str, str, str | None] | None:
    """Bethlehem / Belén — two distinct places:
    - Bethlehem of Judah (Ephratah): David's city, birthplace of Jesus
    - Bethlehem of Zebulun: in Galilee, associated with Ibzan (Judges 12:8-10)
    """
    src = _src(source)
    ch = _chapter_num(source)

    # Bethlehem-Ephratah / Bethlehem Judah — explicit
    if re.search(r"bethlehem.{0,20}(?:ephrat|judah|jud[aá])", window):
        return ("Bethlehem (Judah)", "high",
                "modifier: Bethlehem-Ephratah/Judah", "place")
    if re.search(r"bel[eé]n.{0,20}(?:efrat|jud[aá])", window):
        return ("Bethlehem (Judah)", "high",
                "modifier: Belén de Efrata/Judá (ES)", "place")

    # Micah 5:2 / nativity / David context → Bethlehem of Judah
    if re.search(r"bethlehem.{0,60}(?:david|ruler|governor|born|birth|manger|star"
                 r"|jesus|christ|messiah|shepherd)", window):
        return ("Bethlehem (Judah)", "high",
                "contextual: nativity/David/messianic", "place")
    if re.search(r"bel[eé]n.{0,60}(?:david|gobernante|naci|pesebre|estrella"
                 r"|jes[uú]s|cristo|mes[ií]as|pastor)", window):
        return ("Bethlehem (Judah)", "high",
                "contextual: natividad/David/mesiánico (ES)", "place")

    # Judges 12 — Ibzan of Bethlehem (Zebulun)
    if re.search(r"/(?:judges|jueces)/", src) and ch is not None and 10 <= ch <= 12:
        if re.search(r"(?:ibzan|ibz[aá]n)", window):
            return ("Bethlehem (Zebulun)", "high",
                    "contextual: Ibzan (Judges 12), Bethlehem in Galilee", "place")

    # Default for most scriptural mentions: Bethlehem of Judah
    return ("Bethlehem (Judah)", "low",
            "default: most scriptural references are Bethlehem of Judah", "place")


# ---------------------------------------------------------------------------
# Level 3: temporal/dispensational meaning shifts
# ---------------------------------------------------------------------------

def _rules_gentiles(window: str, source: str) -> tuple[str, str, str, str | None] | None:
    """Gentiles / gentiles — meaning shifts across dispensations:
    - Abrahamic: non-Hebrews
    - Mosaic: non-Israelites
    - Post-exile: non-Jews
    - Restoration: non-members of the Church
    - BofM 1 Nephi 13: European peoples / descendants of Japheth
    """
    src = _src(source)
    ch = _chapter_num(source)

    # BofM: 1 Nephi 13-14 — European peoples / Columbus / promised land
    if re.search(r"/(?:1-nephi|1-nefi)/", src) and ch is not None and 13 <= ch <= 22:
        return ("Gentiles (European peoples)", "high",
                f"source: 1 Nephi {ch} — Nephite prophecy of European colonizers",
                "people")

    # BofM: 3 Nephi — Jesus to Nephites about gentiles = future non-covenant peoples
    if re.search(r"/(?:3-nephi|3-nefi)/", src):
        return ("Gentiles (non-covenant peoples)", "medium",
                "source: 3 Nephi — Jesus' Nephite discourse", "people")

    # BofM general: gentiles in BofM usually means non-covenant / future nations
    if re.search(r"/(?:2-nephi|2-nefi|jacob|jacobo|mormon|morm[oó]n|ether|[eé]ter)/", src):
        return ("Gentiles (non-covenant peoples)", "medium",
                "source: Book of Mormon — prophetic/covenant context", "people")

    # D&C / Restoration: non-members
    if re.search(r"/(?:doctrine-and-covenants|d&c|d-and-c"
                 r"|doctrina-y-convenios)/", src):
        return ("Gentiles (non-members)", "medium",
                "source: D&C — Restoration context", "people")

    # Modern conference: usually non-covenant
    if re.search(r"/general-conference/", src):
        return ("Gentiles (non-covenant peoples)", "low",
                "source: general conference — modern usage", "people")

    # OT: Pentateuch / patriarchal era = non-Hebrews / non-Israelites
    if re.search(r"/(?:genesis|g[eé]nesis|exodus|[eé]xodo|leviticus|lev[ií]tico"
                 r"|numbers|n[uú]meros|deuteronomy|deuteronomio)/", src):
        return ("Gentiles (non-Israelites)", "medium",
                "source: Pentateuch — Mosaic-era usage", "people")

    # OT prophets: usually nations surrounding Judah/Israel = non-Jews
    if re.search(r"/(?:isaiah|isa[ií]as|jeremiah|jerem[ií]as|ezekiel|ezequiel"
                 r"|daniel)/", src):
        return ("Gentiles (non-Jews)", "medium",
                "source: prophetic books — post-monarchy/exile context", "people")

    # NT: non-Jews (standard NT meaning)
    if re.search(r"/(?:matthew|mateo|mark|marcos|luke|lucas|john|juan"
                 r"|acts|hechos|romans|romanos|galatians|g[aá]latas"
                 r"|ephesians|efesios|colossians|colosenses)/", src):
        return ("Gentiles (non-Jews)", "high",
                "source: New Testament — standard NT meaning", "people")

    # Explicit textual clues
    if re.search(r"gentil.{0,60}(?:nation|naci[oó]n|heathen|pagan|idol"
                 r"|[ií]dolo|uncircumcis|incircuncis)", window):
        return ("Gentiles (non-covenant peoples)", "medium",
                "contextual: nations/heathen/idolatry language", "people")

    return None


def _rules_zion(window: str, source: str) -> tuple[str, str, str, str | None] | None:
    """Zion / Sión — meaning shifts across eras:
    - City of David (Mount Zion in Jerusalem)
    - City of Enoch (Moses 7, PGP)
    - The pure in heart (D&C 97:21)
    - New Jerusalem / Independence, Missouri (D&C 57)
    - The Church / gathered saints (modern)
    """
    src = _src(source)

    # City of Enoch (Pearl of Great Price, Moses 7)
    if re.search(r"zi[oó]n.{0,60}(?:enoch|enoc|translated|trasladad"
                 r"|taken\s+up|city\s+of\s+holiness|ciudad\s+de\s+santidad)", window):
        return ("Zion (city of Enoch)", "high",
                "contextual: Enoch/translated/city of holiness", "concept")
    if re.search(r"/(?:moses|mois[eé]s|pearl-of-great-price|perla-de-gran-precio)/", src):
        if re.search(r"zi[oó]n", window):
            return ("Zion (city of Enoch)", "medium",
                    "source: Pearl of Great Price (Enoch context)", "concept")

    # D&C: "the pure in heart" or New Jerusalem
    if re.search(r"/(?:doctrine-and-covenants|d&c|d-and-c"
                 r"|doctrina-y-convenios)/", src):
        if re.search(r"zi[oó]n.{0,60}(?:pure\s+in\s+heart|puros?\s+de\s+coraz[oó]n)", window):
            return ("Zion (the pure in heart)", "high",
                    "contextual: D&C 97:21 — pure in heart", "concept")
        if re.search(r"zi[oó]n.{0,60}(?:new\s+jerusalem|nueva\s+jerusal[eé]n"
                     r"|independence|missouri|jackson\s+county|condado\s+de\s+jackson"
                     r"|center\s+place|lugar\s+central)", window):
            return ("Zion (New Jerusalem/Missouri)", "high",
                    "contextual: D&C — New Jerusalem/Missouri", "place")
        return ("Zion (the pure in heart)", "low",
                "source: D&C — default to pure-in-heart meaning", "concept")

    # Modern conference / manuals: usually the Church / gathered saints
    if re.search(r"/(?:general-conference|manuals)/", src):
        return ("Zion (the Church/gathered saints)", "low",
                "source: modern context — gathered saints", "concept")

    # OT: Mount Zion / City of David
    if re.search(r"(?:mount|monte?)\s+zi[oó]n", window):
        return ("Zion (Mount Zion/Jerusalem)", "high",
                "modifier: Mount Zion", "place")
    if re.search(r"zi[oó]n.{0,60}(?:david|jerusalem|jerusal[eé]n|temple|templo"
                 r"|stronghold|fortaleza)", window):
        return ("Zion (Mount Zion/Jerusalem)", "high",
                "contextual: David/Jerusalem/temple", "place")

    if re.search(r"/(?:psalms?|salmos?|isaiah|isa[ií]as|2-samuel|2-samuel"
                 r"|1-kings|1-reyes|2-kings|2-reyes)/", src):
        return ("Zion (Mount Zion/Jerusalem)", "medium",
                "source: OT (likely Mount Zion/Jerusalem)", "place")

    # BofM: usually covenant/gathering concept
    if re.search(r"/(?:book-of-mormon|1-nephi|2-nephi|3-nephi|jacob"
                 r"|ether|mormon|moroni)/", src):
        return ("Zion (the pure in heart)", "medium",
                "source: Book of Mormon — covenant Zion", "concept")

    return None


def _rules_priesthood(window: str, source: str) -> tuple[str, str, str, str | None] | None:
    """Priesthood — Melchizedek vs Aaronic, plus evolving administrative meaning."""
    # Melchizedek Priesthood
    if re.search(r"(?:melchizedek|melquisedec)\s*(?:priesthood|sacerdocio)", window):
        return ("Melchizedek Priesthood", "high",
                "modifier: Melchizedek/Melquisedec Priesthood", "concept")
    if re.search(r"(?:higher|mayor|holy)\s+(?:priesthood|sacerdocio"
                 r"|order|orden)", window):
        return ("Melchizedek Priesthood", "high",
                "modifier: higher/holy priesthood", "concept")

    # Aaronic Priesthood
    if re.search(r"(?:aaronic|aar[oó]nico)\s*(?:priesthood|sacerdocio)", window):
        return ("Aaronic Priesthood", "high",
                "modifier: Aaronic/Aarónico Priesthood", "concept")
    if re.search(r"(?:lesser|menor|levitical|lev[ií]tico)\s+(?:priesthood|sacerdocio"
                 r"|order|orden)", window):
        return ("Aaronic Priesthood", "high",
                "modifier: lesser/Levitical priesthood", "concept")

    # Contextual: D&C with John the Baptist → Aaronic
    if re.search(r"priesthood.{0,80}(?:john\s+the\s+baptist|juan\s+el\s+bautista"
                 r"|baptist\s+conferr|bautista\s+confir)", window):
        return ("Aaronic Priesthood", "high",
                "contextual: John the Baptist conferring priesthood", "concept")

    # Contextual: Peter, James, John → Melchizedek
    if re.search(r"priesthood.{0,80}(?:peter.{0,10}james.{0,10}john"
                 r"|pedro.{0,10}santiago.{0,10}juan)", window):
        return ("Melchizedek Priesthood", "high",
                "contextual: Peter, James, John conferring priesthood", "concept")

    return None


def _rules_temple(window: str, source: str) -> tuple[str, str, str, str | None] | None:
    """Temple — different structures across dispensations:
    - Tabernacle of Moses
    - Solomon's Temple (First Temple)
    - Zerubbabel / Herod's Temple (Second Temple)
    - Latter-day temples
    - Body as temple (spiritual metaphor)
    """
    src = _src(source)

    # Tabernacle of Moses (Level 3 — same concept, different era)
    if re.search(r"(?:tabernacle|tabern[aá]culo)\s+(?:of\s+(?:the\s+)?(?:congregation"
                 r"|meeting)|de\s+(?:la\s+)?(?:congregaci[oó]n|reuni[oó]n))", window):
        return ("Tabernacle of Moses", "high",
                "modifier: tabernacle of the congregation", "place")
    if re.search(r"temple.{0,40}(?:solomon|salom[oó]n)", window):
        return ("Solomon's Temple", "high", "modifier: Solomon's Temple", "place")
    if re.search(r"templo.{0,40}(?:salom[oó]n)", window):
        return ("Solomon's Temple", "high", "modifier: Templo de Salomón (ES)", "place")

    # Herod's temple / Second Temple
    if re.search(r"temple.{0,40}(?:herod|herodes|second|segundo)", window):
        return ("Herod's Temple", "high",
                "modifier: Herod's/Second Temple", "place")

    # Body as temple
    if re.search(r"(?:body|cuerpo).{0,30}(?:(?:is|as)\s+(?:a\s+)?temple"
                 r"|(?:es|como)\s+(?:un\s+)?templo)", window):
        return ("Temple (body/spiritual)", "high",
                "contextual: body as temple metaphor", "concept")
    if re.search(r"temple.{0,30}(?:of\s+(?:the\s+)?(?:holy\s+)?(?:ghost|spirit|god)"
                 r"|del?\s+(?:esp[ií]ritu\s+(?:santo)?|dios))", window):
        return ("Temple (body/spiritual)", "high",
                "contextual: temple of God/Holy Ghost", "concept")

    # Latter-day temples
    if re.search(r"temple.{0,60}(?:kirtland|nauvoo|salt\s+lake|manti|logan"
                 r"|st\.?\s*george|dedicat)", window):
        return ("Temple (latter-day)", "high",
                "contextual: specific LDS temple", "place")
    if re.search(r"templo.{0,60}(?:kirtland|nauvoo|salt\s+lake|manti|logan"
                 r"|san\s*jorge|dedica)", window):
        return ("Temple (latter-day)", "high",
                "contextual: templo SUD específico (ES)", "place")
    if re.search(r"/(?:doctrine-and-covenants|d&c|d-and-c"
                 r"|doctrina-y-convenios)/", src):
        return ("Temple (latter-day)", "medium",
                "source: D&C — likely latter-day temple", "place")

    return None


def _rules_ark(window: str, source: str) -> tuple[str, str, str, str | None] | None:
    """Ark — Noah's ark vs Ark of the Covenant."""
    # Ark of the Covenant
    if re.search(r"ark\s+of\s+(?:the\s+)?covenant", window):
        return ("Ark of the Covenant", "high",
                "modifier: Ark of the Covenant", "object")
    if re.search(r"arca\s+del?\s+(?:la\s+)?(?:convenio|alianza|pacto|testimonio)", window):
        return ("Ark of the Covenant", "high",
                "modifier: Arca del Convenio/Alianza (ES)", "object")

    # Ark of the Covenant contextual (mercy seat, cherubim, tabernacle)
    if re.search(r"ark.{0,60}(?:mercy\s+seat|cherub|tabernacle|tablets?"
                 r"|command|aaron|lev)", window):
        return ("Ark of the Covenant", "high",
                "contextual: mercy seat/cherubim/tabernacle", "object")

    # Noah's ark
    if re.search(r"(?:noah|no[eé]).{0,40}ark", window):
        return ("Noah's Ark", "high", "modifier: Noah's ark", "object")
    if re.search(r"arca.{0,40}(?:no[eé])", window):
        return ("Noah's Ark", "high", "modifier: Arca de Noé (ES)", "object")
    if re.search(r"ark.{0,60}(?:flood|water|rain|cubit|gopher\s+wood"
                 r"|animal|two\s+(?:of\s+)?every)", window):
        return ("Noah's Ark", "high", "contextual: flood/animals/cubits", "object")
    if re.search(r"arca.{0,60}(?:diluvio|agua|lluvia|codo|animales?|dos\s+de\s+cada)", window):
        return ("Noah's Ark", "high", "contextual: diluvio/animales (ES)", "object")

    return None


def _rules_jacobo(window: str, source: str) -> tuple[str, str, str] | None:
    """Jacobo (ES) = Santiago = James (EN).  In Spanish, "Jacobo" is a
    rendering of James (NT), NOT of Jacob the patriarch (who is "Jacob"
    in both languages).  Try James rules first; fall back to Jacob only
    if no James match and source is clearly OT/BofM."""
    result = _rules_james(window, source)
    if result is not None:
        return result
    # Rare fallback: "Jacobo" used loosely for Jacob patriarch in some ES texts
    src = _src(source)
    if re.search(r"/(?:genesis|g[eé]nesis)/", src):
        return _rules_jacob_patriarch(window, source)
    return None


def _rules_emma(window: str, source: str) -> tuple[str, str, str] | None:
    """Emma Smith / Emma Hale Smith — same person, maiden vs married name."""
    if re.search(r"emma\s+hale", window):
        return ("Emma Smith", "high", "alias: Emma Hale = Emma Smith (maiden name)")
    if re.search(r"emma\s+smith", window):
        return ("Emma Smith", "high", "modifier: Emma Smith")
    # "Emma" alone in D&C or Joseph Smith context
    src = _src(source)
    if re.search(r"/(?:doctrine-and-covenants|d&c|d-and-c|doctrina-y-convenios)/", src):
        return ("Emma Smith", "high", "source: D&C — Emma = Emma Smith")
    if re.search(r"emma.{0,60}(?:joseph|jos[eé]|prophet|profeta|wife|esposa"
                 r"|elect\s+lady|dama\s+elegida)", window):
        return ("Emma Smith", "high", "contextual: Joseph's wife / elect lady")
    return None


def _rules_law(window: str, source: str) -> tuple[str, str, str, str | None] | None:
    """Law — Law of Moses vs law of the gospel vs civil law."""
    src = _src(source)

    # Law of Moses
    if re.search(r"law\s+of\s+moses", window):
        return ("Law of Moses", "high", "modifier: Law of Moses", "concept")
    if re.search(r"ley\s+de\s+mois[eé]s", window):
        return ("Law of Moses", "high", "modifier: Ley de Moisés (ES)", "concept")

    # OT ritual/sacrifice context
    if re.search(r"(?:the\s+)?law.{0,40}(?:sacrifice|offering|burnt|clean"
                 r"|unclean|sabbath|circumcis)", window):
        return ("Law of Moses", "high",
                "contextual: ritual/sacrifice/sabbath", "concept")

    # Law of the gospel / higher law
    if re.search(r"(?:higher\s+)?law.{0,30}(?:gospel|evangeli|christ|cristo)", window):
        return ("Law of the Gospel", "high",
                "modifier: law of the gospel/Christ", "concept")
    if re.search(r"ley.{0,30}(?:evangelio|cristo|superior)", window):
        return ("Law of the Gospel", "high",
                "modifier: ley del evangelio/Cristo (ES)", "concept")

    return None


# ---------------------------------------------------------------------------
# Registry: maps lowered entity names to their rule function
# ---------------------------------------------------------------------------

_DISAMBIGUATION_RULES: dict[str, _RuleFn] = {
    # --- Level 1: person identity ---
    "judas": _rules_judas,
    "james": _rules_james,
    "santiago": _rules_james,      # ES alias
    # "jacobo" handled below (composite: James or Jacob patriarch)
    "mary": _rules_mary,
    "maría": _rules_mary,
    "maria": _rules_mary,          # without accent
    "john": _rules_john,
    "juan": _rules_john,           # ES alias
    "joseph": _rules_joseph,
    "josé": _rules_joseph,
    "jose": _rules_joseph,         # without accent
    "nephi": _rules_nephi,
    "nefi": _rules_nephi,          # ES alias
    "alma": _rules_alma,
    "moroni": _rules_moroni,
    "moroní": _rules_moroni,       # ES alias
    # Alternate-name aliases (same person, multiple names)
    "peter": _rules_peter,
    "pedro": _rules_peter,
    "cephas": _rules_peter,
    "cefas": _rules_peter,
    "simon peter": _rules_peter,
    "simón pedro": _rules_peter,
    "matthew": _rules_matthew,
    "mateo": _rules_matthew,
    "levi": _rules_levi,
    "leví": _rules_levi,
    "saul": _rules_saul,
    "saúl": _rules_saul,
    "saulo": _rules_saul,
    "paul": _rules_paul,
    "pablo": _rules_paul,
    "jacob": _rules_jacob_patriarch,
    "jacobo": _rules_jacobo,          # ES: Jacobo = James/Santiago; rare: Jacob patriarch
    "emma": _rules_emma,
    "emma smith": _rules_emma,
    "emma hale": _rules_emma,
    "emma hale smith": _rules_emma,
    # --- Level 2: entity-type disambiguation ---
    "judah": _rules_judah,
    "judá": _rules_judah,
    "bethlehem": _rules_bethlehem,
    "belén": _rules_bethlehem,
    "belen": _rules_bethlehem,     # without accent
    "israel": _rules_israel_entity,
    # --- Level 3: temporal/dispensational meaning ---
    "gentiles": _rules_gentiles,
    "gentile": _rules_gentiles,
    "gentil": _rules_gentiles,     # ES singular
    "zion": _rules_zion,
    "sion": _rules_zion,           # ES without accent
    "sión": _rules_zion,
    "priesthood": _rules_priesthood,
    "sacerdocio": _rules_priesthood,
    "temple": _rules_temple,
    "templo": _rules_temple,
    "ark": _rules_ark,
    "arca": _rules_ark,
    "law": _rules_law,
    "ley": _rules_law,
}

# Names that should be checked -- if the canonical gazetteer name is already
# fully qualified (e.g. "Mary Magdalene"), disambiguation is unnecessary.
_AMBIGUOUS_CANONICAL: frozenset[str] = frozenset(_DISAMBIGUATION_RULES.keys())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class Disambiguator:
    """Rule-based resolver for ambiguous entity mentions in scripture text.

    Usage::

        d = Disambiguator()
        result = d.resolve("Alma", "person", chunk_text, source_file="corpus/en/scriptures/alma/36.txt")
        if result:
            print(result.resolved_name)  # "Alma the Younger"
    """

    def __init__(self) -> None:
        self._rules = _DISAMBIGUATION_RULES

    # Expose the set of entity names this resolver knows about.
    ambiguous_names: frozenset[str] = _AMBIGUOUS_CANONICAL

    def is_ambiguous(self, entity_name: str) -> bool:
        """Return True if *entity_name* is one we have disambiguation rules for."""
        return entity_name.lower() in self._rules

    def resolve(
        self,
        entity_name: str,
        entity_type: str,
        text: str,
        source_file: str = "",
    ) -> DisambiguatedMention | None:
        """Try to disambiguate an entity mention using contextual rules.

        Parameters
        ----------
        entity_name:
            The surface form as extracted (e.g. "Alma", "Mary", "Juan").
        entity_type:
            The entity type from the gazetteer or NER (e.g. "person").
            Passed through for context; all types are now eligible.
        text:
            The chunk / passage text surrounding the mention.
        source_file:
            Corpus file path (e.g. ``corpus/en/scriptures/alma/36.txt``).
            Used for book/chapter heuristics.

        Returns
        -------
        DisambiguatedMention if the entity could be resolved, else None.
        None means either the entity is not ambiguous or there is not enough
        signal to resolve it confidently.
        """
        key = entity_name.lower()
        rule_fn = self._rules.get(key)
        if rule_fn is None:
            return None

        window = _window_around(text, entity_name)
        result = rule_fn(window, source_file)
        if result is None:
            return None

        # Rules may return 3-tuple (name, conf, evidence) or
        # 4-tuple (name, conf, evidence, type_resolved) for Level 2.
        if len(result) == 4:
            resolved_name, confidence, evidence, type_resolved = result
        else:
            resolved_name, confidence, evidence = result
            type_resolved = None

        return DisambiguatedMention(
            original_name=entity_name,
            resolved_name=resolved_name,
            confidence=confidence,
            evidence=evidence,
            entity_type_resolved=type_resolved,
        )

    def resolve_all(
        self,
        entities: list[tuple[str, str]],
        text: str,
        source_file: str = "",
    ) -> dict[str, DisambiguatedMention]:
        """Batch-resolve a list of (name, type) pairs.

        Returns a dict mapping original names to their disambiguated form.
        Only entries that could be resolved are included.
        """
        results: dict[str, DisambiguatedMention] = {}
        for name, etype in entities:
            dm = self.resolve(name, etype, text, source_file)
            if dm is not None:
                results[name] = dm
        return results

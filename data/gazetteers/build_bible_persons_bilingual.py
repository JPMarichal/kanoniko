#!/usr/bin/env python3
"""
Build a comprehensive bilingual (EN/ES) gazetteer of all named persons in the Bible.

Sources:
- Theographic Bible Metadata (robertrouse/theographic-bible-metadata) - 1815 unique names
- BibleData (BradyStephenson/bible-data) - 1789 unique names
- Hitchcock's Bible Names Dictionary - meanings
- Manual EN-ES name mapping based on Reina-Valera 1960 conventions

Output: bible_persons_bilingual.json
"""

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).parent

# ──────────────────────────────────────────────────────────────────────
# 1. Comprehensive EN → ES mapping for biblical proper names
#    Based on Reina-Valera 1960 and common Spanish biblical usage
# ──────────────────────────────────────────────────────────────────────

EN_ES_MAP = {
    # ── Patriarchs & Genesis ──
    "Adam": "Adán",
    "Eve": "Eva",
    "Cain": "Caín",
    "Abel": "Abel",
    "Seth": "Set",
    "Enoch": "Enoc",
    "Methuselah": "Matusalén",
    "Lamech": "Lamec",
    "Noah": "Noé",
    "Shem": "Sem",
    "Ham": "Cam",
    "Japheth": "Jafet",
    "Nimrod": "Nimrod",
    "Abraham": "Abraham",
    "Abram": "Abram",
    "Sarah": "Sara",
    "Sarai": "Sarai",
    "Hagar": "Agar",
    "Ishmael": "Ismael",
    "Isaac": "Isaac",
    "Rebekah": "Rebeca",
    "Rebecca": "Rebeca",
    "Esau": "Esaú",
    "Jacob": "Jacob",
    "Leah": "Lea",
    "Rachel": "Raquel",
    "Laban": "Labán",
    "Reuben": "Rubén",
    "Simeon": "Simeón",
    "Levi": "Leví",
    "Judah": "Judá",
    "Dan": "Dan",
    "Naphtali": "Neftalí",
    "Gad": "Gad",
    "Asher": "Aser",
    "Issachar": "Isacar",
    "Zebulun": "Zabulón",
    "Joseph": "José",
    "Benjamin": "Benjamín",
    "Dinah": "Dina",
    "Tamar": "Tamar",
    "Lot": "Lot",
    "Melchizedek": "Melquisedec",
    "Potiphar": "Potifar",
    "Asenath": "Asenat",
    "Ephraim": "Efraín",
    "Manasseh": "Manasés",
    "Keturah": "Cetura",
    "Bilhah": "Bilha",
    "Zilpah": "Zilpa",
    "Bethuel": "Betuel",
    "Nahor": "Nacor",
    "Terah": "Taré",
    "Peleg": "Peleg",
    "Eber": "Heber",
    "Shelah": "Sela",

    # ── Exodus & Wilderness ──
    "Moses": "Moisés",
    "Aaron": "Aarón",
    "Miriam": "María",  # OT Miriam = María in RV
    "Pharaoh": "Faraón",
    "Jethro": "Jetro",
    "Zipporah": "Séfora",
    "Gershom": "Gersón",
    "Eliezer": "Eliezer",
    "Joshua": "Josué",
    "Caleb": "Caleb",
    "Korah": "Coré",
    "Dathan": "Datán",
    "Abiram": "Abiram",
    "Balaam": "Balaam",
    "Balak": "Balac",
    "Phinehas": "Finees",
    "Eleazar": "Eleazar",
    "Ithamar": "Itamar",
    "Nadab": "Nadab",
    "Abihu": "Abiú",
    "Bezalel": "Bezaleel",
    "Oholiab": "Aholiab",
    "Hobab": "Hobab",
    "Eldad": "Eldad",
    "Medad": "Medad",
    "Nun": "Nun",
    "Jochebed": "Jocabed",
    "Amram": "Amram",

    # ── Judges ──
    "Othniel": "Otoniel",
    "Ehud": "Aod",
    "Shamgar": "Samgar",
    "Deborah": "Débora",
    "Barak": "Barac",
    "Gideon": "Gedeón",
    "Abimelech": "Abimelec",
    "Tola": "Tola",
    "Jair": "Jaír",
    "Jephthah": "Jefté",
    "Ibzan": "Ibzán",
    "Elon": "Elón",
    "Abdon": "Abdón",
    "Samson": "Sansón",
    "Delilah": "Dalila",
    "Sisera": "Sísara",
    "Jael": "Jael",
    "Micah": "Micaía",

    # ── Ruth ──
    "Ruth": "Rut",
    "Naomi": "Noemí",
    "Boaz": "Booz",
    "Obed": "Obed",
    "Orpah": "Orfa",

    # ── United Monarchy ──
    "Samuel": "Samuel",
    "Eli": "Elí",
    "Hannah": "Ana",
    "Elkanah": "Elcana",
    "Saul": "Saúl",
    "Jonathan": "Jonatán",
    "David": "David",
    "Abigail": "Abigail",
    "Bathsheba": "Betsabé",
    "Nathan": "Natán",
    "Solomon": "Salomón",
    "Absalom": "Absalón",
    "Joab": "Joab",
    "Abner": "Abner",
    "Michal": "Mical",
    "Goliath": "Goliat",
    "Jesse": "Isaí",
    "Uriah": "Urías",
    "Zadok": "Sadoc",
    "Abiathar": "Abiatar",
    "Amnon": "Amnón",
    "Adonijah": "Adonías",
    "Mephibosheth": "Mefi-boset",
    "Ish-bosheth": "Is-boset",
    "Hushai": "Husai",
    "Ahithophel": "Ahitofel",
    "Shimei": "Simei",
    "Rizpah": "Rizpa",
    "Abishai": "Abisai",
    "Benaiah": "Benaía",
    "Hiram": "Hiram",

    # ── Divided Kingdom - Israel (North) ──
    "Jeroboam": "Jeroboam",
    "Ahab": "Acab",
    "Jezebel": "Jezabel",
    "Elijah": "Elías",
    "Elisha": "Eliseo",
    "Obadiah": "Abdías",
    "Jehu": "Jehú",
    "Omri": "Omri",
    "Zimri": "Zimri",
    "Baasha": "Baasa",
    "Tibni": "Tibni",
    "Ahaziah": "Ocozías",
    "Jehoram": "Joram",
    "Jehoahaz": "Joacaz",
    "Jehoash": "Joás",
    "Menahem": "Manahem",
    "Pekahiah": "Pekaía",
    "Pekah": "Peka",
    "Hoshea": "Oseas",

    # ── Divided Kingdom - Judah (South) ──
    "Rehoboam": "Roboam",
    "Abijah": "Abías",
    "Asa": "Asa",
    "Jehoshaphat": "Josafat",
    "Athaliah": "Atalía",
    "Joash": "Joás",
    "Amaziah": "Amasías",
    "Uzziah": "Uzías",
    "Jotham": "Jotam",
    "Ahaz": "Acaz",
    "Hezekiah": "Ezequías",
    "Manasseh": "Manasés",
    "Amon": "Amón",
    "Josiah": "Josías",
    "Jehoiakim": "Joacim",
    "Jehoiachin": "Joaquín",
    "Zedekiah": "Sedequías",

    # ── Major Prophets ──
    "Isaiah": "Isaías",
    "Jeremiah": "Jeremías",
    "Ezekiel": "Ezequiel",
    "Daniel": "Daniel",
    "Baruch": "Baruc",

    # ── Minor Prophets ──
    "Hosea": "Oseas",
    "Joel": "Joel",
    "Amos": "Amós",
    "Jonah": "Jonás",
    "Nahum": "Nahúm",
    "Habakkuk": "Habacuc",
    "Zephaniah": "Sofonías",
    "Haggai": "Hageo",
    "Zechariah": "Zacarías",
    "Malachi": "Malaquías",

    # ── Exile & Post-Exile ──
    "Nebuchadnezzar": "Nabucodonosor",
    "Belshazzar": "Belsasar",
    "Cyrus": "Ciro",
    "Darius": "Darío",
    "Artaxerxes": "Artajerjes",
    "Ezra": "Esdras",
    "Nehemiah": "Nehemías",
    "Mordecai": "Mardoqueo",
    "Esther": "Ester",
    "Haman": "Amán",
    "Vashti": "Vasti",
    "Ahasuerus": "Asuero",
    "Xerxes": "Jerjes",
    "Zerubbabel": "Zorobabel",
    "Haggai": "Hageo",
    "Shadrach": "Sadrac",
    "Meshach": "Mesac",
    "Abednego": "Abed-nego",
    "Tobias": "Tobías",
    "Tobit": "Tobit",

    # ── Wisdom & Poetry ──
    "Job": "Job",

    # ── Other OT figures ──
    "Rahab": "Rahab",
    "Achan": "Acán",
    "Gershon": "Gersón",
    "Kohath": "Coat",
    "Merari": "Merari",
    "Og": "Og",
    "Sihon": "Sehón",
    "Jabez": "Jabes",
    "Nabal": "Nabal",
    "Gehazi": "Giezi",
    "Naamán": "Naamán",
    "Naaman": "Naamán",
    "Huldah": "Hulda",
    "Sheba": "Seba",
    "Jezreel": "Jezreel",
    "Sennacherib": "Senaquerib",

    # ═══════════════════════════════════════════════
    # NEW TESTAMENT
    # ═══════════════════════════════════════════════

    # ── Jesus & Family ──
    "Jesus": "Jesús",
    "Mary": "María",
    "Christ": "Cristo",

    # ── The Twelve Apostles ──
    "Peter": "Pedro",
    "Simon": "Simón",
    "Andrew": "Andrés",
    "James": "Santiago",  # James son of Zebedee
    "John": "Juan",
    "Philip": "Felipe",
    "Bartholomew": "Bartolomé",
    "Thomas": "Tomás",
    "Matthew": "Mateo",
    "Thaddaeus": "Tadeo",
    "Judas": "Judas",
    "Matthias": "Matías",

    # ── Other NT Figures ──
    "Paul": "Pablo",
    "Barnabas": "Bernabé",
    "Stephen": "Esteban",
    "Timothy": "Timoteo",
    "Titus": "Tito",
    "Silas": "Silas",
    "Luke": "Lucas",
    "Mark": "Marcos",
    "Apollos": "Apolos",
    "Aquila": "Aquila",
    "Priscilla": "Priscila",
    "Lydia": "Lidia",
    "Phoebe": "Febe",
    "Philemon": "Filemón",
    "Onesimus": "Onésimo",
    "Epaphras": "Epafras",
    "Epaphroditus": "Epafrodito",
    "Tychicus": "Tíquico",
    "Aristarchus": "Aristarco",
    "Demas": "Demas",
    "Trophimus": "Trófimo",
    "Erastus": "Erasto",
    "Gaius": "Gayo",
    "Sopater": "Sópater",
    "Secundus": "Segundo",
    "Sosthenes": "Sóstenes",
    "Crispus": "Crispo",
    "Justus": "Justo",
    "Cornelius": "Cornelio",
    "Ananias": "Ananías",
    "Sapphira": "Safira",
    "Lazarus": "Lázaro",
    "Martha": "Marta",
    "Nicodemus": "Nicodemo",
    "Nathanael": "Natanael",
    "Zacchaeus": "Zaqueo",
    "Caiaphas": "Caifás",
    "Annas": "Anás",
    "Herod": "Herodes",
    "Pilate": "Pilato",
    "Barabbas": "Barrabás",
    "Cleopas": "Cleofas",
    "Dorcas": "Dorcas",
    "Tabitha": "Tabita",
    "Agabus": "Ágabo",
    "Rhoda": "Rode",
    "Eutychus": "Eutico",
    "Felix": "Félix",
    "Festus": "Festo",
    "Agrippa": "Agripa",
    "Bernice": "Berenice",
    "Drusilla": "Drusila",
    "Alexander": "Alejandro",
    "Rufus": "Rufo",
    "Linus": "Lino",
    "Claudia": "Claudia",
    "Pudens": "Pudente",
    "Archippus": "Arquipo",
    "Nympha": "Ninfas",
    "Eunice": "Eunice",
    "Lois": "Loida",
    "Joanna": "Juana",
    "Susanna": "Susana",
    "Salome": "Salomé",
    "Elizabeth": "Elisabet",
    "Zacharias": "Zacarías",
    "Anna": "Ana",

    # ── Herodian / Roman ──
    "Augustus": "Augusto",
    "Tiberius": "Tiberio",
    "Claudius": "Claudio",
    "Nero": "Nerón",
    "Quirinius": "Cirenio",

    # ── John the Baptist ──
    "Baptist": "Bautista",

    # ── Revelation ──
    "Antipas": "Antipas",
    "Jezebel": "Jezabel",
    "Abaddon": "Abadón",
    "Apollyon": "Apolión",

    # ── Additional mappings ──
    "Cephas": "Cefas",
    "Silvanus": "Silvano",
    "Silas": "Silas",
    "Nehemiah": "Nehemías",
    "Habakkuk": "Habacuc",
    "Lamentations": "Lamentaciones",
    "Ecclesiastes": "Eclesiastés",
    "Jude": "Judas",
    "Philippi": "Filipos",
    "Gamaliel": "Gamaliel",
    "Theophilus": "Teófilo",
    "Simeon": "Simeón",
    "Cleophas": "Cleofas",
    "Clopas": "Cleofas",
    "Jairus": "Jairo",
    "Bartimaeus": "Bartimeo",
    "Legion": "Legión",
    "Archelaus": "Arquelao",
    "Herodias": "Herodías",
}


def load_theographic():
    """Load and parse Theographic People.csv"""
    people = {}
    with open(HERE / "theographic_people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            name = r.get("name", "").strip()
            if not name:
                continue
            key = name
            # Handle duplicates (Abdi 1, Abdi 2, etc.)
            display = r.get("displayTitle", "").strip()
            gender = r.get("gender", "").strip()
            also_called = r.get("alsoCalled", "").strip()
            desc = r.get("dictText", "").strip()
            # Get first sentence of description
            if desc:
                first_sent = desc.split(".")[0].strip()
                if len(first_sent) > 150:
                    first_sent = first_sent[:150] + "..."
                desc = first_sent

            if key not in people:
                people[key] = {
                    "name_en": name,
                    "display": display,
                    "gender": gender,
                    "also_called": also_called,
                    "description": desc,
                }
    return people


def load_bibledata():
    """Load BibleData-Person.csv"""
    people = {}
    with open(HERE / "bibledata_person.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            name = r.get("person_name", "").strip()
            if not name:
                continue
            attr = r.get("unique_attribute", "").strip()
            sex = r.get("sex", "").strip()
            tribe = r.get("tribe", "").strip()

            if name not in people:
                people[name] = {
                    "name_en": name,
                    "attribute": attr,
                    "gender": sex.capitalize() if sex else "",
                    "tribe": tribe,
                }
    return people


def load_hitchcocks():
    """Load Hitchcock's Bible Names Dictionary"""
    names = {}
    with open(HERE / "hitchcocks_bible_names.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            name = r.get("Name", "").strip()
            meaning = r.get("Meaning", "").strip()
            if name:
                names[name] = meaning
    return names


def get_spanish_name(en_name):
    """Get the Spanish equivalent of an English biblical name."""
    # Direct lookup
    if en_name in EN_ES_MAP:
        return EN_ES_MAP[en_name]

    # Try without trailing numbers (e.g., "Abdi 1" -> "Abdi")
    base = re.sub(r'\s*\d+$', '', en_name)
    if base in EN_ES_MAP:
        return EN_ES_MAP[base]

    # Many Hebrew/Aramaic names stay the same or have minor accent changes
    # Apply common Spanish transliteration rules
    es = en_name

    # Common patterns for Spanish biblical names
    replacements = [
        # -iah / -jah endings → -ías
        (r'iah$', 'ías'),
        (r'jah$', 'ías'),
        # -iel endings usually stay
        # -el endings usually stay
        # -am endings usually stay
        # ph → f
        (r'ph(?=[aeiou])', 'f'),
        (r'Ph', 'F'),
        # th at start → T
        (r'^Th', 'T'),
        # sh → S (sometimes)
        # Double letters simplified
        # -ech → -ec
        (r'ech$', 'ec'),
    ]

    for pattern, repl in replacements:
        es = re.sub(pattern, repl, es)

    # If no change was made, return original (many names are the same)
    return es


def determine_testament(desc, attr):
    """Try to determine OT/NT from description and verse references."""
    text = f"{desc} {attr}".upper()

    # Use regex word-boundary patterns to avoid false matches
    # e.g. "2SA" should match, but "SA" inside a word shouldn't
    nt_patterns = [
        r'\bMAT\b', r'\bMATT\b', r'\bMRK\b', r'\bMARK\b',
        r'\bLUK\b', r'\bLUKE\b', r'\bJHN\b', r'\bJOHN\b',
        r'\bACT\b', r'\bACTS\b', r'\bROM\b', r'\bROMANS\b',
        r'\b\d?CO\b', r'\b\d?COR\b', r'\bGAL\b',
        r'\bEPH\b', r'\bPHP\b', r'\bCOL\b',
        r'\b\d?TH[ES]\b', r'\b\d?TIM\b', r'\bTIT\b', r'\bPHM\b',
        r'\bHEB\b', r'\bJAS\b', r'\b\d?PET\b', r'\b\d?PE\b',
        r'\bJDE\b', r'\bJUD\b', r'\bREV\b', r'\bREVELATION\b',
    ]

    ot_patterns = [
        r'\bGEN\b', r'\bEXO\b', r'\bEX\b', r'\bLEV\b', r'\bNUM\b',
        r'\bDEU\b', r'\bDT\b', r'\bJOS\b', r'\bJDG\b', r'\bRUT\b',
        r'\b\d?SA\b', r'\b\d?SAM\b', r'\b\d?KI\b', r'\b\d?KIN\b',
        r'\b\d?CH\b', r'\b\d?CHR\b', r'\bEZR\b', r'\bNEH\b',
        r'\bEST\b', r'\bJOB\b', r'\bPSA\b', r'\bPS\b',
        r'\bPRO\b', r'\bPRV\b', r'\bECC\b', r'\bSNG\b', r'\bSOL\b',
        r'\bISA\b', r'\bJER\b', r'\bLAM\b', r'\bEZK\b', r'\bEZE\b',
        r'\bDAN\b', r'\bHOS\b', r'\bJOL\b', r'\bAMO\b',
        r'\bOBA\b', r'\bJON\b', r'\bMIC\b', r'\bNAH\b',
        r'\bHAB\b', r'\bZEP\b', r'\bHAG\b', r'\bZEC\b', r'\bMAL\b',
    ]

    has_nt = any(re.search(p, text) for p in nt_patterns)
    has_ot = any(re.search(p, text) for p in ot_patterns)

    if has_nt and not has_ot:
        return "NT"
    elif has_ot and not has_nt:
        return "OT"
    elif has_nt and has_ot:
        return "Both"
    return "Unknown"


def main():
    print("Loading datasets...")
    theographic = load_theographic()
    bibledata = load_bibledata()
    hitchcocks = load_hitchcocks()

    print(f"  Theographic: {len(theographic)} unique names")
    print(f"  BibleData: {len(bibledata)} unique names")
    print(f"  Hitchcock's: {len(hitchcocks)} names with meanings")

    # Merge all names
    all_names = sorted(set(list(theographic.keys()) + list(bibledata.keys())))
    print(f"  Combined unique: {len(all_names)}")

    # Build final list
    persons = []
    for name in all_names:
        entry = {
            "name_en": name,
            "name_es": get_spanish_name(name),
        }

        # Get description from bibledata (more concise) or theographic
        desc = ""
        gender = ""

        if name in bibledata:
            bd = bibledata[name]
            desc = bd["attribute"]
            gender = bd["gender"]

        if name in theographic:
            tg = theographic[name]
            if not desc and tg["description"]:
                desc = tg["description"]
            if not gender and tg["gender"]:
                gender = tg["gender"]
            if tg["also_called"]:
                entry["also_called"] = tg["also_called"]

        # Add Hitchcock meaning
        if name in hitchcocks:
            entry["meaning"] = hitchcocks[name]

        entry["gender"] = gender
        entry["description"] = desc
        entry["testament"] = determine_testament(
            desc,
            theographic.get(name, {}).get("description", "")
        )

        persons.append(entry)

    # Write JSON
    output = HERE / "bible_persons_bilingual.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(persons, f, ensure_ascii=False, indent=2)

    # Stats
    ot = sum(1 for p in persons if p["testament"] == "OT")
    nt = sum(1 for p in persons if p["testament"] == "NT")
    both = sum(1 for p in persons if p["testament"] == "Both")
    unk = sum(1 for p in persons if p["testament"] == "Unknown")
    mapped = sum(1 for p in persons if p["name_en"] != p["name_es"])

    print(f"\nOutput: {output}")
    print(f"Total persons: {len(persons)}")
    print(f"  OT: {ot}")
    print(f"  NT: {nt}")
    print(f"  Both: {both}")
    print(f"  Unknown: {unk}")
    print(f"  With ES translation different from EN: {mapped}")

    # Also write a simple CSV for easy viewing
    csv_output = HERE / "bible_persons_bilingual.csv"
    with open(csv_output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name_en", "name_es", "gender", "testament", "description", "meaning"])
        for p in persons:
            writer.writerow([
                p["name_en"],
                p["name_es"],
                p["gender"],
                p["testament"],
                p["description"][:200],
                p.get("meaning", ""),
            ])
    print(f"CSV: {csv_output}")


if __name__ == "__main__":
    main()

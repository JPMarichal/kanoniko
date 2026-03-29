from __future__ import annotations
"""
Batch-translate all pericope names from ES to EN.
Strategy: merge existing partial translations (_trans_*.json) with
pattern-based and phrase-based automatic translation, then output
a single combined pericopae_translations.json.
"""
import json
import re
import os

DATA_DIR = "C:/own/alejandria/data/scripture_structure"
SCRIPT_DIR = "C:/own/alejandria/scripts"

# ── Proper noun map ──────────────────────────────────────────────────────────
NAMES = {
    # OT
    "Adán": "Adam", "Eva": "Eve", "Caín": "Cain", "Abel": "Abel",
    "Set": "Seth", "Enós": "Enos", "Enoc": "Enoch", "Noé": "Noah",
    "Matusalén": "Methuselah", "Lamec": "Lamech", "Sem": "Shem",
    "Cam": "Ham", "Jafet": "Japheth", "Abraham": "Abraham", "Abram": "Abram",
    "Sara": "Sarah", "Sarai": "Sarai", "Agar": "Hagar", "Isaac": "Isaac",
    "Isaác": "Isaac", "Rebeca": "Rebekah", "Jacob": "Jacob", "Esaú": "Esau",
    "Labán": "Laban", "Raquel": "Rachel", "Lea": "Leah", "José": "Joseph",
    "Judá": "Judah", "Rubén": "Reuben", "Simeón": "Simeon", "Leví": "Levi",
    "Benjamín": "Benjamin", "Tamar": "Tamar", "Dina": "Dinah",
    "Moisés": "Moses", "Aarón": "Aaron", "Miriam": "Miriam",
    "Josué": "Joshua", "Caleb": "Caleb", "Balaam": "Balaam", "Balac": "Balak",
    "Rahab": "Rahab", "Débora": "Deborah", "Barac": "Barak",
    "Gedeón": "Gideon", "Jefté": "Jephthah", "Sansón": "Samson",
    "Dalila": "Delilah", "Rut": "Ruth", "Booz": "Boaz", "Noemí": "Naomi",
    "Samuel": "Samuel", "Saúl": "Saul", "David": "David",
    "Jonatán": "Jonathan", "Salomón": "Solomon", "Absalón": "Absalom",
    "Roboam": "Rehoboam", "Jeroboam": "Jeroboam", "Acab": "Ahab",
    "Jezabel": "Jezebel", "Elías": "Elijah", "Eliseo": "Elisha",
    "Isaías": "Isaiah", "Jeremías": "Jeremiah", "Ezequiel": "Ezekiel",
    "Daniel": "Daniel", "Oseas": "Hosea", "Joel": "Joel", "Amós": "Amos",
    "Jonás": "Jonah", "Miqueas": "Micah", "Nahúm": "Nahum",
    "Habacuc": "Habakkuk", "Sofonías": "Zephaniah", "Hageo": "Haggai",
    "Zacarías": "Zechariah", "Malaquías": "Malachi", "Nehemías": "Nehemiah",
    "Esdras": "Ezra", "Ester": "Esther", "Job": "Job",
    "Faraón": "Pharaoh", "Potifar": "Potiphar",
    "Nabucodonosor": "Nebuchadnezzar", "Ciro": "Cyrus", "Darío": "Darius",
    "Zorobabel": "Zerubbabel", "Manasés": "Manasseh", "Ezequías": "Hezekiah",
    "Josías": "Josiah", "Sedequías": "Zedekiah", "Acaz": "Ahaz",
    "Jotam": "Jotham", "Uzías": "Uzziah", "Asá": "Asa",
    "Josafat": "Jehoshaphat", "Joram": "Joram", "Ocozías": "Ahaziah",
    "Atalía": "Athaliah", "Joás": "Joash", "Amasías": "Amaziah",
    "Joacim": "Jehoiakim", "Joaquín": "Jehoiachin",
    # NT
    "Jesús": "Jesus", "Jesucristo": "Jesus Christ", "Cristo": "Christ",
    "Pedro": "Peter", "Pablo": "Paul", "Juan": "John", "Santiago": "James",
    "Mateo": "Matthew", "Marcos": "Mark", "Lucas": "Luke",
    "Andrés": "Andrew", "Felipe": "Philip", "Bartolomé": "Bartholomew",
    "Tomás": "Thomas", "Tadeo": "Thaddaeus", "Simón": "Simon",
    "Judas": "Judas", "María": "Mary", "Marta": "Martha", "Lázaro": "Lazarus",
    "Herodes": "Herod", "Pilato": "Pilate", "Barrabás": "Barabbas",
    "Esteban": "Stephen", "Bernabé": "Barnabas", "Timoteo": "Timothy",
    "Tito": "Titus", "Filemón": "Philemon", "Onésimo": "Onesimus",
    "Apolos": "Apollos", "Aquila": "Aquila", "Priscila": "Priscilla",
    "Nicodemo": "Nicodemus", "Zaqueo": "Zacchaeus",
    # BoM
    "Nefi": "Nephi", "Lehi": "Lehi", "Alma": "Alma", "Mormón": "Mormon",
    "Moroni": "Moroni", "Helamán": "Helaman", "Abinadí": "Abinadi",
    "Ammón": "Ammon", "Amulón": "Amulon", "Amalickíah": "Amalickiah",
    "Gadiantón": "Gadianton", "Mosíah": "Mosiah", "Coriantón": "Corianton",
    "Shiblón": "Shiblon", "Zeniff": "Zeniff", "Limhi": "Limhi",
    "Amulek": "Amulek", "Zoram": "Zoram", "Ismael": "Ishmael",
    "Sherem": "Sherem", "Korihor": "Korihor", "Éter": "Ether",
    "Jarom": "Jarom", "Ómni": "Omni", "Lamoni": "Lamoni",
    "Pahorán": "Pahoran", "Teáncum": "Teancum", "Moriantón": "Morianton",
    "Ammoníah": "Ammonihah", "Ammarón": "Ammaron", "Ammorón": "Ammoron",
    "Zeezrom": "Zeezrom", "Giddoni": "Gidgiddoni", "Laconeo": "Lachoneus",
    "Cezoram": "Cezoram", "Kishkumen": "Kishkumen", "Nehor": "Nehor",
    "Sariah": "Sariah", "Gazelam": "Gazelem",
    # D&C / Restoration
    "José Smith": "Joseph Smith", "Oliverio Cowdery": "Oliver Cowdery",
    "Oliver Cowdery": "Oliver Cowdery", "Sidney Rigdon": "Sidney Rigdon",
    "Hyrum Smith": "Hyrum Smith", "Martín Harris": "Martin Harris",
    "Martin Harris": "Martin Harris", "Emma Smith": "Emma Smith",
    "Brigham Young": "Brigham Young", "Edward Partridge": "Edward Partridge",
    "Satanás": "Satan", "Lucifer": "Lucifer",
    # Places
    "Sión": "Zion", "Sion": "Zion", "Jerusalén": "Jerusalem",
    "Babilonia": "Babylon", "Egipto": "Egypt", "Asiria": "Assyria",
    "Nínive": "Nineveh", "Samaria": "Samaria", "Galilea": "Galilee",
    "Nazaret": "Nazareth", "Belén": "Bethlehem", "Capernaum": "Capernaum",
    "Getsemaní": "Gethsemane", "Gólgota": "Golgotha",
    "Zarahemla": "Zarahemla", "Abundancia": "Bountiful",
    "Canaán": "Canaan", "Harán": "Haran",
    "Misuri": "Missouri", "Kirtland": "Kirtland", "Nauvoo": "Nauvoo",
    "Edén": "Eden",
}

# ── Common phrase translations ───────────────────────────────────────────────
PHRASES = {
    "el Señor": "the Lord",
    "El Señor": "The Lord",
    "del Señor": "of the Lord",
    "al Señor": "to the Lord",
    "el Espíritu Santo": "the Holy Ghost",
    "el Espíritu": "the Spirit",
    "del Espíritu": "of the Spirit",
    "el Evangelio": "the Gospel",
    "del Evangelio": "of the Gospel",
    "el Libro de Mormón": "the Book of Mormon",
    "del Libro de Mormón": "of the Book of Mormon",
    "el Sacerdocio Aarónico": "the Aaronic Priesthood",
    "el Sacerdocio de Melquisedec": "the Melchizedek Priesthood",
    "el sacerdocio": "the priesthood",
    "del sacerdocio": "of the priesthood",
    "la Iglesia": "the Church",
    "de la Iglesia": "of the Church",
    "la Segunda Venida": "the Second Coming",
    "la tierra prometida": "the promised land",
    "la tierra": "the land",
    "los últimos días": "the latter days",
    "los santos": "the Saints",
    "los nefitas": "the Nephites",
    "los lamanitas": "the Lamanites",
    "los gentiles": "the Gentiles",
    "los judíos": "the Jews",
    "los élderes": "the elders",
    "la fe": "faith",
    "el arrepentimiento": "repentance",
    "el bautismo": "baptism",
    "el templo": "the temple",
    "del templo": "of the temple",
    "el convenio": "the covenant",
    "los convenios": "the covenants",
    "la expiación": "the Atonement",
    "la Expiación": "the Atonement",
    "el reino de Dios": "the kingdom of God",
    "la ley de Moisés": "the law of Moses",
    "la Primera Presidencia": "the First Presidency",
    "los Doce": "the Twelve",
    "la orden unida": "the United Order",
    "la Nueva Jerusalén": "the New Jerusalem",
    "la Santa Cena": "the sacrament",
    "la Palabra de Sabiduría": "the Word of Wisdom",
    "el Milenio": "the Millennium",
    "la Restauración": "the Restoration",
    "la Caída": "the Fall",
    "el Diluvio": "the Flood",
    "el jardín de Edén": "the Garden of Eden",
    "las planchas de oro": "the gold plates",
    "las planchas de bronce": "the brass plates",
    "los registros sagrados": "the sacred records",
    "Hijo del Hombre": "Son of Man",
    "Hijo de Dios": "Son of God",
    "el Padre": "the Father",
    "el Hijo": "the Son",
    "hijos de Dios": "sons of God",
    "pueblo de Dios": "people of God",
    "la tierra de herencia": "the land of inheritance",
    "ladrones de Gadiantón": "Gadianton robbers",
    "las Escrituras": "the scriptures",
    "vida eterna": "eternal life",
    "reino celestial": "the celestial kingdom",
    "reino terrestre": "the terrestrial kingdom",
    "reino telestial": "the telestial kingdom",
    "el Espíritu Santo": "the Holy Ghost",
    "la resurrección": "the resurrection",
    "la Resurrección": "the Resurrection",
}


def load_partial_translations():
    """Load all existing _trans_*.json files."""
    combined = {}
    for fname in os.listdir(DATA_DIR):
        if fname.startswith("_trans_") and fname.endswith(".json"):
            path = os.path.join(DATA_DIR, fname)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                combined.update(data)
    return combined


def load_all_pericope_names():
    """Load pericopae.json and get all unique name_es values."""
    path = os.path.join(DATA_DIR, "pericopae.json")
    with open(path, encoding="utf-8") as f:
        pericopae = json.load(f)
    return sorted(set(p["name_es"] for p in pericopae))


def translate_name_token(token):
    """Translate a single proper noun."""
    return NAMES.get(token, token)


def apply_patterns(name):
    """Try regex-based translation patterns."""
    patterns = [
        # Articles of Faith
        (r"^Articulo de Fe (\d+)$", lambda m: "Article of Faith %s" % m.group(1)),
        # Creation days
        (r"^Los seis días de la Creación, día (\d+)$",
         lambda m: "The Six Days of Creation, Day %s" % m.group(1)),
        (r"^Los seis días de la Creación, día (\d+), parte (\d+)$",
         lambda m: "The Six Days of Creation, Day %s, Part %s" % (m.group(1), m.group(2))),
        # Book of generations of Adam
        (r"^El libro de las generaciones de Adán: (.+)$",
         lambda m: "The Book of the Generations of Adam: %s" % translate_sub(m.group(1))),
        # Psalms
        (r"^Salmo (\d+)$", lambda m: "Psalm %s" % m.group(1)),
        (r"^Salmo (\d+): (.+)$", lambda m: "Psalm %s: %s" % (m.group(1), m.group(2))),
        # Reign patterns
        (r"^Reinado de (.+)$", lambda m: "Reign of %s" % translate_sub(m.group(1))),
        (r"^Reinados de (.+)$", lambda m: "Reigns of %s" % translate_sub(m.group(1))),
        # Prophecies
        (r"^Profecías? contra (.+)$", lambda m: "Prophecy against %s" % translate_sub(m.group(1))),
        (r"^Profecías? sobre (.+)$", lambda m: "Prophecy of %s" % translate_sub(m.group(1))),
        # Parables
        (r"^Parábola de la (.+)$", lambda m: "Parable of the %s" % translate_sub(m.group(1))),
        (r"^Parábola de los (.+)$", lambda m: "Parable of the %s" % translate_sub(m.group(1))),
        (r"^Parábola del (.+)$", lambda m: "Parable of the %s" % translate_sub(m.group(1))),
        (r"^Parábola de (.+)$", lambda m: "Parable of %s" % translate_sub(m.group(1))),
        # Introductions
        (r"^Introducción a (.+)$", lambda m: "Introduction to %s" % translate_sub(m.group(1))),
        (r"^Introducción al (.+)$", lambda m: "Introduction to the %s" % translate_sub(m.group(1))),
        # Visions
        (r"^Visión de (.+)$", lambda m: "Vision of %s" % translate_sub(m.group(1))),
        (r"^Visión sobre (.+)$", lambda m: "Vision of %s" % translate_sub(m.group(1))),
        # Discurso de Enoc
        (r"^El discurso de Enoc, (.+)$",
         lambda m: "The Discourse of Enoch, %s" % translate_sub(m.group(1))),
        # La visión de Enoc
        (r"^La visión de Enoc: (.+)$",
         lambda m: "The Vision of Enoch: %s" % translate_sub(m.group(1))),
        # Satanás tienta a Moisés
        (r"^Satanás tienta a Moisés, intento (\d+)$",
         lambda m: "Satan Tempts Moses, Attempt %s" % m.group(1)),
    ]
    for pattern, handler in patterns:
        m = re.match(pattern, name)
        if m:
            return handler(m)
    return None


def translate_sub(text):
    """Translate a sub-expression: try name map, then return as-is."""
    # Try direct name lookup
    if text in NAMES:
        return NAMES[text]
    # Try common suffixes like "parte 1"
    m = re.match(r"^(.+), parte (\d+)$", text)
    if m:
        return "%s, Part %s" % (translate_sub(m.group(1)), m.group(2))
    # Try "X y Y" pattern
    if " y " in text:
        parts = text.split(" y ", 1)
        return "%s and %s" % (translate_sub(parts[0]), translate_sub(parts[1]))
    # Try "X e Y" pattern
    if " e " in text:
        parts = text.split(" e ", 1)
        return "%s and %s" % (translate_sub(parts[0]), translate_sub(parts[1]))
    return text


def main():
    # Load existing translations
    existing = load_partial_translations()
    print("Loaded %d existing translations from _trans_*.json files" % len(existing))

    # Load all unique names
    all_names = load_all_pericope_names()
    print("Total unique pericope names: %d" % len(all_names))

    # Apply patterns
    translations = dict(existing)
    pattern_count = 0
    for name in all_names:
        if name in translations:
            continue
        en = apply_patterns(name)
        if en:
            translations[name] = en
            pattern_count += 1

    print("From patterns: %d" % pattern_count)

    # Count what's left
    untranslated = [n for n in all_names if n not in translations]
    print("Still untranslated: %d" % len(untranslated))

    # Write combined translations
    out_path = os.path.join(SCRIPT_DIR, "pericopae_translations.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2, sort_keys=True)
    print("Wrote %d translations to %s" % (len(translations), out_path))

    # Write untranslated for review
    if untranslated:
        ut_path = os.path.join(DATA_DIR, "_untranslated.json")
        with open(ut_path, "w", encoding="utf-8") as f:
            json.dump(untranslated, f, ensure_ascii=False, indent=2)
        print("Wrote %d untranslated names to %s" % (len(untranslated), ut_path))

        # Show breakdown by volume
        peri_path = os.path.join(DATA_DIR, "pericopae.json")
        with open(peri_path, encoding="utf-8") as f:
            pericopae = json.load(f)

        # Map name to volumes
        name_volumes = {}
        for p in pericopae:
            name_volumes.setdefault(p["name_es"], set()).add(p.get("volume_slug", "?"))

        vol_counts = {}
        for n in untranslated:
            for v in name_volumes.get(n, {"?"}):
                vol_counts[v] = vol_counts.get(v, 0) + 1
        print("\nUntranslated by volume:")
        for v, c in sorted(vol_counts.items()):
            print("  %s: %d" % (v, c))


if __name__ == "__main__":
    main()

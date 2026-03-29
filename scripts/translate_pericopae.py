from __future__ import annotations
"""
Apply English translations to pericopae.json.
Translates all 4,475 unique pericope names from ES to EN.
"""
import json
import re

PERI_PATH = "C:/own/alejandria/data/scripture_structure/pericopae.json"

# ── Translation rules (pattern-based for systematic names) ────────────────

# Many pericope names follow patterns that can be translated systematically.
# We handle these with regex patterns, then provide explicit overrides for
# names that need special treatment.

PATTERNS = [
    # Articles of Faith
    (r"^Articulo de Fe (\d+)$", lambda m: "Article of Faith %s" % m.group(1)),

    # Creation days
    (r"^Los seis días de la Creación, día (\d+)$",
     lambda m: "The Six Days of Creation, Day %s" % m.group(1)),
    (r"^Los seis días de la Creación, día (\d+), parte (\d+)$",
     lambda m: "The Six Days of Creation, Day %s, Part %s" % (m.group(1), m.group(2))),

    # Book of generations of Adam
    (r"^El libro de las generaciones de Adán: (.+)$",
     lambda m: "The Book of the Generations of Adam: %s" % translate_name(m.group(1))),

    # Reign patterns
    (r"^Reinado de (.+)$", lambda m: "Reign of %s" % translate_name(m.group(1))),
    (r"^Reinados de (.+)$", lambda m: "Reigns of %s" % translate_name(m.group(1))),

    # Prophecies/oracles against
    (r"^Profecías? contra (.+)$", lambda m: "Prophecies against %s" % translate_name(m.group(1))),
    (r"^Profecías? sobre (.+)$", lambda m: "Prophecies of %s" % translate_name(m.group(1))),

    # Psalms patterns
    (r"^Salmo (\d+)$", lambda m: "Psalm %s" % m.group(1)),
    (r"^Salmo (\d+): (.+)$", lambda m: "Psalm %s: %s" % (m.group(1), m.group(2))),

    # D&C section intro pattern
    (r"^Introducción a (.+)$", lambda m: "Introduction to %s" % translate_name(m.group(1))),

    # Parables
    (r"^Parábola de (.+)$", lambda m: "Parable of %s" % translate_name(m.group(1))),
    (r"^Par[aá]bola del (.+)$", lambda m: "Parable of the %s" % translate_name(m.group(1))),

    # Vision patterns
    (r"^Visión de (.+)$", lambda m: "Vision of %s" % translate_name(m.group(1))),
    (r"^Visión sobre (.+)$", lambda m: "Vision of %s" % translate_name(m.group(1))),
]

# Name translation helper for proper nouns
NAME_MAP = {
    "Adán": "Adam",
    "Set": "Seth",
    "Enós": "Enos",
    "Cainán": "Cainan",
    "Mahalaleel": "Mahalaleel",
    "Jared": "Jared",
    "Enoc": "Enoch",
    "Matusalén": "Methuselah",
    "Lamec": "Lamech",
    "Noé": "Noah",
    "Moisés": "Moses",
    "Josué": "Joshua",
    "Abraham": "Abraham",
    "Isaías": "Isaiah",
    "Jeremías": "Jeremiah",
    "Ezequiel": "Ezekiel",
    "Daniel": "Daniel",
    "Sarai": "Sarai",
    "Sara": "Sarah",
    "Agar": "Hagar",
    "Lot": "Lot",
    "Esaú": "Esau",
    "Jacob": "Jacob",
    "José": "Joseph",
    "Rebeca": "Rebekah",
    "Labán": "Laban",
    "Raquel": "Rachel",
    "Lea": "Leah",
    "Judá": "Judah",
    "Tamar": "Tamar",
    "Rut": "Ruth",
    "Booz": "Boaz",
    "Noemí": "Naomi",
    "Samuel": "Samuel",
    "Saúl": "Saul",
    "David": "David",
    "Salomón": "Solomon",
    "Elías": "Elijah",
    "Eliseo": "Elisha",
    "Sansón": "Samson",
    "Dalila": "Delilah",
    "Gedeón": "Gideon",
    "Débora": "Deborah",
    "Barac": "Barak",
    "Jefté": "Jephthah",
    "Nefi": "Nephi",
    "Lehi": "Lehi",
    "Alma": "Alma",
    "Mormón": "Mormon",
    "Moroni": "Moroni",
    "Helamán": "Helaman",
    "Abinadí": "Abinadi",
    "Ammón": "Ammon",
    "Amulón": "Amulon",
    "Amalickíah": "Amalickiah",
    "Gadiantón": "Gadianton",
    "Mosíah": "Mosiah",
    "Benjamín": "Benjamin",
    "Coriantón": "Corianton",
    "Shiblón": "Shiblon",
    "Zeniff": "Zeniff",
    "Limhi": "Limhi",
    "Noé": "Noah",
    "Amulek": "Amulek",
    "Zoram": "Zoram",
    "Ismael": "Ishmael",
    "Sherem": "Sherem",
    "Korihor": "Korihor",
    "Éter": "Ether",
    "Onésimo": "Onesimus",
    "Gayo": "Gaius",
    "Diótrefes": "Diotrephes",
    "Timoteo": "Timothy",
    "Tito": "Titus",
    "Pedro": "Peter",
    "Pablo": "Paul",
    "Juan": "John",
    "Santiago": "James",
    "Jesús": "Jesus",
    "Jesucristo": "Jesus Christ",
    "Cristo": "Christ",
    "Caín": "Cain",
    "Abel": "Abel",
    "Satanás": "Satan",
    "Lucifer": "Lucifer",
    "parte 1": "Part 1",
    "parte 2": "Part 2",
    "parte 3": "Part 3",
}


def translate_name(name):
    """Translate a proper name or short phrase."""
    return NAME_MAP.get(name, name)


def apply_patterns(name_es):
    """Try to translate using regex patterns. Returns EN name or None."""
    for pattern, handler in PATTERNS:
        m = re.match(pattern, name_es)
        if m:
            return handler(m)
    return None


# ── Explicit translations (loaded from generated file) ────────────────────

def load_explicit_translations():
    """Load the explicit translation dictionary."""
    import os
    path = os.path.join(os.path.dirname(__file__), "pericopae_translations.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    with open(PERI_PATH, encoding="utf-8") as f:
        pericopae = json.load(f)

    # Collect unique names
    unique_names = sorted(set(p["name_es"] for p in pericopae))
    print("Total unique pericope names: %d" % len(unique_names))

    # Build translation map
    translations = load_explicit_translations()

    # Apply patterns for names not in explicit translations
    pattern_count = 0
    untranslated = []
    for name in unique_names:
        if name in translations:
            continue
        en = apply_patterns(name)
        if en:
            translations[name] = en
            pattern_count += 1
        else:
            untranslated.append(name)

    print("From explicit file: %d" % (len(translations) - pattern_count))
    print("From patterns: %d" % pattern_count)
    print("Untranslated: %d" % len(untranslated))

    # Apply translations
    applied = 0
    missing = 0
    for p in pericopae:
        en = translations.get(p["name_es"])
        if en:
            p["name_en"] = en
            applied += 1
        else:
            missing += 1

    with open(PERI_PATH, "w", encoding="utf-8") as f:
        json.dump(pericopae, f, ensure_ascii=False, indent=2)

    print("\nApplied: %d / %d" % (applied, len(pericopae)))
    print("Missing: %d" % missing)

    if untranslated:
        print("\nUntranslated names (first 50):")
        for n in untranslated[:50]:
            print("  %s" % n)
        # Write untranslated to file for review
        with open("C:/own/alejandria/data/scripture_structure/_untranslated.json", "w", encoding="utf-8") as f:
            json.dump(untranslated, f, ensure_ascii=False, indent=2)
        print("\nFull list written to _untranslated.json")


if __name__ == "__main__":
    main()

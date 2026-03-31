#!/usr/bin/env python3
"""Add missing entities from P6 Phases 8-13 relations to the gazetteer."""

import json
from pathlib import Path

ENTITIES_PATH = Path(__file__).resolve().parent.parent / "src" / "alejandria" / "knowledge" / "gazetteers" / "entities.json"

NEW_ENTITIES = {
    "person": [
        {"name": "Aaron (son of Mosiah)", "aliases": ["Aaron hijo de Mosiah"]},
        {"name": "Ammon (son of Mosiah)", "aliases": ["Ammon hijo de Mosiah", "Ammon"]},
        {"name": "Angel of the Lord", "aliases": ["Angel del Senor"]},
        {"name": "Ishmael (companion of Lehi)", "aliases": ["Ismael"]},
        {"name": "Joseph (patriarch)", "aliases": ["Jose el patriarca", "Joseph son of Jacob"]},
        {"name": "King Lamoni's Father", "aliases": ["Padre del rey Lamoni", "Father of Lamoni"]},
        {"name": "Lamoni", "aliases": ["Rey Lamoni", "King Lamoni"]},
        {"name": "Nephi (disciple)", "aliases": ["Nefi discipulo", "Nephi son of Nephi"]},
        {"name": "Zeezrom", "aliases": []},
        {"name": "Zerahemnah", "aliases": []},
    ],
    "people": [
        {"name": "Twelve Apostles (NT)", "aliases": ["Los Doce Apostoles", "The Twelve"]},
    ],
    "object": [
        {"name": "Brazen Serpent", "aliases": ["Serpiente de Bronce", "Nehushtan"]},
        {"name": "Bread", "aliases": ["Pan"]},
        {"name": "Wine", "aliases": ["Vino"]},
        {"name": "Sword", "aliases": ["Espada"]},
        {"name": "Rock in Horeb", "aliases": ["Roca de Horeb"]},
        {"name": "Temple Veil", "aliases": ["Velo del Templo"]},
        {"name": "Small Plates of Nephi", "aliases": ["Planchas Menores de Nefi"]},
        {"name": "Large Plates of Nephi", "aliases": ["Planchas Mayores de Nefi"]},
        {"name": "Plates of Mormon", "aliases": ["Planchas de Mormon"]},
        {"name": "Plates of Ether", "aliases": ["Planchas de Eter"]},
    ],
    "concept": [
        # Symbols from Phase 9
        {"name": "Olive Tree", "aliases": ["Olivo", "Arbol de olivo"]},
        {"name": "Vine", "aliases": ["Vid"]},
        {"name": "Shepherd", "aliases": ["Pastor", "Buen Pastor"]},
        {"name": "Cornerstone", "aliases": ["Piedra Angular"]},
        {"name": "Lamb", "aliases": ["Cordero"]},
        {"name": "Lion of Judah", "aliases": ["Leon de Juda"]},
        {"name": "Passover Lamb", "aliases": ["Cordero Pascual"]},
        {"name": "Fire", "aliases": ["Fuego"]},
        {"name": "Water", "aliases": ["Agua"]},
        {"name": "Great and Spacious Building", "aliases": ["Grande y espacioso edificio"]},
        {"name": "Mist of Darkness", "aliases": ["Niebla de tinieblas"]},
        {"name": "River of Water", "aliases": ["Rio de agua"]},
        # Typology targets
        {"name": "Atonement of Christ", "aliases": ["Expiacion de Cristo"]},
        {"name": "Day of Atonement", "aliases": ["Dia de la Expiacion", "Yom Kippur"]},
        {"name": "Body of Christ", "aliases": ["Cuerpo de Cristo"]},
        {"name": "Blood of Christ", "aliases": ["Sangre de Cristo"]},
        {"name": "Love of God", "aliases": ["Amor de Dios"]},
        {"name": "Word of God", "aliases": ["Palabra de Dios"]},
        {"name": "Pride of the World", "aliases": ["Orgullo del mundo"]},
        {"name": "Depths of Hell", "aliases": ["Profundidades del infierno"]},
        {"name": "Temptations of the Devil", "aliases": ["Tentaciones del diablo"]},
        {"name": "Living Water / Holy Ghost", "aliases": ["Agua Viva"]},
        {"name": "White Garments", "aliases": ["Vestiduras blancas"]},
        {"name": "Suffering Servant", "aliases": ["Siervo Sufriente"]},
        {"name": "Righteousness", "aliases": ["Rectitud", "Justicia"]},
        # Prophecy fulfillments
        {"name": "Birth of Immanuel", "aliases": ["Nacimiento de Emanuel"]},
        {"name": "Birth of Christ", "aliases": ["Nacimiento de Cristo"]},
        {"name": "Ministry of Christ", "aliases": ["Ministerio de Cristo"]},
        {"name": "Restoration of gospel", "aliases": ["Restauracion del evangelio"]},
        {"name": "Restoration of Israel", "aliases": ["Restauracion de Israel"]},
        {"name": "Gathering of Israel", "aliases": ["Recogimiento de Israel"]},
        {"name": "Columbus discovery", "aliases": ["Descubrimiento de Colon"]},
        {"name": "American Revolution", "aliases": ["Revolucion americana"]},
        {"name": "Destruction of Jerusalem", "aliases": ["Destruccion de Jerusalen"]},
        {"name": "Destruction of Nephites", "aliases": ["Destruccion de los nefitas"]},
        {"name": "Signs of Christ's birth", "aliases": ["Senales del nacimiento de Cristo"]},
        {"name": "Signs of Christ's death", "aliases": ["Senales de la muerte de Cristo"]},
        {"name": "End times", "aliases": ["Ultimos dias", "Tiempos finales"]},
        {"name": "Outpouring of the Spirit", "aliases": ["Derramamiento del Espiritu"]},
        {"name": "Elijah before great day", "aliases": ["Elias antes del gran dia"]},
        {"name": "Four kingdoms and God's kingdom", "aliases": ["Cuatro reinos y el reino de Dios"]},
        {"name": "Son of Man coming in clouds", "aliases": ["Hijo del Hombre en las nubes"]},
        # Visions
        {"name": "God on throne", "aliases": ["Dios en el trono"]},
        {"name": "Valley of dry bones", "aliases": ["Valle de huesos secos"]},
        {"name": "Four beasts", "aliases": ["Cuatro bestias"]},
        {"name": "God the Father and Jesus Christ", "aliases": ["Dios el Padre y Jesucristo"]},
        {"name": "Three degrees of glory", "aliases": ["Tres grados de gloria"]},
        {"name": "God and all creation", "aliases": ["Dios y toda la creacion"]},
        {"name": "God weeping", "aliases": ["Dios llorando"]},
        {"name": "Finger of God", "aliases": ["Dedo de Dios"]},
        {"name": "All inhabitants of earth", "aliases": ["Todos los habitantes de la tierra"]},
        # Priesthood / Restoration
        {"name": "Sealing Power", "aliases": ["Poder sellador"]},
        {"name": "Temple Ordinances", "aliases": ["Ordenanzas del templo"]},
        # Genre types
        {"name": "Narrative", "aliases": ["Narrativa"]},
        {"name": "Law", "aliases": ["Ley"]},
        {"name": "Poetry", "aliases": ["Poesia"]},
        {"name": "Poetry/Hymn", "aliases": ["Poesia/Himno"]},
        {"name": "Poetry/Lament", "aliases": ["Poesia/Lamento"]},
        {"name": "Wisdom Literature", "aliases": ["Literatura sapiencial"]},
        {"name": "Prophecy/Apocalyptic", "aliases": ["Profecia/Apocaliptica"]},
        {"name": "Apocalyptic", "aliases": ["Apocaliptica"]},
        {"name": "Gospel", "aliases": ["Evangelio"]},
        {"name": "Epistle", "aliases": ["Epistola"]},
        {"name": "Epistle/Homily", "aliases": ["Epistola/Homilia"]},
        {"name": "Epistle/Exhortation", "aliases": ["Epistola/Exhortacion"]},
        {"name": "History", "aliases": ["Historia"]},
        {"name": "Narrative/Law", "aliases": ["Narrativa/Ley"]},
        {"name": "Narrative/Prophecy", "aliases": ["Narrativa/Profecia"]},
        {"name": "Prophecy/Exhortation", "aliases": ["Profecia/Exhortacion"]},
        {"name": "Narrative/Sermon", "aliases": ["Narrativa/Sermon"]},
        {"name": "Gospel Narrative", "aliases": ["Narrativa evangelica"]},
        {"name": "Narrative/Abridgment", "aliases": ["Narrativa/Compendio"]},
        {"name": "Narrative/Revelation", "aliases": ["Narrativa/Revelacion"]},
        {"name": "Narrative/Cosmology", "aliases": ["Narrativa/Cosmologia"]},
    ],
    "period": [
        {"name": "Adamic Dispensation", "aliases": ["Dispensacion adamica"]},
        {"name": "Dispensation of Enoch", "aliases": ["Dispensacion de Enoc"]},
        {"name": "Dispensation of Noah", "aliases": ["Dispensacion de Noe"]},
        {"name": "Dispensation of Abraham", "aliases": ["Dispensacion de Abraham"]},
        {"name": "Dispensation of Moses", "aliases": ["Dispensacion de Moises"]},
        {"name": "Meridian of Time", "aliases": ["Meridiano de los tiempos"]},
        {"name": "Dispensation of the Fulness of Times", "aliases": ["Dispensacion del cumplimiento de los tiempos"]},
    ],
}


def main():
    with open(ENTITIES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    total_before = sum(len(v) for v in data.values())
    print(f"=== Before: {total_before} entities ===")

    added = 0
    for etype, entries in NEW_ENTITIES.items():
        existing_names = {e["name"].lower() for e in data.get(etype, [])}
        for entry in entries:
            if entry["name"].lower() not in existing_names:
                data.setdefault(etype, []).append(entry)
                added += 1

    with open(ENTITIES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_after = sum(len(v) for v in data.values())
    print(f"=== After: {total_after} entities (added {added}) ===")


if __name__ == "__main__":
    main()

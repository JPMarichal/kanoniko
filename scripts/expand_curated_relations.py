#!/usr/bin/env python3
"""Expand relations.json with curated data from P6 Phases 8-12.

Adds relation types for:
- Phase 8: Citations/Intertextuality (QUOTES, ALLUDES_TO, JST_OF)
- Phase 9: Typology/Symbolism (TYPE_OF, SYMBOLIZES, PROPHECY_OF)
- Phase 10: Covenants/Priesthood (COVENANT_WITH, HOLDS_PRIESTHOOD, CONFERRED_KEYS_TO, etc.)
- Phase 11: Extended (DESCENDANT_OF, CONQUERED, CONVERTED_BY, SAW_IN_VISION, etc.)
- Phase 12: LDS Dispensational (DISPENSATION_HEAD, RESTORED, RECORD_KEPT_BY, ABRIDGED_BY, etc.)
- Phase 13: Literary (CHIASM_IN, GENRE_OF)
"""

import json
from pathlib import Path

RELATIONS_PATH = Path(__file__).resolve().parent.parent / "src" / "alejandria" / "knowledge" / "gazetteers" / "relations.json"

def r(from_name, from_type, to_name, to_type, source_ref, confidence="curated", **kwargs):
    """Helper to build a relation dict."""
    d = {
        "from": {"name": from_name, "type": from_type},
        "to": {"name": to_name, "type": to_type},
        "source_ref": source_ref,
        "confidence": confidence,
    }
    d.update(kwargs)
    return d


NEW_RELATIONS = {
    # ══════════════════════════════════════════════════════════════════
    # Phase 8: Citations and Intertextuality
    # ══════════════════════════════════════════════════════════════════
    "QUOTES": [
        # Jesus quoting OT
        r("Jesus Christ", "person", "Deuteronomy 6:5", "scripture", "Matthew 22:37", verbatim=True),
        r("Jesus Christ", "person", "Leviticus 19:18", "scripture", "Matthew 22:39", verbatim=True),
        r("Jesus Christ", "person", "Psalm 22:1", "scripture", "Matthew 27:46", verbatim=True),
        r("Jesus Christ", "person", "Isaiah 61:1-2", "scripture", "Luke 4:18-19", verbatim=True),
        r("Jesus Christ", "person", "Psalm 110:1", "scripture", "Matthew 22:44", verbatim=True),
        r("Jesus Christ", "person", "Deuteronomy 8:3", "scripture", "Matthew 4:4", verbatim=True),
        r("Jesus Christ", "person", "Isaiah 29:13", "scripture", "Matthew 15:8-9", verbatim=True),
        r("Jesus Christ", "person", "Zechariah 13:7", "scripture", "Matthew 26:31"),
        # Paul quoting OT
        r("Paul", "person", "Genesis 15:6", "scripture", "Romans 4:3", verbatim=True),
        r("Paul", "person", "Habakkuk 2:4", "scripture", "Romans 1:17", verbatim=True),
        r("Paul", "person", "Psalm 51:4", "scripture", "Romans 3:4"),
        r("Paul", "person", "Isaiah 59:20-21", "scripture", "Romans 11:26-27"),
        r("Paul", "person", "Isaiah 28:11-12", "scripture", "1 Corinthians 14:21"),
        r("Paul", "person", "Hosea 2:23", "scripture", "Romans 9:25"),
        r("Paul", "person", "Psalm 68:18", "scripture", "Ephesians 4:8"),
        # Peter quoting OT
        r("Peter", "person", "Joel 2:28-32", "scripture", "Acts 2:16-21", verbatim=True),
        r("Peter", "person", "Psalm 16:8-11", "scripture", "Acts 2:25-28", verbatim=True),
        r("Peter", "person", "Isaiah 28:16", "scripture", "1 Peter 2:6"),
        # BofM quoting Isaiah
        r("Nephi", "person", "Isaiah 48", "scripture", "1 Nephi 20", verbatim=True),
        r("Nephi", "person", "Isaiah 49", "scripture", "1 Nephi 21", verbatim=True),
        r("Nephi", "person", "Isaiah 2-14", "scripture", "2 Nephi 12-24", verbatim=True),
        r("Jacob (son of Lehi)", "person", "Isaiah 50", "scripture", "2 Nephi 7", verbatim=True),
        r("Jacob (son of Lehi)", "person", "Isaiah 51-52", "scripture", "2 Nephi 8", verbatim=True),
        r("Abinadi", "person", "Isaiah 53", "scripture", "Mosiah 14", verbatim=True),
        # Jesus quoting in 3 Nephi
        r("Jesus Christ", "person", "Malachi 3-4", "scripture", "3 Nephi 24-25", verbatim=True),
        r("Jesus Christ", "person", "Isaiah 54", "scripture", "3 Nephi 22", verbatim=True),
    ],

    "ALLUDES_TO": [
        r("Alma the Younger", "person", "Isaiah 6:10", "scripture", "Alma 36:20", note="Alma's conversion echoes Isaiah's cleansing"),
        r("Nephi", "person", "Exodus 14", "scripture", "1 Nephi 4:2", note="Nephi references Red Sea crossing"),
        r("King Benjamin", "person", "Isaiah 53:3-5", "scripture", "Mosiah 3:7-9", note="Suffering servant language"),
        r("Mormon", "person", "1 Corinthians 13", "scripture", "Moroni 7:45-48", note="Charity discourse parallels Paul"),
        r("Moroni", "person", "Hebrews 11", "scripture", "Ether 12:6-22", note="Faith chapter parallels"),
        r("Jacob (son of Lehi)", "person", "Genesis 25:23", "scripture", "2 Nephi 25:23", note="Grace after all we can do echoes election"),
    ],

    "JST_OF": [
        r("Genesis 50:24-38 (JST)", "scripture", "Genesis 50:24-26", "scripture", "JST Genesis 50", change_type="expansion", note="Prophecy of Moses and Joseph Smith"),
        r("Matthew 4 (JST)", "scripture", "Matthew 4:1-11", "scripture", "JST Matthew 4", change_type="revision", note="Jesus led by Spirit, not tempted of devil"),
        r("Exodus 33:20 (JST)", "scripture", "Exodus 33:20", "scripture", "JST Exodus 33", change_type="correction", note="No sinful man shall see God"),
        r("Romans 4:16 (JST)", "scripture", "Romans 4:16", "scripture", "JST Romans", change_type="clarification"),
        r("1 Timothy 6:15-16 (JST)", "scripture", "1 Timothy 6:15-16", "scripture", "JST 1 Timothy", change_type="clarification", note="God dwelling in light"),
        r("Hebrews 11:40 (JST)", "scripture", "Hebrews 11:40", "scripture", "JST Hebrews", change_type="expansion"),
    ],

    # ══════════════════════════════════════════════════════════════════
    # Phase 9: Typology, Symbolism, and Prophecy
    # ══════════════════════════════════════════════════════════════════
    "TYPE_OF": [
        # Major OT types pointing to Christ
        r("Melchizedek", "person", "Jesus Christ", "person", "Hebrews 7:1-3", note="Priest of Most High God without genealogy"),
        r("Isaac", "person", "Jesus Christ", "person", "Hebrews 11:17-19", note="Offered son, received back as figure"),
        r("Moses", "person", "Jesus Christ", "person", "Deuteronomy 18:15; Acts 3:22", note="Prophet like unto Moses"),
        r("David", "person", "Jesus Christ", "person", "Acts 2:30-31; Psalm 89:3-4", note="King whose throne endures forever"),
        r("Jonah", "person", "Jesus Christ", "person", "Matthew 12:40", note="Three days in belly of whale"),
        r("Joseph (patriarch)", "person", "Jesus Christ", "person", "Genesis 37-50", note="Sold by brethren, became savior"),
        r("Adam", "person", "Jesus Christ", "person", "Romans 5:14; 1 Corinthians 15:45", note="First Adam / last Adam"),
        r("Passover Lamb", "concept", "Jesus Christ", "person", "1 Corinthians 5:7; John 1:29"),
        r("Brazen Serpent", "object", "Jesus Christ", "person", "John 3:14; 1 Nephi 17:41"),
        r("Ark of the Covenant", "object", "Jesus Christ", "person", "Hebrews 9:4-5"),
        r("Temple Veil", "object", "Jesus Christ", "person", "Hebrews 10:20", note="His flesh"),
        r("Day of Atonement", "concept", "Atonement of Christ", "concept", "Hebrews 9:7-14"),
        r("Manna", "object", "Jesus Christ", "person", "John 6:31-35", note="Bread from heaven"),
        r("Rock in Horeb", "object", "Jesus Christ", "person", "1 Corinthians 10:4"),
    ],

    "SYMBOLIZES": [
        r("Olive Tree", "concept", "House of Israel", "people", "Romans 11:17-24; Jacob 5"),
        r("Bread", "object", "Body of Christ", "concept", "Matthew 26:26; 3 Nephi 18:7"),
        r("Wine", "object", "Blood of Christ", "concept", "Matthew 26:27-28; 3 Nephi 18:11"),
        r("Water", "concept", "Living Water / Holy Ghost", "concept", "John 7:38-39; 1 Nephi 11:25"),
        r("Vine", "concept", "Jesus Christ", "person", "John 15:1-5"),
        r("Shepherd", "concept", "Jesus Christ", "person", "John 10:11; Psalm 23:1; 1 Nephi 13:41"),
        r("Cornerstone", "concept", "Jesus Christ", "person", "Ephesians 2:20; Psalm 118:22"),
        r("Lamb", "concept", "Jesus Christ", "person", "John 1:29; Revelation 5:6"),
        r("Lion of Judah", "concept", "Jesus Christ", "person", "Revelation 5:5"),
        r("Tree of Life", "concept", "Love of God", "concept", "1 Nephi 11:21-25"),
        r("Iron Rod", "concept", "Word of God", "concept", "1 Nephi 11:25"),
        r("Great and Spacious Building", "concept", "Pride of the World", "concept", "1 Nephi 11:35-36"),
        r("River of Water", "concept", "Depths of Hell", "concept", "1 Nephi 12:16; 15:26-29"),
        r("Mist of Darkness", "concept", "Temptations of the Devil", "concept", "1 Nephi 12:17"),
        r("White Garments", "concept", "Righteousness", "concept", "Revelation 3:4-5; 3 Nephi 19:25"),
        r("Fire", "concept", "Holy Ghost", "concept", "Matthew 3:11; 2 Nephi 31:17"),
        r("Sword", "object", "Word of God", "concept", "Ephesians 6:17; Hebrews 4:12; 1 Nephi 16:2"),
    ],

    "PROPHECY_OF": [
        # Major prophecies with fulfillment status
        r("Isaiah", "person", "Birth of Immanuel", "concept", "Isaiah 7:14; Matthew 1:22-23", fulfillment="fulfilled"),
        r("Isaiah", "person", "Suffering Servant", "concept", "Isaiah 53; Mosiah 14", fulfillment="fulfilled"),
        r("Micah", "person", "Bethlehem birthplace", "concept", "Micah 5:2; Matthew 2:5-6", fulfillment="fulfilled"),
        r("Daniel", "person", "Four kingdoms and God's kingdom", "concept", "Daniel 2:31-45", fulfillment="dual"),
        r("Daniel", "person", "Son of Man coming in clouds", "concept", "Daniel 7:13-14", fulfillment="dual"),
        r("Malachi", "person", "Elijah before great day", "concept", "Malachi 4:5-6; D&C 110:13-16", fulfillment="fulfilled"),
        r("Joel", "person", "Outpouring of the Spirit", "concept", "Joel 2:28-32; Acts 2:16-21", fulfillment="dual"),
        r("Nephi", "person", "Columbus discovery", "concept", "1 Nephi 13:12", fulfillment="fulfilled"),
        r("Nephi", "person", "American Revolution", "concept", "1 Nephi 13:16-19", fulfillment="fulfilled"),
        r("Nephi", "person", "Restoration of gospel", "concept", "1 Nephi 13:34-37", fulfillment="fulfilled"),
        r("Lehi", "person", "Destruction of Jerusalem", "concept", "1 Nephi 1:13,18", fulfillment="fulfilled"),
        r("Samuel the Lamanite", "person", "Signs of Christ's birth", "concept", "Helaman 14:2-7; 3 Nephi 1:15-21", fulfillment="fulfilled"),
        r("Samuel the Lamanite", "person", "Signs of Christ's death", "concept", "Helaman 14:20-27; 3 Nephi 8:5-19", fulfillment="fulfilled"),
        r("Ezekiel", "person", "Restoration of Israel", "concept", "Ezekiel 37:15-22", fulfillment="dual"),
        r("Isaiah", "person", "Gathering of Israel", "concept", "Isaiah 11:11-12; 2 Nephi 21:11-12", fulfillment="in_progress"),
        r("John the Revelator", "person", "Second Coming", "concept", "Revelation 19:11-16", fulfillment="pending"),
    ],

    # ══════════════════════════════════════════════════════════════════
    # Phase 10: Covenants, Priesthood, and Ordinances
    # ══════════════════════════════════════════════════════════════════
    "COVENANT_WITH": [
        r("God", "person", "Adam", "person", "Moses 6:51-68", covenant_name="Adamic"),
        r("God", "person", "Noah", "person", "Genesis 9:8-17", covenant_name="Noahic", note="Rainbow sign"),
        r("God", "person", "Abraham", "person", "Genesis 17:1-8; Abraham 2:6-11", covenant_name="Abrahamic"),
        r("God", "person", "Isaac", "person", "Genesis 26:3-5", covenant_name="Abrahamic renewal"),
        r("God", "person", "Jacob (patriarch)", "person", "Genesis 35:10-12", covenant_name="Abrahamic renewal"),
        r("God", "person", "Moses", "person", "Exodus 19:5-6; 24:3-8", covenant_name="Mosaic"),
        r("God", "person", "David", "person", "2 Samuel 7:12-16; Psalm 89:3-4", covenant_name="Davidic"),
        r("Jesus Christ", "person", "Twelve Apostles (NT)", "people", "Luke 22:20; Matthew 26:28", covenant_name="New Covenant"),
        r("Jesus Christ", "person", "Nephites", "people", "3 Nephi 20:25-27", covenant_name="New Covenant"),
        r("God", "person", "Joseph Smith", "person", "D&C 1:17-22; 84:33-40", covenant_name="New and Everlasting"),
    ],

    "HOLDS_PRIESTHOOD": [
        r("Melchizedek", "person", "Melchizedek Priesthood", "concept", "Genesis 14:18; Alma 13:14-19"),
        r("Aaron", "person", "Aaronic Priesthood", "concept", "Exodus 28:1; D&C 84:18"),
        r("Peter", "person", "Melchizedek Priesthood", "concept", "Matthew 16:18-19"),
        r("James", "person", "Melchizedek Priesthood", "concept", "Mark 9:2"),
        r("John", "person", "Melchizedek Priesthood", "concept", "Mark 9:2"),
        r("Joseph Smith", "person", "Melchizedek Priesthood", "concept", "D&C 27:12-13"),
        r("Joseph Smith", "person", "Aaronic Priesthood", "concept", "D&C 13:1"),
        r("Oliver Cowdery", "person", "Aaronic Priesthood", "concept", "D&C 13:1"),
        r("Oliver Cowdery", "person", "Melchizedek Priesthood", "concept", "D&C 27:12-13"),
        r("Alma the Elder", "person", "Melchizedek Priesthood", "concept", "Mosiah 18:13-18"),
    ],

    "CONFERRED_KEYS_TO": [
        r("John the Baptist", "person", "Joseph Smith", "person", "D&C 13:1", keys="Aaronic Priesthood"),
        r("John the Baptist", "person", "Oliver Cowdery", "person", "D&C 13:1", keys="Aaronic Priesthood"),
        r("Peter", "person", "Joseph Smith", "person", "D&C 27:12-13", keys="Melchizedek Priesthood"),
        r("James", "person", "Joseph Smith", "person", "D&C 27:12-13", keys="Melchizedek Priesthood"),
        r("John", "person", "Joseph Smith", "person", "D&C 27:12-13", keys="Melchizedek Priesthood"),
        r("Moses", "person", "Joseph Smith", "person", "D&C 110:11", keys="Gathering of Israel"),
        r("Elias", "person", "Joseph Smith", "person", "D&C 110:12", keys="Dispensation of Abraham"),
        r("Elijah", "person", "Joseph Smith", "person", "D&C 110:13-16", keys="Sealing power"),
    ],

    "BAPTIZED_BY": [
        r("Jesus Christ", "person", "John the Baptist", "person", "Matthew 3:13-16"),
        r("Alma the Elder", "person", "Alma the Elder", "person", "Mosiah 18:13-14", note="Self-baptism at Waters of Mormon"),
        r("Nephi (son of Helaman)", "person", "Nephi (disciple)", "person", "3 Nephi 19:11-12", note="Baptized the twelve"),
        r("Joseph Smith", "person", "Oliver Cowdery", "person", "JS-H 1:71", note="After Aaronic Priesthood restoration"),
        r("Oliver Cowdery", "person", "Joseph Smith", "person", "JS-H 1:71"),
    ],

    "ORDAINED_BY": [
        r("Aaron", "person", "Moses", "person", "Exodus 28:1; Leviticus 8:12"),
        r("Joshua", "person", "Moses", "person", "Numbers 27:18-23; Deuteronomy 34:9"),
        r("Twelve Apostles (NT)", "people", "Jesus Christ", "person", "Mark 3:14; John 15:16"),
        r("Paul", "person", "Ananias", "person", "Acts 9:17-18"),
        r("Timothy", "person", "Paul", "person", "1 Timothy 4:14; 2 Timothy 1:6"),
    ],

    # ══════════════════════════════════════════════════════════════════
    # Phase 11: Extended Relations
    # ══════════════════════════════════════════════════════════════════
    "DESCENDANT_OF": [
        # Patriarchal genealogy (key links)
        r("Seth", "person", "Adam", "person", "Genesis 5:3"),
        r("Enoch", "person", "Seth", "person", "Genesis 5:6-18"),
        r("Noah", "person", "Enoch", "person", "Genesis 5:28-29", note="Through Methuselah and Lamech"),
        r("Abraham", "person", "Noah", "person", "Genesis 11:10-26", note="Through Shem"),
        r("Jesus Christ", "person", "Abraham", "person", "Matthew 1:1"),
        r("Jesus Christ", "person", "David", "person", "Matthew 1:1; Romans 1:3"),
        r("Jesus Christ", "person", "Judah", "person", "Hebrews 7:14"),
        r("Ephraim", "person", "Joseph (patriarch)", "person", "Genesis 41:50-52"),
        r("Manasseh", "person", "Joseph (patriarch)", "person", "Genesis 41:50-52"),
        r("Lehi", "person", "Manasseh", "person", "Alma 10:3"),
        r("Ishmael (companion of Lehi)", "person", "Ephraim", "person", "Journal of Discourses 23:184", confidence="metadata"),
    ],

    "CONQUERED": [
        r("Joshua", "person", "Jericho", "place", "Joshua 6:20-21"),
        r("David", "person", "Jerusalem", "place", "2 Samuel 5:6-9"),
        r("Nebuchadnezzar", "person", "Jerusalem", "place", "2 Kings 25:1-10"),
        r("Cyrus", "person", "Babylon", "place", "Daniel 5:30-31", note="Through Darius"),
        r("Captain Moroni", "person", "Zerahemnah", "person", "Alma 44:12-15"),
        r("Nephites", "people", "Lamanites", "people", "Alma 44:20-24", note="Battle at Sidon"),
        r("Lamanites", "people", "Nephites", "people", "Mormon 6:10-15", note="Final destruction at Cumorah"),
    ],

    "CONVERTED_BY": [
        r("Alma the Younger", "person", "Angel of the Lord", "person", "Mosiah 27:11-16"),
        r("Sons of Mosiah", "people", "Angel of the Lord", "person", "Mosiah 27:11-16"),
        r("Lamoni", "person", "Ammon (son of Mosiah)", "person", "Alma 18:40-43; 19:12-13"),
        r("Anti-Nephi-Lehies", "people", "Sons of Mosiah", "people", "Alma 23:1-7"),
        r("Paul", "person", "Jesus Christ", "person", "Acts 9:3-6"),
        r("Cornelius", "person", "Peter", "person", "Acts 10:44-48"),
        r("King Lamoni's Father", "person", "Aaron (son of Mosiah)", "person", "Alma 22:15-18"),
        r("Zeezrom", "person", "Alma the Younger", "person", "Alma 15:3-12"),
        r("Enos", "person", "Jacob (son of Lehi)", "person", "Enos 1:1-4", note="Father's teachings"),
    ],

    "SAW_IN_VISION": [
        r("Lehi", "person", "Tree of Life", "concept", "1 Nephi 8:10-12"),
        r("Nephi", "person", "Birth of Christ", "concept", "1 Nephi 11:13-21"),
        r("Nephi", "person", "Ministry of Christ", "concept", "1 Nephi 11:24-33"),
        r("Nephi", "person", "Destruction of Nephites", "concept", "1 Nephi 12:19-20"),
        r("Nephi", "person", "Columbus discovery", "concept", "1 Nephi 13:12"),
        r("John the Revelator", "person", "End times", "concept", "Revelation 1-22"),
        r("Isaiah", "person", "God on throne", "concept", "Isaiah 6:1-4"),
        r("Ezekiel", "person", "Valley of dry bones", "concept", "Ezekiel 37:1-14"),
        r("Daniel", "person", "Four beasts", "concept", "Daniel 7:1-14"),
        r("Joseph Smith", "person", "God the Father and Jesus Christ", "concept", "JS-H 1:17", note="First Vision"),
        r("Joseph Smith", "person", "Three degrees of glory", "concept", "D&C 76:19-24"),
        r("Joseph Smith", "person", "Celestial kingdom", "concept", "D&C 137:1-5"),
        r("Moses", "person", "God and all creation", "concept", "Moses 1:1-8, 27-29"),
        r("Enoch", "person", "God weeping", "concept", "Moses 7:28-37"),
        r("Brother of Jared", "person", "Finger of God", "concept", "Ether 3:4-6"),
        r("Brother of Jared", "person", "All inhabitants of earth", "concept", "Ether 3:25"),
    ],

    # ══════════════════════════════════════════════════════════════════
    # Phase 12: LDS Dispensational
    # ══════════════════════════════════════════════════════════════════
    "DISPENSATION_HEAD": [
        r("Adam", "person", "Adamic Dispensation", "period", "Moses 5-6; D&C 107:41-53"),
        r("Enoch", "person", "Dispensation of Enoch", "period", "Moses 6-7"),
        r("Noah", "person", "Dispensation of Noah", "period", "Genesis 6-9; Moses 8"),
        r("Abraham", "person", "Dispensation of Abraham", "period", "Abraham 1-2; Genesis 12-25"),
        r("Moses", "person", "Dispensation of Moses", "period", "Exodus-Deuteronomy"),
        r("Jesus Christ", "person", "Meridian of Time", "period", "Matthew-John; 3 Nephi 11-28"),
        r("Joseph Smith", "person", "Dispensation of the Fulness of Times", "period", "D&C 27:13; 128:18; 138:53"),
    ],

    "RESTORED": [
        r("Joseph Smith", "person", "Aaronic Priesthood", "concept", "D&C 13; JS-H 1:68-72"),
        r("Joseph Smith", "person", "Melchizedek Priesthood", "concept", "D&C 27:12-13"),
        r("Joseph Smith", "person", "Book of Mormon", "concept", "JS-H 1:59-62"),
        r("Joseph Smith", "person", "Baptism", "concept", "D&C 13:1; 20:72-74"),
        r("Joseph Smith", "person", "Sealing Power", "concept", "D&C 110:13-16"),
        r("Joseph Smith", "person", "Gathering of Israel", "concept", "D&C 110:11"),
        r("Joseph Smith", "person", "Temple Ordinances", "concept", "D&C 124:33-41"),
    ],

    "RECORD_KEPT_BY": [
        r("Small Plates of Nephi", "object", "Nephi", "person", "1 Nephi 1:1-3; 19:1-6"),
        r("Small Plates of Nephi", "object", "Jacob (son of Lehi)", "person", "Jacob 1:1-4"),
        r("Small Plates of Nephi", "object", "Enos", "person", "Enos 1:1"),
        r("Small Plates of Nephi", "object", "Jarom", "person", "Jarom 1:1"),
        r("Small Plates of Nephi", "object", "Omni", "person", "Omni 1:1"),
        r("Large Plates of Nephi", "object", "Nephi", "person", "1 Nephi 9:2-4"),
        r("Large Plates of Nephi", "object", "Mormon", "person", "Words of Mormon 1:3-5", note="Abridged by Mormon"),
        r("Plates of Mormon", "object", "Mormon", "person", "Mormon 1:1-4"),
        r("Plates of Ether", "object", "Ether", "person", "Ether 1:1-2; 15:33"),
        r("Brass Plates", "object", "Laban", "person", "1 Nephi 3:3-4"),
        r("Gold Plates", "object", "Moroni", "person", "Mormon 8:1; Moroni 10:2"),
    ],

    "ABRIDGED_BY": [
        r("Book of Mosiah", "scripture", "Mormon", "person", "Words of Mormon 1:3-5"),
        r("Book of Alma", "scripture", "Mormon", "person", "Alma 1:1"),
        r("Book of Helaman", "scripture", "Mormon", "person", "Helaman 1:1"),
        r("3 Nephi", "scripture", "Mormon", "person", "3 Nephi 5:8-12"),
        r("4 Nephi", "scripture", "Mormon", "person", "4 Nephi 1:1"),
        r("Book of Mormon (record)", "scripture", "Mormon", "person", "Mormon 1:1"),
        r("Book of Ether", "scripture", "Moroni", "person", "Ether 1:1-2"),
    ],

    # ══════════════════════════════════════════════════════════════════
    # Phase 13: Literary (curated high-confidence)
    # ══════════════════════════════════════════════════════════════════
    "CHIASM_IN": [
        r("Alma 36", "scripture", "Alma the Younger", "person", "Alma 36", note="Classic conversion chiasm, Welch 1969"),
        r("Mosiah 3:18-19", "scripture", "King Benjamin", "person", "Mosiah 3:18-19", note="Natural man chiasm"),
        r("1 Nephi 15:13-16", "scripture", "Nephi", "person", "1 Nephi 15:13-16"),
        r("Leviticus 24:13-23", "scripture", "Moses", "person", "Leviticus 24:13-23"),
        r("Psalm 3", "scripture", "David", "person", "Psalm 3"),
        r("Isaiah 55:8-9", "scripture", "Isaiah", "person", "Isaiah 55:8-9"),
    ],

    "GENRE_OF": [
        # OT Genres
        r("Genesis", "scripture", "Narrative", "concept", "Genesis"),
        r("Exodus", "scripture", "Narrative/Law", "concept", "Exodus"),
        r("Leviticus", "scripture", "Law", "concept", "Leviticus"),
        r("Psalms", "scripture", "Poetry/Hymn", "concept", "Psalms"),
        r("Proverbs", "scripture", "Wisdom Literature", "concept", "Proverbs"),
        r("Ecclesiastes", "scripture", "Wisdom Literature", "concept", "Ecclesiastes"),
        r("Song of Solomon", "scripture", "Poetry", "concept", "Song of Solomon"),
        r("Isaiah", "scripture", "Prophecy", "concept", "Isaiah"),
        r("Jeremiah", "scripture", "Prophecy", "concept", "Jeremiah"),
        r("Ezekiel", "scripture", "Prophecy/Apocalyptic", "concept", "Ezekiel"),
        r("Daniel", "scripture", "Apocalyptic", "concept", "Daniel"),
        r("Job", "scripture", "Wisdom Literature", "concept", "Job"),
        r("Lamentations", "scripture", "Poetry/Lament", "concept", "Lamentations"),
        r("Ruth", "scripture", "Narrative", "concept", "Ruth"),
        r("Esther", "scripture", "Narrative", "concept", "Esther"),
        # NT Genres
        r("Matthew", "scripture", "Gospel", "concept", "Matthew"),
        r("Mark", "scripture", "Gospel", "concept", "Mark"),
        r("Luke", "scripture", "Gospel", "concept", "Luke"),
        r("John", "scripture", "Gospel", "concept", "John"),
        r("Acts", "scripture", "History", "concept", "Acts"),
        r("Romans", "scripture", "Epistle", "concept", "Romans"),
        r("Revelation", "scripture", "Apocalyptic", "concept", "Revelation"),
        r("Hebrews", "scripture", "Epistle/Homily", "concept", "Hebrews"),
        # BofM Genres
        r("1 Nephi", "scripture", "Narrative/Prophecy", "concept", "1 Nephi"),
        r("2 Nephi", "scripture", "Prophecy/Exhortation", "concept", "2 Nephi"),
        r("Book of Alma", "scripture", "Narrative/Sermon", "concept", "Alma"),
        r("3 Nephi", "scripture", "Gospel Narrative", "concept", "3 Nephi"),
        r("Ether", "scripture", "Narrative/Abridgment", "concept", "Ether"),
        r("Moroni", "scripture", "Epistle/Exhortation", "concept", "Moroni"),
        # D&C
        r("Doctrine and Covenants", "scripture", "Revelation", "concept", "D&C"),
        # PGP
        r("Book of Moses", "scripture", "Narrative/Revelation", "concept", "Moses"),
        r("Book of Abraham", "scripture", "Narrative/Cosmology", "concept", "Abraham"),
    ],
}


def main():
    # Load existing
    with open(RELATIONS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    print("=== Before ===")
    total_before = sum(len(v) for v in data.values())
    print(f"  Types: {len(data)}, Relations: {total_before}")

    # Add new types
    added = 0
    for rel_type, relations in NEW_RELATIONS.items():
        if rel_type in data:
            # Append to existing
            existing_keys = {
                (r["from"]["name"], r["to"]["name"])
                for r in data[rel_type]
            }
            new_count = 0
            for rel in relations:
                key = (rel["from"]["name"], rel["to"]["name"])
                if key not in existing_keys:
                    data[rel_type].append(rel)
                    new_count += 1
            if new_count:
                print(f"  {rel_type}: added {new_count} to existing {len(data[rel_type]) - new_count}")
            added += new_count
        else:
            data[rel_type] = relations
            print(f"  {rel_type}: NEW type with {len(relations)} relations")
            added += len(relations)

    # Write back
    with open(RELATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_after = sum(len(v) for v in data.values())
    print(f"\n=== After ===")
    print(f"  Types: {len(data)}, Relations: {total_after}")
    print(f"  Added: {added} new relations")


if __name__ == "__main__":
    main()

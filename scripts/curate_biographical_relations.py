"""One-time script to add biographical relations for major scripture characters.

WI-1: Biographical KG Curation — adds BORN_IN, DIED_IN, LIVED_IN, and enriches
existing biographical types for ~58 Tier 1 characters across all volumes.

Run: python scripts/curate_biographical_relations.py
"""
import json
from pathlib import Path

RELATIONS_PATH = Path(__file__).parent.parent / "src" / "alejandria" / "knowledge" / "gazetteers" / "relations.json"

def p(name, type_="person"):
    return {"name": name, "type": type_}

def place(name):
    return {"name": name, "type": "place"}

def role(name):
    return {"name": name, "type": "role"}

def scripture(name):
    return {"name": name, "type": "scripture"}

def concept(name):
    return {"name": name, "type": "concept"}

def period(name):
    return {"name": name, "type": "period"}

def rel(from_, to_, ref, confidence="curated"):
    return {"from": from_, "to": to_, "source_ref": ref, "confidence": confidence}


NEW_RELATIONS = {
    # ============================================================
    # BORN_IN — entirely new type
    # ============================================================
    "BORN_IN": [
        # OT
        rel(p("Abraham"), place("Ur of the Chaldees"), "Genesis 11:28,31; Abraham 2:1"),
        rel(p("Isaac"), place("Beer-lahai-roi area"), "Genesis 21:1-3"),
        rel(p("Jacob"), place("Canaan"), "Genesis 25:26"),
        rel(p("Joseph"), place("Canaan"), "Genesis 30:24"),
        rel(p("Moses"), place("Egypt"), "Exodus 2:1-2"),
        rel(p("Samuel"), place("Ramathaim-zophim"), "1 Samuel 1:1,19-20"),
        rel(p("David"), place("Bethlehem"), "1 Samuel 17:12"),
        # NT
        rel(p("Jesus Christ"), place("Bethlehem"), "Matthew 2:1; Luke 2:4-7; Alma 7:10"),
        rel(p("John the Baptist"), place("Hill country of Judea"), "Luke 1:39-40,57-60"),
        rel(p("Paul"), place("Tarsus"), "Acts 22:3"),
        # BofM
        rel(p("Nephi"), place("Jerusalem"), "1 Nephi 1:4"),
        rel(p("Jacob (son of Lehi)"), place("Wilderness"), "1 Nephi 18:7"),
        rel(p("Mormon"), place("Land Northward"), "Mormon 1:6"),
        # D&C
        rel(p("Joseph Smith"), place("Sharon, Vermont"), "JS-H 1:3"),
        rel(p("Hyrum Smith"), place("Tunbridge, Vermont"), "D&C 135:3"),
        rel(p("Brigham Young"), place("Whitingham, Vermont"), "D&C 126 header"),
        rel(p("Oliver Cowdery"), place("Wells, Vermont"), "JS-H 1:66 note"),
    ],

    # ============================================================
    # DIED_IN — entirely new type
    # ============================================================
    "DIED_IN": [
        # OT
        rel(p("Abraham"), place("Canaan"), "Genesis 25:8"),
        rel(p("Isaac"), place("Mamre/Hebron"), "Genesis 35:27-29"),
        rel(p("Jacob"), place("Egypt"), "Genesis 49:33"),
        rel(p("Joseph"), place("Egypt"), "Genesis 50:26"),
        rel(p("Moses"), place("Mount Nebo"), "Deuteronomy 34:1,5"),
        rel(p("Aaron"), place("Mount Hor"), "Numbers 20:27-28"),
        rel(p("Joshua"), place("Timnath-serah"), "Joshua 24:29-30"),
        rel(p("Samuel"), place("Ramah"), "1 Samuel 25:1"),
        rel(p("David"), place("Jerusalem"), "1 Kings 2:10-11"),
        rel(p("Solomon"), place("Jerusalem"), "1 Kings 11:43"),
        # NT
        rel(p("Jesus Christ"), place("Golgotha/Jerusalem"), "Matthew 27:33-50; John 19:17-30"),
        rel(p("John the Baptist"), place("Machaerus (Herod's prison)"), "Matthew 14:10-11"),
        # BofM
        rel(p("Lehi"), place("Promised Land"), "2 Nephi 4:12"),
        rel(p("Abinadi"), place("City of Nephi"), "Mosiah 17:13-20"),
        rel(p("Mormon"), place("Cumorah"), "Mormon 8:2-3"),
        # D&C (martyrdom details in MARTYRED_AT, this is geographic)
        rel(p("Joseph Smith"), place("Carthage, Illinois"), "D&C 135:1"),
        rel(p("Hyrum Smith"), place("Carthage, Illinois"), "D&C 135:1"),
    ],

    # ============================================================
    # LIVED_IN — new biographical type
    # ============================================================
    "LIVED_IN": [
        # OT
        rel(p("Abraham"), place("Haran"), "Genesis 11:31"),
        rel(p("Abraham"), place("Canaan"), "Genesis 12:5-6"),
        rel(p("Jacob"), place("Haran"), "Genesis 28:10; 29:1"),
        rel(p("Jacob"), place("Egypt"), "Genesis 46:6-7"),
        rel(p("Joseph"), place("Egypt"), "Genesis 39:1"),
        rel(p("Moses"), place("Egypt"), "Exodus 2:10"),
        rel(p("Moses"), place("Midian"), "Exodus 2:15,21"),
        rel(p("David"), place("Hebron"), "2 Samuel 2:11"),
        rel(p("David"), place("Jerusalem"), "2 Samuel 5:5-7"),
        rel(p("Daniel"), place("Babylon"), "Daniel 1:1-6"),
        rel(p("Esther"), place("Shushan/Susa"), "Esther 2:5-8"),
        rel(p("Ruth"), place("Bethlehem"), "Ruth 1:19,22"),
        # NT
        rel(p("Jesus Christ"), place("Nazareth"), "Matthew 2:23"),
        rel(p("Jesus Christ"), place("Capernaum"), "Matthew 4:13"),
        rel(p("Peter"), place("Capernaum"), "Matthew 8:14"),
        rel(p("Paul"), place("Tarsus"), "Acts 22:3"),
        rel(p("Paul"), place("Jerusalem"), "Acts 22:3"),
        rel(p("Mary Magdalene"), place("Magdala"), "Luke 8:2 (name implies origin)"),
        # BofM
        rel(p("Lehi"), place("Jerusalem"), "1 Nephi 1:4"),
        rel(p("Nephi"), place("Land of Nephi"), "2 Nephi 5:8"),
        rel(p("Alma the Elder"), place("Zarahemla"), "Mosiah 25:19"),
        rel(p("Mormon"), place("Zarahemla"), "Mormon 1:6"),
        # D&C
        rel(p("Joseph Smith"), place("Palmyra, New York"), "JS-H 1:3"),
        rel(p("Joseph Smith"), place("Kirtland, Ohio"), "D&C 41 header"),
        rel(p("Joseph Smith"), place("Nauvoo, Illinois"), "D&C 124 header"),
        rel(p("Brigham Young"), place("Salt Lake Valley"), "D&C 136"),
    ],

    # ============================================================
    # Additional TRAVELED_TO (enrich existing)
    # ============================================================
    "TRAVELED_TO": [
        # OT
        rel(p("Abraham"), place("Haran"), "Genesis 11:31"),
        rel(p("Jacob"), place("Haran"), "Genesis 28:10"),
        rel(p("Jacob"), place("Egypt"), "Genesis 46:6"),
        rel(p("Moses"), place("Midian"), "Exodus 2:15"),
        rel(p("Moses"), place("Egypt (return)"), "Exodus 4:20"),
        rel(p("Joshua"), place("Jericho"), "Joshua 6:1-2"),
        rel(p("Elijah"), place("Mount Horeb"), "1 Kings 19:8"),
        rel(p("Daniel"), place("Babylon"), "Daniel 1:1-6"),
        rel(p("Ruth"), place("Bethlehem"), "Ruth 1:19"),
        rel(p("Jonah"), place("Nineveh"), "Jonah 3:3"),
        # NT
        rel(p("Jesus Christ"), place("Samaria"), "John 4:4-5"),
        rel(p("Jesus Christ"), place("Bethany"), "John 11:17-18"),
        rel(p("Jesus Christ"), place("Capernaum"), "Matthew 4:13"),
        rel(p("Peter"), place("Antioch"), "Galatians 2:11"),
        rel(p("Peter"), place("Joppa"), "Acts 9:43"),
        rel(p("Peter"), place("Caesarea"), "Acts 10:24-25"),
        rel(p("Paul"), place("Antioch"), "Acts 13:1-3"),
        rel(p("Paul"), place("Jerusalem"), "Acts 21:17"),
        rel(p("Paul"), place("Philippi"), "Acts 16:12"),
        rel(p("Barnabas"), place("Cyprus"), "Acts 13:4"),
        rel(p("Philip"), place("Samaria"), "Acts 8:5"),
        # BofM
        rel(p("Lehi"), place("Valley of Lemuel"), "1 Nephi 2:10"),
        rel(p("Lehi"), place("Land Bountiful"), "1 Nephi 17:5"),
        rel(p("Alma the Younger"), place("Ammonihah"), "Alma 8:6"),
        rel(p("Alma the Younger"), place("Gideon"), "Alma 6:7"),
        rel(p("Ammon (son of Mosiah)"), place("Land of Ishmael"), "Alma 17:19"),
        rel(p("Captain Moroni"), place("Land of Manti"), "Alma 43:22"),
        rel(p("Mormon"), place("Cumorah"), "Mormon 6:2"),
        # D&C
        rel(p("Joseph Smith"), place("Kirtland, Ohio"), "D&C 41 header"),
        rel(p("Joseph Smith"), place("Independence, Missouri"), "D&C 57"),
        rel(p("Joseph Smith"), place("Nauvoo, Illinois"), "D&C 124 header"),
        rel(p("Oliver Cowdery"), place("Harmony, Pennsylvania"), "JS-H 1:66"),
        rel(p("Brigham Young"), place("Salt Lake Valley"), "D&C 136"),
    ],

    # ============================================================
    # Additional CALLED_AS (enrich)
    # ============================================================
    "CALLED_AS": [
        # OT
        rel(p("Abraham"), role("Prophet"), "Genesis 20:7; Abraham 2:6-11"),
        rel(p("Moses"), role("Prophet"), "Deuteronomy 34:10"),
        rel(p("Moses"), role("Lawgiver"), "Exodus 20:1-17"),
        rel(p("Joshua"), role("Leader of Israel"), "Joshua 1:1-2"),
        rel(p("Samuel"), role("Prophet"), "1 Samuel 3:20"),
        rel(p("Samuel"), role("Judge"), "1 Samuel 7:15"),
        rel(p("David"), role("King of Israel"), "2 Samuel 5:3"),
        rel(p("Solomon"), role("King of Israel"), "1 Kings 1:39"),
        rel(p("Isaiah"), role("Prophet"), "Isaiah 6:8-9"),
        rel(p("Jeremiah"), role("Prophet"), "Jeremiah 1:5"),
        rel(p("Daniel"), role("Governor"), "Daniel 2:48"),
        rel(p("Elijah"), role("Prophet"), "1 Kings 17:1"),
        rel(p("Elisha"), role("Prophet"), "1 Kings 19:16,19"),
        rel(p("Esther"), role("Queen"), "Esther 2:17"),
        rel(p("Enoch"), role("Prophet"), "Moses 6:26-27"),
        rel(p("Noah"), role("Prophet"), "Moses 8:19"),
        # NT
        rel(p("Jesus Christ"), role("Messiah"), "John 1:41; 4:25-26"),
        rel(p("Stephen"), role("Deacon"), "Acts 6:5"),
        rel(p("Luke"), role("Physician"), "Colossians 4:14"),
        rel(p("Mary Magdalene"), role("Witness of the Resurrection"), "John 20:16-18"),
        # BofM
        rel(p("Nephi"), role("Ruler and Teacher"), "2 Nephi 5:19"),
        rel(p("King Benjamin"), role("King"), "Mosiah 1:1"),
        rel(p("King Benjamin"), role("Prophet"), "Words of Mormon 1:17-18"),
        rel(p("Alma the Elder"), role("High Priest"), "Mosiah 23:16"),
        rel(p("Alma the Elder"), role("Founder of the Church"), "Mosiah 18:17"),
        rel(p("Mosiah"), role("King"), "Mosiah 29:46"),
        rel(p("Mormon"), role("Prophet"), "Mormon 1:2"),
        rel(p("Mormon"), role("Military Commander"), "Mormon 2:1-2"),
        rel(p("Moroni"), role("Prophet"), "Mormon 8:1"),
        rel(p("Moroni"), role("Last Nephite record-keeper"), "Moroni 10:1-2"),
        rel(p("Abinadi"), role("Prophet"), "Mosiah 11:20"),
        rel(p("Ammon (son of Mosiah)"), role("Missionary"), "Alma 17:12-13"),
        rel(p("Brother of Jared"), role("Prophet"), "Ether 1:34-37"),
        rel(p("Ether"), role("Prophet"), "Ether 12:2"),
        # D&C
        rel(p("Joseph Smith"), role("Prophet"), "D&C 1:17; 21:1"),
        rel(p("Joseph Smith"), role("Seer"), "D&C 21:1"),
        rel(p("Joseph Smith"), role("Revelator"), "D&C 21:1"),
        rel(p("Joseph Smith"), role("Translator"), "D&C 21:1"),
        rel(p("Oliver Cowdery"), role("Second Elder"), "D&C 20:3"),
        rel(p("Oliver Cowdery"), role("Scribe"), "JS-H 1:67"),
        rel(p("Brigham Young"), role("President of the Church"), "D&C 136:1-2"),
        rel(p("Sidney Rigdon"), role("Counselor"), "D&C 35:4"),
        rel(p("Hyrum Smith"), role("Patriarch"), "D&C 124:91-92,124"),
        rel(p("Emma Smith"), role("Elect Lady"), "D&C 25:3"),
        rel(p("Martin Harris"), role("Witness"), "D&C 17:1-3"),
    ],

    # ============================================================
    # Additional APPEARED_TO (enrich — only 3 exist)
    # ============================================================
    "APPEARED_TO": [
        rel(p("Jesus Christ"), p("Paul"), "Acts 9:3-6"),
        rel(p("Jesus Christ"), p("Nephites"), "3 Nephi 11:8-10"),
        rel(p("Jesus Christ"), p("Mary Magdalene"), "John 20:14-17"),
        rel(p("Jesus Christ"), p("Thomas"), "John 20:26-28"),
        rel(p("Jesus Christ"), p("Peter"), "1 Corinthians 15:5; Luke 24:34"),
        rel(p("Jesus Christ"), p("James (brother of Jesus)"), "1 Corinthians 15:7"),
        rel(p("Jesus Christ"), p("Five hundred brethren"), "1 Corinthians 15:6"),
        rel(p("Jesus Christ"), p("Joseph Smith"), "JS-H 1:17"),
        rel(p("God"), p("Abraham"), "Genesis 12:7; Abraham 2:6"),
        rel(p("God"), p("Jacob"), "Genesis 32:30"),
        rel(p("God"), p("Joseph Smith"), "JS-H 1:17"),
        rel(p("Angel of the Lord"), p("Gideon"), "Judges 6:11-12"),
        rel(p("Angel of the Lord"), p("Samson's parents"), "Judges 13:3"),
        rel(p("Angel of the Lord"), p("Mary"), "Luke 1:26-28"),
        rel(p("Angel of the Lord"), p("Shepherds"), "Luke 2:9-10"),
        rel(p("Elijah"), p("Joseph Smith"), "D&C 110:13-16"),
        rel(p("Peter"), p("Joseph Smith"), "D&C 27:12"),
        rel(p("James"), p("Joseph Smith"), "D&C 27:12"),
        rel(p("John"), p("Joseph Smith"), "D&C 27:12"),
    ],

    # ============================================================
    # Additional SAW_IN_VISION (enrich)
    # ============================================================
    "SAW_IN_VISION": [
        rel(p("Abraham"), concept("Stars/posterity"), "Abraham 3:2-14"),
        rel(p("Abraham"), concept("Pre-mortal council"), "Abraham 3:22-28"),
        rel(p("Jacob"), concept("Ladder to heaven"), "Genesis 28:12-15"),
        rel(p("Samuel"), concept("David as future king"), "1 Samuel 16:12-13"),
        rel(p("Elijah"), concept("Still small voice"), "1 Kings 19:11-12"),
        rel(p("Ezekiel"), concept("Wheels within wheels"), "Ezekiel 1:15-21"),
        rel(p("Ezekiel"), concept("Temple of the Lord"), "Ezekiel 40-43"),
        rel(p("Joseph Smith"), concept("Kirtland Temple visitation"), "D&C 110:1-10"),
        rel(p("Moroni"), concept("Latter-day events"), "Mormon 8:34-35"),
        rel(p("King Benjamin"), concept("Angel delivering sermon"), "Mosiah 3:2-4"),
        rel(p("Alma the Younger"), concept("God on His throne"), "Alma 36:22"),
    ],

    # ============================================================
    # Additional MARTYRED_AT (enrich)
    # ============================================================
    "MARTYRED_AT": [
        rel(p("John the Baptist"), place("Machaerus (Herod's prison)"), "Matthew 14:10-11"),
        rel(p("Paul"), place("Rome"), "2 Timothy 4:6-8 (tradition)"),
        rel(p("Peter"), place("Rome"), "John 21:18-19 (tradition)"),
        rel(p("Isaiah"), place("Jerusalem"), "Hebrews 11:37 (tradition); GEE, Isaías"),
    ],

    # ============================================================
    # Additional BAPTIZED_BY (enrich)
    # ============================================================
    "BAPTIZED_BY": [
        rel(p("Paul"), p("Ananias"), "Acts 9:17-18; 22:16"),
        rel(p("Cornelius"), p("Peter's companions"), "Acts 10:47-48"),
        rel(p("Lamoni"), p("Ammon (son of Mosiah)"), "Alma 19:35; implied"),
    ],

    # ============================================================
    # Additional HOLDS_PRIESTHOOD (enrich)
    # ============================================================
    "HOLDS_PRIESTHOOD": [
        rel(p("Adam"), concept("Melchizedek Priesthood"), "D&C 84:16; 107:41-42"),
        rel(p("Enoch"), concept("Melchizedek Priesthood"), "D&C 84:16; 107:48-49"),
        rel(p("Noah"), concept("Melchizedek Priesthood"), "D&C 84:16; 107:52"),
        rel(p("Abraham"), concept("Melchizedek Priesthood"), "D&C 84:14; Abraham 1:2-4"),
        rel(p("Moses"), concept("Melchizedek Priesthood"), "D&C 84:6"),
        rel(p("Peter"), concept("Melchizedek Priesthood"), "D&C 27:12-13"),
        rel(p("James"), concept("Melchizedek Priesthood"), "D&C 27:12-13"),
        rel(p("John"), concept("Melchizedek Priesthood"), "D&C 27:12-13"),
        rel(p("Joseph Smith"), concept("Melchizedek Priesthood"), "D&C 27:12-13"),
        rel(p("Oliver Cowdery"), concept("Melchizedek Priesthood"), "D&C 27:12-13"),
        rel(p("Joseph Smith"), concept("Aaronic Priesthood"), "D&C 13:1"),
        rel(p("Oliver Cowdery"), concept("Aaronic Priesthood"), "D&C 13:1"),
        rel(p("John the Baptist"), concept("Aaronic Priesthood"), "D&C 13:1; 84:26-28"),
    ],

    # ============================================================
    # Additional TAUGHT (enrich)
    # ============================================================
    "TAUGHT": [
        rel(p("Jesus Christ"), concept("Sermon on the Mount"), "Matthew 5-7"),
        rel(p("Jesus Christ"), concept("Parables of the Kingdom"), "Matthew 13"),
        rel(p("Jesus Christ"), concept("Bread of Life discourse"), "John 6:35-58"),
        rel(p("Jesus Christ"), concept("Sermon at the Temple (Nephites)"), "3 Nephi 12-14"),
        rel(p("Jesus Christ"), concept("Sacrament ordinance (Nephites)"), "3 Nephi 18:1-12"),
        rel(p("King Benjamin"), concept("Service of fellow beings"), "Mosiah 2:17"),
        rel(p("King Benjamin"), concept("Natural man is an enemy to God"), "Mosiah 3:19"),
        rel(p("Abinadi"), concept("Ten Commandments"), "Mosiah 12:33-36; 13:11-24"),
        rel(p("Abinadi"), concept("Christ's atonement and resurrection"), "Mosiah 15-16"),
        rel(p("Alma the Younger"), concept("Faith as a seed"), "Alma 32:28-43"),
        rel(p("Samuel the Lamanite"), concept("Signs of Christ's birth and death"), "Helaman 14:2-7,20-27"),
        rel(p("Paul"), concept("Resurrection"), "1 Corinthians 15"),
        rel(p("Paul"), concept("Justification by faith"), "Romans 3:23-28"),
        rel(p("Paul"), concept("Armor of God"), "Ephesians 6:10-18"),
        rel(p("Peter"), concept("Born again to a living hope"), "1 Peter 1:3-4"),
        rel(p("Jacob (son of Lehi)"), concept("Allegory of the olive tree"), "Jacob 5"),
        rel(p("Jacob (son of Lehi)"), concept("Atonement of Christ"), "2 Nephi 9"),
        rel(p("Moses"), concept("Ten Commandments"), "Exodus 20:1-17"),
        rel(p("Moses"), concept("Law of Moses"), "Leviticus 1-27"),
        rel(p("Joseph Smith"), concept("First Vision account"), "JS-H 1:14-20"),
        rel(p("Joseph Smith"), concept("Plan of salvation"), "D&C 76"),
        rel(p("Joseph Smith"), concept("Articles of Faith"), "Articles of Faith 1:1-13"),
    ],

    # ============================================================
    # Additional PROPHESIED_ABOUT (enrich)
    # ============================================================
    "PROPHESIED_ABOUT": [
        rel(p("Isaiah"), p("Jesus Christ"), "Isaiah 7:14; 9:6; 53"),
        rel(p("Isaiah"), concept("Restoration of Israel"), "Isaiah 11:11-12"),
        rel(p("Jeremiah"), concept("New Covenant"), "Jeremiah 31:31-34"),
        rel(p("Malachi"), p("Elijah"), "Malachi 4:5-6"),
        rel(p("Malachi"), concept("Second Coming"), "Malachi 3:1-3; 4:1"),
        rel(p("Nephi"), concept("Scattering and gathering of Israel"), "1 Nephi 22:3-8"),
        rel(p("Nephi"), concept("Columbus and New World"), "1 Nephi 13:12"),
        rel(p("Lehi"), concept("Tree of Life"), "1 Nephi 8"),
        rel(p("Lehi"), concept("Messiah to come"), "1 Nephi 10:4-11"),
        rel(p("Samuel the Lamanite"), p("Jesus Christ"), "Helaman 14:2-7"),
        rel(p("Moroni"), concept("Coming forth of Book of Mormon"), "Mormon 8:14-16,34-35"),
        rel(p("Daniel"), concept("Kingdom of God in latter days"), "Daniel 2:44-45"),
        rel(p("Ezekiel"), concept("Stick of Judah and Ephraim"), "Ezekiel 37:15-20"),
        rel(p("Joseph (son of Jacob)"), p("Joseph Smith"), "2 Nephi 3:6-15; JST Genesis 50:30-33"),
        rel(p("Enoch"), concept("Zion"), "Moses 7:18-21,62-64"),
        rel(p("Moses"), concept("Prophet like unto Moses"), "Deuteronomy 18:15-18"),
    ],

    # ============================================================
    # Additional AUTHORED (selected key works not already covered)
    # ============================================================
    "AUTHORED": [
        rel(p("Moses"), scripture("Genesis"), "Moses 1:40-41; tradition"),
        rel(p("Moses"), scripture("Exodus"), "Tradition"),
        rel(p("Moses"), scripture("Book of Moses"), "Moses 1:1"),
        rel(p("Isaiah"), scripture("Book of Isaiah"), "Isaiah 1:1"),
        rel(p("Jeremiah"), scripture("Book of Jeremiah"), "Jeremiah 1:1-2"),
        rel(p("Jeremiah"), scripture("Lamentations"), "Tradition"),
        rel(p("Ezekiel"), scripture("Book of Ezekiel"), "Ezekiel 1:1-3"),
        rel(p("Daniel"), scripture("Book of Daniel"), "Daniel 1:1"),
        rel(p("Paul"), scripture("Epistle to the Romans"), "Romans 1:1"),
        rel(p("Paul"), scripture("First Epistle to the Corinthians"), "1 Corinthians 1:1"),
        rel(p("Paul"), scripture("Second Epistle to the Corinthians"), "2 Corinthians 1:1"),
        rel(p("Paul"), scripture("Epistle to the Galatians"), "Galatians 1:1"),
        rel(p("Paul"), scripture("Epistle to the Ephesians"), "Ephesians 1:1"),
        rel(p("Paul"), scripture("Epistle to the Philippians"), "Philippians 1:1"),
        rel(p("Paul"), scripture("Epistle to the Colossians"), "Colossians 1:1"),
        rel(p("Paul"), scripture("First Epistle to Timothy"), "1 Timothy 1:1-2"),
        rel(p("Paul"), scripture("Second Epistle to Timothy"), "2 Timothy 1:1-2"),
        rel(p("Paul"), scripture("Epistle to Titus"), "Titus 1:1"),
        rel(p("Paul"), scripture("Epistle to Philemon"), "Philemon 1:1"),
        rel(p("Paul"), scripture("Epistle to the Hebrews"), "Hebrews 1:1 (attributed)"),
        rel(p("Peter"), scripture("First Epistle of Peter"), "1 Peter 1:1"),
        rel(p("Peter"), scripture("Second Epistle of Peter"), "2 Peter 1:1"),
        rel(p("John"), scripture("Gospel of John"), "John 21:24"),
        rel(p("John"), scripture("First Epistle of John"), "1 John 1:1-4"),
        rel(p("John"), scripture("Second Epistle of John"), "2 John 1:1"),
        rel(p("John"), scripture("Third Epistle of John"), "3 John 1:1"),
        rel(p("John"), scripture("Revelation"), "Revelation 1:1-2"),
        rel(p("Matthew"), scripture("Gospel of Matthew"), "Matthew 1:1 (tradition)"),
        rel(p("Mark"), scripture("Gospel of Mark"), "Mark 1:1 (tradition)"),
        rel(p("Luke"), scripture("Gospel of Luke"), "Luke 1:1-4"),
        rel(p("Luke"), scripture("Acts of the Apostles"), "Acts 1:1-2"),
        rel(p("James (brother of Jesus)"), scripture("Epistle of James"), "James 1:1"),
        rel(p("Jude"), scripture("Epistle of Jude"), "Jude 1:1"),
        rel(p("Nephi"), scripture("1 Nephi"), "1 Nephi 1:1-3"),
        rel(p("Nephi"), scripture("2 Nephi"), "2 Nephi 5:30-33"),
        rel(p("Jacob (son of Lehi)"), scripture("Book of Jacob"), "Jacob 1:1-4"),
        rel(p("Enos"), scripture("Book of Enos"), "Enos 1:1"),
        rel(p("Alma the Younger"), scripture("Book of Alma (portions)"), "Alma 1:1"),
        rel(p("Mormon"), scripture("Book of Mormon (compilation)"), "Words of Mormon 1:1-2"),
        rel(p("Mormon"), scripture("Epistle of Mormon"), "Moroni 8-9"),
        rel(p("Moroni"), scripture("Book of Moroni"), "Moroni 1:1-4"),
        rel(p("Moroni"), scripture("Title Page of the Book of Mormon"), "Title Page"),
        rel(p("Ether"), scripture("Book of Ether (original)"), "Ether 1:1-2"),
        rel(p("Abraham"), scripture("Book of Abraham"), "Abraham 1:1"),
        rel(p("Joseph Smith"), scripture("Doctrine and Covenants"), "D&C 1:1"),
        rel(p("Joseph Smith"), scripture("Pearl of Great Price (compiler)"), "PGP introduction"),
        rel(p("Joseph Smith"), scripture("Joseph Smith—History"), "JS-H 1:1"),
    ],

    # ============================================================
    # Additional COVENANT_WITH (enrich)
    # ============================================================
    "COVENANT_WITH": [
        rel(p("God"), p("Adam"), "Moses 6:51-68"),
        rel(p("God"), p("Enoch"), "Moses 7:51-52"),
        rel(p("God"), p("Jacob"), "Genesis 28:13-15"),
        rel(p("God"), p("David"), "2 Samuel 7:12-16"),
        rel(p("Jesus Christ"), p("Nephites"), "3 Nephi 20:25-27"),
    ],

    # ============================================================
    # Additional CONFERRED_KEYS_TO (enrich)
    # ============================================================
    "CONFERRED_KEYS_TO": [
        rel(p("Moses"), p("Joshua"), "Deuteronomy 31:7-8; 34:9"),
        rel(p("Jesus Christ"), p("Peter"), "Matthew 16:19"),
        rel(p("Elijah"), p("Elisha"), "2 Kings 2:9-14"),
    ],

    # ============================================================
    # DISPENSATION_HEAD (enrich)
    # ============================================================
    "DISPENSATION_HEAD": [
        rel(p("Abraham"), period("Abrahamic dispensation"), "Abraham 2:6-11"),
        rel(p("Moses"), period("Mosaic dispensation"), "Exodus 3:10-12"),
        rel(p("Peter"), period("Meridian of time"), "Matthew 16:18-19"),
    ],

    # ============================================================
    # Additional FOREORDAINED_AS (enrich)
    # ============================================================
    "FOREORDAINED_AS": [
        rel(p("Moses"), role("Deliverer of Israel"), "Moses 1:25-26; Abraham 3:23"),
        rel(p("Nephi"), role("Ruler over his brothers"), "1 Nephi 2:22"),
    ],

    # ============================================================
    # HEALED_BY — new entries
    # ============================================================
    "HEALED_BY": [
        rel(p("Naaman"), p("Elisha"), "2 Kings 5:10-14"),
        rel(p("Lazarus"), p("Jesus Christ"), "John 11:43-44"),
        rel(p("Man born blind"), p("Jesus Christ"), "John 9:6-7"),
        rel(p("Woman with issue of blood"), p("Jesus Christ"), "Mark 5:25-34"),
        rel(p("Ten lepers"), p("Jesus Christ"), "Luke 17:12-14"),
        rel(p("Lame man at gate Beautiful"), p("Peter"), "Acts 3:2-8"),
        rel(p("Aeneas"), p("Peter"), "Acts 9:33-34"),
        rel(p("Zeezrom"), p("Alma the Younger"), "Alma 15:5-11"),
    ],

    # ============================================================
    # BLESSED_BY — new entries
    # ============================================================
    "BLESSED_BY": [
        rel(p("Jacob"), p("Isaac"), "Genesis 27:27-29"),
        rel(p("Ephraim"), p("Jacob"), "Genesis 48:17-20"),
        rel(p("Manasseh"), p("Jacob"), "Genesis 48:17-20"),
        rel(p("Joshua"), p("Moses"), "Deuteronomy 34:9"),
        rel(p("Twelve Tribes"), p("Jacob"), "Genesis 49:1-28"),
        rel(p("Twelve Tribes"), p("Moses"), "Deuteronomy 33:1-29"),
        rel(p("Nephi"), p("Lehi"), "2 Nephi 1:28-29"),
        rel(p("Jacob (son of Lehi)"), p("Lehi"), "2 Nephi 2:1-4"),
    ],

    # ============================================================
    # FOUGHT_AGAINST (key conflicts)
    # ============================================================
    "FOUGHT_AGAINST": [
        rel(p("David"), p("Goliath"), "1 Samuel 17:48-51"),
        rel(p("Joshua"), concept("Canaanite armies"), "Joshua 6-12"),
        rel(p("Gideon"), concept("Midianites"), "Judges 7:19-22"),
        rel(p("Samson"), concept("Philistines"), "Judges 15:14-16"),
        rel(p("Captain Moroni"), p("Zerahemnah"), "Alma 43-44"),
        rel(p("Captain Moroni"), p("Amalickiah"), "Alma 46:1-3; 51:34"),
        rel(p("Helaman"), concept("Lamanite armies (with stripling warriors)"), "Alma 56-58"),
        rel(p("Mormon"), concept("Lamanite armies (final wars)"), "Mormon 6:5-15"),
    ],

    # ============================================================
    # SUCCEEDED_OF / SUCCESSOR_OF (enrich)
    # ============================================================
    "SUCCESSOR_OF": [
        rel(p("Joshua"), p("Moses"), "Joshua 1:1-2"),
        rel(p("Solomon"), p("David"), "1 Kings 1:39; 2:12"),
        rel(p("Elisha"), p("Elijah"), "2 Kings 2:12-14"),
        rel(p("Mosiah"), p("King Benjamin"), "Mosiah 6:3"),
        rel(p("Alma the Younger"), p("Alma the Elder"), "Mosiah 29:42"),
        rel(p("Helaman"), p("Alma the Younger"), "Alma 37:1-2"),
        rel(p("Moroni"), p("Mormon"), "Mormon 8:1-3"),
        rel(p("Brigham Young"), p("Joseph Smith"), "D&C 136:1-2"),
    ],

    # ============================================================
    # HAS_TITLE (biographical titles)
    # ============================================================
    "HAS_TITLE": [
        rel(p("Jesus Christ"), concept("Son of God"), "Matthew 3:17; 2 Nephi 25:19"),
        rel(p("Jesus Christ"), concept("Lamb of God"), "John 1:29; 1 Nephi 11:21"),
        rel(p("Jesus Christ"), concept("Prince of Peace"), "Isaiah 9:6"),
        rel(p("Jesus Christ"), concept("Alpha and Omega"), "Revelation 1:8; 3 Nephi 9:18"),
        rel(p("Peter"), concept("Rock"), "Matthew 16:18"),
        rel(p("Paul"), concept("Apostle to the Gentiles"), "Romans 11:13"),
        rel(p("James"), concept("Son of Thunder (Boanerges)"), "Mark 3:17"),
        rel(p("John"), concept("Son of Thunder (Boanerges)"), "Mark 3:17"),
        rel(p("John"), concept("The Beloved Disciple"), "John 13:23; 21:20"),
        rel(p("Melchizedek"), concept("Prince of Peace"), "JST Genesis 14:33; Alma 13:18"),
        rel(p("Mormon"), concept("Disciple of Christ"), "3 Nephi 5:13"),
        rel(p("Joseph Smith"), concept("Choice Seer"), "2 Nephi 3:6-7"),
        rel(p("Enoch"), concept("Seer"), "Moses 6:36"),
        rel(p("Abraham"), concept("Father of Many Nations"), "Genesis 17:5"),
        rel(p("David"), concept("Sweet Psalmist of Israel"), "2 Samuel 23:1"),
        rel(p("Daniel"), concept("Belteshazzar"), "Daniel 1:7"),
        rel(p("Esther"), concept("Hadassah"), "Esther 2:7"),
    ],

    # ============================================================
    # CONVERTED_BY (enrich)
    # ============================================================
    "CONVERTED_BY": [
        rel(p("Ruth"), p("Naomi"), "Ruth 1:16-17"),
        rel(p("Alma the Elder"), p("Abinadi"), "Mosiah 17:2-4"),
    ],
}


def main():
    with open(RELATIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    added = 0
    skipped = 0

    for rtype, new_rels in NEW_RELATIONS.items():
        if rtype not in data:
            data[rtype] = []

        # Build set of existing (from_name, to_name) for dedup
        existing = set()
        for r in data[rtype]:
            key = (r["from"]["name"].lower(), r["to"]["name"].lower())
            existing.add(key)

        for nr in new_rels:
            key = (nr["from"]["name"].lower(), nr["to"]["name"].lower())
            if key in existing:
                skipped += 1
                continue
            data[rtype].append(nr)
            existing.add(key)
            added += 1

    # Sort keys alphabetically
    sorted_data = dict(sorted(data.items()))

    with open(RELATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, indent=2, ensure_ascii=False)

    total = sum(len(v) for v in sorted_data.values())
    print(f"Added {added} new relations, skipped {skipped} duplicates.")
    print(f"Total relations: {total}")


if __name__ == "__main__":
    main()

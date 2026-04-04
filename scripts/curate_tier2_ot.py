"""Tier 2 OT: Exhaustive biographical relations for ALL significant OT characters.

Covers: Genesis through Malachi — patriarchs, matriarchs, judges, kings,
prophets (major and minor), priests, antagonists, supporting characters.
"""
import json
from pathlib import Path

RELATIONS_PATH = Path(__file__).parent.parent / "src" / "alejandria" / "knowledge" / "gazetteers" / "relations.json"

def p(name, type_="person"):
    return {"name": name, "type": type_}
def pl(name):
    return {"name": name, "type": "place"}
def r(name):
    return {"name": name, "type": "role"}
def c(name):
    return {"name": name, "type": "concept"}
def s(name):
    return {"name": name, "type": "scripture"}
def per(name):
    return {"name": name, "type": "period"}
def rel(rtype, from_, to_, ref):
    return (rtype, {"from": from_, "to": to_, "source_ref": ref, "confidence": "curated"})


ALL = [
    # ================================================================
    # EVE
    # ================================================================
    rel("SPOUSE_OF", p("Eve"), p("Adam"), "Genesis 3:20"),
    rel("LIVED_IN", p("Eve"), pl("Garden of Eden"), "Genesis 2:8,22"),
    rel("HAS_TITLE", p("Eve"), c("Mother of All Living"), "Genesis 3:20; Moses 4:26"),
    rel("TAUGHT", p("Eve"), c("Transgression brought mortality and children"), "Moses 5:11"),
    rel("HAS_ROLE", p("Eve"), r("First to partake of fruit"), "Genesis 3:6; Moses 4:12"),
    rel("COVENANT_WITH", p("God"), p("Eve"), "Moses 5:4-5"),

    # ================================================================
    # CAIN
    # ================================================================
    rel("HAS_ROLE", p("Cain"), r("Tiller of the ground"), "Genesis 4:2"),
    rel("KILLED", p("Cain"), p("Abel"), "Genesis 4:8"),
    rel("TRAVELED_TO", p("Cain"), pl("Land of Nod"), "Genesis 4:16"),
    rel("HAS_TITLE", p("Cain"), c("Master Mahan"), "Moses 5:31"),
    rel("COVENANT_WITH", p("Cain"), p("Satan"), "Moses 5:30"),

    # ================================================================
    # ABEL
    # ================================================================
    rel("HAS_ROLE", p("Abel"), r("Keeper of sheep"), "Genesis 4:2"),
    rel("TAUGHT", p("Abel"), c("Acceptable sacrifice to God"), "Genesis 4:4; Hebrews 11:4"),
    rel("HAS_TITLE", p("Abel"), c("First martyr"), "Genesis 4:8"),

    # ================================================================
    # SETH
    # ================================================================
    rel("HAS_ROLE", p("Seth"), r("Appointed seed after Abel"), "Genesis 4:25"),
    rel("HOLDS_PRIESTHOOD", p("Seth"), c("Melchizedek Priesthood"), "D&C 107:42"),
    rel("FATHER_OF", p("Seth"), p("Enos"), "Genesis 5:6"),

    # ================================================================
    # ENOCH — already Tier 1, skip
    # ================================================================

    # ================================================================
    # METHUSELAH
    # ================================================================
    rel("HAS_TITLE", p("Methuselah"), c("Longest-lived man (969 years)"), "Genesis 5:27"),
    rel("HOLDS_PRIESTHOOD", p("Methuselah"), c("Melchizedek Priesthood"), "D&C 107:50-52"),
    rel("ORDAINED_BY", p("Methuselah"), p("Adam"), "D&C 107:50"),

    # ================================================================
    # NOAH — already Tier 1 for some, enrich
    # ================================================================
    rel("LIVED_IN", p("Noah"), pl("Ark"), "Genesis 7:7"),
    rel("COVENANT_WITH", p("God"), p("Noah"), "Genesis 9:9-13"),
    rel("HAS_TITLE", p("Noah"), c("Gabriel"), "Tradition; GEE, Noé"),
    rel("TAUGHT", p("Noah"), c("Repentance to his generation"), "Moses 8:20-24"),

    # ================================================================
    # SHEM
    # ================================================================
    rel("HAS_ROLE", p("Shem"), r("Father of Semitic peoples"), "Genesis 10:21-31"),
    rel("BLESSED_BY", p("Shem"), p("Noah"), "Genesis 9:26"),
    rel("HOLDS_PRIESTHOOD", p("Shem"), c("Melchizedek Priesthood"), "D&C 84:14 (tradition: Shem=Melchizedek)"),
    rel("IS_SAME_AS", p("Shem"), p("Melchizedek"), "JST Genesis 14:25-40 (tradition)"),

    # ================================================================
    # HAM
    # ================================================================
    rel("HAS_ROLE", p("Ham"), r("Father of Canaan"), "Genesis 9:22; 10:6"),
    rel("LIVED_IN", p("Ham"), pl("Egypt/Africa region"), "Genesis 10:6"),

    # ================================================================
    # JAPHETH
    # ================================================================
    rel("HAS_ROLE", p("Japheth"), r("Father of European/Asian peoples"), "Genesis 10:2-5"),
    rel("BLESSED_BY", p("Japheth"), p("Noah"), "Genesis 9:27"),

    # ================================================================
    # SARAH / SARAI
    # ================================================================
    rel("LIVED_IN", p("Sarah"), pl("Ur of the Chaldees"), "Genesis 11:31"),
    rel("TRAVELED_TO", p("Sarah"), pl("Canaan"), "Genesis 12:5"),
    rel("TRAVELED_TO", p("Sarah"), pl("Egypt"), "Genesis 12:10-11"),
    rel("HAS_TITLE", p("Sarah"), c("Princess"), "Genesis 17:15"),
    rel("CALLED_BY_NAME", p("Sarah"), p("Sarai"), "Genesis 17:15"),
    rel("SAW_IN_VISION", p("Sarah"), c("Promise of Isaac in old age"), "Genesis 18:10-14; 21:1-3"),

    # ================================================================
    # HAGAR
    # ================================================================
    rel("HAS_ROLE", p("Hagar"), r("Handmaid of Sarah"), "Genesis 16:1"),
    rel("MOTHER_OF", p("Hagar"), p("Ishmael"), "Genesis 16:15"),
    rel("TRAVELED_TO", p("Hagar"), pl("Wilderness of Beer-sheba"), "Genesis 21:14"),
    rel("APPEARED_TO", p("Angel of the Lord"), p("Hagar"), "Genesis 16:7-11; 21:17"),
    rel("BORN_IN", p("Hagar"), pl("Egypt"), "Genesis 16:1"),

    # ================================================================
    # LOT
    # ================================================================
    rel("TRAVELED_TO", p("Lot"), pl("Sodom"), "Genesis 13:12"),
    rel("TRAVELED_TO", p("Lot"), pl("Zoar"), "Genesis 19:22-23"),
    rel("HAS_ROLE", p("Lot"), r("Nephew of Abraham"), "Genesis 12:5; 14:12"),
    rel("LIVED_IN", p("Lot"), pl("Sodom"), "Genesis 13:12; 19:1"),

    # ================================================================
    # ISHMAEL (son of Abraham)
    # ================================================================
    rel("BORN_IN", p("Ishmael"), pl("Canaan"), "Genesis 16:15"),
    rel("LIVED_IN", p("Ishmael"), pl("Wilderness of Paran"), "Genesis 21:21"),
    rel("HAS_ROLE", p("Ishmael"), r("Father of twelve princes"), "Genesis 25:13-16"),
    rel("HAS_TITLE", p("Ishmael"), c("Father of Arab nations"), "Genesis 17:20 (tradition)"),

    # ================================================================
    # REBEKAH / REBECCA
    # ================================================================
    rel("BORN_IN", p("Rebekah"), pl("Haran/Nahor"), "Genesis 24:10,15"),
    rel("TRAVELED_TO", p("Rebekah"), pl("Canaan"), "Genesis 24:61-67"),
    rel("HAS_ROLE", p("Rebekah"), r("Helped Jacob obtain the blessing"), "Genesis 27:5-17"),
    rel("LIVED_IN", p("Rebekah"), pl("Beer-lahai-roi"), "Genesis 24:62-67"),

    # ================================================================
    # ESAU
    # ================================================================
    rel("SPOUSE_OF", p("Esau"), p("Judith"), "Genesis 26:34"),
    rel("HAS_ROLE", p("Esau"), r("Sold birthright for pottage"), "Genesis 25:29-34"),
    rel("LIVED_IN", p("Esau"), pl("Mount Seir/Edom"), "Genesis 36:8"),
    rel("HAS_TITLE", p("Esau"), c("Edom"), "Genesis 25:30"),
    rel("FOUGHT_AGAINST", p("Esau"), p("Jacob"), "Genesis 27:41 (intent)"),

    # ================================================================
    # RACHEL
    # ================================================================
    rel("BORN_IN", p("Rachel"), pl("Haran"), "Genesis 29:6"),
    rel("DIED_IN", p("Rachel"), pl("Near Bethlehem"), "Genesis 35:19"),
    rel("HAS_ROLE", p("Rachel"), r("Beloved wife of Jacob"), "Genesis 29:18"),
    rel("MOTHER_OF", p("Rachel"), p("Benjamin"), "Genesis 35:18"),

    # ================================================================
    # LEAH
    # ================================================================
    rel("BORN_IN", p("Leah"), pl("Haran"), "Genesis 29:16"),
    rel("HAS_ROLE", p("Leah"), r("First wife of Jacob"), "Genesis 29:23-25"),
    rel("MOTHER_OF", p("Leah"), p("Dinah"), "Genesis 30:21"),

    # ================================================================
    # LABAN (OT, uncle of Jacob)
    # ================================================================
    rel("HAS_ROLE", p("Laban"), r("Father of Rachel and Leah"), "Genesis 29:16"),
    rel("LIVED_IN", p("Laban"), pl("Haran"), "Genesis 27:43; 29:4-5"),
    rel("COVENANT_WITH", p("Laban"), p("Jacob"), "Genesis 31:44-53"),

    # ================================================================
    # JOSEPH (son of Jacob) — enrich
    # ================================================================
    rel("TRAVELED_TO", p("Joseph"), pl("Egypt (sold into slavery)"), "Genesis 37:28,36"),
    rel("LIVED_IN", p("Joseph"), pl("Egypt"), "Genesis 39:1"),
    rel("CALLED_AS", p("Joseph"), r("Governor of Egypt"), "Genesis 41:40-43"),
    rel("SPOUSE_OF", p("Joseph"), p("Asenath"), "Genesis 41:45"),
    rel("SAW_IN_VISION", p("Joseph"), c("Sheaves and stars bowing"), "Genesis 37:5-10"),
    rel("HAS_TITLE", p("Joseph"), c("Zaphnath-paaneah"), "Genesis 41:45"),
    rel("PROPHESIED_ABOUT", p("Joseph"), p("Joseph Smith"), "2 Nephi 3:6-15"),
    rel("BLESSED_BY", p("Joseph"), p("Jacob"), "Genesis 49:22-26"),

    # ================================================================
    # JUDAH
    # ================================================================
    rel("HAS_ROLE", p("Judah"), r("Fourth son of Jacob"), "Genesis 29:35"),
    rel("FATHER_OF", p("Judah"), p("Perez"), "Genesis 38:29"),
    rel("ANCESTOR_OF", p("Judah"), p("David"), "Ruth 4:18-22"),
    rel("ANCESTOR_OF", p("Judah"), p("Jesus Christ"), "Matthew 1:2-3"),
    rel("BLESSED_BY", p("Judah"), p("Jacob"), "Genesis 49:8-12"),

    # ================================================================
    # REUBEN
    # ================================================================
    rel("HAS_ROLE", p("Reuben"), r("Firstborn of Jacob"), "Genesis 29:32"),
    rel("HAS_ROLE", p("Reuben"), r("Tried to save Joseph"), "Genesis 37:21-22"),
    rel("BLESSED_BY", p("Reuben"), p("Jacob"), "Genesis 49:3-4"),

    # ================================================================
    # LEVI
    # ================================================================
    rel("HAS_ROLE", p("Levi"), r("Father of priestly tribe"), "Genesis 29:34"),
    rel("ANCESTOR_OF", p("Levi"), p("Moses"), "Exodus 2:1"),
    rel("ANCESTOR_OF", p("Levi"), p("Aaron"), "Exodus 4:14"),
    rel("BLESSED_BY", p("Levi"), p("Jacob"), "Genesis 49:5-7"),

    # ================================================================
    # BENJAMIN (son of Jacob)
    # ================================================================
    rel("BORN_IN", p("Benjamin"), pl("Near Bethlehem"), "Genesis 35:18-19"),
    rel("HAS_ROLE", p("Benjamin"), r("Youngest son of Jacob"), "Genesis 35:18"),
    rel("DIED_IN", p("Rachel"), pl("Near Bethlehem (giving birth to Benjamin)"), "Genesis 35:18-19"),

    # ================================================================
    # EPHRAIM
    # ================================================================
    rel("BLESSED_BY", p("Ephraim"), p("Jacob"), "Genesis 48:17-20"),
    rel("HAS_ROLE", p("Ephraim"), r("Received birthright blessing"), "Genesis 48:19-20"),
    rel("HAS_TITLE", p("Ephraim"), c("Father of leading tribe in latter days"), "D&C 133:30-34"),

    # ================================================================
    # MANASSEH
    # ================================================================
    rel("BLESSED_BY", p("Manasseh"), p("Jacob"), "Genesis 48:17-20"),
    rel("HAS_ROLE", p("Manasseh"), r("Firstborn of Joseph"), "Genesis 41:51"),

    # ================================================================
    # DINAH
    # ================================================================
    rel("HAS_ROLE", p("Dinah"), r("Daughter of Jacob and Leah"), "Genesis 30:21"),
    rel("LIVED_IN", p("Dinah"), pl("Shechem"), "Genesis 34:1-2"),

    # ================================================================
    # MIRIAM
    # ================================================================
    rel("HAS_ROLE", p("Miriam"), r("Sister of Moses and Aaron"), "Exodus 15:20"),
    rel("CALLED_AS", p("Miriam"), r("Prophetess"), "Exodus 15:20"),
    rel("TAUGHT", p("Miriam"), c("Song of deliverance at the Red Sea"), "Exodus 15:20-21"),
    rel("DIED_IN", p("Miriam"), pl("Kadesh"), "Numbers 20:1"),

    # ================================================================
    # ZIPPORAH
    # ================================================================
    rel("SPOUSE_OF", p("Zipporah"), p("Moses"), "Exodus 2:21"),
    rel("HAS_ROLE", p("Zipporah"), r("Daughter of Jethro"), "Exodus 2:16-21"),
    rel("BORN_IN", p("Zipporah"), pl("Midian"), "Exodus 2:16"),

    # ================================================================
    # JETHRO / REUEL
    # ================================================================
    rel("HAS_ROLE", p("Jethro"), r("Father-in-law of Moses"), "Exodus 3:1"),
    rel("CALLED_AS", p("Jethro"), r("Priest of Midian"), "Exodus 2:16; 3:1"),
    rel("TAUGHT", p("Jethro"), c("Delegation of judgment to Moses"), "Exodus 18:17-23"),
    rel("HOLDS_PRIESTHOOD", p("Jethro"), c("Melchizedek Priesthood"), "D&C 84:6-7"),
    rel("IS_SAME_AS", p("Jethro"), p("Reuel"), "Exodus 2:18"),

    # ================================================================
    # CALEB
    # ================================================================
    rel("HAS_ROLE", p("Caleb"), r("Faithful spy sent to Canaan"), "Numbers 13:6,30"),
    rel("TRAVELED_TO", p("Caleb"), pl("Canaan (as spy)"), "Numbers 13:2,6"),
    rel("LIVED_IN", p("Caleb"), pl("Hebron"), "Joshua 14:13-14"),
    rel("ALLIED_WITH", p("Caleb"), p("Joshua"), "Numbers 14:6-9"),

    # ================================================================
    # KORAH
    # ================================================================
    rel("FOUGHT_AGAINST", p("Korah"), p("Moses"), "Numbers 16:1-3"),
    rel("DIED_IN", p("Korah"), pl("Wilderness (swallowed by earth)"), "Numbers 16:31-33"),
    rel("HAS_ROLE", p("Korah"), r("Levite rebel"), "Numbers 16:1"),

    # ================================================================
    # BALAAM
    # ================================================================
    rel("CALLED_AS", p("Balaam"), r("Prophet/seer"), "Numbers 22:5-6"),
    rel("PROPHESIED_ABOUT", p("Balaam"), p("Israel"), "Numbers 24:5-9,17"),
    rel("TRAVELED_TO", p("Balaam"), pl("Moab"), "Numbers 22:7-21"),
    rel("HAS_ROLE", p("Balaam"), r("His donkey spoke to him"), "Numbers 22:28-30"),

    # ================================================================
    # RAHAB
    # ================================================================
    rel("LIVED_IN", p("Rahab"), pl("Jericho"), "Joshua 2:1"),
    rel("HAS_ROLE", p("Rahab"), r("Hid the Israelite spies"), "Joshua 2:4-6"),
    rel("ANCESTOR_OF", p("Rahab"), p("David"), "Matthew 1:5"),
    rel("CONVERTED_BY", p("Rahab"), c("Faith in the God of Israel"), "Joshua 2:9-11; Hebrews 11:31"),

    # ================================================================
    # DEBORAH
    # ================================================================
    rel("CALLED_AS", p("Deborah"), r("Judge of Israel"), "Judges 4:4"),
    rel("CALLED_AS", p("Deborah"), r("Prophetess"), "Judges 4:4"),
    rel("FOUGHT_AGAINST", p("Deborah"), p("Sisera"), "Judges 4:6-9"),
    rel("TAUGHT", p("Deborah"), c("Song of Deborah"), "Judges 5"),
    rel("LIVED_IN", p("Deborah"), pl("Hill country of Ephraim"), "Judges 4:5"),

    # ================================================================
    # GIDEON (Judge)
    # ================================================================
    rel("CALLED_AS", p("Gideon"), r("Judge of Israel"), "Judges 6:11-14"),
    rel("APPEARED_TO", p("Angel of the Lord"), p("Gideon"), "Judges 6:11-12"),
    rel("HAS_TITLE", p("Gideon"), c("Jerubbaal"), "Judges 6:32"),
    rel("TAUGHT", p("Gideon"), c("Fleece as a sign from God"), "Judges 6:36-40"),

    # ================================================================
    # SAMSON
    # ================================================================
    rel("CALLED_AS", p("Samson"), r("Judge of Israel"), "Judges 13:5; 15:20"),
    rel("BORN_IN", p("Samson"), pl("Zorah"), "Judges 13:2,24"),
    rel("FOREORDAINED_AS", p("Samson"), r("Nazirite from birth"), "Judges 13:5"),
    rel("SPOUSE_OF", p("Samson"), p("Delilah"), "Judges 16:4"),
    rel("DIED_IN", p("Samson"), pl("Gaza (Philistine temple)"), "Judges 16:28-30"),
    rel("HAS_TITLE", p("Samson"), c("Strongest man"), "Judges 14-16"),

    # ================================================================
    # JEPHTHAH
    # ================================================================
    rel("CALLED_AS", p("Jephthah"), r("Judge of Israel"), "Judges 11:1,11"),
    rel("FOUGHT_AGAINST", p("Jephthah"), c("Ammonites"), "Judges 11:32-33"),
    rel("LIVED_IN", p("Jephthah"), pl("Land of Tob"), "Judges 11:3"),
    rel("COVENANT_WITH", p("Jephthah"), p("God"), "Judges 11:30-31"),

    # ================================================================
    # NAOMI
    # ================================================================
    rel("LIVED_IN", p("Naomi"), pl("Bethlehem"), "Ruth 1:1-2"),
    rel("TRAVELED_TO", p("Naomi"), pl("Moab"), "Ruth 1:1-2"),
    rel("TRAVELED_TO", p("Naomi"), pl("Bethlehem (return)"), "Ruth 1:19"),
    rel("HAS_ROLE", p("Naomi"), r("Mother-in-law of Ruth"), "Ruth 1:3-4"),
    rel("TAUGHT", p("Naomi"), c("Guidance to Ruth about Boaz"), "Ruth 3:1-4"),

    # ================================================================
    # BOAZ
    # ================================================================
    rel("LIVED_IN", p("Boaz"), pl("Bethlehem"), "Ruth 2:1,4"),
    rel("HAS_ROLE", p("Boaz"), r("Kinsman redeemer of Ruth"), "Ruth 4:9-10"),
    rel("FATHER_OF", p("Boaz"), p("Obed"), "Ruth 4:13,17"),
    rel("ANCESTOR_OF", p("Boaz"), p("David"), "Ruth 4:17-22"),

    # ================================================================
    # HANNAH
    # ================================================================
    rel("LIVED_IN", p("Hannah"), pl("Ramathaim-zophim"), "1 Samuel 1:1-2"),
    rel("COVENANT_WITH", p("Hannah"), p("God"), "1 Samuel 1:11"),
    rel("TAUGHT", p("Hannah"), c("Prayer of praise and gratitude"), "1 Samuel 2:1-10"),
    rel("HAS_ROLE", p("Hannah"), r("Dedicated Samuel to the Lord"), "1 Samuel 1:24-28"),

    # ================================================================
    # ELI
    # ================================================================
    rel("CALLED_AS", p("Eli"), r("High Priest"), "1 Samuel 1:9; 2:11"),
    rel("CALLED_AS", p("Eli"), r("Judge of Israel"), "1 Samuel 4:18"),
    rel("LIVED_IN", p("Eli"), pl("Shiloh"), "1 Samuel 1:3,9"),
    rel("HAS_ROLE", p("Eli"), r("Raised Samuel in the tabernacle"), "1 Samuel 2:11; 3:1"),
    rel("DIED_IN", p("Eli"), pl("Shiloh (fell from seat)"), "1 Samuel 4:18"),

    # ================================================================
    # SAUL (king)
    # ================================================================
    rel("CALLED_AS", p("Saul"), r("First King of Israel"), "1 Samuel 10:1,24"),
    rel("BORN_IN", p("Saul"), pl("Gibeah"), "1 Samuel 10:26"),
    rel("ORDAINED_BY", p("Saul"), p("Samuel"), "1 Samuel 10:1"),
    rel("FOUGHT_AGAINST", p("Saul"), c("Philistines"), "1 Samuel 13-14"),
    rel("FOUGHT_AGAINST", p("Saul"), p("David"), "1 Samuel 18:10-11; 19-26"),
    rel("DIED_IN", p("Saul"), pl("Mount Gilboa"), "1 Samuel 31:4-6"),
    rel("TRIBE_OF", p("Saul"), c("Benjamin"), "1 Samuel 9:1-2"),
    rel("FATHER_OF", p("Saul"), p("Jonathan"), "1 Samuel 14:1"),

    # ================================================================
    # JONATHAN
    # ================================================================
    rel("HAS_ROLE", p("Jonathan"), r("Son of Saul, friend of David"), "1 Samuel 18:1-4"),
    rel("ALLIED_WITH", p("Jonathan"), p("David"), "1 Samuel 18:3; 20:42"),
    rel("FOUGHT_AGAINST", p("Jonathan"), c("Philistines"), "1 Samuel 14:1-14"),
    rel("DIED_IN", p("Jonathan"), pl("Mount Gilboa"), "1 Samuel 31:2"),
    rel("COVENANT_WITH", p("Jonathan"), p("David"), "1 Samuel 18:3; 20:16-17"),

    # ================================================================
    # MICHAL
    # ================================================================
    rel("SPOUSE_OF", p("Michal"), p("David"), "1 Samuel 18:27"),
    rel("HAS_ROLE", p("Michal"), r("Daughter of Saul, wife of David"), "1 Samuel 18:20,27"),
    rel("HAS_ROLE", p("Michal"), r("Helped David escape Saul"), "1 Samuel 19:12-13"),

    # ================================================================
    # ABIGAIL
    # ================================================================
    rel("SPOUSE_OF", p("Abigail"), p("David"), "1 Samuel 25:42"),
    rel("HAS_ROLE", p("Abigail"), r("Wise woman who prevented bloodshed"), "1 Samuel 25:23-35"),
    rel("LIVED_IN", p("Abigail"), pl("Carmel"), "1 Samuel 25:2-3"),

    # ================================================================
    # BATHSHEBA
    # ================================================================
    rel("SPOUSE_OF", p("Bathsheba"), p("David"), "2 Samuel 11:27"),
    rel("MOTHER_OF", p("Bathsheba"), p("Solomon"), "2 Samuel 12:24"),
    rel("HAS_ROLE", p("Bathsheba"), r("Formerly wife of Uriah"), "2 Samuel 11:3"),
    rel("ANCESTOR_OF", p("Bathsheba"), p("Jesus Christ"), "Matthew 1:6"),

    # ================================================================
    # NATHAN (prophet)
    # ================================================================
    rel("CALLED_AS", p("Nathan"), r("Prophet"), "2 Samuel 7:2; 12:1"),
    rel("TAUGHT", p("Nathan"), c("Parable of the ewe lamb (to David)"), "2 Samuel 12:1-7"),
    rel("PROPHESIED_ABOUT", p("Nathan"), p("David"), "2 Samuel 7:12-16"),
    rel("PROPHESIED_ABOUT", p("Nathan"), p("Solomon"), "1 Kings 1:11-13"),

    # ================================================================
    # ABSALOM
    # ================================================================
    rel("FOUGHT_AGAINST", p("Absalom"), p("David"), "2 Samuel 15:10-12"),
    rel("DIED_IN", p("Absalom"), pl("Forest of Ephraim"), "2 Samuel 18:9-15"),
    rel("LIVED_IN", p("Absalom"), pl("Jerusalem"), "2 Samuel 15:1-6"),
    rel("HAS_ROLE", p("Absalom"), r("Rebelled against his father David"), "2 Samuel 15"),

    # ================================================================
    # JOAB
    # ================================================================
    rel("CALLED_AS", p("Joab"), r("Commander of David's army"), "2 Samuel 8:16"),
    rel("FOUGHT_AGAINST", p("Joab"), p("Absalom"), "2 Samuel 18:14"),
    rel("FOUGHT_AGAINST", p("Joab"), p("Abner"), "2 Samuel 3:27"),
    rel("DIED_IN", p("Joab"), pl("Tabernacle altar"), "1 Kings 2:28-34"),

    # ================================================================
    # ABNER
    # ================================================================
    rel("CALLED_AS", p("Abner"), r("Commander of Saul's army"), "1 Samuel 14:50"),
    rel("FOUGHT_AGAINST", p("Abner"), p("David's forces"), "2 Samuel 2:12-17"),
    rel("DIED_IN", p("Abner"), pl("Hebron"), "2 Samuel 3:27"),

    # ================================================================
    # REHOBOAM
    # ================================================================
    rel("CALLED_AS", p("Rehoboam"), r("King of Judah"), "1 Kings 12:17"),
    rel("SUCCESSOR_OF", p("Rehoboam"), p("Solomon"), "1 Kings 11:43; 12:1"),
    rel("HAS_ROLE", p("Rehoboam"), r("Kingdom divided under his reign"), "1 Kings 12:16-20"),
    rel("LIVED_IN", p("Rehoboam"), pl("Jerusalem"), "1 Kings 14:21"),

    # ================================================================
    # JEROBOAM
    # ================================================================
    rel("CALLED_AS", p("Jeroboam"), r("First King of Northern Israel"), "1 Kings 12:20"),
    rel("HAS_ROLE", p("Jeroboam"), r("Set up golden calves in Dan and Bethel"), "1 Kings 12:28-29"),
    rel("PROPHESIED_ABOUT", p("Ahijah"), p("Jeroboam"), "1 Kings 11:29-39"),
    rel("LIVED_IN", p("Jeroboam"), pl("Shechem"), "1 Kings 12:25"),

    # ================================================================
    # AHAB
    # ================================================================
    rel("CALLED_AS", p("Ahab"), r("King of Israel"), "1 Kings 16:29"),
    rel("SPOUSE_OF", p("Ahab"), p("Jezebel"), "1 Kings 16:31"),
    rel("FOUGHT_AGAINST", p("Ahab"), p("Elijah"), "1 Kings 18:17-18; 21:20"),
    rel("DIED_IN", p("Ahab"), pl("Ramoth-gilead"), "1 Kings 22:34-37"),
    rel("HAS_ROLE", p("Ahab"), r("Introduced Baal worship to Israel"), "1 Kings 16:31-33"),

    # ================================================================
    # JEZEBEL
    # ================================================================
    rel("SPOUSE_OF", p("Jezebel"), p("Ahab"), "1 Kings 16:31"),
    rel("HAS_ROLE", p("Jezebel"), r("Persecuted prophets of the Lord"), "1 Kings 18:4,13"),
    rel("FOUGHT_AGAINST", p("Jezebel"), p("Elijah"), "1 Kings 19:1-2"),
    rel("KILLED", p("Jezebel"), p("Naboth"), "1 Kings 21:7-16"),
    rel("DIED_IN", p("Jezebel"), pl("Jezreel"), "2 Kings 9:30-37"),

    # ================================================================
    # NAAMAN
    # ================================================================
    rel("LIVED_IN", p("Naaman"), pl("Syria"), "2 Kings 5:1"),
    rel("CALLED_AS", p("Naaman"), r("Captain of Syrian army"), "2 Kings 5:1"),
    rel("TRAVELED_TO", p("Naaman"), pl("Jordan River"), "2 Kings 5:10-14"),
    rel("CONVERTED_BY", p("Naaman"), p("Elisha"), "2 Kings 5:15"),

    # ================================================================
    # GEHAZI
    # ================================================================
    rel("HAS_ROLE", p("Gehazi"), r("Servant of Elisha"), "2 Kings 4:12"),
    rel("HAS_ROLE", p("Gehazi"), r("Received leprosy for greed"), "2 Kings 5:25-27"),

    # ================================================================
    # HEZEKIAH
    # ================================================================
    rel("CALLED_AS", p("Hezekiah"), r("King of Judah"), "2 Kings 18:1"),
    rel("HAS_ROLE", p("Hezekiah"), r("Righteous reformer king"), "2 Kings 18:3-6"),
    rel("HEALED_BY", p("Hezekiah"), p("God (through Isaiah)"), "2 Kings 20:1-7"),
    rel("LIVED_IN", p("Hezekiah"), pl("Jerusalem"), "2 Kings 18:2"),
    rel("ALLIED_WITH", p("Hezekiah"), p("Isaiah"), "2 Kings 19:1-7"),

    # ================================================================
    # JOSIAH
    # ================================================================
    rel("CALLED_AS", p("Josiah"), r("King of Judah"), "2 Kings 22:1"),
    rel("HAS_ROLE", p("Josiah"), r("Found the book of the law"), "2 Kings 22:8-11"),
    rel("HAS_ROLE", p("Josiah"), r("Led religious reform"), "2 Kings 23:1-25"),
    rel("DIED_IN", p("Josiah"), pl("Megiddo"), "2 Kings 23:29"),

    # ================================================================
    # NEBUCHADNEZZAR
    # ================================================================
    rel("CALLED_AS", p("Nebuchadnezzar"), r("King of Babylon"), "2 Kings 24:1; Daniel 1:1"),
    rel("CONQUERED", p("Nebuchadnezzar"), pl("Jerusalem"), "2 Kings 25:1-10"),
    rel("SAW_IN_VISION", p("Nebuchadnezzar"), c("Great image/statue"), "Daniel 2:31-35"),
    rel("SAW_IN_VISION", p("Nebuchadnezzar"), c("Great tree cut down"), "Daniel 4:10-17"),
    rel("CONVERTED_BY", p("Nebuchadnezzar"), p("Daniel"), "Daniel 4:34-37"),
    rel("LIVED_IN", p("Nebuchadnezzar"), pl("Babylon"), "Daniel 4:30"),

    # ================================================================
    # CYRUS
    # ================================================================
    rel("CALLED_AS", p("Cyrus"), r("King of Persia"), "Ezra 1:1-2"),
    rel("HAS_TITLE", p("Cyrus"), c("The Lord's anointed"), "Isaiah 45:1"),
    rel("PROPHESIED_ABOUT", p("Isaiah"), p("Cyrus"), "Isaiah 44:28; 45:1"),
    rel("HAS_ROLE", p("Cyrus"), r("Decreed Jews' return from exile"), "Ezra 1:1-4"),
    rel("CONQUERED", p("Cyrus"), pl("Babylon"), "Daniel 5:30-31 (fall of Babylon)"),

    # ================================================================
    # EZRA
    # ================================================================
    rel("CALLED_AS", p("Ezra"), r("Priest and Scribe"), "Ezra 7:6,11"),
    rel("TRAVELED_TO", p("Ezra"), pl("Jerusalem (from Babylon)"), "Ezra 7:6-9"),
    rel("TAUGHT", p("Ezra"), c("Reading of the Law to the people"), "Nehemiah 8:1-8"),
    rel("HAS_ROLE", p("Ezra"), r("Led second return from exile"), "Ezra 7:6-9"),
    rel("AUTHORED", p("Ezra"), s("Book of Ezra"), "Ezra 7:6 (tradition)"),

    # ================================================================
    # NEHEMIAH
    # ================================================================
    rel("CALLED_AS", p("Nehemiah"), r("Governor of Judah"), "Nehemiah 5:14"),
    rel("TRAVELED_TO", p("Nehemiah"), pl("Jerusalem (from Susa)"), "Nehemiah 2:11"),
    rel("HAS_ROLE", p("Nehemiah"), r("Rebuilt walls of Jerusalem"), "Nehemiah 6:15"),
    rel("AUTHORED", p("Nehemiah"), s("Book of Nehemiah"), "Nehemiah 1:1 (tradition)"),
    rel("LIVED_IN", p("Nehemiah"), pl("Shushan/Susa"), "Nehemiah 1:1"),

    # ================================================================
    # MORDECAI
    # ================================================================
    rel("HAS_ROLE", p("Mordecai"), r("Guardian of Esther"), "Esther 2:5-7"),
    rel("LIVED_IN", p("Mordecai"), pl("Shushan/Susa"), "Esther 2:5"),
    rel("FOUGHT_AGAINST", p("Mordecai"), p("Haman"), "Esther 3-7"),
    rel("CALLED_AS", p("Mordecai"), r("Second to the king"), "Esther 10:3"),

    # ================================================================
    # HAMAN
    # ================================================================
    rel("HAS_ROLE", p("Haman"), r("Antagonist who plotted against the Jews"), "Esther 3:5-6"),
    rel("FOUGHT_AGAINST", p("Haman"), p("Mordecai"), "Esther 3:5-6"),
    rel("DIED_IN", p("Haman"), pl("Shushan (hanged on his own gallows)"), "Esther 7:10"),
    rel("LIVED_IN", p("Haman"), pl("Shushan/Susa"), "Esther 3:1"),

    # ================================================================
    # JOB
    # ================================================================
    rel("LIVED_IN", p("Job"), pl("Land of Uz"), "Job 1:1"),
    rel("HAS_TITLE", p("Job"), c("Perfect and upright man"), "Job 1:1"),
    rel("TAUGHT", p("Job"), c("Patient endurance through suffering"), "Job 1:21; 42:2-6; James 5:11"),
    rel("APPEARED_TO", p("God"), p("Job"), "Job 38:1; 42:5"),
    rel("BLESSED_BY", p("Job"), p("God"), "Job 42:10-17"),
    rel("AUTHORED", p("Job"), s("Book of Job"), "Job 1:1 (tradition)"),

    # ================================================================
    # MINOR PROPHETS
    # ================================================================
    # HOSEA
    rel("CALLED_AS", p("Hosea"), r("Prophet"), "Hosea 1:1"),
    rel("SPOUSE_OF", p("Hosea"), p("Gomer"), "Hosea 1:2-3"),
    rel("AUTHORED", p("Hosea"), s("Book of Hosea"), "Hosea 1:1"),
    rel("TAUGHT", p("Hosea"), c("God's covenant love despite Israel's unfaithfulness"), "Hosea 2:19-20; 11:1-4"),
    rel("PROPHESIED_ABOUT", p("Hosea"), c("Restoration of Israel"), "Hosea 14:4-7"),

    # JOEL
    rel("CALLED_AS", p("Joel"), r("Prophet"), "Joel 1:1"),
    rel("AUTHORED", p("Joel"), s("Book of Joel"), "Joel 1:1"),
    rel("PROPHESIED_ABOUT", p("Joel"), c("Day of the Lord"), "Joel 2:1,31"),
    rel("PROPHESIED_ABOUT", p("Joel"), c("Outpouring of the Spirit"), "Joel 2:28-29"),

    # AMOS
    rel("CALLED_AS", p("Amos"), r("Prophet"), "Amos 1:1; 7:14-15"),
    rel("BORN_IN", p("Amos"), pl("Tekoa"), "Amos 1:1"),
    rel("AUTHORED", p("Amos"), s("Book of Amos"), "Amos 1:1"),
    rel("HAS_ROLE", p("Amos"), r("Herdsman and dresser of sycamore trees"), "Amos 7:14"),
    rel("PROPHESIED_ABOUT", p("Amos"), c("Social justice"), "Amos 5:24"),

    # OBADIAH
    rel("CALLED_AS", p("Obadiah"), r("Prophet"), "Obadiah 1:1"),
    rel("AUTHORED", p("Obadiah"), s("Book of Obadiah"), "Obadiah 1:1"),
    rel("PROPHESIED_ABOUT", p("Obadiah"), c("Fall of Edom"), "Obadiah 1:1-4"),
    rel("PROPHESIED_ABOUT", p("Obadiah"), c("Saviors on Mount Zion"), "Obadiah 1:21"),

    # JONAH
    rel("CALLED_AS", p("Jonah"), r("Prophet"), "Jonah 1:1; 2 Kings 14:25"),
    rel("AUTHORED", p("Jonah"), s("Book of Jonah"), "Jonah 1:1"),
    rel("TRAVELED_TO", p("Jonah"), pl("Tarshish (fled)"), "Jonah 1:3"),
    rel("TRAVELED_TO", p("Jonah"), pl("Nineveh"), "Jonah 3:3"),
    rel("TYPE_OF", p("Jonah"), p("Jesus Christ"), "Matthew 12:40 (three days)"),
    rel("TAUGHT", p("Jonah"), c("Repentance to Nineveh"), "Jonah 3:4-5"),

    # MICAH
    rel("CALLED_AS", p("Micah"), r("Prophet"), "Micah 1:1"),
    rel("BORN_IN", p("Micah"), pl("Moresheth"), "Micah 1:1"),
    rel("AUTHORED", p("Micah"), s("Book of Micah"), "Micah 1:1"),
    rel("PROPHESIED_ABOUT", p("Micah"), p("Jesus Christ"), "Micah 5:2 (Bethlehem)"),
    rel("TAUGHT", p("Micah"), c("Do justly, love mercy, walk humbly"), "Micah 6:8"),

    # NAHUM
    rel("CALLED_AS", p("Nahum"), r("Prophet"), "Nahum 1:1"),
    rel("AUTHORED", p("Nahum"), s("Book of Nahum"), "Nahum 1:1"),
    rel("PROPHESIED_ABOUT", p("Nahum"), c("Destruction of Nineveh"), "Nahum 1:1; 3:7"),

    # HABAKKUK
    rel("CALLED_AS", p("Habakkuk"), r("Prophet"), "Habakkuk 1:1"),
    rel("AUTHORED", p("Habakkuk"), s("Book of Habakkuk"), "Habakkuk 1:1"),
    rel("TAUGHT", p("Habakkuk"), c("The just shall live by faith"), "Habakkuk 2:4"),

    # ZEPHANIAH
    rel("CALLED_AS", p("Zephaniah"), r("Prophet"), "Zephaniah 1:1"),
    rel("AUTHORED", p("Zephaniah"), s("Book of Zephaniah"), "Zephaniah 1:1"),
    rel("PROPHESIED_ABOUT", p("Zephaniah"), c("Day of the Lord"), "Zephaniah 1:14-18"),

    # HAGGAI
    rel("CALLED_AS", p("Haggai"), r("Prophet"), "Haggai 1:1"),
    rel("AUTHORED", p("Haggai"), s("Book of Haggai"), "Haggai 1:1"),
    rel("TAUGHT", p("Haggai"), c("Rebuild the temple"), "Haggai 1:2-8"),
    rel("PROPHESIED_ABOUT", p("Haggai"), c("Glory of the latter temple"), "Haggai 2:9"),

    # ZECHARIAH (prophet)
    rel("CALLED_AS", p("Zechariah"), r("Prophet"), "Zechariah 1:1"),
    rel("AUTHORED", p("Zechariah"), s("Book of Zechariah"), "Zechariah 1:1"),
    rel("SAW_IN_VISION", p("Zechariah"), c("Four horsemen"), "Zechariah 1:8-11"),
    rel("SAW_IN_VISION", p("Zechariah"), c("Golden candlestick and two olive trees"), "Zechariah 4:1-6"),
    rel("PROPHESIED_ABOUT", p("Zechariah"), p("Jesus Christ"), "Zechariah 9:9; 12:10; 13:6"),

    # MALACHI — enrich
    rel("AUTHORED", p("Malachi"), s("Book of Malachi"), "Malachi 1:1"),
    rel("TAUGHT", p("Malachi"), c("Tithing"), "Malachi 3:8-12"),
    rel("TAUGHT", p("Malachi"), c("Book of remembrance"), "Malachi 3:16"),

    # ================================================================
    # ADDITIONAL OT FIGURES
    # ================================================================

    # ASENATH
    rel("SPOUSE_OF", p("Asenath"), p("Joseph"), "Genesis 41:45"),
    rel("MOTHER_OF", p("Asenath"), p("Ephraim"), "Genesis 41:50-52"),
    rel("MOTHER_OF", p("Asenath"), p("Manasseh"), "Genesis 41:50-51"),

    # POTIPHAR
    rel("HAS_ROLE", p("Potiphar"), r("Egyptian officer who bought Joseph"), "Genesis 39:1"),
    rel("LIVED_IN", p("Potiphar"), pl("Egypt"), "Genesis 39:1"),

    # JESSE
    rel("LIVED_IN", p("Jesse"), pl("Bethlehem"), "1 Samuel 16:1"),
    rel("HAS_ROLE", p("Jesse"), r("Father of David"), "1 Samuel 16:10-13"),
    rel("ANCESTOR_OF", p("Jesse"), p("Jesus Christ"), "Isaiah 11:1; Matthew 1:5-6"),

    # URIAH
    rel("HAS_ROLE", p("Uriah"), r("Hittite soldier, husband of Bathsheba"), "2 Samuel 11:3"),
    rel("DIED_IN", p("Uriah"), pl("Siege of Rabbah"), "2 Samuel 11:17"),
    rel("KILLED", p("David"), p("Uriah"), "2 Samuel 11:14-17 (arranged)"),

    # ELKANAH
    rel("SPOUSE_OF", p("Elkanah"), p("Hannah"), "1 Samuel 1:1-2"),
    rel("LIVED_IN", p("Elkanah"), pl("Ramathaim-zophim"), "1 Samuel 1:1"),

    # ABIATHAR
    rel("CALLED_AS", p("Abiathar"), r("High Priest"), "1 Samuel 22:20; 2 Samuel 20:25"),
    rel("ALLIED_WITH", p("Abiathar"), p("David"), "1 Samuel 22:20-23"),

    # ZADOK
    rel("CALLED_AS", p("Zadok"), r("High Priest"), "2 Samuel 20:25"),
    rel("ALLIED_WITH", p("Zadok"), p("Solomon"), "1 Kings 1:38-39"),

    # HIRAM (king of Tyre)
    rel("ALLIED_WITH", p("Hiram"), p("Solomon"), "1 Kings 5:1-12"),
    rel("HAS_ROLE", p("Hiram"), r("King of Tyre who helped build temple"), "1 Kings 5:1-12"),

    # ELIJAH/ELISHA HELPERS
    # Widow of Zarephath
    rel("LIVED_IN", p("Widow of Zarephath"), pl("Zarephath"), "1 Kings 17:9-10"),
    rel("HEALED_BY", p("Widow of Zarephath's son"), p("Elijah"), "1 Kings 17:17-23"),

    # SHADRACH, MESHACH, ABED-NEGO
    rel("LIVED_IN", p("Shadrach"), pl("Babylon"), "Daniel 1:6-7"),
    rel("LIVED_IN", p("Meshach"), pl("Babylon"), "Daniel 1:6-7"),
    rel("LIVED_IN", p("Abed-nego"), pl("Babylon"), "Daniel 1:6-7"),
    rel("HEALED_BY", p("Shadrach"), p("God (fiery furnace)"), "Daniel 3:23-27"),
    rel("ALLIED_WITH", p("Shadrach"), p("Daniel"), "Daniel 1:6-7"),

    # BELSHAZZAR
    rel("CALLED_AS", p("Belshazzar"), r("King of Babylon"), "Daniel 5:1"),
    rel("SAW_IN_VISION", p("Belshazzar"), c("Writing on the wall"), "Daniel 5:5-6"),
    rel("DIED_IN", p("Belshazzar"), pl("Babylon"), "Daniel 5:30"),
]


def main():
    with open(RELATIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    added = 0
    skipped = 0
    new_types = set()

    for rtype, entry in ALL:
        if rtype not in data:
            data[rtype] = []
            new_types.add(rtype)

        existing = {(r["from"]["name"].lower(), r["to"]["name"].lower()) for r in data[rtype]}
        key = (entry["from"]["name"].lower(), entry["to"]["name"].lower())
        if key in existing:
            skipped += 1
            continue
        data[rtype].append(entry)
        added += 1

    sorted_data = dict(sorted(data.items()))
    with open(RELATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, indent=2, ensure_ascii=False)

    total = sum(len(v) for v in sorted_data.values())
    print(f"Added {added} new relations, skipped {skipped} duplicates.")
    if new_types:
        print(f"New relation types: {new_types}")
    print(f"Total relations: {total}")


if __name__ == "__main__":
    main()

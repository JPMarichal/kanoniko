"""Tier 2 BofM: Exhaustive biographical relations for ALL significant Book of Mormon characters.

Covers: 1 Nephi through Moroni — Lehite dynasty, Nephite leaders, Lamanite figures,
Jaredites, prophets, military leaders, dissenters, converts.
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
    # SARIAH
    # ================================================================
    rel("SPOUSE_OF", p("Sariah"), p("Lehi"), "1 Nephi 2:5"),
    rel("MOTHER_OF", p("Sariah"), p("Laman"), "1 Nephi 2:5"),
    rel("MOTHER_OF", p("Sariah"), p("Lemuel"), "1 Nephi 2:5"),
    rel("MOTHER_OF", p("Sariah"), p("Sam"), "1 Nephi 2:5"),
    rel("MOTHER_OF", p("Sariah"), p("Jacob (son of Lehi)"), "1 Nephi 18:7"),
    rel("MOTHER_OF", p("Sariah"), p("Joseph (son of Lehi)"), "1 Nephi 18:7"),
    rel("TRAVELED_TO", p("Sariah"), pl("Promised Land"), "1 Nephi 18:23"),
    rel("LIVED_IN", p("Sariah"), pl("Jerusalem"), "1 Nephi 1:4"),

    # ================================================================
    # LAMAN
    # ================================================================
    rel("HAS_ROLE", p("Laman"), r("Eldest son of Lehi"), "1 Nephi 2:5"),
    rel("FOUGHT_AGAINST", p("Laman"), p("Nephi"), "1 Nephi 3:28; 7:16; 17:48"),
    rel("TRAVELED_TO", p("Laman"), pl("Promised Land"), "1 Nephi 18:23"),
    rel("HAS_ROLE", p("Laman"), r("Murmured against father and brother"), "1 Nephi 2:11-12"),
    rel("HAS_ROLE", p("Laman"), r("Progenitor of the Lamanites"), "Jacob 1:13-14"),
    rel("BROTHER_OF", p("Laman"), p("Nephi"), "1 Nephi 2:5"),

    # ================================================================
    # LEMUEL
    # ================================================================
    rel("HAS_ROLE", p("Lemuel"), r("Second son of Lehi"), "1 Nephi 2:5"),
    rel("FOUGHT_AGAINST", p("Lemuel"), p("Nephi"), "1 Nephi 3:28; 7:16"),
    rel("TRAVELED_TO", p("Lemuel"), pl("Promised Land"), "1 Nephi 18:23"),
    rel("ALLIED_WITH", p("Lemuel"), p("Laman"), "1 Nephi 2:11-12"),

    # ================================================================
    # SAM
    # ================================================================
    rel("HAS_ROLE", p("Sam"), r("Third son of Lehi"), "1 Nephi 2:5"),
    rel("ALLIED_WITH", p("Sam"), p("Nephi"), "1 Nephi 2:17"),
    rel("TRAVELED_TO", p("Sam"), pl("Promised Land"), "1 Nephi 18:23"),
    rel("BLESSED_BY", p("Sam"), p("Lehi"), "2 Nephi 4:11"),

    # ================================================================
    # JOSEPH (son of Lehi)
    # ================================================================
    rel("BORN_IN", p("Joseph (son of Lehi)"), pl("Wilderness"), "1 Nephi 18:7"),
    rel("BLESSED_BY", p("Joseph (son of Lehi)"), p("Lehi"), "2 Nephi 3:1-25"),
    rel("TRAVELED_TO", p("Joseph (son of Lehi)"), pl("Promised Land"), "1 Nephi 18:23"),
    rel("HAS_ROLE", p("Joseph (son of Lehi)"), r("Youngest son of Lehi and Sariah"), "2 Nephi 3:1"),

    # ================================================================
    # ISHMAEL (companion of Lehi)
    # ================================================================
    rel("TRAVELED_TO", p("Ishmael (companion of Lehi)"), pl("Promised Land"), "1 Nephi 7:2-5; 18:23"),
    rel("DIED_IN", p("Ishmael (companion of Lehi)"), pl("Nahom"), "1 Nephi 16:34"),
    rel("HAS_ROLE", p("Ishmael (companion of Lehi)"), r("Father of the wives of Lehi's sons"), "1 Nephi 7:1-2; 16:7"),

    # ================================================================
    # ZORAM
    # ================================================================
    rel("HAS_ROLE", p("Zoram"), r("Servant of Laban"), "1 Nephi 4:20,31-35"),
    rel("TRAVELED_TO", p("Zoram"), pl("Promised Land"), "1 Nephi 4:35; 18:23"),
    rel("COVENANT_WITH", p("Zoram"), p("Nephi"), "1 Nephi 4:31-37"),
    rel("BLESSED_BY", p("Zoram"), p("Lehi"), "2 Nephi 1:30-32"),

    # ================================================================
    # LABAN (BofM)
    # ================================================================
    rel("LIVED_IN", p("Laban (BofM)"), pl("Jerusalem"), "1 Nephi 3:3"),
    rel("HAS_ROLE", p("Laban (BofM)"), r("Keeper of the brass plates"), "1 Nephi 3:3-4"),
    rel("KILLED", p("Nephi"), p("Laban (BofM)"), "1 Nephi 4:18"),
    rel("DIED_IN", p("Laban (BofM)"), pl("Jerusalem"), "1 Nephi 4:18"),

    # ================================================================
    # SHEREM
    # ================================================================
    rel("HAS_ROLE", p("Sherem"), r("Anti-Christ, denied Christ"), "Jacob 7:1-2"),
    rel("FOUGHT_AGAINST", p("Sherem"), p("Jacob (son of Lehi)"), "Jacob 7:1-7"),
    rel("DIED_IN", p("Sherem"), pl("Land of Nephi"), "Jacob 7:15,20"),
    rel("CONVERTED_BY", p("Sherem"), c("Power of the Lord struck him down"), "Jacob 7:13-15"),

    # ================================================================
    # ENOS
    # ================================================================
    rel("AUTHORED", p("Enos"), s("Book of Enos"), "Enos 1:1"),
    rel("TAUGHT", p("Enos"), c("Wrestled before God in mighty prayer"), "Enos 1:2-4"),
    rel("CALLED_AS", p("Enos"), r("Prophet and record keeper"), "Enos 1:1; Jarom 1:1"),
    rel("CONVERTED_BY", p("Enos"), p("Jacob (son of Lehi)"), "Enos 1:1-4"),
    rel("HAS_ROLE", p("Enos"), r("Prayed for Nephites and Lamanites"), "Enos 1:9-17"),

    # ================================================================
    # JAROM
    # ================================================================
    rel("AUTHORED", p("Jarom"), s("Book of Jarom"), "Jarom 1:1"),
    rel("FATHER_OF", p("Enos"), p("Jarom"), "Jarom 1:1 (implied)"),
    rel("CALLED_AS", p("Jarom"), r("Record keeper"), "Jarom 1:1"),

    # ================================================================
    # OMNI
    # ================================================================
    rel("AUTHORED", p("Omni"), s("Book of Omni (portion)"), "Omni 1:1"),
    rel("HAS_ROLE", p("Omni"), r("Wicked man who kept the record"), "Omni 1:2"),
    rel("CALLED_AS", p("Omni"), r("Record keeper"), "Omni 1:1"),

    # ================================================================
    # ZENIFF
    # ================================================================
    rel("TRAVELED_TO", p("Zeniff"), pl("Land of Nephi"), "Mosiah 9:3-5"),
    rel("CALLED_AS", p("Zeniff"), r("King of Nephite colony in land of Nephi"), "Mosiah 7:9,21"),
    rel("FOUGHT_AGAINST", p("Zeniff"), c("Lamanites"), "Mosiah 9:14-18; 10:6-11"),
    rel("AUTHORED", p("Zeniff"), s("Record of Zeniff"), "Mosiah 9-10"),
    rel("FATHER_OF", p("Zeniff"), p("Noah (Nephite king)"), "Mosiah 11:1"),

    # ================================================================
    # KING NOAH
    # ================================================================
    rel("CALLED_AS", p("Noah (Nephite king)"), r("King (wicked)"), "Mosiah 11:1"),
    rel("SUCCESSOR_OF", p("Noah (Nephite king)"), p("Zeniff"), "Mosiah 11:1"),
    rel("FOUGHT_AGAINST", p("Noah (Nephite king)"), p("Abinadi"), "Mosiah 11:27-29; 17:1"),
    rel("KILLED", p("Noah (Nephite king)"), p("Abinadi"), "Mosiah 17:13-20"),
    rel("DIED_IN", p("Noah (Nephite king)"), pl("Land of Nephi (death by fire)"), "Mosiah 19:20"),
    rel("HAS_ROLE", p("Noah (Nephite king)"), r("Built lavish buildings, imposed heavy taxes"), "Mosiah 11:2-13"),
    rel("FATHER_OF", p("Noah (Nephite king)"), p("Limhi"), "Mosiah 19:26"),

    # ================================================================
    # LIMHI
    # ================================================================
    rel("CALLED_AS", p("Limhi"), r("King"), "Mosiah 19:26"),
    rel("SUCCESSOR_OF", p("Limhi"), p("Noah (Nephite king)"), "Mosiah 19:26"),
    rel("LIVED_IN", p("Limhi"), pl("Land of Nephi"), "Mosiah 7:9"),
    rel("TRAVELED_TO", p("Limhi"), pl("Zarahemla (escaped Lamanite bondage)"), "Mosiah 22:11-13"),
    rel("HAS_ROLE", p("Limhi"), r("Led his people out of bondage"), "Mosiah 22"),

    # ================================================================
    # GIDEON (BofM)
    # ================================================================
    rel("FOUGHT_AGAINST", p("Gideon (BofM)"), p("Noah (Nephite king)"), "Mosiah 19:4"),
    rel("HAS_ROLE", p("Gideon (BofM)"), r("Counselor to King Limhi"), "Mosiah 22:3-9"),
    rel("KILLED", p("Nehor"), p("Gideon (BofM)"), "Alma 1:9"),
    rel("DIED_IN", p("Gideon (BofM)"), pl("Zarahemla"), "Alma 1:9"),
    rel("HAS_TITLE", p("Gideon (BofM)"), c("Strong man and enemy of the king"), "Mosiah 19:4"),

    # ================================================================
    # NEHOR
    # ================================================================
    rel("HAS_ROLE", p("Nehor"), r("False teacher who introduced priestcraft"), "Alma 1:2-6"),
    rel("KILLED", p("Nehor"), p("Gideon (BofM)"), "Alma 1:9"),
    rel("DIED_IN", p("Nehor"), pl("Hill Manti (executed)"), "Alma 1:15"),
    rel("TAUGHT", p("Nehor"), c("All mankind should be saved / paid clergy"), "Alma 1:3-4"),

    # ================================================================
    # AMULEK
    # ================================================================
    rel("LIVED_IN", p("Amulek"), pl("Ammonihah"), "Alma 8:20"),
    rel("CALLED_AS", p("Amulek"), r("Missionary companion of Alma"), "Alma 8:20-21"),
    rel("APPEARED_TO", p("Angel of the Lord"), p("Amulek"), "Alma 8:20"),
    rel("TAUGHT", p("Amulek"), c("Atonement is infinite and eternal"), "Alma 34:8-16"),
    rel("TAUGHT", p("Amulek"), c("Pray in all things"), "Alma 34:17-27"),
    rel("HAS_ROLE", p("Amulek"), r("Wealthy man who gave up all to follow"), "Alma 10:4-6; 15:16"),

    # ================================================================
    # ZEEZROM
    # ================================================================
    rel("LIVED_IN", p("Zeezrom"), pl("Ammonihah"), "Alma 11:21"),
    rel("HAS_ROLE", p("Zeezrom"), r("Lawyer who tried to trap Alma and Amulek"), "Alma 11:21-25"),
    rel("CONVERTED_BY", p("Zeezrom"), p("Alma the Younger"), "Alma 15:3-12"),
    rel("HEALED_BY", p("Zeezrom"), p("Alma the Younger"), "Alma 15:5-11"),
    rel("CALLED_AS", p("Zeezrom"), r("Missionary after conversion"), "Alma 31:6"),

    # ================================================================
    # KORIHOR
    # ================================================================
    rel("HAS_ROLE", p("Korihor"), r("Anti-Christ, demanded a sign"), "Alma 30:6-18"),
    rel("FOUGHT_AGAINST", p("Korihor"), p("Alma the Younger"), "Alma 30:30-44"),
    rel("TAUGHT", p("Korihor"), c("No God, no Christ, no atonement"), "Alma 30:12-18"),
    rel("DIED_IN", p("Korihor"), pl("Among the Zoramites (trampled)"), "Alma 30:59"),
    rel("HAS_ROLE", p("Korihor"), r("Struck dumb as a sign"), "Alma 30:49-50"),

    # ================================================================
    # AARON (son of Mosiah)
    # ================================================================
    rel("CALLED_AS", p("Aaron (son of Mosiah)"), r("Missionary to the Lamanites"), "Alma 21:1"),
    rel("TRAVELED_TO", p("Aaron (son of Mosiah)"), pl("Land of Nephi"), "Alma 21:1"),
    rel("CONVERTED_BY", p("Aaron (son of Mosiah)"), p("Angel of the Lord"), "Mosiah 27:11-16"),
    rel("TAUGHT", p("Aaron (son of Mosiah)"), c("Plan of redemption to Lamoni's father"), "Alma 22:12-14"),
    rel("HAS_ROLE", p("Aaron (son of Mosiah)"), r("Imprisoned and delivered"), "Alma 21:13-14; 22:1"),

    # ================================================================
    # LAMONI
    # ================================================================
    rel("CALLED_AS", p("Lamoni"), r("Lamanite King"), "Alma 17:21"),
    rel("LIVED_IN", p("Lamoni"), pl("Land of Ishmael"), "Alma 17:21"),
    rel("CONVERTED_BY", p("Lamoni"), p("Ammon (son of Mosiah)"), "Alma 18:40-43; 19:12-13"),
    rel("HAS_ROLE", p("Lamoni"), r("Fell as if dead upon conversion"), "Alma 18:42-43"),
    rel("FATHER_OF", p("King Lamoni's Father"), p("Lamoni"), "Alma 20:2 (implied)"),

    # ================================================================
    # KING LAMONI'S FATHER
    # ================================================================
    rel("CALLED_AS", p("King Lamoni's Father"), r("King over all the Lamanites"), "Alma 20:8"),
    rel("CONVERTED_BY", p("King Lamoni's Father"), p("Aaron (son of Mosiah)"), "Alma 22:15-18"),
    rel("HAS_ROLE", p("King Lamoni's Father"), r("Offered half his kingdom to the Lord"), "Alma 22:15"),
    rel("TAUGHT", p("King Lamoni's Father"), c("Gave up all his sins to know God"), "Alma 22:18"),

    # ================================================================
    # ANTI-NEPHI-LEHIES / PEOPLE OF AMMON
    # ================================================================
    rel("CONVERTED_BY", p("Anti-Nephi-Lehies"), p("Sons of Mosiah"), "Alma 23:1-7"),
    rel("COVENANT_WITH", p("Anti-Nephi-Lehies"), p("God"), "Alma 24:17-19"),
    rel("TRAVELED_TO", p("Anti-Nephi-Lehies"), pl("Zarahemla / Land of Jershon"), "Alma 27:21-26"),
    rel("HAS_ROLE", p("Anti-Nephi-Lehies"), r("Buried weapons, covenanted never to fight"), "Alma 24:17-19"),
    rel("IS_SAME_AS", p("Anti-Nephi-Lehies"), p("People of Ammon"), "Alma 27:26"),

    # ================================================================
    # STRIPLING WARRIORS / SONS OF HELAMAN
    # ================================================================
    rel("HAS_ROLE", p("Stripling Warriors"), r("2000 young men who fought for Nephites"), "Alma 53:18-22"),
    rel("FATHER_OF", p("Anti-Nephi-Lehies"), p("Stripling Warriors"), "Alma 53:16 (collectively)"),
    rel("COMMANDED_BY", p("Stripling Warriors"), p("Helaman"), "Alma 53:19-22"),
    rel("FOUGHT_AGAINST", p("Stripling Warriors"), c("Lamanite armies"), "Alma 56:44-54"),
    rel("TAUGHT", p("Stripling Warriors"), c("Faith of their mothers preserved them"), "Alma 56:47-48"),
    rel("HAS_TITLE", p("Stripling Warriors"), c("Sons of Helaman"), "Alma 56:10"),

    # ================================================================
    # TEANCUM
    # ================================================================
    rel("CALLED_AS", p("Teancum"), r("Nephite Military Commander"), "Alma 50:35"),
    rel("KILLED", p("Teancum"), p("Amalickiah"), "Alma 51:34"),
    rel("KILLED", p("Teancum"), p("Ammoron"), "Alma 62:36"),
    rel("DIED_IN", p("Teancum"), pl("Battle (killed after slaying Ammoron)"), "Alma 62:36"),
    rel("FOUGHT_AGAINST", p("Teancum"), c("Lamanite armies"), "Alma 50-62"),

    # ================================================================
    # AMALICKIAH
    # ================================================================
    rel("HAS_ROLE", p("Amalickiah"), r("Nephite dissenter who became Lamanite king"), "Alma 46:3-10; 47:35"),
    rel("FOUGHT_AGAINST", p("Amalickiah"), p("Captain Moroni"), "Alma 46:1-3; 51:34"),
    rel("LIVED_IN", p("Amalickiah"), pl("Land of Nephi (Lamanite territory)"), "Alma 47:1"),
    rel("KILLED", p("Amalickiah"), c("By deception (multiple murders)"), "Alma 47:18-24"),
    rel("DIED_IN", p("Amalickiah"), pl("Camp (killed by Teancum)"), "Alma 51:34"),

    # ================================================================
    # AMMORON
    # ================================================================
    rel("HAS_ROLE", p("Ammoron"), r("Succeeded Amalickiah as Lamanite king"), "Alma 52:3"),
    rel("BROTHER_OF", p("Ammoron"), p("Amalickiah"), "Alma 52:3"),
    rel("FOUGHT_AGAINST", p("Ammoron"), p("Captain Moroni"), "Alma 54"),
    rel("DIED_IN", p("Ammoron"), pl("City of Moroni (killed by Teancum)"), "Alma 62:36"),

    # ================================================================
    # PAHORAN
    # ================================================================
    rel("CALLED_AS", p("Pahoran"), r("Chief Judge"), "Alma 50:39-40"),
    rel("SUCCESSOR_OF", p("Pahoran"), p("Nephihah"), "Alma 50:39-40"),
    rel("FOUGHT_AGAINST", p("Pahoran"), c("King-men (Nephite dissenters)"), "Alma 61:3-8"),
    rel("ALLIED_WITH", p("Pahoran"), p("Captain Moroni"), "Alma 61; 62:1-6"),
    rel("LIVED_IN", p("Pahoran"), pl("Zarahemla"), "Alma 50:39"),

    # ================================================================
    # ZERAHEMNAH
    # ================================================================
    rel("CALLED_AS", p("Zerahemnah"), r("Lamanite Commander"), "Alma 43:5,44"),
    rel("FOUGHT_AGAINST", p("Zerahemnah"), p("Captain Moroni"), "Alma 43-44"),
    rel("HAS_ROLE", p("Zerahemnah"), r("Defeated and disarmed by Moroni"), "Alma 44:12-15"),

    # ================================================================
    # NEPHIHAH
    # ================================================================
    rel("CALLED_AS", p("Nephihah"), r("Chief Judge"), "Alma 4:17,20"),
    rel("SUCCESSOR_OF", p("Nephihah"), p("Alma the Younger"), "Alma 4:17,20"),
    rel("LIVED_IN", p("Nephihah"), pl("Zarahemla"), "Alma 4:17"),

    # ================================================================
    # HELAMAN (son of Helaman)
    # ================================================================
    rel("CALLED_AS", p("Helaman (son of Helaman)"), r("Chief Judge"), "Helaman 2:2"),
    rel("AUTHORED", p("Helaman (son of Helaman)"), s("Book of Helaman (portion)"), "Helaman 2:2"),
    rel("SUCCESSOR_OF", p("Helaman (son of Helaman)"), p("Helaman"), "Helaman 2:2"),
    rel("LIVED_IN", p("Helaman (son of Helaman)"), pl("Zarahemla"), "Helaman 2:2"),
    rel("FOUGHT_AGAINST", p("Helaman (son of Helaman)"), c("Gadianton robbers"), "Helaman 2:3-14"),

    # ================================================================
    # NEPHI (son of Helaman)
    # ================================================================
    rel("CALLED_AS", p("Nephi (son of Helaman)"), r("Chief Judge (resigned)"), "Helaman 5:1-4"),
    rel("TRAVELED_TO", p("Nephi (son of Helaman)"), pl("Land of Nephi (missionary)"), "Helaman 5:20"),
    rel("HAS_ROLE", p("Nephi (son of Helaman)"), r("Imprisoned and delivered by fire"), "Helaman 5:20-52"),
    rel("TAUGHT", p("Nephi (son of Helaman)"), c("Standing on the wall, prophesying"), "Helaman 7:6-29"),
    rel("SAW_IN_VISION", p("Nephi (son of Helaman)"), c("Murder of the chief judge"), "Helaman 8:27; 9:36-38"),
    rel("HOLDS_PRIESTHOOD", p("Nephi (son of Helaman)"), c("Sealing power"), "Helaman 10:7"),

    # ================================================================
    # NEPHI (disciple, 3 Nephi)
    # ================================================================
    rel("CALLED_AS", p("Nephi (disciple)"), r("Disciple of Christ"), "3 Nephi 19:4"),
    rel("BAPTIZED_BY", p("Nephi (disciple)"), p("Jesus Christ (authority)"), "3 Nephi 11:21-26"),
    rel("HAS_ROLE", p("Nephi (disciple)"), r("First of twelve Nephite disciples"), "3 Nephi 19:4"),
    rel("TAUGHT", p("Nephi (disciple)"), c("Baptized the people"), "3 Nephi 19:11-12"),

    # ================================================================
    # THREE NEPHITES
    # ================================================================
    rel("HAS_ROLE", p("Three Nephites"), r("Desired to remain until Christ's return"), "3 Nephi 28:1-9"),
    rel("HAS_TITLE", p("Three Nephites"), c("Translated beings"), "3 Nephi 28:15-17"),
    rel("TAUGHT", p("Three Nephites"), c("Ministered among Nephites and Lamanites"), "3 Nephi 28:18-23"),
    rel("APPEARED_TO", p("Three Nephites"), p("Mormon"), "3 Nephi 28:24-26; Mormon 8:11"),

    # ================================================================
    # LACHONEUS
    # ================================================================
    rel("CALLED_AS", p("Lachoneus"), r("Chief Judge"), "3 Nephi 1:1"),
    rel("FOUGHT_AGAINST", p("Lachoneus"), p("Giddianhi"), "3 Nephi 3:1-12"),
    rel("HAS_ROLE", p("Lachoneus"), r("Gathered Nephites against Gadianton robbers"), "3 Nephi 3:13-22"),
    rel("LIVED_IN", p("Lachoneus"), pl("Zarahemla"), "3 Nephi 1:1"),

    # ================================================================
    # GIDDIANHI
    # ================================================================
    rel("CALLED_AS", p("Giddianhi"), r("Leader of Gadianton robbers"), "3 Nephi 3:9"),
    rel("FOUGHT_AGAINST", p("Giddianhi"), p("Lachoneus"), "3 Nephi 3-4"),
    rel("DIED_IN", p("Giddianhi"), pl("Battle against Nephites"), "3 Nephi 4:14"),
    rel("AUTHORED", p("Giddianhi"), s("Epistle to Lachoneus"), "3 Nephi 3:1-10"),

    # ================================================================
    # SAMUEL THE LAMANITE — enrich further
    # ================================================================
    rel("BORN_IN", p("Samuel the Lamanite"), pl("Lamanite lands"), "Helaman 13:2 (implied)"),
    rel("LIVED_DURING", p("Samuel the Lamanite"), per("~6 BC"), "Helaman 13:2; 14:2"),
    rel("TAUGHT", p("Samuel the Lamanite"), c("If ye do not repent, great city Zarahemla will be destroyed"), "Helaman 13:12-14"),

    # ================================================================
    # CORIANTUMR (last Jaredite)
    # ================================================================
    rel("CALLED_AS", p("Coriantumr"), r("Last Jaredite king"), "Ether 12:1; 13:15-21"),
    rel("FOUGHT_AGAINST", p("Coriantumr"), p("Shiz"), "Ether 14-15"),
    rel("HAS_ROLE", p("Coriantumr"), r("Sole survivor of Jaredite destruction"), "Ether 15:32; Omni 1:21"),
    rel("LIVED_IN", p("Coriantumr"), pl("Among the people of Zarahemla"), "Omni 1:21"),
    rel("PROPHESIED_ABOUT", p("Ether"), p("Coriantumr"), "Ether 13:20-21"),

    # ================================================================
    # SHIZ
    # ================================================================
    rel("FOUGHT_AGAINST", p("Shiz"), p("Coriantumr"), "Ether 14-15"),
    rel("DIED_IN", p("Shiz"), pl("Hill Ramah/Cumorah"), "Ether 15:29-31"),
    rel("HAS_ROLE", p("Shiz"), r("Military leader in final Jaredite wars"), "Ether 14:17"),

    # ================================================================
    # JARED
    # ================================================================
    rel("BROTHER_OF", p("Jared"), p("Brother of Jared"), "Ether 1:33-34"),
    rel("TRAVELED_TO", p("Jared"), pl("Promised Land"), "Ether 6:12"),
    rel("TRAVELED_TO", p("Jared"), pl("Valley of Nimrod"), "Ether 2:1"),
    rel("LIVED_DURING", p("Jared"), per("Tower of Babel"), "Ether 1:33"),
    rel("HAS_ROLE", p("Jared"), r("Asked his brother to pray God would not confound their language"), "Ether 1:34-37"),

    # ================================================================
    # AKISH
    # ================================================================
    rel("HAS_ROLE", p("Akish"), r("Introduced secret combinations among Jaredites"), "Ether 8:11-18"),
    rel("FOUGHT_AGAINST", p("Akish"), c("Own family (civil war)"), "Ether 9:1-12"),
    rel("KILLED", p("Akish"), p("Jared (son of Omer)"), "Ether 9:5"),

    # ================================================================
    # OMER
    # ================================================================
    rel("CALLED_AS", p("Omer"), r("Jaredite King"), "Ether 8:1"),
    rel("HAS_ROLE", p("Omer"), r("Overthrown by son, later restored"), "Ether 8:2-4; 9:13"),

    # ================================================================
    # SONS OF MOSIAH (collective)
    # ================================================================
    rel("TRAVELED_TO", p("Sons of Mosiah"), pl("Land of Nephi"), "Alma 17:7-8"),
    rel("CALLED_AS", p("Sons of Mosiah"), r("Missionaries to the Lamanites"), "Mosiah 28:1-9"),
    rel("CONVERTED_BY", p("Sons of Mosiah"), p("Angel of the Lord"), "Mosiah 27:11-16"),
    rel("HAS_ROLE", p("Sons of Mosiah"), r("Refused the kingdom to serve missions"), "Mosiah 28:10"),

    # ================================================================
    # ABISH
    # ================================================================
    rel("LIVED_IN", p("Abish"), pl("Land of Ishmael"), "Alma 19:16"),
    rel("HAS_ROLE", p("Abish"), r("Lamanite servant woman, secret believer"), "Alma 19:16-17"),
    rel("CONVERTED_BY", p("Abish"), c("Vision of her father"), "Alma 19:16"),
    rel("HAS_ROLE", p("Abish"), r("Gathered people to witness the conversion of Lamoni"), "Alma 19:17"),

    # ================================================================
    # ISABEL
    # ================================================================
    rel("LIVED_IN", p("Isabel"), pl("Land of Siron"), "Alma 39:3"),
    rel("HAS_ROLE", p("Isabel"), r("Harlot who led away Corianton"), "Alma 39:3"),

    # ================================================================
    # CORIANTON
    # ================================================================
    rel("HAS_ROLE", p("Corianton"), r("Son of Alma the Younger, erred during mission"), "Alma 39:2-3"),
    rel("TRAVELED_TO", p("Corianton"), pl("Land of Siron"), "Alma 39:3"),
    rel("TAUGHT", p("Alma the Younger"), c("Repentance and resurrection to Corianton"), "Alma 39-42"),
    rel("FATHER_OF", p("Alma the Younger"), p("Corianton"), "Alma 39:1"),

    # ================================================================
    # SHIBLON
    # ================================================================
    rel("HAS_ROLE", p("Shiblon"), r("Son of Alma the Younger, faithful"), "Alma 38:1-2"),
    rel("CALLED_AS", p("Shiblon"), r("Record keeper"), "Alma 63:1"),
    rel("FATHER_OF", p("Alma the Younger"), p("Shiblon"), "Alma 38:1"),

    # ================================================================
    # HAGOTH
    # ================================================================
    rel("HAS_ROLE", p("Hagoth"), r("Curious man who built ships"), "Alma 63:5"),
    rel("TRAVELED_TO", p("Hagoth"), pl("Land Northward (by ship)"), "Alma 63:5-7"),
    rel("LIVED_IN", p("Hagoth"), pl("Land Bountiful"), "Alma 63:5"),
]


def main():
    with open(RELATIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    added = 0
    skipped = 0

    for rtype, entry in ALL:
        if rtype not in data:
            data[rtype] = []

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
    print(f"Total relations: {total}")


if __name__ == "__main__":
    main()

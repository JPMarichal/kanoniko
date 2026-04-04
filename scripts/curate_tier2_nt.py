"""Tier 2 NT: Exhaustive biographical relations for ALL significant NT characters.

Covers: Gospels, Acts, Epistles, Revelation — apostles, disciples, women,
early church leaders, converts, antagonists, supporting figures.
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
    # JOSEPH (husband of Mary)
    # ================================================================
    rel("LIVED_IN", p("Joseph (NT)"), pl("Nazareth"), "Matthew 2:23"),
    rel("BORN_IN", p("Joseph (NT)"), pl("Bethlehem (lineage)"), "Luke 2:4"),
    rel("HAS_ROLE", p("Joseph (NT)"), r("Carpenter"), "Matthew 13:55"),
    rel("DESCENDANT_OF", p("Joseph (NT)"), p("David"), "Matthew 1:1-16; Luke 3:23-31"),
    rel("TRAVELED_TO", p("Joseph (NT)"), pl("Egypt (with Mary and Jesus)"), "Matthew 2:13-14"),
    rel("TRAVELED_TO", p("Joseph (NT)"), pl("Bethlehem (for census)"), "Luke 2:4"),
    rel("SAW_IN_VISION", p("Joseph (NT)"), c("Angel declaring Mary's conception"), "Matthew 1:20-21"),
    rel("SAW_IN_VISION", p("Joseph (NT)"), c("Angel warning to flee to Egypt"), "Matthew 2:13"),

    # ================================================================
    # ELIZABETH
    # ================================================================
    rel("SPOUSE_OF", p("Elisabeth"), p("Zacharias"), "Luke 1:5"),
    rel("HAS_ROLE", p("Elisabeth"), r("Mother of John the Baptist"), "Luke 1:57-60"),
    rel("DESCENDANT_OF", p("Elisabeth"), c("Daughters of Aaron"), "Luke 1:5"),
    rel("LIVED_IN", p("Elisabeth"), pl("Hill country of Judea"), "Luke 1:39-40"),
    rel("TAUGHT", p("Elisabeth"), c("Blessed art thou among women"), "Luke 1:42-45"),

    # ================================================================
    # ZACHARIAS (father of John the Baptist)
    # ================================================================
    rel("CALLED_AS", p("Zacharias"), r("Priest"), "Luke 1:5,8"),
    rel("SAW_IN_VISION", p("Zacharias"), c("Angel Gabriel announcing John's birth"), "Luke 1:11-20"),
    rel("LIVED_IN", p("Zacharias"), pl("Hill country of Judea"), "Luke 1:39-40"),
    rel("TAUGHT", p("Zacharias"), c("Prophecy/Benedictus"), "Luke 1:67-79"),

    # ================================================================
    # SIMEON (at the temple)
    # ================================================================
    rel("LIVED_IN", p("Simeon"), pl("Jerusalem"), "Luke 2:25"),
    rel("SAW_IN_VISION", p("Simeon"), c("Would not die before seeing the Messiah"), "Luke 2:26"),
    rel("BLESSED_BY", p("Jesus Christ"), p("Simeon"), "Luke 2:28-35"),
    rel("TAUGHT", p("Simeon"), c("A light to lighten the Gentiles"), "Luke 2:32"),
    rel("PROPHESIED_ABOUT", p("Simeon"), p("Mary"), "Luke 2:34-35"),

    # ================================================================
    # ANNA (prophetess)
    # ================================================================
    rel("CALLED_AS", p("Anna"), r("Prophetess"), "Luke 2:36"),
    rel("LIVED_IN", p("Anna"), pl("Jerusalem (temple)"), "Luke 2:37"),
    rel("TRIBE_OF", p("Anna"), c("Asher"), "Luke 2:36"),
    rel("TAUGHT", p("Anna"), c("Spoke of Christ to all who waited for redemption"), "Luke 2:38"),

    # ================================================================
    # ANDREW
    # ================================================================
    rel("BORN_IN", p("Andrew"), pl("Bethsaida"), "John 1:44"),
    rel("HAS_ROLE", p("Andrew"), r("First called disciple"), "John 1:35-40"),
    rel("HAS_ROLE", p("Andrew"), r("Brought Peter to Christ"), "John 1:41-42"),
    rel("LIVED_IN", p("Andrew"), pl("Capernaum"), "Mark 1:29"),
    rel("TRAVELED_TO", p("Andrew"), pl("Bethsaida"), "John 1:44"),

    # ================================================================
    # PHILIP (apostle)
    # ================================================================
    rel("BORN_IN", p("Philip"), pl("Bethsaida"), "John 1:44"),
    rel("HAS_ROLE", p("Philip"), r("Brought Nathanael to Christ"), "John 1:45-46"),
    rel("TAUGHT", p("Philip"), c("Lord, show us the Father"), "John 14:8-9"),

    # ================================================================
    # BARTHOLOMEW / NATHANAEL
    # ================================================================
    rel("CALLED_AS", p("Bartholomew"), r("Apostle"), "Matthew 10:3"),
    rel("IS_SAME_AS", p("Bartholomew"), p("Nathanael"), "John 1:45-49 (tradition)"),
    rel("HAS_TITLE", p("Nathanael"), c("An Israelite in whom is no guile"), "John 1:47"),
    rel("LIVED_IN", p("Nathanael"), pl("Cana of Galilee"), "John 21:2"),

    # ================================================================
    # MATTHEW / LEVI
    # ================================================================
    rel("HAS_ROLE", p("Matthew"), r("Tax collector before calling"), "Matthew 9:9; 10:3"),
    rel("IS_SAME_AS", p("Matthew"), p("Levi"), "Mark 2:14; Matthew 9:9"),
    rel("LIVED_IN", p("Matthew"), pl("Capernaum"), "Matthew 9:1,9"),
    rel("CALLED_BY_NAME", p("Matthew"), p("Levi"), "Mark 2:14"),

    # ================================================================
    # THOMAS
    # ================================================================
    rel("HAS_TITLE", p("Thomas"), c("Didymus (the Twin)"), "John 11:16; 20:24"),
    rel("TAUGHT", p("Thomas"), c("My Lord and my God"), "John 20:28"),
    rel("HAS_ROLE", p("Thomas"), r("Doubted until seeing the risen Christ"), "John 20:24-29"),
    rel("TRAVELED_TO", p("Thomas"), pl("India"), "Tradition; GEE, Tomas"),

    # ================================================================
    # JAMES (son of Alphaeus)
    # ================================================================
    rel("CALLED_AS", p("James (son of Alphaeus)"), r("Apostle"), "Matthew 10:3"),
    rel("HAS_TITLE", p("James (son of Alphaeus)"), c("James the Less"), "Mark 15:40 (tradition)"),

    # ================================================================
    # THADDAEUS / JUDAS son of James
    # ================================================================
    rel("CALLED_AS", p("Thaddaeus"), r("Apostle"), "Matthew 10:3"),
    rel("IS_SAME_AS", p("Thaddaeus"), p("Judas son of James"), "Luke 6:16; Acts 1:13"),
    rel("TAUGHT", p("Judas son of James"), c("Asked why Jesus would manifest to disciples, not world"), "John 14:22"),

    # ================================================================
    # SIMON THE ZEALOT
    # ================================================================
    rel("CALLED_AS", p("Simon the Zealot"), r("Apostle"), "Matthew 10:4; Luke 6:15"),
    rel("HAS_TITLE", p("Simon the Zealot"), c("Simon the Canaanite"), "Matthew 10:4"),

    # ================================================================
    # JUDAS ISCARIOT
    # ================================================================
    rel("CALLED_AS", p("Judas Iscariot"), r("Apostle"), "Matthew 10:4"),
    rel("HAS_ROLE", p("Judas Iscariot"), r("Treasurer of the Twelve"), "John 12:6; 13:29"),
    rel("HAS_ROLE", p("Judas Iscariot"), r("Betrayed Jesus for 30 pieces of silver"), "Matthew 26:14-16,47-50"),
    rel("DIED_IN", p("Judas Iscariot"), pl("Field of Blood (Akeldama)"), "Matthew 27:3-5; Acts 1:18-19"),
    rel("BORN_IN", p("Judas Iscariot"), pl("Kerioth"), "Name implies Ish-Kerioth"),

    # ================================================================
    # MATTHIAS
    # ================================================================
    rel("CALLED_AS", p("Matthias"), r("Apostle (replacement for Judas)"), "Acts 1:26"),
    rel("HAS_ROLE", p("Matthias"), r("Chosen by lot"), "Acts 1:23-26"),
    rel("HAS_ROLE", p("Matthias"), r("Witnessed Christ's ministry from baptism to ascension"), "Acts 1:21-22"),

    # ================================================================
    # MARY MAGDALENE — enrich
    # ================================================================
    rel("HAS_ROLE", p("Mary Magdalene"), r("First witness of the resurrected Christ"), "John 20:14-17; Mark 16:9"),
    rel("HEALED_BY", p("Mary Magdalene"), p("Jesus Christ"), "Luke 8:2"),
    rel("TRAVELED_TO", p("Mary Magdalene"), pl("Tomb of Jesus"), "John 20:1"),
    rel("HAS_ROLE", p("Mary Magdalene"), r("Faithful follower at the cross"), "John 19:25"),

    # ================================================================
    # MARTHA
    # ================================================================
    rel("LIVED_IN", p("Martha"), pl("Bethany"), "John 11:1"),
    rel("HAS_ROLE", p("Martha"), r("Sister of Mary and Lazarus"), "John 11:1"),
    rel("TAUGHT", p("Martha"), c("I know that he shall rise again / I believe thou art the Christ"), "John 11:24,27"),
    rel("HAS_ROLE", p("Martha"), r("Served Jesus in her home"), "Luke 10:38-40"),

    # ================================================================
    # MARY OF BETHANY
    # ================================================================
    rel("LIVED_IN", p("Mary of Bethany"), pl("Bethany"), "John 11:1"),
    rel("HAS_ROLE", p("Mary of Bethany"), r("Sister of Martha and Lazarus"), "John 11:1"),
    rel("TAUGHT", p("Mary of Bethany"), c("Chose the good part — sat at Jesus' feet"), "Luke 10:39,42"),
    rel("HAS_ROLE", p("Mary of Bethany"), r("Anointed Jesus' feet with costly ointment"), "John 12:3"),

    # ================================================================
    # LAZARUS
    # ================================================================
    rel("LIVED_IN", p("Lazarus"), pl("Bethany"), "John 11:1"),
    rel("HAS_ROLE", p("Lazarus"), r("Brother of Martha and Mary"), "John 11:1"),
    rel("DIED_IN", p("Lazarus"), pl("Bethany (raised from dead)"), "John 11:14,43-44"),
    rel("HAS_TITLE", p("Lazarus"), c("He whom Jesus loved"), "John 11:3"),

    # ================================================================
    # NICODEMUS
    # ================================================================
    rel("HAS_ROLE", p("Nicodemus"), r("Pharisee and ruler of the Jews"), "John 3:1"),
    rel("TRAVELED_TO", p("Nicodemus"), pl("To Jesus by night"), "John 3:2"),
    rel("TAUGHT", p("Jesus Christ"), c("Born again / of water and Spirit"), "John 3:3-5"),
    rel("HAS_ROLE", p("Nicodemus"), r("Helped prepare Jesus' body for burial"), "John 19:39"),

    # ================================================================
    # JOSEPH OF ARIMATHEA
    # ================================================================
    rel("LIVED_IN", p("Joseph of Arimathea"), pl("Arimathea"), "Matthew 27:57"),
    rel("HAS_ROLE", p("Joseph of Arimathea"), r("Wealthy disciple who provided tomb for Jesus"), "Matthew 27:57-60"),
    rel("HAS_ROLE", p("Joseph of Arimathea"), r("Member of the Sanhedrin"), "Mark 15:43"),

    # ================================================================
    # ZACCHAEUS
    # ================================================================
    rel("LIVED_IN", p("Zacchaeus"), pl("Jericho"), "Luke 19:1-2"),
    rel("HAS_ROLE", p("Zacchaeus"), r("Chief publican who climbed sycamore tree"), "Luke 19:2-4"),
    rel("CONVERTED_BY", p("Zacchaeus"), p("Jesus Christ"), "Luke 19:5-10"),

    # ================================================================
    # HEROD THE GREAT
    # ================================================================
    rel("CALLED_AS", p("Herod"), r("King of Judea"), "Matthew 2:1"),
    rel("LIVED_IN", p("Herod"), pl("Jerusalem"), "Matthew 2:1"),
    rel("KILLED", p("Herod"), c("Innocents of Bethlehem"), "Matthew 2:16"),
    rel("FOUGHT_AGAINST", p("Herod"), p("Jesus Christ (sought to kill)"), "Matthew 2:13"),

    # ================================================================
    # HEROD ANTIPAS
    # ================================================================
    rel("CALLED_AS", p("Herod Antipas"), r("Tetrarch of Galilee"), "Luke 3:1,19"),
    rel("KILLED", p("Herod Antipas"), p("John the Baptist"), "Matthew 14:10-11"),
    rel("HAS_ROLE", p("Herod Antipas"), r("Tried Jesus before crucifixion"), "Luke 23:7-11"),
    rel("SPOUSE_OF", p("Herod Antipas"), p("Herodias"), "Mark 6:17"),

    # ================================================================
    # HERODIAS
    # ================================================================
    rel("HAS_ROLE", p("Herodias"), r("Plotted death of John the Baptist"), "Mark 6:19,24"),
    rel("SPOUSE_OF", p("Herodias"), p("Herod Antipas"), "Mark 6:17"),

    # ================================================================
    # PONTIUS PILATE
    # ================================================================
    rel("CALLED_AS", p("Pontius Pilate"), r("Roman Governor of Judea"), "Luke 3:1; Matthew 27:2"),
    rel("HAS_ROLE", p("Pontius Pilate"), r("Condemned Jesus to crucifixion"), "Matthew 27:24-26"),
    rel("HAS_ROLE", p("Pontius Pilate"), r("Washed his hands declaring innocence"), "Matthew 27:24"),
    rel("LIVED_IN", p("Pontius Pilate"), pl("Jerusalem"), "Matthew 27:2"),

    # ================================================================
    # CAIAPHAS
    # ================================================================
    rel("CALLED_AS", p("Caiaphas"), r("High Priest"), "Matthew 26:3,57"),
    rel("HAS_ROLE", p("Caiaphas"), r("Presided over trial of Jesus"), "Matthew 26:57-66"),
    rel("PROPHESIED_ABOUT", p("Caiaphas"), p("Jesus Christ"), "John 11:49-51 (one man should die for the people)"),

    # ================================================================
    # BARABBAS
    # ================================================================
    rel("HAS_ROLE", p("Barabbas"), r("Prisoner released instead of Jesus"), "Matthew 27:16-26"),
    rel("LIVED_IN", p("Barabbas"), pl("Jerusalem"), "Matthew 27:16"),

    # ================================================================
    # PHILIP (deacon/evangelist)
    # ================================================================
    rel("CALLED_AS", p("Philip (evangelist)"), r("Deacon"), "Acts 6:5"),
    rel("TRAVELED_TO", p("Philip (evangelist)"), pl("Samaria"), "Acts 8:5"),
    rel("CONVERTED_BY", p("Ethiopian eunuch"), p("Philip (evangelist)"), "Acts 8:26-38"),
    rel("BAPTIZED_BY", p("Ethiopian eunuch"), p("Philip (evangelist)"), "Acts 8:38"),
    rel("LIVED_IN", p("Philip (evangelist)"), pl("Caesarea"), "Acts 21:8"),

    # ================================================================
    # ANANIAS (of Damascus)
    # ================================================================
    rel("LIVED_IN", p("Ananias"), pl("Damascus"), "Acts 9:10"),
    rel("HAS_ROLE", p("Ananias"), r("Healed and baptized Paul"), "Acts 9:17-18"),
    rel("SAW_IN_VISION", p("Ananias"), c("The Lord telling him to go to Saul"), "Acts 9:10-16"),

    # ================================================================
    # CORNELIUS
    # ================================================================
    rel("CALLED_AS", p("Cornelius"), r("Roman Centurion"), "Acts 10:1"),
    rel("LIVED_IN", p("Cornelius"), pl("Caesarea"), "Acts 10:1"),
    rel("SAW_IN_VISION", p("Cornelius"), c("Angel telling him to send for Peter"), "Acts 10:3-6"),
    rel("HAS_TITLE", p("Cornelius"), c("First Gentile convert"), "Acts 10:44-48"),

    # ================================================================
    # TIMOTHY
    # ================================================================
    rel("BORN_IN", p("Timothy"), pl("Lystra"), "Acts 16:1"),
    rel("CONVERTED_BY", p("Timothy"), p("Paul"), "Acts 16:1-3; 1 Timothy 1:2"),
    rel("CALLED_AS", p("Timothy"), r("Companion and delegate of Paul"), "Acts 16:3; 1 Timothy 1:3"),
    rel("LIVED_IN", p("Timothy"), pl("Ephesus"), "1 Timothy 1:3"),
    rel("MOTHER_OF", p("Eunice"), p("Timothy"), "2 Timothy 1:5"),

    # ================================================================
    # TITUS
    # ================================================================
    rel("CALLED_AS", p("Titus"), r("Companion and delegate of Paul"), "Titus 1:4-5"),
    rel("TRAVELED_TO", p("Titus"), pl("Crete"), "Titus 1:5"),
    rel("LIVED_IN", p("Titus"), pl("Crete"), "Titus 1:5"),
    rel("HAS_ROLE", p("Titus"), r("Organized churches in Crete"), "Titus 1:5"),

    # ================================================================
    # SILAS / SILVANUS
    # ================================================================
    rel("CALLED_AS", p("Silas"), r("Companion of Paul"), "Acts 15:40"),
    rel("TRAVELED_TO", p("Silas"), pl("Philippi"), "Acts 16:12,19"),
    rel("HAS_ROLE", p("Silas"), r("Imprisoned with Paul, earthquake freed them"), "Acts 16:25-26"),
    rel("IS_SAME_AS", p("Silas"), p("Silvanus"), "1 Peter 5:12 (tradition)"),

    # ================================================================
    # APOLLOS
    # ================================================================
    rel("BORN_IN", p("Apollos"), pl("Alexandria"), "Acts 18:24"),
    rel("TRAVELED_TO", p("Apollos"), pl("Ephesus"), "Acts 18:24"),
    rel("TRAVELED_TO", p("Apollos"), pl("Corinth"), "Acts 19:1; 1 Corinthians 3:6"),
    rel("HAS_ROLE", p("Apollos"), r("Eloquent preacher, mighty in the scriptures"), "Acts 18:24-25"),
    rel("TAUGHT", p("Priscilla"), c("Way of God more perfectly to Apollos"), "Acts 18:26"),

    # ================================================================
    # PRISCILLA AND AQUILA
    # ================================================================
    rel("SPOUSE_OF", p("Priscilla"), p("Aquila"), "Acts 18:2"),
    rel("LIVED_IN", p("Priscilla"), pl("Corinth"), "Acts 18:1-2"),
    rel("LIVED_IN", p("Priscilla"), pl("Ephesus"), "Acts 18:18-19"),
    rel("ALLIED_WITH", p("Priscilla"), p("Paul"), "Acts 18:2-3"),
    rel("HAS_ROLE", p("Aquila"), r("Tentmaker, co-worker with Paul"), "Acts 18:2-3"),
    rel("BORN_IN", p("Aquila"), pl("Pontus"), "Acts 18:2"),

    # ================================================================
    # LYDIA
    # ================================================================
    rel("BORN_IN", p("Lydia"), pl("Thyatira"), "Acts 16:14"),
    rel("LIVED_IN", p("Lydia"), pl("Philippi"), "Acts 16:14-15"),
    rel("CONVERTED_BY", p("Lydia"), p("Paul"), "Acts 16:14-15"),
    rel("BAPTIZED_BY", p("Lydia"), p("Paul"), "Acts 16:15"),
    rel("HAS_ROLE", p("Lydia"), r("Seller of purple, first European convert"), "Acts 16:14"),

    # ================================================================
    # MARK (John Mark)
    # ================================================================
    rel("HAS_ROLE", p("Mark"), r("Companion of Paul and Barnabas"), "Acts 12:25; 13:5"),
    rel("LIVED_IN", p("Mark"), pl("Jerusalem"), "Acts 12:12"),
    rel("ALLIED_WITH", p("Mark"), p("Peter"), "1 Peter 5:13"),
    rel("MOTHER_OF", p("Mary (mother of Mark)"), p("Mark"), "Acts 12:12"),

    # ================================================================
    # LUKE — enrich
    # ================================================================
    rel("HAS_ROLE", p("Luke"), r("Companion of Paul"), "Colossians 4:14; 2 Timothy 4:11"),
    rel("HAS_TITLE", p("Luke"), c("The Beloved Physician"), "Colossians 4:14"),
    rel("TRAVELED_TO", p("Luke"), pl("Philippi"), "Acts 16:10-12 (we passages)"),
    rel("TRAVELED_TO", p("Luke"), pl("Rome"), "Acts 28:16 (we passages)"),

    # ================================================================
    # JUDE (brother of James)
    # ================================================================
    rel("HAS_ROLE", p("Jude"), r("Brother of James/Jacobo"), "Jude 1:1"),
    rel("AUTHORED", p("Jude"), s("Epistle of Jude"), "Jude 1:1"),
    rel("TAUGHT", p("Jude"), c("Contend for the faith once delivered"), "Jude 1:3"),
    rel("TAUGHT", p("Jude"), c("Warning against apostasy"), "Jude 1:4-19"),

    # ================================================================
    # SALOME
    # ================================================================
    rel("HAS_ROLE", p("Salome"), r("Mother of James and John (sons of Zebedee)"), "Matthew 27:56; Mark 15:40 (tradition)"),
    rel("HAS_ROLE", p("Salome"), r("Present at the crucifixion"), "Mark 15:40"),
    rel("TRAVELED_TO", p("Salome"), pl("Tomb of Jesus"), "Mark 16:1"),

    # ================================================================
    # ZEBEDEE
    # ================================================================
    rel("FATHER_OF", p("Zebedee"), p("James"), "Matthew 4:21"),
    rel("FATHER_OF", p("Zebedee"), p("John"), "Matthew 4:21"),
    rel("HAS_ROLE", p("Zebedee"), r("Fisherman, father of James and John"), "Matthew 4:21"),

    # ================================================================
    # GAMALIEL
    # ================================================================
    rel("HAS_ROLE", p("Gamaliel"), r("Pharisee, teacher of the law"), "Acts 5:34"),
    rel("TAUGHT", p("Gamaliel"), c("If this counsel be of God, ye cannot overthrow it"), "Acts 5:38-39"),
    rel("HAS_ROLE", p("Gamaliel"), r("Teacher of Paul"), "Acts 22:3"),

    # ================================================================
    # DORCAS / TABITHA
    # ================================================================
    rel("LIVED_IN", p("Dorcas"), pl("Joppa"), "Acts 9:36"),
    rel("HAS_ROLE", p("Dorcas"), r("Full of good works and charitable deeds"), "Acts 9:36"),
    rel("HEALED_BY", p("Dorcas"), p("Peter"), "Acts 9:40-41"),
    rel("IS_SAME_AS", p("Dorcas"), p("Tabitha"), "Acts 9:36"),

    # ================================================================
    # PHILEMON
    # ================================================================
    rel("LIVED_IN", p("Philemon"), pl("Colossae"), "Philemon 1:1-2 (tradition)"),
    rel("HAS_ROLE", p("Philemon"), r("Slaveholder whom Paul asked to receive Onesimus"), "Philemon 1:10-16"),
    rel("CONVERTED_BY", p("Philemon"), p("Paul"), "Philemon 1:19"),

    # ================================================================
    # ONESIMUS
    # ================================================================
    rel("HAS_ROLE", p("Onesimus"), r("Runaway slave converted by Paul"), "Philemon 1:10-16"),
    rel("CONVERTED_BY", p("Onesimus"), p("Paul"), "Philemon 1:10"),
    rel("TRAVELED_TO", p("Onesimus"), pl("Rome (to Paul in prison)"), "Philemon 1:10"),

    # ================================================================
    # MARY (mother of Mark)
    # ================================================================
    rel("LIVED_IN", p("Mary (mother of Mark)"), pl("Jerusalem"), "Acts 12:12"),
    rel("HAS_ROLE", p("Mary (mother of Mark)"), r("Hosted early church gatherings"), "Acts 12:12"),

    # ================================================================
    # EUNICE AND LOIS (Timothy's mother and grandmother)
    # ================================================================
    rel("HAS_ROLE", p("Eunice"), r("Mother of Timothy"), "2 Timothy 1:5"),
    rel("HAS_ROLE", p("Lois"), r("Grandmother of Timothy"), "2 Timothy 1:5"),
    rel("TAUGHT", p("Eunice"), c("Scriptures to Timothy from childhood"), "2 Timothy 3:15"),
    rel("TAUGHT", p("Lois"), c("Unfeigned faith"), "2 Timothy 1:5"),

    # ================================================================
    # JOANNA
    # ================================================================
    rel("HAS_ROLE", p("Joanna"), r("Wife of Chuza, Herod's steward"), "Luke 8:3"),
    rel("HAS_ROLE", p("Joanna"), r("Supported Jesus' ministry"), "Luke 8:3"),
    rel("TRAVELED_TO", p("Joanna"), pl("Tomb of Jesus"), "Luke 24:10"),

    # ================================================================
    # SIMON OF CYRENE
    # ================================================================
    rel("BORN_IN", p("Simon of Cyrene"), pl("Cyrene"), "Mark 15:21"),
    rel("HAS_ROLE", p("Simon of Cyrene"), r("Carried the cross of Jesus"), "Mark 15:21"),

    # ================================================================
    # CENTURION AT THE CROSS
    # ================================================================
    rel("HAS_ROLE", p("Centurion at the cross"), r("Testified: Truly this was the Son of God"), "Matthew 27:54"),

    # ================================================================
    # FELIX AND FESTUS
    # ================================================================
    rel("CALLED_AS", p("Felix"), r("Roman Governor"), "Acts 23:24"),
    rel("HAS_ROLE", p("Felix"), r("Heard Paul's defense, delayed judgment"), "Acts 24:22-27"),
    rel("CALLED_AS", p("Festus"), r("Roman Governor (successor of Felix)"), "Acts 24:27; 25:1"),
    rel("HAS_ROLE", p("Festus"), r("Heard Paul's appeal to Caesar"), "Acts 25:9-12"),

    # ================================================================
    # AGRIPPA
    # ================================================================
    rel("CALLED_AS", p("Agrippa"), r("King"), "Acts 25:13; 26:1"),
    rel("HAS_ROLE", p("Agrippa"), r("Heard Paul's testimony: 'Almost thou persuadest me'"), "Acts 26:28"),

    # ================================================================
    # EPAPHRAS
    # ================================================================
    rel("LIVED_IN", p("Epaphras"), pl("Colossae"), "Colossians 1:7; 4:12"),
    rel("HAS_ROLE", p("Epaphras"), r("Founded church at Colossae"), "Colossians 1:7"),
    rel("ALLIED_WITH", p("Epaphras"), p("Paul"), "Colossians 4:12; Philemon 1:23"),
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

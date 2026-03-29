from __future__ import annotations
"""Apply English translations to parts.json."""
import json

PARTS_PATH = "C:/own/alejandria/data/scripture_structure/parts.json"

# Complete ES → EN mapping for all 389 parts
TRANSLATIONS = {
    # OT - Genesis
    "La Creación": "The Creation",
    "La Caída": "The Fall",
    "El Diluvio": "The Flood",
    "La dispersión de las naciones": "The Dispersion of Nations",
    "Abraham": "Abraham",
    "Isaac": "Isaac",
    "Jacob": "Jacob",
    "José": "Joseph",
    # OT - Exodus
    "La necesidad de la redención": "The Need for Redemption",
    "Preparación de líderes para la redención": "Preparation of Leaders for Redemption",
    "La liberación de Israel de la opresión egipcia": "The Deliverance of Israel from Egyptian Oppression",
    "La preservación de Israel en el desierto": "The Preservation of Israel in the Wilderness",
    "La revelación del antiguo convenio": "The Revelation of the Old Covenant",
    "La respuesta de Israel al convenio": "Israel's Response to the Covenant",
    # OT - Leviticus
    "Leyes sobre el sacrificio": "Laws of Sacrifice",
    "Leyes sobre el sacerdocio aarónico": "Laws of the Aaronic Priesthood",
    "Leyes sobre la purificación": "Laws of Purification",
    "Leyes sobre la expiación nacional": "Laws of National Atonement",
    "Leyes de santificación para el pueblo": "Laws of Sanctification for the People",
    "Leyes de santificación para el sacerdocio": "Laws of Sanctification for the Priesthood",
    "Leyes de santificación para la adoración": "Laws of Sanctification for Worship",
    "Leyes de santificación en la tierra prometida": "Laws of Sanctification in the Promised Land",
    "Leyes de santificación por medio de votos": "Laws of Sanctification through Vows",
    # OT - Numbers
    "La organización de Israel": "The Organization of Israel",
    "La santificación de Israel": "The Sanctification of Israel",
    "El fracaso de Israel en camino a Cades": "Israel's Failure on the Way to Kadesh",
    "El fracaso de Israel en Cades": "Israel's Failure at Kadesh",
    "El fracaso de Israel en el desierto": "Israel's Failure in the Wilderness",
    "El fracaso de Israel en camino a Moab": "Israel's Failure on the Way to Moab",
    "La reorganización de Israel": "The Reorganization of Israel",
    "Las regulaciones sobre ofrendas y votos": "Regulations on Offerings and Vows",
    "La conquista y división de Israel": "The Conquest and Division of Israel",
    # OT - Deuteronomy
    "El primer discurso de Moisés": "Moses' First Discourse",
    "El segundo discurso de Moisés": "Moses' Second Discourse",
    "El tercer discurso de Moisés": "Moses' Third Discourse",
    "La transición profética de Moisés a Josué": "The Prophetic Transition from Moses to Joshua",
    # OT - Joshua
    "La preparación de Israel para la conquista": "Israel's Preparation for the Conquest",
    "Israel conquista Canáan": "Israel Conquers Canaan",
    "Asentamiento al este del Jordán": "Settlement East of the Jordan",
    "Asentamiento al oeste del Jordán": "Settlement West of the Jordan",
    "Asentamiento de la tribu de Leví": "Settlement of the Tribe of Levi",
    "Las condiciones para la permanencia en Canáan": "Conditions for Remaining in Canaan",
    # OT - Judges
    "El fracaso de Israel en completar la conquista": "Israel's Failure to Complete the Conquest",
    "Las consecuencias por no completar la conquista": "Consequences of Not Completing the Conquest",
    "La campaña del sur": "The Southern Campaign",
    "La primera campaña del norte": "The First Northern Campaign",
    "La campaña central": "The Central Campaign",
    "La campaña del este y segunda campaña del norte": "The Eastern Campaign and Second Northern Campaign",
    "La campaña del oeste": "The Western Campaign",
    "El fracaso de Israel por la idolatría": "Israel's Failure through Idolatry",
    "El fracaso de Israel por la inmoralidad": "Israel's Failure through Immorality",
    "El fracaso de Israel por la guerra entre las tribus": "Israel's Failure through Intertribal War",
    # OT - Ruth
    "Rut procura la redención de Booz": "Ruth Seeks Redemption from Boaz",
    "Rut obtiene la redención de Booz": "Ruth Obtains Redemption from Boaz",
    "La devoción de Rut al cuidar de Noemí": "Ruth's Devotion in Caring for Naomi",
    "La decisión de Rut de permanecer con Noemí": "Ruth's Decision to Remain with Naomi",
    # OT - 1 Samuel
    "Primera transición: De Elí a Samuel": "First Transition: From Eli to Samuel",
    "La judicatura de Samuel": "The Judgeship of Samuel",
    "Segunda transición: De Samuel a Saúl": "Second Transition: From Samuel to Saul",
    "El reinado de Saúl": "The Reign of Saul",
    "Tercera transición: De Saúl a David": "Third Transition: From Saul to David",
    # OT - 2 Samuel
    "Triunfos políticos de David": "David's Political Triumphs",
    "Triunfos espirituales de David": "David's Spiritual Triumphs",
    "Triunfos militares de David": "David's Military Triumphs",
    "El adulterio de David": "David's Adultery",
    "Problemas en la casa de David": "Troubles in David's House",
    "Problemas en el reino de David": "Troubles in David's Kingdom",
    # OT - 1 Kings
    "El establecimiento de Salomón como rey": "The Establishment of Solomon as King",
    "El ascenso de Salomón como rey": "The Rise of Solomon as King",
    "El declive de Salomón como rey": "The Decline of Solomon as King",
    "La división del reino": "The Division of the Kingdom",
    "Los reinados de tres reyes en Judá y siete en Israel": "The Reigns of Three Kings in Judah and Seven in Israel",
    # OT - 2 Kings
    "Enfasis en el reino del norte": "Emphasis on the Northern Kingdom",
    "Enfasis en ambos reinos": "Emphasis on Both Kingdoms",
    "Enfasis en el reino del sur": "Emphasis on the Southern Kingdom",
    # OT - 1 Chronicles
    "Genealogías de Adán a Jacob": "Genealogies from Adam to Jacob",
    "Genealogías de Jacob a David": "Genealogies from Jacob to David",
    "Genealogías de David a la cautividad": "Genealogies from David to the Captivity",
    "Genealogías de las doce tribus": "Genealogies of the Twelve Tribes",
    "Genealogías del remanente y de Saúl": "Genealogies of the Remnant and of Saul",
    "La ascensión del rey David": "The Ascent of King David",
    "La adquisición del arca del convenio": "The Acquisition of the Ark of the Covenant",
    "Las victorias militares del rey David": "The Military Victories of King David",
    "Preparación y organización para el templo": "Preparation and Organization for the Temple",
    "Los últimos días del rey David": "The Last Days of King David",
    # OT - 2 Chronicles
    "La instalación de Salomón como rey": "The Installation of Solomon as King",
    "La finalización del templo": "The Completion of the Temple",
    "El esplendor del reinado de Salomón": "The Splendor of Solomon's Reign",
    "Reinado de Roboam": "Reign of Rehoboam",
    "Reinado de Abías": "Reign of Abijah",
    "Reinado de Asa": "Reign of Asa",
    "Reinado de Josafat": "Reign of Jehoshaphat",
    "Reinado de Joram": "Reign of Jehoram",
    "Reinado de Ocozías, Atalía y Joas": "Reign of Ahaziah, Athaliah, and Joash",
    "Reinado de Amasías": "Reign of Amaziah",
    "Reinado de Uzías": "Reign of Uzziah",
    "Reinado de Jotam": "Reign of Jotham",
    "Reinado de Acaz": "Reign of Ahaz",
    "Reinado de Ezequías": "Reign of Hezekiah",
    "Reinados de Manasés y Amón": "Reigns of Manasseh and Amon",
    "Reinado de Josías": "Reign of Josiah",
    "Reinados de Joacaz, Joacim, Joaquín y Sedequías": "Reigns of Jehoahaz, Jehoiakim, Jehoiachin, and Zedekiah",
    # OT - Ezra
    "Primer retorno a Jerusalén bajo Zorobabel": "First Return to Jerusalem under Zerubbabel",
    "La construción del templo": "The Building of the Temple",
    "Segundo retorno a Jerusalén bajo Esdrás": "Second Return to Jerusalem under Ezra",
    "La restauración del pueblo": "The Restoration of the People",
    # OT - Nehemiah
    "La preparación para la reconstrucción del muro": "Preparation for Rebuilding the Wall",
    "La reconstrucción del muro": "The Rebuilding of the Wall",
    "La renovación del convenio": "The Renewal of the Covenant",
    "La obediencia al convenio": "Obedience to the Covenant",
    # OT - Esther
    "La selección de Ester como reina": "The Selection of Esther as Queen",
    "La conspiración de Amán": "Haman's Conspiracy",
    "El triunfo de Mardoqueo sobre Amán": "Mordecai's Triumph over Haman",
    "El triunfo de Israel sobre sus enemigos": "Israel's Triumph over Its Enemies",
    # OT - Job
    "El dilema de Job": "Job's Dilemma",
    "Primer ciclo de debate": "First Cycle of Debate",
    "Segundo ciclo de debate": "Second Cycle of Debate",
    "Tercer ciclo de debate": "Third Cycle of Debate",
    "La defensa final de Job": "Job's Final Defense",
    "La solución de Elihú": "Elihu's Solution",
    "La redención de Job": "Job's Redemption",
    # OT - Psalms
    "Libro I de Salmos": "Book I of Psalms",
    "Libro II de Salmos": "Book II of Psalms",
    "Libro III de Salmos": "Book III of Psalms",
    "Libro IV de Salmos": "Book IV of Psalms",
    "Libro V de Salmos": "Book V of Psalms",
    # OT - Proverbs
    "Proverbios para la juventud": "Proverbs for Youth",
    "Proverbios de Salomón": "Proverbs of Solomon",
    "Proverbios de Salomón copiados por los hombres de Ezequías": "Proverbs of Solomon Copied by Hezekiah's Men",
    "Las palabras de Agur": "The Words of Agur",
    "Las palabras del rey Lemuel": "The Words of King Lemuel",
    # OT - Ecclesiastes
    "La prueba de que todo es vanidad por la experiencia": "Proof of Vanity through Experience",
    "La prueba de que todo es vanidad por la observación": "Proof of Vanity through Observation",
    "Cómo lidiar con la vanidad en un mundo inicuo": "Dealing with Vanity in a Wicked World",
    "Cómo lidiar con las incertidumbres": "Dealing with Uncertainties",
    # OT - Song of Solomon
    "El despertar del amor": "The Awakening of Love",
    "El florecimiento del amor": "The Flourishing of Love",
    # OT - Isaiah
    "Cargas contra Judá": "Burdens against Judah",
    "Cargas contra las naciones": "Burdens against the Nations",
    "Las profecías del día del Señor": "Prophecies of the Day of the Lord",
    "Profecías de juicio y bendición": "Prophecies of Judgment and Blessing",
    "Ezequías es librado de Asiria": "Hezekiah Is Delivered from Assyria",
    "Ezequías es librado de la enfermedad": "Hezekiah Is Delivered from Illness",
    "El pecado de Ezequías": "Hezekiah's Sin",
    "Profecías sobre la liberación de Israel": "Prophecies of Israel's Deliverance",
    "Profecías sobre el Redentor de Israel": "Prophecies of the Redeemer of Israel",
    "Profecías sobre la gloria futura de Israel": "Prophecies of Israel's Future Glory",
    # OT - Jeremiah
    "El llamamiento de Jeremías": "The Calling of Jeremiah",
    "Condenación de Judá": "Condemnation of Judah",
    "Conflictos de Jeremías": "Jeremiah's Conflicts",
    "La restauración futura de Jerusalén": "The Future Restoration of Jerusalem",
    "La caída actual de Jerusalén": "The Present Fall of Jerusalem",
    "Profecías contra Egipto": "Prophecies against Egypt",
    "Profecías contra Filistea": "Prophecies against Philistia",
    "Profecías contra Moab": "Prophecies against Moab",
    "Profecías contra Amón, Edom, Damasco, Cedar, Hazor y Elam": "Prophecies against Ammon, Edom, Damascus, Kedar, Hazor, and Elam",
    "Profecías contra Babilonia": "Prophecies against Babylon",
    "La caída de Jerusalén y el exilio": "The Fall of Jerusalem and the Exile",
    # OT - Lamentations
    "La destrucción de Jerusalén": "The Destruction of Jerusalem",
    "La ira de Dios": "The Wrath of God",
    "Oración pidiendo misericordia": "Prayer for Mercy",
    "La siega de Jerusalén": "The Harvest of Jerusalem",
    "Oración por la restitución de Jerusalén": "Prayer for the Restoration of Jerusalem",
    # OT - Ezekiel
    "Ezequiel contempla la gloria de Dios": "Ezekiel Beholds the Glory of God",
    "Ezequiel es llamado a predicar": "Ezekiel Is Called to Preach",
    "Cuatro señales del juicio venidero": "Four Signs of Coming Judgment",
    "Dos mensajes del juicio venidero": "Two Messages of Coming Judgment",
    "La visión del juicio venidero": "The Vision of Coming Judgment",
    "Señales, parábolas y mensajes de juicio": "Signs, Parables, and Messages of Judgment",
    "Juicios sobre Amón, Moab, Edom y Filistea": "Judgments on Ammon, Moab, Edom, and Philistia",
    "Juicios sobre Tiro y Sidón": "Judgments on Tyre and Sidon",
    "Juicios sobre Egipto": "Judgments on Egypt",
    "El retorno a la tierra de Israel": "The Return to the Land of Israel",
    "La restauración del reino de Israel": "The Restoration of the Kingdom of Israel",
    # OT - Daniel
    "La historia personal de Daniel": "The Personal History of Daniel",
    "El sueño de Nabucodonosor": "Nebuchadnezzar's Dream",
    "La estatua de oro de Nabucodonosor": "Nebuchadnezzar's Golden Image",
    "La visión de Nabucodonosor del gran árbol": "Nebuchadnezzar's Vision of the Great Tree",
    "Belsasar y la escritura sobre el muro": "Belshazzar and the Writing on the Wall",
    "El decreto insensato de Darío": "Darius' Foolish Decree",
    "Visión de Daniel de las cuatro bestias": "Daniel's Vision of the Four Beasts",
    "Visión del carnero y el macho cabrío": "Vision of the Ram and the Goat",
    "Visión de las setenta semanas": "Vision of the Seventy Weeks",
    "Visión de Daniel del futuro de Israel": "Daniel's Vision of Israel's Future",
    # OT - Minor Prophets
    "La esposa adúltera y el marido fiel": "The Adulterous Wife and the Faithful Husband",
    "El Israel adúltero y su Señor fiel": "Adulterous Israel and Its Faithful Lord",
    "El día del Señor en retrospectiva": "The Day of the Lord in Retrospect",
    "El día del Señor en perspectiva": "The Day of the Lord in Prospect",
    "Los ocho juicios": "The Eight Judgments",
    "Los tres sermones del juicio": "The Three Sermons of Judgment",
    "Las cinco visiones del juicio": "The Five Visions of Judgment",
    "Profecías sobre el juicio de Edom": "Prophecies of Judgment on Edom",
    "La primera asignación de Jonás": "Jonah's First Commission",
    "La segunda asignación de Jonás": "Jonah's Second Commission",
    "Miqueas predice el juicio": "Micah Predicts Judgment",
    "Miqueas predice la restauración": "Micah Predicts Restoration",
    "Miqueas suplica por el arrepentimiento": "Micah Pleads for Repentance",
    "Se decreta la destrucción de Nínive": "The Destruction of Nineveh Is Decreed",
    "Se describe la destrucción de Nínive": "The Destruction of Nineveh Is Described",
    "Se justifica la destrucción de Nínive": "The Destruction of Nineveh Is Justified",
    "Problemas de Habacuc": "Habakkuk's Problems",
    "Alabanza de Habacuc": "Habakkuk's Praise",
    "Juicio y salvación en el día del Señor": "Judgment and Salvation in the Day of the Lord",
    "La finalización de la construcción del templo": "The Completion of the Temple Construction",
    "La gloria del templo y las bendiciones de la obediencia": "The Glory of the Temple and the Blessings of Obedience",
    "Las ocho visiones de Zacarías y el coronamiento de Josué": "Zechariah's Eight Visions and the Crowning of Joshua",
    "Los cuatro mensajes de Zacarías": "Zechariah's Four Messages",
    "La primera carga: el rechazo del Mesías": "The First Burden: The Rejection of the Messiah",
    "La segunda carga: el reinado del Mesías": "The Second Burden: The Reign of the Messiah",
    "Privilegios, contaminación y promesas de la nación": "Privileges, Defilement, and Promises of the Nation",
    # NT - Matthew
    "La presentación del Rey": "The Presentation of the King",
    "La proclamación del Rey": "The Proclamation of the King",
    "El poder del Rey": "The Power of the King",
    "El progresivo rechazo del Rey": "The Progressive Rejection of the King",
    "La preparación de los discípulos del Rey": "The Preparation of the King's Disciples",
    "La presentación y rechazo del Rey": "The Presentation and Rejection of the King",
    "La demostración del Rey": "The Demonstration of the King",
    # NT - Mark
    "La presentación del Siervo": "The Presentation of the Servant",
    "La oposición al Siervo": "The Opposition to the Servant",
    "La instrucción del Siervo": "The Instruction of the Servant",
    "El rechazo al Siervo": "The Rejection of the Servant",
    "La resurrección del Siervo": "The Resurrection of the Servant",
    # NT - Luke
    "La presentación del Hijo del Hombre": "The Presentation of the Son of Man",
    "El ministerio del Hijo del Hombre": "The Ministry of the Son of Man",
    "El rechazo al Hijo del Hombre": "The Rejection of the Son of Man",
    "La crucifixión y resurrección del Hijo del Hombre": "The Crucifixion and Resurrection of the Son of Man",
    # NT - John
    "La encarnación y presentación del Hijo de Dios": "The Incarnation and Presentation of the Son of God",
    "La oposición al Hijo de Dios": "The Opposition to the Son of God",
    "La preparación de los discípulos del Hijo de Dios": "The Preparation of the Son of God's Disciples",
    "La crucifixión y resurrección del Hijo de Dios": "The Crucifixion and Resurrection of the Son of God",
    # NT - Acts
    "Testigos en Jerusalén": "Witnesses in Jerusalem",
    "Testigos en Judea y en Samaria": "Witnesses in Judea and Samaria",
    "Testigos hasta lo último de la tierra": "Witnesses to the Ends of the Earth",
    # NT - Romans
    "La revelación de la justicia de Dios": "The Revelation of God's Righteousness",
    "La vindicación de la justicia de Dios": "The Vindication of God's Righteousness",
    "La aplicación de la justicia de Dios": "The Application of God's Righteousness",
    # NT - 1 Corinthians
    "Respuesta al informe de Cloe sobre divisiones": "Response to Chloe's Report on Divisions",
    "Respuesta a los reportes sobre asuntos disciplinarios": "Response to Reports on Disciplinary Matters",
    "Respuesta a la carta con preguntas": "Response to the Letter with Questions",
    # NT - 2 Corinthians
    "Exposición de Pablo sobre su ministerio": "Paul's Exposition on His Ministry",
    "La colecta de Pablo para los santos": "Paul's Collection for the Saints",
    "Vindicación del apostolado de Pablo": "Vindication of Paul's Apostleship",
    # NT - Galatians
    "Defensa del evangelio de la gracia": "Defense of the Gospel of Grace",
    "Explicación del evangelio de la gracia": "Explanation of the Gospel of Grace",
    "Aplicación del evangelio de la gracia": "Application of the Gospel of Grace",
    # NT - Ephesians
    "La postura de los cristianos": "The Standing of Christians",
    "La práctica de los cristianos": "The Practice of Christians",
    # NT - Philippians
    "Relato de Pablo sobre su situación actual": "Paul's Account of His Present Situation",
    "Reclamo de la mente de Cristo": "Claiming the Mind of Christ",
    "Reclamo del conocimiento de Cristo": "Claiming the Knowledge of Christ",
    "Reclamo de la paz de Cristo": "Claiming the Peace of Christ",
    # NT - Colossians
    "La supremacía de Cristo en la Iglesia": "The Supremacy of Christ in the Church",
    "El sometimiento a Cristo en la Iglesia": "Submission to Christ in the Church",
    # NT - 1 Thessalonians
    "Reflexiones personales de Pablo sobre los tesalonicenses": "Paul's Personal Reflections on the Thessalonians",
    "Instrucciones de Pablo a los tesalonicenses": "Paul's Instructions to the Thessalonians",
    # NT - 2 Thessalonians
    "Pablo alienta a los santos ante la persecución": "Paul Encourages the Saints amid Persecution",
    "Explicación de Pablo sobre el día del Señor": "Paul's Explanation of the Day of the Lord",
    "Exhortación de Pablo a la Iglesia": "Paul's Exhortation to the Church",
    # NT - 1 Timothy
    "Instrucciones de Pablo sobre la doctrina": "Paul's Instructions on Doctrine",
    "Instrucciones de Pablo sobre la adoración pública": "Paul's Instructions on Public Worship",
    "Instrucciones de Pablo sobre los falsos maestros": "Paul's Instructions on False Teachers",
    "Instrucciones de Pablo sobre la disciplina de la Iglesia": "Paul's Instructions on Church Discipline",
    "Instrucciones de Pablo sobre los motivos del ministerio": "Paul's Instructions on the Motives of Ministry",
    # NT - 2 Timothy
    "Perseverancia en las pruebas presentes": "Perseverance in Present Trials",
    "Persistencia en las pruebas futuras": "Persistence in Future Trials",
    # NT - Titus
    "Instrucciones sobre el llamamiento de líderes": "Instructions on Calling Leaders",
    "Poner las cosas en orden": "Setting Things in Order",
    # NT - Philemon
    "Intercesión de Pablo por Onésimo": "Paul's Intercession for Onesimus",
    # NT - Hebrews
    "La superioridad del ser de Cristo": "The Superiority of Christ's Person",
    "La superioridad de la obra de Cristo": "The Superiority of Christ's Work",
    "La superioridad del camino de Cristo": "The Superiority of Christ's Way",
    # NT - James
    "La práctica de la fe": "The Practice of Faith",
    "Los problemas de la fe": "The Problems of Faith",
    "La proyección de la fe": "The Projection of Faith",
    # NT - 1 Peter
    "Vivir en la esperanza": "Living in Hope",
    "Vivir en la obediencia": "Living in Obedience",
    "Vivir en el padecimiento": "Living in Suffering",
    "Exhortaciones finales": "Final Exhortations",
    # NT - 2 Peter
    "Cultivo de un carácter cristiano": "Cultivating Christian Character",
    "Condena de los falsos maestros": "Condemnation of False Teachers",
    "Confianza en la Segunda Venida": "Confidence in the Second Coming",
    # NT - 1 John
    "El fundamento de la fraternidad": "The Foundation of Fellowship",
    "El comportamiento fraternal": "Fraternal Conduct",
    # NT - 2 John
    "Reprobación de los falsos maestros": "Reproof of False Teachers",
    # NT - 3 John
    "Elogio de Gayo y condenación de Diótrefes": "Praise of Gaius and Condemnation of Diotrephes",
    # NT - Jude
    "Denuncia de los falsos maestros": "Denunciation of False Teachers",
    # NT - Revelation
    "La visión de Jesucristo en la isla de Patmos": "The Vision of Jesus Christ on the Isle of Patmos",
    "Las cartas a las siete iglesias": "The Letters to the Seven Churches",
    "Visiones del juicio de Dios": "Visions of God's Judgment",
    "La Segunda Venida de Jesucristo": "The Second Coming of Jesus Christ",
    "Cielo nuevo y tierra nueva": "A New Heaven and a New Earth",
    # BoM - 1 Nephi
    "El ministerio de Lehi en Jerusalén": "Lehi's Ministry in Jerusalem",
    "El acampamento en el valle de Lemuel": "The Camp in the Valley of Lemuel",
    "La obtención de las planchas de bronce": "Obtaining the Brass Plates",
    "La unión con la familia de Ismael": "Joining Ishmael's Family",
    "La visión del árbol de Lehi": "Lehi's Vision of the Tree",
    "Profecías de Lehi": "Lehi's Prophecies",
    "La visión de Nefi": "Nephi's Vision",
    "Explicación de Nefi de las profecías de Lehi": "Nephi's Explanation of Lehi's Prophecies",
    "El viaje hacia la tierra prometida": "The Journey to the Promised Land",
    "El ministerio en la tierra prometida": "The Ministry in the Promised Land",
    "Nefi cita las profecías de Isaías": "Nephi Quotes the Prophecies of Isaiah",
    "Nefi explica las profecías de Isaías": "Nephi Explains the Prophecies of Isaiah",
    # BoM - 2 Nephi
    "Las palabras de Lehi": "The Words of Lehi",
    "Las palabras de Jacob": "The Words of Jacob",
    "Las palabras de Isaías": "The Words of Isaiah",
    "Las palabras de Nefi sobre la doctrina de Cristo": "Nephi's Words on the Doctrine of Christ",
    "Separación y prosperidad de los nefitas": "Separation and Prosperity of the Nephites",
    "La profecía de Nefi": "Nephi's Prophecy",
    # BoM - Jacob
    "Predicación de Jacob en el templo": "Jacob's Preaching in the Temple",
    "La profecía de Jacob": "Jacob's Prophecy",
    "El encuentro con Sherem, el anticristo": "The Encounter with Sherem, the Anti-Christ",
    # BoM - Enos
    "La oración y predicación de Enós": "The Prayer and Preaching of Enos",
    # BoM - Jarom
    "Relación entre nefitas y lamanitas": "Relations between Nephites and Lamanites",
    # BoM - Omni
    "Cinco autores nefitas": "Five Nephite Authors",
    # BoM - Words of Mormon
    "Los reinados de Mosíah I y el rey Benjamín": "The Reigns of Mosiah I and King Benjamin",
    # BoM - Mosiah
    "La fusión con Zarahemla": "The Merger with Zarahemla",
    "El registro de Zeniff": "The Record of Zeniff",
    "El relato de Alma": "The Account of Alma",
    "La nueva nación nefita": "The New Nephite Nation",
    # BoM - Alma
    "La apostasía de Nehor y la rebelión amlicita": "The Apostasy of Nehor and the Amlicite Rebellion",
    "El ministerio de Alma": "The Ministry of Alma",
    "El ministerio de los hijos de Mosíah": "The Ministry of the Sons of Mosiah",
    "La predicación entre los zoramitas": "Preaching among the Zoramites",
    "Los mandamientos de Alma a Helamán": "Alma's Commandments to Helaman",
    "Los mandamientos de Alma a Shiblón": "Alma's Commandments to Shiblon",
    "Los mandamientos de Alma a Coriantón": "Alma's Commandments to Corianton",
    "Guerra entre nefitas y lamanitas": "War between Nephites and Lamanites",
    "Invasión lamanita, disensiones y guerras": "Lamanite Invasion, Dissensions, and Wars",
    "Palabras finales de Alma y disensión de Amalickíah": "Alma's Final Words and Amalickiah's Dissension",
    # BoM - Helaman
    "Origen de los ladrones de Gadiantón": "Origin of the Gadianton Robbers",
    "Orgullo y debilitamiento": "Pride and Weakening",
    "Las profecías de Nefi II": "The Prophecies of Nephi II",
    "La obra de la destrucción": "The Work of Destruction",
    "Las profecías de Samuel el lamanita": "The Prophecies of Samuel the Lamanite",
    # BoM - 3 Nephi
    "El nacimiento de Cristo ycrecimiento de los ladrones de Gadiantón": "The Birth of Christ and Growth of the Gadianton Robbers",
    "Iniquidad y la guerra con los ladrones de Gadiantón": "Iniquity and the War with the Gadianton Robbers",
    "Destrucción y oscuridad en toda la tierra": "Destruction and Darkness throughout the Land",
    "Jesucristo aparece y declara su doctrina": "Jesus Christ Appears and Declares His Doctrine",
    "El Sermón del templo": "The Sermon at the Temple",
    "La ley de Moisés y el recogimiento de Israel": "The Law of Moses and the Gathering of Israel",
    "Jesús sana y bendice a la multitud": "Jesus Heals and Blesses the Multitude",
    "Instrucciones sobre la Santa Cena": "Instructions on the Sacrament",
    "Jesús regresa y hace una oración": "Jesus Returns and Offers a Prayer",
    "Jesús administra la Santa Cena y explica el recogimiento": "Jesus Administers the Sacrament and Explains the Gathering",
    "El cumplimiento de las profecías de Samuel el lamanita": "The Fulfillment of Samuel the Lamanite's Prophecies",
    "Jesús hace una exposición de todas las escrituras": "Jesus Expounds All the Scriptures",
    "El nombre de la Iglesia y el evangelio de Jesucristo": "The Name of the Church and the Gospel of Jesus Christ",
    "La misión de los tres nefitas": "The Mission of the Three Nephites",
    "Exhortación a los gentiles de escuchar las palabras del Señor": "Exhortation to the Gentiles to Hear the Words of the Lord",
    # BoM - 4 Nephi
    "Prosperidad, corrupción y división del pueblo": "Prosperity, Corruption, and Division of the People",
    # BoM - Mormon
    "Elección de Mormón y guerra en Zarahemla": "Mormon's Calling and War in Zarahemla",
    "Retirada a la tierra hacia el norte": "Retreat to the Land Northward",
    "Acontecimientos en la tierra del norte": "Events in the Land Northward",
    "Destrucción en Cumorah": "Destruction at Cumorah",
    "Palabras de Mormón para el remanente": "Mormon's Words to the Remnant",
    "Introducción a los escritos de Moroni": "Introduction to Moroni's Writings",
    "Palabras de Moroni para los incrédulos": "Moroni's Words to the Unbelievers",
    # BoM - Ether
    "La salida desde la gran torre": "The Departure from the Great Tower",
    "Los preparativos para el viaje": "Preparations for the Journey",
    "La visión del hermano de Jared": "The Vision of the Brother of Jared",
    "Palabras de Moroni al traductor del Libro de Mormón": "Moroni's Words to the Translator of the Book of Mormon",
    "La travesía hacia la tierra prometida": "The Voyage to the Promised Land",
    "Los reinados de los reyes jareditas": "The Reigns of the Jaredite Kings",
    "Las profecías de Eter": "The Prophecies of Ether",
    "La destrucción de los jareditas": "The Destruction of the Jaredites",
    # BoM - Moroni
    "Ordenanzas y prácticas de la Iglesia": "Ordinances and Practices of the Church",
    "Palabras de Mormón sobre fe, esperanza y caridad": "Mormon's Words on Faith, Hope, and Charity",
    "Palabras de Mormón sobre el bautismo de infantes": "Mormon's Words on Infant Baptism",
    "Palabras de Mormón sobre la guerra": "Mormon's Words on War",
    "Despedida de Moroni": "Moroni's Farewell",
    # D&C
    "Periodo de Nueva York": "New York Period",
    "Periodo de Ohio": "Ohio Period",
    "Periodo de Misuri": "Missouri Period",
    "Periodo de Illinois": "Illinois Period",
    "El Oeste": "The West",
    "La Iglesia moderna": "The Modern Church",
    # PGP
    "Introducción a la visión de Moisés": "Introduction to the Vision of Moses",
    "El ministerio de Enoc": "The Ministry of Enoch",
    "De Matusalén a Noé": "From Methuselah to Noah",
    "Preparación de Abraham": "Preparation of Abraham",
    "La visión de Abraham": "The Vision of Abraham",
    "Segmento del Sermón del Olivar": "Segment of the Olivet Discourse",
    "Historia de José Smith": "Joseph Smith's History",
    "Los Artículos de Fe de La Iglesia de Jesucristo": "The Articles of Faith of The Church of Jesus Christ",
    "Facsímiles del Libro de Abraham": "Facsimiles of the Book of Abraham",
}

def main():
    with open(PARTS_PATH, encoding="utf-8") as f:
        parts = json.load(f)

    missing = []
    applied = 0
    for p in parts:
        en = TRANSLATIONS.get(p["name_es"])
        if en:
            p["name_en"] = en
            applied += 1
        elif p.get("name_en"):
            applied += 1  # Already has EN (e.g., facsimiles)
        else:
            missing.append(p["name_es"])

    with open(PARTS_PATH, "w", encoding="utf-8") as f:
        json.dump(parts, f, ensure_ascii=False, indent=2)

    print("Applied: %d / %d" % (applied, len(parts)))
    if missing:
        print("MISSING translations (%d):" % len(missing))
        for m in missing:
            print("  %s" % m)
    else:
        print("All parts have EN translations")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""IJCSUD batch — individual Fase 0 per work. 88 items.

Categories:
  - Old Liahonas (1962-1989) → magazines/liahona/YYYY/MM (pre-corpus coverage)
  - Manuals (Preparation, Camp, Ministración, etc.) → manuals
  - Santos tomos I-III → books (narrative church history)
  - Para la Fortaleza Juventud → manuals (pamphlet)
  - Mapas/Posters/Tarjetas → reference
  - Courses/broadcasts → manuals
"""
import subprocess, sys, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READY = ROOT / "epub" / "!Ready"
DONE = ROOT / "epub" / "!Done"
EXTRACT = ROOT / "scripts" / "epub_extract.py"

MESES = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
}

# Old Liahonas (pre-2002): parse filename → year+month auto-gen metadata
LIAHONA_FILES = [
    ("LIAHONA 1989-01 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1989", "01"),
    ("Liahona, abril 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "04"),
    ("Liahona, abril de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "04"),
    ("Liahona, agosto 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "08"),
    ("Liahona, agosto de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "08"),
    ("Liahona, diciembre 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "12"),
    ("Liahona, diciembre de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "12"),
    ("Liahona, diciembre de 1975 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1975", "12"),
    ("Liahona, enero 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "01"),
    ("Liahona, enero 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "01"),
    ("Liahona, enero 1985 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1985", "01"),
    ("Liahona, enero de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "01"),  # dup of 'enero 1963'?
    ("Liahona, febrero 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "02"),
    ("Liahona, febrero de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "02"),
    ("Liahona, julio 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "07"),
    ("Liahona, julio de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "07"),
    ("Liahona, junio 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "06"),
    ("Liahona, junio de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "06"),
    ("Liahona, marzo 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "03"),
    ("Liahona, marzo de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "03"),
    ("Liahona, mayo 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "05"),
    ("Liahona, mayo de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "05"),
    ("Liahona, noviembre 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "11"),
    ("Liahona, noviembre de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "11"),
    ("Liahona, octubre 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "10"),
    ("Liahona, octubre de 1963 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1963", "10"),
    ("Liahona, septiembre 1962 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub", "1962", "09"),
]

# Para la Fortaleza de la Juventud 2021 numbered pamphlets — 4 numbered issues (themes)
FORTALEZA = [
    ("Para la Fortaleza de la Juventud 202101 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "para-la-fortaleza-de-la-juventud-202101", "Para la Fortaleza de la Juventud 2021 #01"),
    ("Para la Fortaleza de la Juventud 202102 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "para-la-fortaleza-de-la-juventud-202102", "Para la Fortaleza de la Juventud 2021 #02"),
    ("Para la Fortaleza de la Juventud 202103 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "para-la-fortaleza-de-la-juventud-202103", "Para la Fortaleza de la Juventud 2021 #03"),
    ("Para la Fortaleza de la Juventud 202104 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "para-la-fortaleza-de-la-juventud-202104", "Para la Fortaleza de la Juventud 2021 #04"),
]

# Main curated list (manuals + reference + books)
WORKS = [
    ("Los Artículos de Fe (póster) - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "articulos-de-fe-poster", 45, 70, "opcional",
     "reference", ["articles-of-faith", "poster", "reference"],
     "Póster oficial de los Artículos de Fe."),
    ("Manual 2 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "manual-2", 50, 80, "importante",
     "manuals", ["handbook-2", "church-administration"],
     "Manual 2 (anterior al Manual General 2020)."),
    ("Manual 2 Administración de la Iglesia 2010 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "manual-2-administracion-2010", 50, 80, "importante",
     "manuals", ["handbook-2", "church-administration", "2010-edition"],
     "Manual 2 Administración de la Iglesia, edición 2010."),
    ("Manual General - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "manual-general", 55, 85, "importante",
     "manuals", ["handbook", "current", "church-administration"],
     "Manual General de la Iglesia (2020+)."),
    ("Manual de Oratoria y Redacción - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "manual-oratoria-redaccion", 35, 70, "opcional",
     "manuals", ["oratory", "writing", "public-speaking"],
     "Manual de Oratoria y Redacción."),
    ("Mapas bíblicos - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "mapas-biblicos-ijcsud", 45, 75, "importante",
     "reference", ["bible-maps", "biblical-geography"],
     "Mapas bíblicos oficiales IJCSUD."),
    ("Mapas de historia de la Iglesia, 2 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "mapas-historia-iglesia-2", 45, 75, "opcional",
     "reference", ["church-history", "maps"],
     "Mapas de historia de la Iglesia, vol. 2."),
    ("Mapas de historia de la Iglesia, 4 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "mapas-historia-iglesia-4", 45, 75, "opcional",
     "reference", ["church-history", "maps"],
     "Mapas de historia de la Iglesia, vol. 4."),
    ("Mapas de historia de la Iglesia, 5 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "mapas-historia-iglesia-5", 45, 75, "opcional",
     "reference", ["church-history", "maps"],
     "Mapas de historia de la Iglesia, vol. 5."),
    ("Mapas de historia de la Iglesia, 6 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "mapas-historia-iglesia-6", 45, 75, "opcional",
     "reference", ["church-history", "maps"],
     "Mapas de historia de la Iglesia, vol. 6."),
    ("Mapas de historia de la Iglesia, 7 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "mapas-historia-iglesia-7", 45, 75, "opcional",
     "reference", ["church-history", "maps"],
     "Mapas de historia de la Iglesia, vol. 7."),
    ("Matrimonio y relaciones familiares - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "matrimonio-y-relaciones-familiares", 50, 80, "importante",
     "manuals", ["marriage", "family", "course-manual"],
     "Manual del curso Matrimonio y relaciones familiares."),
    ("Mi plan - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "mi-plan-ijcsud", 45, 70, "opcional",
     "manuals", ["returned-missionary", "life-planning"],
     "Mi plan: Una guía para el misionero retornado."),
    ("Mi reino se extenderá - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "mi-reino-se-extendera", 45, 75, "opcional",
     "books", ["church-growth", "missionary", "international"],
     "Mi reino se extenderá."),
    ("Ministración eficaz - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "ministracion-eficaz", 50, 80, "importante",
     "manuals", ["ministering", "current", "2018-initiative"],
     "Ministración eficaz (introducción oficial al programa de ministración, 2018)."),
    ("NECESITO UN AMIGO - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "necesito-un-amigo", 40, 65, "opcional",
     "manuals", ["fellowship", "pamphlet"],
     "Necesito un amigo (folleto)."),
    ("Niños y jóvenes de La Iglesia de Jesucristo de losia de Jesucristo de los Santos de los Últimos Días.epub",
     "ninos-y-jovenes-ijcsud", 50, 80, "importante",
     "manuals", ["children", "youth", "current", "2020-initiative"],
     "Niños y jóvenes (programa 2020)."),
    ("Nuestra familia - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "nuestra-familia", 45, 70, "opcional",
     "manuals", ["family-history", "pamphlet"],
     "Nuestra familia (folleto de historia familiar)."),
    ("Oraciones sacramentales - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "oraciones-sacramentales", 55, 85, "importante",
     "reference", ["sacrament-prayers", "ordinance", "primary-source"],
     "Oraciones sacramentales (texto oficial de las oraciones)."),
    ("Orar en las reuniones dominicales - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "orar-en-reuniones-dominicales", 40, 65, "opcional",
     "manuals", ["prayer", "worship", "pamphlet"],
     "Orar en las reuniones dominicales."),
    ("PREPARACIÓN MISIONAL MANUAL PARA EL ALUMNO - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "preparacion-misional-manual-alumno", 50, 80, "importante",
     "manuals", ["missionary-preparation", "student-manual"],
     "Preparación Misional — Manual para el alumno."),
    ("PREPARACIÓN MISIONAL_ MANUAL PARA EL MAESTRO - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "preparacion-misional-manual-maestro", 50, 80, "importante",
     "manuals", ["missionary-preparation", "teacher-manual"],
     "Preparación Misional — Manual para el maestro."),
    ("Palabra de Sabiduría, La - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "palabra-de-sabiduria-folleto", 45, 75, "opcional",
     "reference", ["word-of-wisdom", "pamphlet"],
     "La Palabra de Sabiduría (folleto oficial)."),
    ("Planificación de la búsqueda de empleo - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "planificacion-busqueda-empleo", 35, 65, "opcional",
     "manuals", ["employment", "self-reliance"],
     "Planificación de la búsqueda de empleo."),
    ("Preparación misional - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "preparacion-misional-folleto", 45, 70, "opcional",
     "manuals", ["missionary-preparation", "pamphlet"],
     "Preparación misional (folleto breve)."),
    ("Principios (de ministración) - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "principios-de-ministracion", 50, 75, "importante",
     "manuals", ["ministering", "principles"],
     "Principios de ministración."),
    ("Principios de liderazgo - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "principios-de-liderazgo", 50, 75, "importante",
     "manuals", ["leadership", "course-manual"],
     "Principios de liderazgo."),
    ("Principios del Evangelio - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "principios-del-evangelio-manual", 55, 85, "importante",
     "manuals", ["gospel-principles", "classic-manual"],
     "Principios del Evangelio (manual doctrinal básico)."),
    ("RELATOS DE DOCTRINA Y CONVENIOS - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "relatos-de-doctrina-y-convenios", 45, 70, "opcional",
     "reference", ["doctrine-and-covenants", "stories", "primary-children"],
     "Relatos de Doctrina y Convenios (narrativa infantil)."),
    ("RELATOS DEL ANTIGUO TESTAMENTO - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "relatos-del-antiguo-testamento", 45, 70, "opcional",
     "reference", ["old-testament", "stories", "primary-children"],
     "Relatos del Antiguo Testamento."),
    ("RELATOS DEL NUEVO TESTAMENTO - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "relatos-del-nuevo-testamento", 45, 70, "opcional",
     "reference", ["new-testament", "stories", "primary-children"],
     "Relatos del Nuevo Testamento."),
    ("Reseñas de cursos seleccionados de Instituto - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "resenas-cursos-instituto", 45, 70, "opcional",
     "manuals", ["institute", "course-overview"],
     "Reseñas de cursos seleccionados de Instituto."),
    ("Responsabilidades de miembros y líderes - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "responsabilidades-miembros-lideres", 50, 75, "importante",
     "manuals", ["member-responsibilities", "leadership"],
     "Responsabilidades de miembros y líderes."),
    ("Reunión mundial del cuerpo docente del Sei - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "reunion-mundial-cuerpo-docente-si", 45, 70, "opcional",
     "manuals", ["seminaries-institutes", "faculty-meeting"],
     "Reunión mundial del cuerpo docente del S&I."),
    ("Revelaciones en contexto - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "revelaciones-en-contexto", 50, 85, "importante",
     "books", ["doctrine-and-covenants", "church-history", "revelations-in-context"],
     "Revelaciones en contexto (contextos históricos de las secciones de DyC)."),
    ("S&I Annual Training Broadcast 2021 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "si-annual-training-2021", 45, 70, "opcional",
     "manuals", ["seminaries-institutes", "training-broadcast", "2021"],
     "S&I Annual Training Broadcast 2021."),
    ("Sacerdocio Aarónico, manual 1 - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "sacerdocio-aaronico-manual-1", 50, 75, "importante",
     "manuals", ["aaronic-priesthood", "young-men"],
     "Sacerdocio Aarónico, manual 1."),
    ("Santos tomo I - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "santos-tomo-1", 55, 85, "importante",
     "history", ["church-history", "santos", "narrative-history", "modern-official-history"],
     "Santos, tomo I: El Estandarte de la Verdad, 1815-1846 (historia oficial narrativa)."),
    ("Santos tomo II - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "santos-tomo-2", 55, 85, "importante",
     "history", ["church-history", "santos", "narrative-history"],
     "Santos, tomo II: Ninguna mano impía, 1846-1893."),
    ("Santos, tomo III - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "santos-tomo-3", 55, 85, "importante",
     "history", ["church-history", "santos", "narrative-history"],
     "Santos, tomo III: Valientes, nobles e independientes, 1893-1955."),
    ("Seminaries and Institutes Objective - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "si-objective", 50, 75, "importante",
     "manuals", ["seminaries-institutes", "mission-statement"],
     "Seminaries and Institutes Objective."),
    ("Sociedad de Socorro_ Aprended para enseñar - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "sociedad-socorro-aprended-ensenar", 45, 70, "opcional",
     "manuals", ["relief-society", "teaching", "women"],
     "Sociedad de Socorro: Aprended para enseñar."),
    ("Spurious Materials in Circulation - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "spurious-materials-in-circulation", 50, 75, "importante",
     "reference", ["spurious-materials", "warning", "church-communication"],
     "Spurious Materials in Circulation (advertencia sobre materiales falsos)."),
    ("Taller de autosuficiencia laboral - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "taller-autosuficiencia-laboral", 35, 65, "opcional",
     "manuals", ["self-reliance", "employment"],
     "Taller de autosuficiencia laboral."),
    ("Tarjetas de bendición de los sacramentos - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "tarjetas-bendicion-sacramentos", 50, 75, "opcional",
     "reference", ["sacrament-prayers", "cards", "priesthood-aid"],
     "Tarjetas de bendición de los sacramentos."),
    ("Tecnicas para entrevistas - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "tecnicas-para-entrevistas", 30, 65, "opcional",
     "manuals", ["self-reliance", "interview-skills"],
     "Técnicas para entrevistas (autosuficiencia)."),
    ("Temas de historia de la Iglesia - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "temas-historia-iglesia", 50, 80, "importante",
     "reference", ["church-history-topics", "gospel-topics-essays", "current"],
     "Temas de historia de la Iglesia (Gospel Topics Essays)."),
    ("Técnicas de negociación - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "tecnicas-negociacion", 25, 60, "opcional",
     "manuals", ["self-reliance", "negotiation"],
     "Técnicas de negociación (autosuficiencia)."),
    ("Una velada con una Autoridad General - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "velada-con-autoridad-general", 50, 75, "importante",
     "discourses", ["general-authority", "evening-with", "pastoral-discourse"],
     "Una velada con una Autoridad General (compilación de charlas)."),
    ("Unidad en cuestiones de dinero - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "unidad-cuestiones-dinero", 40, 65, "opcional",
     "manuals", ["finances", "marriage", "self-reliance"],
     "Unidad en cuestiones de dinero."),
    ("VERSIÓN SIMPLIFICADA DE LOS HIMNOS - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "version-simplificada-himnos", 40, 70, "opcional",
     "reference", ["hymns", "simplified", "music"],
     "Versión simplificada de los himnos."),
    ("Ven sígueme 2023, Primaria - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "ven-sigueme-2023-primaria", 50, 80, "importante",
     "manuals", ["come-follow-me", "2023", "primary"],
     "Ven, sígueme 2023 — Primaria."),
    ("Yo En 30 segundos - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "yo-en-30-segundos", 25, 60, "opcional",
     "manuals", ["self-reliance", "elevator-pitch"],
     "Yo en 30 segundos (autosuficiencia)."),
    ("mandato a los maestros de religión, Un - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "mandato-maestros-religion", 55, 85, "importante",
     "discourses", ["packer", "seminaries-institutes", "charge-to-religious-educators", "classic"],
     "Un mandato a los maestros de religión (Charge to Religious Educators, Packer 1994)."),
    ("plan de salvación, El - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "plan-de-salvacion-folleto", 50, 80, "importante",
     "reference", ["plan-of-salvation", "pamphlet", "missionary-aid"],
     "El plan de salvación (folleto misional oficial)."),
    ("uso eficaz de La red de contactos, El - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "uso-eficaz-red-contactos", 25, 60, "opcional",
     "manuals", ["self-reliance", "networking"],
     "El uso eficaz de la red de contactos."),
    ("verdad restaurada, La - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "la-verdad-restaurada", 50, 75, "importante",
     "reference", ["restoration", "proclamation-of-restoration-of-fulness", "2020"],
     "La verdad restaurada / Proclamación del Bicentenario de la Restauración 2020."),
    ("Manual de campamento de Mujeres Jóvenes - La Iglesia de Jesucristo de los Santos de los Últimos Días.epub",
     "manual-campamento-mujeres-jovenes", 45, 70, "opcional",
     "manuals", ["young-women", "camp", "outdoor"],
     "Manual de campamento de Mujeres Jóvenes."),
]

AUTHOR = "La Iglesia de Jesucristo de los Santos de los Últimos Días"

ok = 0
broken = []

# Liahonas
print("=== Liahonas viejas ===")
for fn, year, month in LIAHONA_FILES:
    src = READY / fn
    if not src.exists():
        broken.append((fn, "MISSING"))
        continue
    slug = f"liahona-{year}-{month}"
    # magazine-style: put in magazines/liahona/YEAR/MONTH/
    cat = "magazines"
    subcat = f"liahona/{year}/{month}"
    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    fase0.write_text(json.dumps({
        "authority": 50, "rigor": 75, "importance": "opcional",
        "official": True, "current": False, "context": "magazine",
        "audience": "all", "tags": ["liahona", f"year-{year}", "pre-corpus-coverage", "magazine"],
        "category": cat, "author": AUTHOR, "source_url": None,
        "note": f"Liahona {year}-{month} (pre-2002 issue, not previously in corpus).",
    }, indent=2), encoding="utf-8")
    cmd = [sys.executable, str(EXTRACT), str(src),
           "--lang", "es", "--category", cat, "--subcategory", subcat, "--apply",
           "--slug", slug, "--author", AUTHOR, "--fase0", str(fase0)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        src.rename(DONE / fn)
        print(f"  OK {slug}")
    else:
        broken.append((fn, r.stderr[-120:] if r.stderr else "?"))
        print(f"  BROKEN {slug}")

# Fortaleza pamphlets
print("\n=== Para la Fortaleza de la Juventud 2021 (pamphlets) ===")
for fn, slug, title in FORTALEZA:
    src = READY / fn
    if not src.exists():
        broken.append((fn, "MISSING"))
        continue
    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    fase0.write_text(json.dumps({
        "authority": 50, "rigor": 75, "importance": "importante",
        "official": True, "current": True, "context": "magazine",
        "audience": "youth",
        "tags": ["for-the-strength-of-youth", "2021", "youth-pamphlet"],
        "category": "manuals", "author": AUTHOR, "source_url": None,
        "note": title,
    }, indent=2), encoding="utf-8")
    cmd = [sys.executable, str(EXTRACT), str(src),
           "--lang", "es", "--category", "manuals", "--apply",
           "--slug", slug, "--author", AUTHOR, "--fase0", str(fase0)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        src.rename(DONE / fn)
        print(f"  OK {slug}")
    else:
        broken.append((fn, r.stderr[-120:] if r.stderr else "?"))
        print(f"  BROKEN {slug}")

# Main curated
print("\n=== Main IJCSUD curated ===")
for fn, slug, auth, rigor, imp, cat, tags, note in WORKS:
    src = READY / fn
    if not src.exists():
        broken.append((fn, "MISSING"))
        continue
    fase0 = ROOT / "proj" / "P4-corpus-expansion" / "fase0" / f"{slug}.fase0.json"
    fase0.write_text(json.dumps({
        "authority": auth, "rigor": rigor, "importance": imp,
        "official": True, "current": True, "context": "ijcsud-official",
        "audience": "all", "tags": tags, "category": cat,
        "author": AUTHOR, "source_url": None, "note": note,
    }, indent=2), encoding="utf-8")
    cmd = [sys.executable, str(EXTRACT), str(src),
           "--lang", "es", "--category", cat, "--apply",
           "--slug", slug, "--author", AUTHOR, "--fase0", str(fase0)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        src.rename(DONE / fn)
        print(f"  OK {slug}")
    else:
        broken.append((fn, r.stderr[-120:] if r.stderr else "?"))
        print(f"  BROKEN {slug}")

print(f"\nIJCSUD batch: {ok} OK, {len(broken)} broken")
for fn, err in broken:
    print(f"  - {fn[:60]}: {err[:100]}")
print(f"\n!Ready={len(list(READY.iterdir()))}  !Done={len(list(DONE.iterdir()))}")

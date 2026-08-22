"""Generate KG seed files from wp_bc's authors-enriched.json and wikidata sources.

Outputs to data/kg-seeds/:
  - general-authorities.json (entities + relations for all persons)
  - general-authorities-places.json (place entities)

Also outputs data/gazetteer-extra.json for manual merge into entities.json
"""

import json
import os
from collections import defaultdict

WP_BC = r"C:\own\wp_bc"
SEEDS_DIR = r"C:\own\alejandria\data\kg-seeds"
GAZETTEER_PATH = r"C:\own\alejandria\src\alejandria\knowledge\gazetteers\entities.json"

# Load authors-enriched (primary source)
with open(os.path.join(WP_BC, "bin", "authors-enriched.json"), "r", encoding="utf-8") as f:
    AUTHORS = json.load(f)
print(f"Loaded {len(AUTHORS)} authors")

# Build name lookup
authors_by_name = {}
for entry in AUTHORS:
    authors_by_name[entry["name"].lower()] = entry

# Load wikidata-bio (birth/death years)
with open(os.path.join(WP_BC, "bin", "wikidata-bio.json"), "r", encoding="utf-8") as f:
    WD_BIO = json.load(f)

# Load wikidata-places (birth/death place names)
with open(os.path.join(WP_BC, "bin", "wikidata-places.json"), "r", encoding="utf-8") as f:
    WD_PLACES = json.load(f)

# Build slug lookup for places
places_by_slug = {}
for p in WD_PLACES:
    slug = p.get("slug", "")
    if slug:
        places_by_slug[slug] = p

# Load wikidata-claims (birth/death place QIDs)
with open(os.path.join(WP_BC, "bin", "wikidata-claims.json"), "r", encoding="utf-8") as f:
    WD_CLAIMS = json.load(f)

claims_by_qid = {}
claims_by_slug = {}
for c in WD_CLAIMS:
    qid = c.get("qid", "")
    slug = c.get("slug", "")
    if qid:
        claims_by_qid[qid] = c
    if slug:
        claims_by_slug[slug] = c

# Load qid-list for slug -> qid mapping
with open(os.path.join(WP_BC, "bin", "qid-list.json"), "r", encoding="utf-8") as f:
    QID_LIST = json.load(f)

qid_by_slug = {}
for q in QID_LIST:
    qid_by_slug[q["slug"]] = q["qid"]

# Load descriptions for aliases
with open(os.path.join(WP_BC, "bin", "wikidata-descriptions.json"), "r", encoding="utf-8") as f:
    WD_DESC = json.load(f)

# Load wikipedia-birthplaces
with open(os.path.join(WP_BC, "bin", "wikipedia-birthplaces.json"), "r", encoding="utf-8") as f:
    WP_BIRTHPLACES = json.load(f)


# ---- Mapping helpers ----

CALLING_TO_AUTHORITY = {
    "presidente-de-la-iglesia": ("autoridad_general", "Autoridad General", 85),
    "apostol": ("autoridad_general", "Autoridad General", 85),
    "asistente-cuorum-doce": ("autoridad_general", "Autoridad General", 85),
    "setenta-autoridad-general": ("autoridad_general", "Autoridad General", 85),
    "obispo-presidente": ("autoridad_general", "Autoridad General", 85),
    "obispado-presidente": ("autoridad_general", "Autoridad General", 85),
    "patriarca-general": ("autoridad_general", "Autoridad General", 85),
    "consejero-primera-presidencia": ("autoridad_general", "Autoridad General", 85),
    "consejero-asistente-pp": ("autoridad_general", "Autoridad General", 85),
    "presidencia-escuela-dominical": ("lider_general_iglesia", "Líder General de la Iglesia", 68),
    "presidencia-sociedad-socorro": ("lider_general_iglesia", "Líder General de la Iglesia", 68),
    "presidencia-mujeres-jovenes": ("lider_general_iglesia", "Líder General de la Iglesia", 68),
    "presidencia-hombres-jovenes": ("lider_general_iglesia", "Líder General de la Iglesia", 68),
    "presidencia-primaria": ("lider_general_iglesia", "Líder General de la Iglesia", 68),
}

CALLING_TO_ROLE = {
    "presidente-de-la-iglesia": ("President of the Church", "role"),
    "apostol": ("Quorum of the Twelve Apostles", "council"),
    "asistente-cuorum-doce": ("Assistant to the Quorum of the Twelve", "role"),
    "setenta-autoridad-general": ("Seventy", "role"),
    "obispo-presidente": ("Presiding Bishop", "role"),
    "obispado-presidente": ("Presiding Bishopric", "council"),
    "patriarca-general": ("Presiding Patriarch", "role"),
    "presidencia-escuela-dominical": ("Sunday School General Presidency", "council"),
    "presidencia-sociedad-socorro": ("Relief Society General Presidency", "council"),
    "presidencia-mujeres-jovenes": ("Young Women General Presidency", "council"),
    "presidencia-hombres-jovenes": ("Young Men General Presidency", "council"),
    "presidencia-primaria": ("Primary General Presidency", "council"),
    "consejero-primera-presidencia": ("Counselor in the First Presidency", "role"),
    "consejero-asistente-pp": ("Assistant Counselor in the First Presidency", "role"),
    "otro": None,
}

# President succession order
PRESIDENTS = [
    "Joseph Smith Jr.",
    "Brigham Young",
    "John Taylor",
    "Wilford Woodruff",
    "Lorenzo Snow",
    "Joseph F. Smith",
    "Heber J. Grant",
    "George Albert Smith",
    "David O. McKay",
    "Joseph Fielding Smith",
    "Harold B. Lee",
    "Spencer W. Kimball",
    "Ezra Taft Benson",
    "Howard W. Hunter",
    "Gordon B. Hinckley",
    "Thomas S. Monson",
    "Russell M. Nelson",
]

# President terms (for counselor matching)
PRESIDENT_TERMS = [
    ("Joseph Smith Jr.", 1830, 1844),
    ("Brigham Young", 1847, 1877),
    ("John Taylor", 1880, 1887),
    ("Wilford Woodruff", 1889, 1898),
    ("Lorenzo Snow", 1898, 1901),
    ("Joseph F. Smith", 1901, 1918),
    ("Heber J. Grant", 1918, 1945),
    ("George Albert Smith", 1945, 1951),
    ("David O. McKay", 1951, 1970),
    ("Joseph Fielding Smith", 1970, 1972),
    ("Harold B. Lee", 1972, 1973),
    ("Spencer W. Kimball", 1973, 1985),
    ("Ezra Taft Benson", 1985, 1994),
    ("Howard W. Hunter", 1994, 1995),
    ("Gordon B. Hinckley", 1995, 2008),
    ("Thomas S. Monson", 2008, 2018),
    ("Russell M. Nelson", 2018, 2030),
]

# Known family relations for presidents (source: Church history)
FAMILY_RELATIONS = [
    # Joseph Smith family
    ("Joseph Smith Jr.", "FATHER_OF", "Joseph Smith Sr.", "person"),
    ("Joseph Smith Jr.", "MOTHER_OF", "Lucy Mack Smith", "person"),
    ("Hyrum Smith", "FATHER_OF", "Joseph F. Smith", "person"),
    ("Joseph Smith Jr.", "BROTHER_OF", "Hyrum Smith", "person"),
    ("Joseph Smith Jr.", "BROTHER_OF", "Samuel H. Smith", "person"),
    ("Joseph Smith Jr.", "BROTHER_OF", "Don Carlos Smith", "person"),
    ("Joseph Smith Jr.", "SPOUSE_OF", "Emma Hale Smith", "person"),
    # Brigham Young
    ("Brigham Young", "BROTHER_OF", "Joseph Young", "person"),
    ("Brigham Young", "FATHER_OF", "Brigham Young Jr.", "person"),
    # Joseph F. Smith family
    ("Joseph F. Smith", "SON_OF", "Hyrum Smith", "person"),
    ("Joseph Fielding Smith", "SON_OF", "Joseph F. Smith", "person"),
    ("Joseph Fielding Smith", "BROTHER_OF", "Joseph F. Smith Jr.", "person"),
    # George A. Smith family (George Albert Smith's grandfather - cousin of Joseph Smith)
    ("George Albert Smith", "FATHER_OF", "John Henry Smith", "person"),
    # Lorenzo Snow
    ("Lorenzo Snow", "BROTHER_OF", "Eliza R. Snow", "person"),
    ("Lorenzo Snow", "SPOUSE_OF", "Sarah Ann Snow", "person"),
    # Gordon B. Hinckley family
    ("Gordon B. Hinckley", "SON_OF", "Bryant S. Hinckley", "person"),
    # Heber C. Kimball
    ("Heber C. Kimball", "FATHER_OF", "Spencer W. Kimball", "person"),
    # David O. McKay
    ("David O. McKay", "FATHER_OF", "David Lawrence McKay", "person"),
    # Marion G. Romney
    ("Marion G. Romney", "FATHER_OF", "George S. Romney", "person"),
    # Dallin H. Oaks
    ("Dallin H. Oaks", "SON_OF", "Lloyd E. Oaks", "person"),
    # Henry B. Eyring
    ("Henry B. Eyring", "SON_FATHER", "Henry Eyring", "person"),
    # Thomas S. Monson
    ("Thomas S. Monson", "FATHER_OF", "Clark S. Monson", "person"),
    # Spencer W. Kimball
    ("Spencer W. Kimball", "SON_OF", "Heber C. Kimball", "person"),
]

# ---- Collect all places ----
all_places = set()
person_birth_places = {}  # person_name -> place_name
person_death_places = {}  # person_name -> place_name

# From wikidata-places
for p in WD_PLACES:
    slug = p.get("slug", "")
    birth_place = p.get("birthPlace", "")
    death_place = p.get("deathPlace", "")
    if slug:
        # Find person name by slug
        for entry in AUTHORS:
            if entry.get("name", "").lower().replace(" ", "-").replace(
                ".", ""
            ) == slug.lower().replace(".", "").replace(" ", "-"):
                name = entry["name"]
                if birth_place and birth_place not in ("Position Died", "Position Born", ""):
                    person_birth_places[name] = birth_place
                    all_places.add(birth_place)
                if death_place and death_place not in ("Position Died", "Position Born", ""):
                    person_death_places[name] = death_place
                    all_places.add(death_place)
                break

# From wikipedia-birthplaces
for name, place in WP_BIRTHPLACES.items():
    if isinstance(place, str) and place:
        # Find matching person
        for entry in AUTHORS:
            if entry["name"].lower() == name.lower():
                if name not in person_birth_places:
                    person_birth_places[name] = place
                    all_places.add(place)
                break

# ---- Build relations ----


def get_calling_years(org_str):
    """Extract start/end years from an org string like 'Consejero (1985-1994)'"""
    import re

    years = re.findall(r"(\d{4})", org_str)
    if len(years) >= 1:
        start = int(years[0])
        end = int(years[1]) if len(years) >= 2 else None
        return start, end
    return None, None


# Pre-compute authority metadata for all authors (Two-pass approach:
# metadata is computed here and applied regardless of which code path
# first creates the entity — preventing COUNSELOR_TO, FAMILY_RELATIONS,
# or Wikidata from creating entities without metadata.)
authority_meta_by_name = {}  # dict[str, dict]
for entry in AUTHORS:
    name = entry["name"]
    if not name:
        continue
    tier = "erudito_sud"
    label = "Erudito SUD"
    score = 40
    for calling in entry.get("callings", []):
        ctype = calling.get("calling", "")
        if ctype in CALLING_TO_AUTHORITY:
            t, l, s = CALLING_TO_AUTHORITY[ctype]
            if s > score or (s == score and t == "autoridad_general"):
                tier, label, score = t, l, s
    meta: dict = {
        "authority_tier": tier,
        "authority_label": label,
        "authority_score": score,
    }
    by = entry.get("birthYear", "")
    dy = entry.get("deathYear", "")
    if by:
        meta["birth_year"] = int(by) if isinstance(by, (int, str)) and str(by).isdigit() else by
    if dy:
        meta["death_year"] = int(dy) if isinstance(dy, (int, str)) and str(dy).isdigit() else dy
    authority_meta_by_name[name] = meta


def _make_entity(name, etype="person", aliases=None):
    """Create entity dict, attaching metadata if available."""
    ent = {"name": name, "type": etype, "aliases": aliases or []}
    if etype == "person" and name in authority_meta_by_name:
        ent["metadata"] = authority_meta_by_name[name]
    return ent


entities = []  # person entities
role_entities = {}  # role/council entities by name
place_entities = {}  # place entities by name
relations = []
seen_entities = set()
seed_person_count = 0

for entry in AUTHORS:
    name = entry["name"]
    if not name:
        continue

    # Collect aliases
    aliases = []
    desc_en = entry.get("description_en", "")
    if desc_en:
        # Extract short name from description like "17th President..."
        import re

        m = re.match(r"^(\w[\w\s]+?)(?:,|$)", desc_en)
        if m and m.group(1).strip() != name and len(m.group(1).strip()) > 3:
            aliases.append(m.group(1).strip())
    birth_name = entry.get("birthName", "")
    if isinstance(birth_name, dict):
        birth_name = birth_name.get("text", "")
    if birth_name and birth_name != name and birth_name not in aliases:
        aliases.append(birth_name)

    # Create entity (metadata from pre-computed authority_meta_by_name)
    if name not in seen_entities:
        entities.append(_make_entity(name, aliases=aliases[:5]))
        seen_entities.add(name)
        seed_person_count += 1

    # Process callings
    for calling in entry.get("callings", []):
        ctype = calling.get("calling", "")
        org = calling.get("org", "")

        role_info = CALLING_TO_ROLE.get(ctype)
        if role_info:
            role_name, role_type = role_info
            if role_name not in role_entities:
                role_entities[role_name] = role_type

            call_props = {}
            c_start = calling.get("start")
            c_end = calling.get("end")
            if c_start:
                call_props["year"] = c_start
            if c_end:
                call_props["year_end"] = c_end
            relations.append(
                {
                    "subject": name,
                    "subject_type": "person",
                    "predicate": "CALLED_AS",
                    "object": role_name,
                    "object_type": role_type,
                    "source_ref": org,
                    "properties": call_props,
                }
            )

        # Extract counselor relationships from org descriptions
        if ctype in ("consejero-primera-presidencia", "consejero-asistente-pp"):
            import re

            # Use calling start/end fields (more reliable than parsing org)
            c_start = calling.get("start")
            c_end = calling.get("end")

            # Strategy 1: Extract president's name from parenthetical in org
            pres_name_found = None
            paren_match = re.search(r"\(([^)]+)\)", org)
            if paren_match:
                candidate = paren_match.group(1).strip()
                if not re.match(r"^\d{4}[\s–-]*\d*$", candidate) and candidate not in (
                    "sostenido pero no apartado",
                    "1832",
                ):
                    for pres_name, _, _ in PRESIDENT_TERMS:
                        if pres_name in candidate:
                            pres_name_found = pres_name
                            break

            if pres_name_found:
                # Single known president
                matched_presidents = [pres_name_found]
            elif c_start:
                # Strategy 2: Match ALL presidents whose terms overlap with counselor tenure
                cs = c_start
                ce = c_end if c_end else 2030
                matched_presidents = []
                for pres_name, pstart, pend in PRESIDENT_TERMS:
                    if cs < pend and ce > pstart:
                        matched_presidents.append(pres_name)
            else:
                matched_presidents = []

            for pres_name in matched_presidents:
                if pres_name == name:
                    continue  # skip self-reference
                if pres_name not in seen_entities:
                    entities.append(_make_entity(pres_name))
                    seen_entities.add(pres_name)
                rel = {
                    "subject": name,
                    "subject_type": "person",
                    "predicate": "COUNSELOR_TO",
                    "object": pres_name,
                    "object_type": "person",
                    "source_ref": org,
                }
                if rel not in relations:
                    relations.append(rel)

# ---- Place entities ----
for place in sorted(all_places):
    if place and place not in place_entities:
        aliases = []
        # Add simpler versions
        parts = place.split(", ")
        if len(parts) >= 2:
            aliases.append(parts[0])
        place_entities[place] = {
            "name": place,
            "type": "place",
            "aliases": aliases,
        }

# ---- Birth/death relations ----
for name, place in person_birth_places.items():
    if place in place_entities:
        relations.append(
            {
                "subject": name,
                "subject_type": "person",
                "predicate": "BORN_IN",
                "object": place,
                "object_type": "place",
            }
        )

for name, place in person_death_places.items():
    if place in place_entities:
        relations.append(
            {
                "subject": name,
                "subject_type": "person",
                "predicate": "DIED_IN",
                "object": place,
                "object_type": "place",
            }
        )

# ---- Wikidata enrichment: spouses, family, nationality ----
WD_ENRICHMENT_PATH = os.path.join(WP_BC, "bin", "wikidata-enrichment.json")
WD_SPOUSES_PATH = os.path.join(WP_BC, "bin", "wikidata-spouses-resolved.json")

if os.path.exists(WD_ENRICHMENT_PATH):
    with open(WD_ENRICHMENT_PATH, "r", encoding="utf-8") as f:
        WD_ENRICHMENT = json.load(f)
    print(f"Loaded Wikidata enrichment for {len(WD_ENRICHMENT)} QIDs")
else:
    WD_ENRICHMENT = {}

# Slug -> QID mapping from per-person wikidata files
import glob

slug_to_qid = {}
for wd_file in glob.glob(os.path.join(WP_BC, "corpus", "personajes", "*", "wikidata.json")):
    try:
        with open(wd_file, "r", encoding="utf-8") as f:
            wd = json.load(f)
        qid = wd.get("qid", "")
        slug = os.path.basename(os.path.dirname(wd_file))
        if qid and slug:
            slug_to_qid[slug] = qid
    except:
        pass

# Build name -> qid lookup from authors
name_to_qid = {}
for entry in AUTHORS:
    slug = entry.get("name", "").lower().replace(" ", "-").replace(".", "")
    if slug in slug_to_qid:
        name_to_qid[entry["name"]] = slug_to_qid[slug]

# QID -> name (from enrichment labels)
qid_to_name = {}
for qid, data in WD_ENRICHMENT.items():
    label = data.get("label", "")
    if label and label != "UNKNOWN":
        qid_to_name[qid] = label
# Also add from authors-enriched
for name, qid in name_to_qid.items():
    qid_to_name[qid] = name

# Spouses from wikidata-claims.json
if os.path.exists(WD_SPOUSES_PATH):
    with open(WD_SPOUSES_PATH, "r", encoding="utf-8") as f:
        wd_spouse_names = json.load(f)
else:
    wd_spouse_names = {}

with open(os.path.join(WP_BC, "bin", "wikidata-claims.json"), "r", encoding="utf-8") as f:
    WD_CLAIMS_FULL = json.load(f)

spouse_relations_added = 0
for c in WD_CLAIMS_FULL:
    slug = c.get("slug", "")
    if c.get("spouses"):
        # Find the person name from slug
        person_name = None
        for entry in AUTHORS:
            if entry["name"].lower().replace(" ", "-").replace(".", "") == slug.lower().replace(
                ".", ""
            ).replace(" ", "-"):
                person_name = entry["name"]
                break
        if not person_name:
            continue
        for s in c["spouses"]:
            sq = s.get("spouseQid", "")
            spouse_name = None
            if sq:
                # Resolve from enrichment, wd_spouse_names, or per-person files
                if sq in qid_to_name:
                    spouse_name = qid_to_name[sq]
                elif sq in wd_spouse_names:
                    spouse_name = wd_spouse_names[sq]
                elif sq in slug_to_qid.values():
                    # Find by reverse lookup
                    for slug2, qid2 in slug_to_qid.items():
                        if qid2 == sq:
                            # Find name from AUTHORS
                            for entry in AUTHORS:
                                if (
                                    entry["name"].lower().replace(" ", "-").replace(".", "")
                                    == slug2
                                ):
                                    spouse_name = entry["name"]
                                    break
                            break
            if not spouse_name:
                continue
            # Ensure both entities exist
            if person_name not in seen_entities:
                entities.append(_make_entity(person_name))
                seen_entities.add(person_name)
            if spouse_name not in seen_entities:
                entities.append(_make_entity(spouse_name))
                seen_entities.add(spouse_name)
            relations.append(
                {
                    "subject": person_name,
                    "subject_type": "person",
                    "predicate": "SPOUSE_OF",
                    "object": spouse_name,
                    "object_type": "person",
                    "source_ref": "wikidata",
                }
            )
            spouse_relations_added += 1

print(f"Added {spouse_relations_added} SPOUSE_OF relations from Wikidata")

# Family relations from wikidata-enrichment.json (father, mother, children, siblings)
family_qid_relations = []  # (subj_qid, pred, obj_qid, source_ref)
for qid, data in WD_ENRICHMENT.items():
    name = qid_to_name.get(qid, "")
    if not name:
        continue
    if data.get("father"):
        f = data["father"]
        fname = qid_to_name.get(f.get("qid", ""), f.get("label", ""))
        if fname and fname != "UNKNOWN":
            family_qid_relations.append((qid, "FATHER_OF", f["qid"], fname))
    if data.get("mother"):
        m = data["mother"]
        mname = qid_to_name.get(m.get("qid", ""), m.get("label", ""))
        if mname and mname != "UNKNOWN":
            family_qid_relations.append((qid, "MOTHER_OF", m["qid"], mname))
    if data.get("children"):
        for c in data["children"]:
            cname = qid_to_name.get(c.get("qid", ""), c.get("label", ""))
            if cname and cname != "UNKNOWN":
                family_qid_relations.append((qid, "CHILD_OF", c["qid"], cname))
    if data.get("siblings"):
        for s in data["siblings"]:
            sname = qid_to_name.get(s.get("qid", ""), s.get("label", ""))
            if sname and sname != "UNKNOWN":
                family_qid_relations.append((qid, "SIBLING_OF", s["qid"], sname))

family_relations_added = 0
for subj_qid, pred, obj_qid, obj_name in family_qid_relations:
    subj_name = qid_to_name.get(subj_qid, "")
    if not subj_name:
        continue
    if subj_name not in seen_entities:
        entities.append(_make_entity(subj_name))
        seen_entities.add(subj_name)
    if obj_name not in seen_entities:
        entities.append(_make_entity(obj_name))
        seen_entities.add(obj_name)
    relations.append(
        {
            "subject": subj_name,
            "subject_type": "person",
            "predicate": pred,
            "object": obj_name,
            "object_type": "person",
            "source_ref": "wikidata",
        }
    )
    family_relations_added += 1

print(f"Added {family_relations_added} family relations from wikidata-enrichment.json")

# Nationality relations from wikidata-enrichment.json
nationality_countries = {}  # normalized name -> canonical name
nationality_relations_added = 0
for qid, data in WD_ENRICHMENT.items():
    name = qid_to_name.get(qid, "")
    if not name:
        continue
    if data.get("nationality"):
        for n in data["nationality"]:
            country_name = n.get("label", "")
            if country_name and country_name != "UNKNOWN":
                if country_name not in seen_entities:
                    entities.append({"name": country_name, "type": "country", "aliases": []})
                    seen_entities.add(country_name)
                relations.append(
                    {
                        "subject": name,
                        "subject_type": "person",
                        "predicate": "NATIONALITY",
                        "object": country_name,
                        "object_type": "country",
                        "source_ref": "wikidata",
                    }
                )
                nationality_relations_added += 1

print(f"Added {nationality_relations_added} NATIONALITY relations from wikidata")

# Birth/death dates and images — export as bridge-data.json for the bridge script
bridge_data = {}
for entry in AUTHORS:
    name = entry["name"]
    slug = name.lower().replace(" ", "-").replace(".", "")
    qid = slug_to_qid.get(slug, "")
    img = entry.get("image", "")
    birth_year = entry.get("birthYear", "")
    death_year = entry.get("deathYear", "")

    # Try per-person wikidata.json for more precise dates
    wd_path = os.path.join(WP_BC, "corpus", "personajes", slug, "wikidata.json")
    wd_birth = ""
    wd_death = ""
    wd_image = ""
    if os.path.exists(wd_path):
        try:
            with open(wd_path, "r", encoding="utf-8") as f:
                wd = json.load(f)
            bd = wd.get("birthDate")
            dd = wd.get("deathDate")
            wd_image = wd.get("image", "")
            if bd:
                wd_birth = str(bd)
            if dd:
                wd_death = str(dd)
        except:
            pass

    if name:
        bridge_data[name] = {
            "birth_date": str(birth_year) if birth_year else wd_birth,
            "death_date": str(death_year) if death_year else wd_death,
            "image": img or wd_image,
            "qid": qid or "",
        }

bridge_path = os.path.join(SEEDS_DIR, "bridge-data.json")
with open(bridge_path, "w", encoding="utf-8") as f:
    json.dump(bridge_data, f, indent=2, ensure_ascii=False)
print(f"Wrote {bridge_path}: {len(bridge_data)} entries for bridge script")

# ---- Event entities for biographical milestones ----
event_entities = []
event_relations = []
event_entity_names = set()

for entry in AUTHORS:
    name = entry["name"]
    if not name:
        continue
    birth_year = entry.get("birthYear", "")
    death_year = entry.get("deathYear", "")

    if birth_year:
        try:
            by_val = int(birth_year) if str(birth_year).isdigit() else birth_year
        except (ValueError, TypeError):
            by_val = birth_year
        evt_name = f"Birth of {name} ({by_val})"
        if evt_name not in event_entity_names and name in seen_entities:
            event_entity_names.add(evt_name)
            event_entities.append({"name": evt_name, "type": "event", "aliases": []})
            event_relations.append(
                {
                    "subject": evt_name,
                    "subject_type": "event",
                    "predicate": "BIRTH_OF",
                    "object": name,
                    "object_type": "person",
                    "properties": {"year": int(by_val)} if isinstance(by_val, int) else {},
                }
            )

    if death_year:
        try:
            dy_val = int(death_year) if str(death_year).isdigit() else death_year
        except (ValueError, TypeError):
            dy_val = death_year
        evt_name = f"Death of {name} ({dy_val})"
        if evt_name not in event_entity_names and name in seen_entities:
            event_entity_names.add(evt_name)
            event_entities.append({"name": evt_name, "type": "event", "aliases": []})
            event_relations.append(
                {
                    "subject": evt_name,
                    "subject_type": "event",
                    "predicate": "DEATH_OF",
                    "object": name,
                    "object_type": "person",
                    "properties": {"year": int(dy_val)} if isinstance(dy_val, int) else {},
                }
            )

print(f"Generated {len(event_entities)} biographical events ({len(event_relations)} relations)")

# ---- Family relations (hardcoded) ----
for subj, pred, obj, obj_type in FAMILY_RELATIONS:
    if subj not in seen_entities:
        entities.append(_make_entity(subj))
        seen_entities.add(subj)
    if obj not in seen_entities:
        entities.append(_make_entity(obj))
        seen_entities.add(obj)
    relations.append(
        {
            "subject": subj,
            "subject_type": "person",
            "predicate": pred,
            "object": obj,
            "object_type": obj_type,
            "source_ref": "Church history records",
        }
    )

# ---- President SUCCESSOR_OF ----
for i in range(1, len(PRESIDENTS)):
    if PRESIDENTS[i - 1] not in seen_entities:
        entities.append(_make_entity(PRESIDENTS[i - 1]))
        seen_entities.add(PRESIDENTS[i - 1])
    if PRESIDENTS[i] not in seen_entities:
        entities.append(_make_entity(PRESIDENTS[i]))
        seen_entities.add(PRESIDENTS[i])
    relations.append(
        {
            "subject": PRESIDENTS[i],
            "subject_type": "person",
            "predicate": "SUCCESSOR_OF",
            "object": PRESIDENTS[i - 1],
            "object_type": "person",
            "source_ref": f"President of the Church, {PRESIDENT_TERMS[i][1]}-{PRESIDENT_TERMS[i][2]}",
        }
    )

# ---- Output seed files ----

os.makedirs(SEEDS_DIR, exist_ok=True)

# Add role/council entities to main list
for role_name, role_type in role_entities.items():
    if role_name not in seen_entities:
        entities.append(
            {
                "name": role_name,
                "type": role_type,
                "aliases": [],
            }
        )
        seen_entities.add(role_name)

# 1. Main general-authorities seed file
output = {
    "name": "General Authorities and Church Leaders — biographical entities",
    "confidence": "curated",
    "description": f"All {seed_person_count} persons from wp_bc authors-enriched.json with calling, birth/death, family, and succession relations. Generated from wp_bc structured data.",
    "entities": entities,
    "relations": relations,
}

path = os.path.join(SEEDS_DIR, "general-authorities.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"Wrote {path}: {len(entities)} entities, {len(relations)} relations")

# 2. Place entities
place_output = {
    "name": "Biographical places — birth/death locations for church leaders",
    "confidence": "curated",
    "description": f"All {len(place_entities)} places referenced in biographical data",
    "entities": list(place_entities.values()),
    "relations": [],
}

path = os.path.join(SEEDS_DIR, "general-authorities-places.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(place_output, f, indent=2, ensure_ascii=False)
print(f"Wrote {path}: {len(place_entities)} place entities")

# 3. Biographical events seed file
event_output = {
    "name": "Biographical events — birth and death milestones",
    "confidence": "curated",
    "description": f"Birth and death events for {len(event_entities)} persons",
    "entities": event_entities,
    "relations": event_relations,
}
path = os.path.join(SEEDS_DIR, "biographical-events.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(event_output, f, indent=2, ensure_ascii=False)
print(f"Wrote {path}: {len(event_entities)} event entities, {len(event_relations)} relations")

# 4. Gazetteer entries for entities.json
gazetteer_entries = {}
for ent in entities:
    name = ent["name"]
    if name not in gazetteer_entries:
        gazetteer_entries[name] = {
            "name": name,
            "type": "person",
            "id": name.lower().replace(" ", "-").replace(".", ""),
            "aliases": ent.get("aliases", []),
        }

gazetteer_path = os.path.join(r"C:\own\alejandria\data", "gazetteer-extra.json")
with open(gazetteer_path, "w", encoding="utf-8") as f:
    json.dump(list(gazetteer_entries.values()), f, indent=2, ensure_ascii=False)
print(f"Wrote {gazetteer_path}: {len(gazetteer_entries)} entries for gazetteer merge")

# Stats
print(f"\nStats:")
print(f"  Person entities: {len(entities)}")
print(f"  Event entities: {len(event_entities)}")
print(f"  Role/council entities: {len(role_entities)}")
print(f"  Place entities: {len(place_entities)}")
print(f"  Total relations (general-authorities): {len(relations)}")
print(f"  Total relations (events): {len(event_relations)}")

# Count by type
rel_counts = defaultdict(int)
for r in relations:
    rel_counts[r["predicate"]] += 1
for rtype, count in sorted(rel_counts.items(), key=lambda x: -x[1]):
    print(f"    {rtype}: {count}")

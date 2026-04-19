"""Fix the earlier `_pg_seed_paronyms.py` pass.

Three categories got conflated under "paronyms". Only TRUE paronyms
belong in entity_aliases as name-variant links. Disambiguators (parenthetical
modifiers distinguishing two distinct people with the same bare name) must
NOT be treated as aliases — collapsing them would merge e.g. Alma Sr.
with Alma the Younger.

This script:
  1. Removes dangerous disambiguator aliases that were seeded by mistake.
  2. Keeps the genuine paronyms (Abram→Abraham, etc.) and bilingual
     transliterations (Moses↔Moisés, Nephi↔Nefi, etc.) — both are legit
     canonicalization targets.
  3. Re-classifies the remaining seeds into paronym / bilingual for
     auditing.

Idempotent.
"""
import os
import psycopg

# Aliases that must be REMOVED — they conflate distinct persons.
DANGEROUS_ALIASES_TO_REMOVE = [
    # Alma Sr. vs Alma the Younger are two different people.
    ("Alma", "Alma the Younger"),
    ("Alma", "Alma el Joven"),
    ("Alma", "Alma hijo de Alma"),
    # "Moroni" alone vs "Moroni (son of Mormon)" — the bare "Moroni" is
    # ambiguous (Captain Moroni is a different Moroni). Don't auto-resolve.
    ("Moroni", "Moroni (son of Mormon)"),
    # "Isaac"/"Jacob"/"Joseph (son of Jacob)" etc. — the parenthetical form
    # is a DISAMBIGUATOR, not an alias. A bare "Isaac" should remain
    # ambiguous (there may be other Isaacs in the corpus — Isaac Watts,
    # Isaac Newton references in manuals, etc.).
    ("Isaac", "Isaac (son of Abraham)"),
    ("Jacob", "Jacob (son of Isaac)"),
    ("Joseph", "Joseph (son of Jacob)"),
    ("Mary", "Mary (mother of Jesus)"),
]

# Categorization of remaining seeds, for documentation / audit.
TRUE_PARONYMS = {
    # Name-change events in scripture
    ("Abraham", "Abram"),
    ("Sarah", "Sarai"),
    ("Israel", "Jacob"),           # Gen 32:28 new name
    ("Paul", "Saul"),              # Acts 13:9 renamed
    # Onomastic reconciliation (Esau's wives in Gen 26/28/36)
    ("Basemath", "Mahalath"),
    ("Adah", "Basemath (wife of Esau)"),
    ("Oholibamah", "Judith"),
    # Greek/Aramaic names for the same person
    ("Peter", "Cephas"),
    ("Peter", "Simon Peter"),
}
BILINGUAL_TRANSLITERATIONS = {
    # Spanish renderings (accents, phonetic adaptation)
    ("Paul", "Saulo"),
    ("Peter", "Simón Pedro"),
    ("Peter", "Cefas"),
    ("Moses", "Moisés"),
    ("Noah", "Noé"),
    ("Joseph", "José"),
    ("Mary", "María"),
    ("Jesus", "Jesús"),
    ("Jesus", "Jesus Christ"),
    ("Jesus", "Jesucristo"),
    ("Nephi", "Nefi"),
    ("Lehi", "Lehí"),
    ("Mormon", "Mormón"),
    ("Basemath", "Basmat"),
    ("Amaleki", "Amalekí"),
    ("Abinadom", "Abinádom"),
    ("Chemish", "Quemis"),
}


with psycopg.connect(
    host=os.environ["ALEJANDRIA_POSTGRES_HOST"],
    port=int(os.environ["ALEJANDRIA_POSTGRES_PORT"]),
    user=os.environ["ALEJANDRIA_POSTGRES_USER"],
    password=os.environ["ALEJANDRIA_POSTGRES_PASSWORD"],
    dbname=os.environ["ALEJANDRIA_POSTGRES_DB"],
) as c:
    # Remove dangerous aliases
    removed = 0
    for canonical, bad_alias in DANGEROUS_ALIASES_TO_REMOVE:
        row = c.execute(
            "SELECT id FROM entities WHERE name = %s LIMIT 1", (canonical,)
        ).fetchone()
        if not row:
            continue
        cur = c.execute(
            "DELETE FROM entity_aliases "
            "WHERE entity_id = %s AND alias = %s",
            (row[0], bad_alias),
        )
        if cur.rowcount:
            removed += cur.rowcount
            print(f"  removed dangerous alias: {bad_alias!r} → {canonical!r}")
    c.commit()

    print(f"\nRemoved {removed} disambiguator-as-alias entries.\n")

    # Report remaining by category
    all_rows = c.execute(
        "SELECT e.name, ea.alias FROM entity_aliases ea "
        "JOIN entities e ON e.id = ea.entity_id "
        "WHERE ea.alias = ANY(%s)",
        ([a for _, a in TRUE_PARONYMS | BILINGUAL_TRANSLITERATIONS],),
    ).fetchall()

    paronyms_present = {(n, a) for n, a in all_rows
                         if (n, a) in TRUE_PARONYMS}
    bilingual_present = {(n, a) for n, a in all_rows
                          if (n, a) in BILINGUAL_TRANSLITERATIONS}

    print(f"True paronyms in DB:       {len(paronyms_present):>3} "
          f"/ {len(TRUE_PARONYMS)}")
    print(f"Bilingual translit in DB:  {len(bilingual_present):>3} "
          f"/ {len(BILINGUAL_TRANSLITERATIONS)}")
    print("\n=== Sample alias verification ===")
    for row in c.execute(
        "SELECT e.name, ea.alias FROM entity_aliases ea "
        "JOIN entities e ON e.id = ea.entity_id "
        "WHERE ea.alias IN ('Abram','Sarai','Quemis','Moisés','Cephas','Saul') "
        "ORDER BY ea.alias"
    ).fetchall():
        print(f"  {row[1]!r} → {row[0]!r}")

"""Seed entity_aliases with well-known biblical paronyms — cases where
the same person appears under multiple names (renames, Greek/Hebrew
doubles, onomastic reconciliation like Esau's wives).

Only pairs well-attested in scripture or universally accepted by LDS/
Christian commentary are added. Anything requiring theological or
text-critical judgment stays out of the seed; those belong in
docs/ as curated decisions.

Idempotent: uses ON CONFLICT DO NOTHING.
"""
import os
import psycopg

# (canonical_name, [aliases]) — canonical is what gets kept; aliases
# get added to entity_aliases pointing at the canonical's id.
PARONYM_SEEDS: list[tuple[str, list[str]]] = [
    # Name-change events in the text itself
    ("Abraham", ["Abram"]),
    ("Sarah", ["Sarai"]),
    ("Israel", ["Jacob"]),            # Gen 32:28 — "Israel" as new name
    ("Paul", ["Saul", "Saulo"]),      # Acts 13:9 — renamed post-conversion
    ("Peter", ["Simon Peter", "Cephas", "Simón Pedro", "Cefas"]),
    # Esau's wives — three listings, reconciled by assuming each woman
    # had multiple names (Gen 26:34, 28:9, 36:2-3)
    ("Basemath", ["Mahalath", "Basmat"]),
    ("Adah", ["Basemath (wife of Esau)"]),
    ("Oholibamah", ["Judith"]),
    # Common EN/ES transliteration pairs for core scripture figures
    ("Moses", ["Moisés"]),
    ("Noah", ["Noé"]),
    ("Isaac", ["Isaac (son of Abraham)"]),
    ("Jacob", ["Jacob (son of Isaac)"]),
    ("Joseph", ["José", "Joseph (son of Jacob)"]),
    ("Mary", ["María", "Mary (mother of Jesus)"]),
    ("Jesus", ["Jesús", "Jesus Christ", "Jesucristo"]),
    # BoM figures with Spanish/English doublets or epithets
    ("Nephi", ["Nefi"]),
    ("Lehi", ["Lehí"]),
    ("Mormon", ["Mormón"]),
    ("Moroni", ["Moroni (son of Mormon)"]),
    ("Alma", ["Alma the Younger", "Alma el Joven", "Alma hijo de Alma"]),
    ("Amaleki", ["Amalekí"]),
    ("Abinadom", ["Abinádom"]),
    ("Chemish", ["Quemis"]),
]

with psycopg.connect(
    host=os.environ["ALEJANDRIA_POSTGRES_HOST"],
    port=int(os.environ["ALEJANDRIA_POSTGRES_PORT"]),
    user=os.environ["ALEJANDRIA_POSTGRES_USER"],
    password=os.environ["ALEJANDRIA_POSTGRES_PASSWORD"],
    dbname=os.environ["ALEJANDRIA_POSTGRES_DB"],
) as c:
    added = 0
    missing_canonical = 0
    missing_aliases = 0

    for canonical, aliases in PARONYM_SEEDS:
        # Resolve canonical to an entity_id (prefer type=person).
        row = c.execute(
            "SELECT id FROM entities WHERE name = %s "
            "ORDER BY CASE entity_type WHEN 'person' THEN 0 "
            "  WHEN 'people' THEN 1 ELSE 2 END LIMIT 1",
            (canonical,),
        ).fetchone()
        if not row:
            missing_canonical += 1
            print(f"  canonical not found: {canonical!r}")
            continue
        canonical_id = row[0]

        for alias in aliases:
            # Insert alias; skip if already present.
            # entity_aliases schema: (entity_id, alias)
            cur = c.execute(
                "INSERT INTO entity_aliases (entity_id, alias) "
                "VALUES (%s, %s) "
                "ON CONFLICT DO NOTHING",
                (canonical_id, alias),
            )
            if cur.rowcount:
                added += 1
            else:
                # Could be a duplicate OR the alias was never there.
                # We don't distinguish here.
                missing_aliases += 1

    c.commit()
    total_attempted = sum(len(a) for _, a in PARONYM_SEEDS)
    print(f"\nSeeded {added}/{total_attempted} paronym aliases")
    print(f"Canonicals not found in entities: {missing_canonical}")
    print(f"Aliases already present (or skipped): {missing_aliases}")

    # Verify
    sample = c.execute(
        "SELECT e.name, ea.alias "
        "FROM entity_aliases ea JOIN entities e ON e.id = ea.entity_id "
        "WHERE ea.alias IN ('Abram','Sarai','Jacob','Nefi','Quemis','Moisés') "
        "ORDER BY e.name"
    ).fetchall()
    print("\nSample of seeded aliases now queryable:")
    for name, alias in sample:
        print(f"  {alias!r} → {name!r}")

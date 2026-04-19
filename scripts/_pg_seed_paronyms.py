"""Seed entity_aliases with name-variant links that are safe to collapse.

Two legitimate categories handled here:

    1. **True paronyms** — two genuinely distinct names for the same
       person (scriptural renaming events, Greek/Aramaic doublets,
       onomastic reconciliation across parallel listings).
       Examples: Abram → Abraham (Gen 17:5), Sarai → Sarah (Gen 17:15),
       Jacob / Israel (Gen 32:28), Saul / Paul (Acts 13:9),
       Simon / Cephas / Peter, Mahalath / Basemath (Esau's wives
       reconciled across Gen 26:34, 28:9, 36:2-3).

    2. **Bilingual transliterations** — same underlying name rendered
       in English and Spanish orthography. These are phonetic variants
       of one name, not different names. Examples: Moses ↔ Moisés,
       Nephi ↔ Nefi, Chemish ↔ Quemis, Amaleki ↔ Amalekí, Lehi ↔ Lehí.

**What MUST NOT go in entity_aliases:** disambiguators. A phrase like
'Alma the Younger' or 'Moroni (son of Mormon)' is NOT a name-variant of
the bare 'Alma' / 'Moroni' — it's a parenthetical that distinguishes
two distinct people sharing the same bare name. Collapsing them merges
father with son (Alma Sr. with Alma Jr.) or confuses the Captain Moroni
with the prophet-editor Moroni. See `_pg_fix_paronyms.py` for the
cleanup that removed an earlier mistaken batch of these.

Idempotent: uses ON CONFLICT DO NOTHING.
"""
import os
import psycopg

# (canonical_name, [aliases]) — canonical is what gets kept; aliases
# get added to entity_aliases pointing at the canonical's id.
#
# Mixed here for convenience; each entry falls into one of TWO safe
# categories (paronym / bilingual). Disambiguators like "Alma the
# Younger" or "X (son of Y)" are INTENTIONALLY absent — see module
# docstring.
PARONYM_SEEDS: list[tuple[str, list[str]]] = [
    # ── TRUE PARONYMS (distinct names, same referent) ────────────────
    ("Abraham", ["Abram"]),               # Gen 17:5 rename
    ("Sarah", ["Sarai"]),                 # Gen 17:15 rename
    ("Israel", ["Jacob"]),                # Gen 32:28 rename
    ("Paul", ["Saul"]),                   # Acts 13:9 rename
    ("Peter", ["Simon Peter", "Cephas"]), # Greek/Aramaic doublets
    # Esau's wives — Gen 26:34, 28:9, 36:2-3 reconciled by assuming
    # each wife had multiple names.
    ("Basemath", ["Mahalath"]),
    ("Adah", ["Basemath (wife of Esau)"]),
    ("Oholibamah", ["Judith"]),

    # ── BILINGUAL TRANSLITERATIONS (same name, EN↔ES spelling) ───────
    ("Paul", ["Saulo"]),
    ("Peter", ["Simón Pedro", "Cefas"]),
    ("Moses", ["Moisés"]),
    ("Noah", ["Noé"]),
    ("Joseph", ["José"]),
    ("Mary", ["María"]),
    ("Jesus", ["Jesús", "Jesus Christ", "Jesucristo"]),
    ("Nephi", ["Nefi"]),
    ("Lehi", ["Lehí"]),
    ("Mormon", ["Mormón"]),
    ("Basemath", ["Basmat"]),
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

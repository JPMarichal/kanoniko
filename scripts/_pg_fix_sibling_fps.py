"""Retroactively remove false-positive BROTHER_OF / SISTER_OF edges from
Postgres (and the FATHER_OF edges that were inferred downstream from them),
then re-extract and re-infer with the hardened family_patterns module.

Strategy:
  1. Delete ALL family_pattern_backfill BROTHER_OF/SISTER_OF whose endpoints
     fail the hardened `_is_person_candidate` check, or whose names are
     substrings of each other, or whose right-hand side equals 'Jared'
     (the BoM epithet cascade).
  2. Delete ALL family_inference edges (FATHER_OF, MOTHER_OF, BROTHER/SISTER)
     sourced as 'family_inference' — we'll regenerate them cleanly.
  3. Caller should then re-run: `--stage family --apply` and `--stage infer
     --apply` to repopulate with the hardened patterns.
"""
import os, sys, psycopg

sys.path.insert(0, "/repo/src")
from alejandria.knowledge.family_patterns import _is_person_candidate

FAMILY_RELS_INFERABLE = ("BROTHER_OF", "SISTER_OF", "FATHER_OF", "MOTHER_OF", "SPOUSE_OF")

with psycopg.connect(
    host=os.environ["ALEJANDRIA_POSTGRES_HOST"],
    port=int(os.environ["ALEJANDRIA_POSTGRES_PORT"]),
    user=os.environ["ALEJANDRIA_POSTGRES_USER"],
    password=os.environ["ALEJANDRIA_POSTGRES_PASSWORD"],
    dbname=os.environ["ALEJANDRIA_POSTGRES_DB"],
) as c:
    # --- Step 1: identify FP BROTHER_OF/SISTER_OF to delete ----------------
    print("Scanning BROTHER_OF/SISTER_OF for FP patterns...")
    rows = c.execute("""
        SELECT r.id, s.name, d.name, r.rel_type
        FROM relations r
        JOIN entities s ON s.id = r.src_id
        JOIN entities d ON d.id = r.dst_id
        WHERE r.rel_type IN ('BROTHER_OF', 'SISTER_OF')
          AND r.source = 'family_pattern_backfill'
    """).fetchall()

    fp_ids = []
    for rid, src, dst, rel in rows:
        if not src or not dst:
            fp_ids.append(rid)
            continue
        # Hardening rule 1: non-person (ALL CAPS, place prefix, title)
        if not _is_person_candidate(src) or not _is_person_candidate(dst):
            fp_ids.append(rid)
            continue
        # Rule 2: substring = same-person fragment
        sl, dl = src.lower(), dst.lower()
        if sl != dl and (sl in dl or dl in sl):
            fp_ids.append(rid)
            continue
        # Rule 3: 'Jared' epithet cascade (BoM)
        if dst == "Jared":
            fp_ids.append(rid)

    print(f"  total BROTHER/SISTER edges: {len(rows):,}")
    print(f"  FP matches: {len(fp_ids):,} ({100*len(fp_ids)/max(len(rows),1):.0f}%)")

    if fp_ids:
        # Delete in batches
        for i in range(0, len(fp_ids), 5000):
            batch = fp_ids[i:i + 5000]
            c.execute("DELETE FROM relations WHERE id = ANY(%s)", (batch,))
        print(f"  deleted {len(fp_ids):,} FP sibling edges")

    # --- Step 2: wipe all family_inference edges (will regenerate cleanly)  -
    cur = c.execute(
        "DELETE FROM relations "
        "WHERE source = 'family_inference' "
        "  AND rel_type = ANY(%s)",
        (list(FAMILY_RELS_INFERABLE),),
    )
    print(f"  deleted {cur.rowcount:,} family_inference edges (regenerate next)")

    c.commit()
    print("\nFinal pre-regeneration family counts:")
    for rel, n in c.execute(
        "SELECT rel_type, count(*) FROM relations WHERE rel_type = ANY(%s) "
        "GROUP BY rel_type ORDER BY rel_type",
        (list(FAMILY_RELS_INFERABLE),),
    ).fetchall():
        print(f"  {rel}: {n:,}")

"""Postgres + pgvector benchmark for Alejandria migration (Phase 1, validatorio).

Generates synthetic data matching the real corpus shape, loads it via COPY,
builds indexes, and measures query latency against the four target patterns
from the migration design doc.

Run inside a container with psycopg[binary] and numpy installed. The DB must
be reachable at the host/port configured via env vars.

Env vars:
    PG_HOST      (default: postgres)
    PG_PORT      (default: 5432)
    PG_USER      (default: bench)
    PG_PASSWORD  (default: bench)
    PG_DB        (default: alejandria_bench)
    N_CHUNKS     (default: 30000)
    N_ENTITIES   (default: 5000)
    N_RELATIONS  (default: 500000)
    EMBED_DIM    (default: 384)
    Q_ITERATIONS (default: 100)
"""
from __future__ import annotations

import io
import json
import os
import random
import statistics
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np
import psycopg
from psycopg import sql


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

PG = dict(
    host=os.environ.get("PG_HOST", "postgres"),
    port=int(os.environ.get("PG_PORT", 5432)),
    user=os.environ.get("PG_USER", "bench"),
    password=os.environ.get("PG_PASSWORD", "bench"),
    dbname=os.environ.get("PG_DB", "alejandria_bench"),
)

N_CHUNKS = int(os.environ.get("N_CHUNKS", 30_000))
N_ENTITIES = int(os.environ.get("N_ENTITIES", 5_000))
N_RELATIONS = int(os.environ.get("N_RELATIONS", 500_000))
EMBED_DIM = int(os.environ.get("EMBED_DIM", 384))
Q_ITERATIONS = int(os.environ.get("Q_ITERATIONS", 100))

RNG = np.random.default_rng(42)
random.seed(42)

REL_TYPES = [
    ("authored", "authorship"),
    ("parent_of", "family"),
    ("son_of", "family"),
    ("daughter_of", "family"),
    ("sibling_of", "family"),
    ("prophesied_of", "prophetic"),
    ("fulfilled_by", "prophetic"),
    ("traveled_to", "geographic"),
    ("ruled", "governance"),
    ("appears_in", "intertextuality"),
    ("mentions", "intertextuality"),
    ("typifies", "typology"),
    ("covenant_with", "covenants"),
    ("contemporary_of", "temporal"),
]

# Family ties are SPARSE in a biblical/LDS KG (most entities don't have extracted
# parent_of edges). Intertextuality dominates (mentions, appears_in). Weights
# reflect this so recursive CTEs on parent_of stay bounded.
REL_TYPE_WEIGHTS = [30, 3, 2, 2, 2, 5, 5, 15, 5, 80, 120, 8, 3, 15]

ENTITY_TYPES = ["person", "place", "concept", "object", "peoples", "period"]

SPANISH_WORDS = (
    "porque mas pero cuando entonces señor dios padre hijo espíritu pueblo "
    "tierra ciudad templo sacerdote profeta apóstol testimonio evangelio "
    "fe arrepentimiento bautismo don santo pacto convenio restauración "
    "revelación escrituras libro mormón josé smith nefi lehi alma helamán "
    "moroni jesucristo jerusalén tiempo generación corazón alma"
).split()

ENGLISH_WORDS = (
    "and the they shall that have which unto them who not this from with "
    "lord god father son spirit people land city temple priest prophet "
    "apostle testimony gospel faith repentance baptism gift holy covenant "
    "restoration revelation scriptures book mormon nephi lehi alma helaman "
    "moroni jesus christ jerusalem time generation heart soul"
).split()


# --------------------------------------------------------------------------- #
# Timing helpers
# --------------------------------------------------------------------------- #

@dataclass
class Timings:
    label: str
    wall_seconds: float
    rows: int = 0
    notes: str = ""

    @property
    def rows_per_sec(self) -> float:
        return self.rows / self.wall_seconds if self.wall_seconds > 0 else 0.0


@dataclass
class QueryStats:
    label: str
    iterations: int
    p50_ms: float
    p95_ms: float
    p99_ms: float
    mean_ms: float
    max_ms: float


@dataclass
class BenchmarkReport:
    config: dict
    ingestion: list[Timings] = field(default_factory=list)
    indexing: list[Timings] = field(default_factory=list)
    queries: list[QueryStats] = field(default_factory=list)
    storage: dict = field(default_factory=dict)


def timed(label: str, rows: int = 0, notes: str = ""):
    class Ctx:
        def __enter__(self):
            self.t0 = time.perf_counter()
            return self

        def __exit__(self, *exc):
            self.elapsed = time.perf_counter() - self.t0
            self.timings = Timings(label, self.elapsed, rows, notes)
            print(
                f"  [{label:40s}] {self.elapsed:7.2f}s"
                + (f"  ({rows/self.elapsed:10.0f} rows/s)" if rows else "")
                + (f"  — {notes}" if notes else "")
            )

    return Ctx()


def percentiles(samples_ms: list[float]) -> tuple[float, float, float, float, float]:
    samples_ms = sorted(samples_ms)
    n = len(samples_ms)
    return (
        samples_ms[int(0.50 * n)],
        samples_ms[int(0.95 * n)],
        samples_ms[min(int(0.99 * n), n - 1)],
        statistics.mean(samples_ms),
        samples_ms[-1],
    )


# --------------------------------------------------------------------------- #
# Synthetic data
# --------------------------------------------------------------------------- #

def gen_chunk_text(lang: str = "es") -> str:
    """Generate realistic-length pseudo-text (~150-300 tokens)."""
    pool = SPANISH_WORDS if lang == "es" else ENGLISH_WORDS
    length = random.randint(150, 300)
    return " ".join(random.choices(pool, k=length))


def gen_entity_name(i: int) -> tuple[str, str]:
    etype = random.choice(ENTITY_TYPES)
    # Names with a variety of prefixes so trigram search has something real to chew on
    prefixes = {
        "person": ["Nefi", "Alma", "Helamán", "Moroni", "José", "Jacob", "Samuel"],
        "place": ["Zarahemla", "Jerusalén", "Bountiful", "Manti", "Gadiandi"],
        "concept": ["Expiación", "Fe", "Esperanza", "Caridad", "Pacto"],
        "object": ["Liahona", "Urim", "Tumim", "Espada", "Plancha"],
        "peoples": ["Lamanitas", "Nefitas", "Jareditas", "Zoramitas"],
        "period": ["Año", "Era", "Tiempo", "Dispensación"],
    }[etype]
    name = f"{random.choice(prefixes)}-{i:05d}"
    return name, etype


def build_relations(n_entities: int, n_relations: int) -> list[tuple]:
    """Build relations with a power-law src distribution (hub-like entities)."""
    # Power-law: a few hub entities, long tail.
    weights = (1.0 / (np.arange(1, n_entities + 1))) ** 0.8
    weights /= weights.sum()
    src_ids = RNG.choice(np.arange(1, n_entities + 1), size=n_relations, p=weights)
    dst_ids = RNG.integers(1, n_entities + 1, size=n_relations)

    rels = []
    for src, dst in zip(src_ids, dst_ids):
        if src == dst:
            dst = (dst % n_entities) + 1
        rt_idx = random.choices(range(len(REL_TYPES)), weights=REL_TYPE_WEIGHTS, k=1)[0]
        rel_type, category = REL_TYPES[rt_idx]
        rels.append(
            (
                int(src),
                int(dst),
                rel_type,
                category,
                random.choice(["curated", "metadata", "llm_high", "llm_low", "ner"]),
                None,                           # source_ref
                "llm",                          # source
                False,                          # verified
                None,                           # role
                "{}",                           # properties
            )
        )
    return rels


def build_genealogy_chain(n_entities: int, depth: int = 12) -> None:
    """Returns nothing — this function is used later in SQL: we pick entities 1..depth
    and add parent_of edges to guarantee a genealogy_path test can find them."""
    return


# --------------------------------------------------------------------------- #
# Ingestion via COPY
# --------------------------------------------------------------------------- #

def copy_documents(conn: psycopg.Connection, n_docs: int) -> Timings:
    with timed("COPY document_registry", n_docs) as t:
        with conn.cursor().copy(
            "COPY document_registry (file_path, sha256, file_size, chunk_count, status) FROM STDIN"
        ) as cp:
            for i in range(n_docs):
                cp.write_row((
                    f"corpus/es/synthetic/doc_{i:06d}.txt",
                    f"{i:064x}",
                    1024 * (i % 100 + 1),
                    0,
                    "indexed",
                ))
        conn.commit()
    return t.timings


def copy_chunks(conn: psycopg.Connection, n_chunks: int, n_docs: int) -> Timings:
    with timed("COPY chunks", n_chunks) as t:
        with conn.cursor().copy(
            "COPY chunks (file_path, chunk_index, text, reference, metadata, language) "
            "FROM STDIN"
        ) as cp:
            for i in range(n_chunks):
                lang = "es" if i % 3 else "en"
                doc_idx = i % n_docs
                cp.write_row((
                    f"corpus/es/synthetic/doc_{doc_idx:06d}.txt",
                    i,
                    gen_chunk_text(lang),
                    f"Libro {doc_idx}:{i}",
                    json.dumps({"source": "synthetic", "seq": i}),
                    lang,
                ))
        conn.commit()
    return t.timings


def copy_embeddings(conn: psycopg.Connection, n_chunks: int) -> Timings:
    with timed("COPY chunk_embeddings", n_chunks) as t:
        with conn.cursor().copy(
            "COPY chunk_embeddings (chunk_id, embedding) FROM STDIN"
        ) as cp:
            for i in range(1, n_chunks + 1):
                vec = RNG.standard_normal(EMBED_DIM).astype(np.float32)
                vec /= np.linalg.norm(vec) + 1e-9
                # pgvector text format: "[v1,v2,...,vN]"
                vec_str = "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
                cp.write_row((i, vec_str))
        conn.commit()
    return t.timings


def copy_entities(conn: psycopg.Connection, n_entities: int) -> Timings:
    with timed("COPY entities", n_entities) as t:
        with conn.cursor().copy(
            "COPY entities (name, entity_type, metadata) FROM STDIN"
        ) as cp:
            for i in range(1, n_entities + 1):
                name, etype = gen_entity_name(i)
                cp.write_row((name, etype, "{}"))
        conn.commit()
    return t.timings


def copy_relations(conn: psycopg.Connection, relations: list[tuple]) -> Timings:
    with timed("COPY relations", len(relations)) as t:
        with conn.cursor().copy(
            "COPY relations (src_id, dst_id, rel_type, category, confidence, "
            "source_ref, source, verified, role, properties) FROM STDIN"
        ) as cp:
            for row in relations:
                cp.write_row(row)
        conn.commit()
    return t.timings


def seed_genealogy(conn: psycopg.Connection, depth: int = 12) -> None:
    """Force a deterministic parent_of chain 1 -> 2 -> 3 -> ... -> depth for
    a reproducible kg_genealogy_path benchmark."""
    with conn.cursor() as cur:
        for i in range(1, depth):
            cur.execute(
                "INSERT INTO relations (src_id, dst_id, rel_type, category, confidence) "
                "VALUES (%s, %s, 'parent_of', 'family', 'curated')",
                (i, i + 1),
            )
        conn.commit()


# --------------------------------------------------------------------------- #
# Index build
# --------------------------------------------------------------------------- #

def build_hnsw(conn: psycopg.Connection) -> Timings:
    with timed("CREATE INDEX hnsw (cosine)", 0, notes=f"dim={EMBED_DIM}") as t:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE INDEX chunk_embeddings_hnsw ON chunk_embeddings "
                "USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64)"
            )
        conn.commit()
    return t.timings


def analyze(conn: psycopg.Connection) -> Timings:
    with timed("ANALYZE (all tables)") as t:
        with conn.cursor() as cur:
            cur.execute("ANALYZE")
        conn.commit()
    return t.timings


# --------------------------------------------------------------------------- #
# Query benchmarks
# --------------------------------------------------------------------------- #

def run_query_bench(
    conn: psycopg.Connection,
    label: str,
    query_fn,
    iterations: int = Q_ITERATIONS,
) -> QueryStats:
    # Warm up
    for _ in range(5):
        query_fn(conn)
    samples_ms = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        query_fn(conn)
        samples_ms.append((time.perf_counter() - t0) * 1000)
    p50, p95, p99, mean, mx = percentiles(samples_ms)
    stats = QueryStats(label, iterations, p50, p95, p99, mean, mx)
    print(f"  [{label:40s}] p50={p50:6.1f}ms p95={p95:6.1f}ms p99={p99:6.1f}ms max={mx:6.1f}ms")
    return stats


def q_fts(conn):
    # Spanish phrase search — realistic user query
    term = random.choice(["profeta", "alma", "pacto", "espíritu", "pueblo",
                          "testimonio", "restauración", "evangelio"])
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, reference, ts_rank_cd(tsv, q) AS score "
            "FROM chunks, websearch_to_tsquery('spanish', %s) q "
            "WHERE tsv @@ q "
            "ORDER BY score DESC LIMIT 20",
            (term,),
        )
        cur.fetchall()


def q_semantic(conn):
    vec = RNG.standard_normal(EMBED_DIM).astype(np.float32)
    vec /= np.linalg.norm(vec) + 1e-9
    vec_str = "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
    with conn.cursor() as cur:
        cur.execute(
            "SELECT c.id, c.reference, 1 - (e.embedding <=> %s::vector) AS score "
            "FROM chunk_embeddings e JOIN chunks c ON c.id = e.chunk_id "
            "ORDER BY e.embedding <=> %s::vector LIMIT 20",
            (vec_str, vec_str),
        )
        cur.fetchall()


def q_kg_profile(conn):
    # Simulates kg_profile: entity + 1-hop relations + categories aggregated
    eid = random.randint(1, min(500, N_ENTITIES))  # hit the hub region
    with conn.cursor() as cur:
        cur.execute(
            "SELECT e.id, e.name, e.entity_type, "
            "       (SELECT json_agg(row_to_json(x)) FROM ("
            "           SELECT r.rel_type, r.category, r.confidence, "
            "                  e2.name AS target_name, e2.entity_type AS target_type "
            "           FROM relations r JOIN entities e2 ON e2.id = r.dst_id "
            "           WHERE r.src_id = e.id LIMIT 50"
            "       ) x) AS outgoing, "
            "       (SELECT count(*) FROM relations WHERE src_id = e.id) AS out_count, "
            "       (SELECT count(*) FROM relations WHERE dst_id = e.id) AS in_count "
            "FROM entities e WHERE e.id = %s",
            (eid,),
        )
        cur.fetchall()


def q_kg_neighbors(conn):
    eid = random.randint(1, min(500, N_ENTITIES))
    with conn.cursor() as cur:
        cur.execute(
            "SELECT e2.id, e2.name, r.rel_type, r.category "
            "FROM relations r JOIN entities e2 ON e2.id = r.dst_id "
            "WHERE r.src_id = %s "
            "UNION ALL "
            "SELECT e2.id, e2.name, r.rel_type, r.category "
            "FROM relations r JOIN entities e2 ON e2.id = r.src_id "
            "WHERE r.dst_id = %s "
            "LIMIT 100",
            (eid, eid),
        )
        cur.fetchall()


def q_kg_genealogy_path(conn):
    # Recursive CTE from seeded 1->2->...->12 chain; target a path ~5 hops deep.
    # Bidirectional BFS is overkill for 10 hops; a depth-limited recursive CTE
    # suffices, but MUST cap intermediate rows to avoid fan-out blowups.
    src, dst = 1, random.randint(5, 8)
    with conn.cursor() as cur:
        cur.execute(
            "WITH RECURSIVE path AS ("
            "   SELECT src_id, dst_id, ARRAY[src_id, dst_id] AS nodes, 1 AS depth "
            "   FROM relations "
            "   WHERE src_id = %s AND rel_type IN ('parent_of','son_of','daughter_of') "
            "   UNION ALL "
            "   SELECT r.src_id, r.dst_id, p.nodes || r.dst_id, p.depth + 1 "
            "   FROM relations r "
            "   JOIN path p ON r.src_id = p.dst_id "
            "   WHERE r.rel_type IN ('parent_of','son_of','daughter_of') "
            "     AND NOT r.dst_id = ANY(p.nodes) "
            "     AND p.depth < 8"
            "), capped AS (SELECT * FROM path LIMIT 5000) "
            "SELECT nodes, depth FROM capped WHERE dst_id = %s ORDER BY depth LIMIT 1",
            (src, dst),
        )
        cur.fetchall()


def q_trgm_find(conn):
    # Simulates kg_find: partial name match via trigram
    frag = random.choice(["Nef", "Alm", "Helam", "Jeru", "Bounti", "Expiac"])
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, entity_type FROM entities "
            "WHERE name ILIKE %s ORDER BY name LIMIT 20",
            (f"%{frag}%",),
        )
        cur.fetchall()


# --------------------------------------------------------------------------- #
# Storage snapshot
# --------------------------------------------------------------------------- #

def snapshot_storage(conn: psycopg.Connection) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT relname, pg_total_relation_size(oid) AS total_bytes "
            "FROM pg_class WHERE relkind = 'r' AND relnamespace = 'public'::regnamespace "
            "ORDER BY total_bytes DESC"
        )
        rows = cur.fetchall()
        cur.execute("SELECT pg_database_size(current_database())")
        db_bytes = cur.fetchone()[0]
    return {
        "db_bytes": db_bytes,
        "db_human": f"{db_bytes/1e6:.1f} MB",
        "per_table": [{"table": r[0], "bytes": r[1], "human": f"{r[1]/1e6:.1f} MB"} for r in rows],
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    print(f"Connecting to {PG['host']}:{PG['port']}/{PG['dbname']} …")
    print(
        f"Scale: {N_CHUNKS:,} chunks, {EMBED_DIM}-dim vectors, "
        f"{N_ENTITIES:,} entities, {N_RELATIONS:,} relations, "
        f"{Q_ITERATIONS} iterations/query\n"
    )

    conn = psycopg.connect(**PG, options="-c statement_timeout=10000")
    report = BenchmarkReport(config={
        "n_chunks": N_CHUNKS,
        "n_entities": N_ENTITIES,
        "n_relations": N_RELATIONS,
        "embed_dim": EMBED_DIM,
        "q_iterations": Q_ITERATIONS,
    })

    # --- Build relations ahead of time (largest dataset) ---
    print("Generating synthetic relations (in-memory) …")
    t0 = time.perf_counter()
    relations = build_relations(N_ENTITIES, N_RELATIONS)
    print(f"  {len(relations):,} relations generated in {time.perf_counter()-t0:.1f}s\n")

    # --- Phase: Ingestion ---
    print("── INGESTION ──────────────────────────────────────────────────────")
    n_docs = max(100, N_CHUNKS // 30)  # synthetic: ~30 chunks per doc
    report.ingestion.append(copy_documents(conn, n_docs))
    report.ingestion.append(copy_chunks(conn, N_CHUNKS, n_docs))
    report.ingestion.append(copy_embeddings(conn, N_CHUNKS))
    report.ingestion.append(copy_entities(conn, N_ENTITIES))
    report.ingestion.append(copy_relations(conn, relations))
    seed_genealogy(conn, depth=12)

    # --- Phase: Indexing ---
    print("\n── INDEX BUILD ────────────────────────────────────────────────────")
    report.indexing.append(build_hnsw(conn))
    report.indexing.append(analyze(conn))

    # --- Phase: Storage snapshot ---
    report.storage = snapshot_storage(conn)
    print(f"\n── STORAGE ────────────────────────────────────────────────────────")
    print(f"  Database size: {report.storage['db_human']}")
    for t in report.storage["per_table"][:8]:
        print(f"    {t['table']:25s} {t['human']:>10s}")

    # --- Phase: Queries ---
    print("\n── QUERY BENCHMARKS ───────────────────────────────────────────────")
    report.queries.append(run_query_bench(conn, "FTS (websearch_to_tsquery)", q_fts))
    report.queries.append(run_query_bench(conn, "semantic (HNSW cosine)", q_semantic))
    report.queries.append(run_query_bench(conn, "kg_neighbors (1 hop)", q_kg_neighbors))
    report.queries.append(run_query_bench(conn, "kg_profile (aggregated)", q_kg_profile))
    report.queries.append(run_query_bench(conn, "kg_genealogy_path (recursive CTE)", q_kg_genealogy_path))
    report.queries.append(run_query_bench(conn, "kg_find (pg_trgm ILIKE)", q_trgm_find))

    conn.close()

    # --- Output ---
    out_path = Path(os.environ.get("REPORT_PATH", "/out/report.json"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(
            {
                "config": report.config,
                "ingestion": [asdict(x) for x in report.ingestion],
                "indexing": [asdict(x) for x in report.indexing],
                "queries": [asdict(x) for x in report.queries],
                "storage": report.storage,
            },
            f,
            indent=2,
        )
    print(f"\nReport written to {out_path}")


if __name__ == "__main__":
    main()

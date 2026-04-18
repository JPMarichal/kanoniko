-- Schema for Postgres migration benchmark.
-- Mirrors docs/postgres-migration.md §2.2 (simplified: only what the benchmark exercises).

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- unaccent() is STABLE by default (dictionary lookups). Wrap as IMMUTABLE so it
-- can be used in GENERATED ALWAYS AS ... STORED columns. Safe because the
-- 'unaccent' dictionary doesn't change at runtime.
CREATE OR REPLACE FUNCTION immutable_unaccent(text)
  RETURNS text
  LANGUAGE sql
  IMMUTABLE
  PARALLEL SAFE
  STRICT
AS $$ SELECT public.unaccent('public.unaccent'::regdictionary, $1) $$;

-- === Index Layer ===

DROP TABLE IF EXISTS chunk_embeddings CASCADE;
DROP TABLE IF EXISTS chunks CASCADE;
DROP TABLE IF EXISTS document_registry CASCADE;

CREATE TABLE document_registry (
    file_path     TEXT PRIMARY KEY,
    sha256        TEXT NOT NULL,
    file_size     BIGINT NOT NULL,
    chunk_count   INTEGER NOT NULL DEFAULT 0,
    last_indexed  TIMESTAMPTZ NOT NULL DEFAULT now(),
    status        TEXT NOT NULL DEFAULT 'indexed'
);

CREATE TABLE chunks (
    id            BIGSERIAL PRIMARY KEY,
    file_path     TEXT NOT NULL,
    chunk_index   INTEGER NOT NULL,
    text          TEXT NOT NULL,
    reference     TEXT,
    start_char    INTEGER,
    end_char      INTEGER,
    metadata      JSONB NOT NULL DEFAULT '{}',
    language      CHAR(2) NOT NULL DEFAULT 'es',
    tsv           tsvector GENERATED ALWAYS AS (
                    to_tsvector(
                      CASE language WHEN 'en' THEN 'english'::regconfig
                                     ELSE 'spanish'::regconfig END,
                      immutable_unaccent(text)
                    )
                  ) STORED
);

CREATE INDEX chunks_file_idx     ON chunks(file_path);
CREATE INDEX chunks_metadata_gin ON chunks USING GIN (metadata);
CREATE INDEX chunks_tsv_gin      ON chunks USING GIN (tsv);

CREATE TABLE chunk_embeddings (
    chunk_id      BIGINT PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    embedding     vector(384) NOT NULL,
    model_version TEXT NOT NULL DEFAULT 'paraphrase-multilingual-MiniLM-L12-v2'
);
-- HNSW index built AFTER bulk load for speed (see benchmark.py).

-- === Knowledge Layer ===

DROP TABLE IF EXISTS relations CASCADE;
DROP TABLE IF EXISTS entity_aliases CASCADE;
DROP TABLE IF EXISTS entities CASCADE;

CREATE TABLE entities (
    id            BIGSERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    entity_type   TEXT NOT NULL,
    disambiguator TEXT,
    metadata      JSONB NOT NULL DEFAULT '{}',
    UNIQUE (name, entity_type, disambiguator)
);
CREATE INDEX entities_name_trgm ON entities USING GIN (name gin_trgm_ops);
CREATE INDEX entities_type_idx  ON entities(entity_type);

CREATE TABLE entity_aliases (
    entity_id     BIGINT REFERENCES entities(id) ON DELETE CASCADE,
    alias         TEXT NOT NULL,
    language      CHAR(2),
    PRIMARY KEY (entity_id, alias)
);

CREATE TABLE relations (
    id            BIGSERIAL PRIMARY KEY,
    src_id        BIGINT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    dst_id        BIGINT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    rel_type      TEXT NOT NULL,
    category      TEXT,
    confidence    TEXT NOT NULL DEFAULT 'llm_low',
    source_ref    TEXT,
    source        TEXT,
    verified      BOOLEAN NOT NULL DEFAULT false,
    role          TEXT,
    properties    JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX relations_src_type_idx ON relations(src_id, rel_type);
CREATE INDEX relations_dst_type_idx ON relations(dst_id, rel_type);
CREATE INDEX relations_type_idx     ON relations(rel_type);
CREATE INDEX relations_category_idx ON relations(category);

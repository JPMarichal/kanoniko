-- Canonical DDL for Alejandria's Postgres 16 + pgvector backend.
-- Applied idempotently by alejandria.storage.postgres.schema.apply_schema().
-- Mirrors docs/postgres-migration.md §2.2. Any change here must be reflected
-- there and bump SCHEMA_VERSION in schema.py.

-- ------------------------------------------------------------------ --
-- Extensions
-- ------------------------------------------------------------------ --
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- unaccent() is STABLE by default (dictionary lookup). Wrap as IMMUTABLE so
-- it can be used in GENERATED ALWAYS AS ... STORED columns. Safe because the
-- 'unaccent' dictionary does not change at runtime. Finding from Phase 1.
CREATE OR REPLACE FUNCTION immutable_unaccent(text)
  RETURNS text
  LANGUAGE sql
  IMMUTABLE
  PARALLEL SAFE
  STRICT
AS $$ SELECT public.unaccent('public.unaccent'::regdictionary, $1) $$;

-- ------------------------------------------------------------------ --
-- Schema version registry
-- ------------------------------------------------------------------ --
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes       TEXT
);

-- ------------------------------------------------------------------ --
-- Index Layer — chunks, FTS, embeddings, document registry
-- ------------------------------------------------------------------ --
CREATE TABLE IF NOT EXISTS document_registry (
    file_path     TEXT PRIMARY KEY,
    sha256        TEXT NOT NULL,
    file_size     BIGINT NOT NULL,
    chunk_count   INTEGER NOT NULL DEFAULT 0,
    last_indexed  TIMESTAMPTZ NOT NULL DEFAULT now(),
    status        TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS chunks (
    id            BIGSERIAL PRIMARY KEY,
    file_path     TEXT NOT NULL REFERENCES document_registry(file_path) ON DELETE CASCADE,
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
CREATE INDEX IF NOT EXISTS chunks_file_idx     ON chunks(file_path);
CREATE INDEX IF NOT EXISTS chunks_metadata_gin ON chunks USING GIN (metadata);
CREATE INDEX IF NOT EXISTS chunks_tsv_gin      ON chunks USING GIN (tsv);

CREATE TABLE IF NOT EXISTS chunk_embeddings (
    chunk_id      BIGINT PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
    embedding     vector(384) NOT NULL,
    model_version TEXT NOT NULL DEFAULT 'paraphrase-multilingual-MiniLM-L12-v2'
);
-- HNSW index is created AFTER bulk load for performance; see
-- storage/postgres/schema.py::ensure_hnsw_index().

-- ------------------------------------------------------------------ --
-- Knowledge Layer — entities, aliases, relations, profiles, candidates
-- ------------------------------------------------------------------ --
CREATE TABLE IF NOT EXISTS entities (
    id            BIGSERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    entity_type   TEXT NOT NULL,
    disambiguator TEXT,
    metadata      JSONB NOT NULL DEFAULT '{}',
    UNIQUE (name, entity_type, disambiguator)
);
CREATE INDEX IF NOT EXISTS entities_name_trgm ON entities USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS entities_type_idx  ON entities(entity_type);

CREATE TABLE IF NOT EXISTS entity_aliases (
    entity_id     BIGINT REFERENCES entities(id) ON DELETE CASCADE,
    alias         TEXT NOT NULL,
    language      CHAR(2),
    PRIMARY KEY (entity_id, alias)
);
CREATE INDEX IF NOT EXISTS entity_aliases_alias_trgm ON entity_aliases USING GIN (alias gin_trgm_ops);

CREATE TABLE IF NOT EXISTS relations (
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
CREATE INDEX IF NOT EXISTS relations_src_type_idx ON relations(src_id, rel_type);
CREATE INDEX IF NOT EXISTS relations_dst_type_idx ON relations(dst_id, rel_type);
CREATE INDEX IF NOT EXISTS relations_type_idx     ON relations(rel_type);
CREATE INDEX IF NOT EXISTS relations_category_idx ON relations(category);

CREATE TABLE IF NOT EXISTS entity_profiles (
    entity_id       BIGINT PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    mention_count   INTEGER NOT NULL DEFAULT 0,
    document_count  INTEGER NOT NULL DEFAULT 0,
    books           JSONB NOT NULL DEFAULT '[]',
    key_passages    JSONB NOT NULL DEFAULT '[]',
    summary_en      TEXT,
    summary_es      TEXT,
    disambiguation_notes TEXT,
    disambiguated_counts JSONB NOT NULL DEFAULT '{}',
    profile_version INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'metadata',
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Entity→Document mention edges (ex-MENTIONED_IN en Neo4j).
-- Decisión §6.1 del doc kg-client-port-audit.md (2026-04-18): añadida en
-- SCHEMA_VERSION=2 para desbloquear 4 métodos del cliente
-- (get_documents_for_entity, get_documents_for_entities_batch,
-- get_all_entity_mentions, get_disambiguated_counts).
CREATE TABLE IF NOT EXISTS entity_document_mentions (
    entity_id     BIGINT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    file_path     TEXT NOT NULL REFERENCES document_registry(file_path) ON DELETE CASCADE,
    resolved_name TEXT NOT NULL DEFAULT '',
    confidence    TEXT,
    PRIMARY KEY (entity_id, file_path, resolved_name)
);
CREATE INDEX IF NOT EXISTS entity_doc_mentions_entity_idx ON entity_document_mentions(entity_id);
CREATE INDEX IF NOT EXISTS entity_doc_mentions_file_idx   ON entity_document_mentions(file_path);

CREATE TABLE IF NOT EXISTS ner_candidates (
    id            BIGSERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    entity_type   TEXT NOT NULL,
    frequency     INTEGER NOT NULL DEFAULT 1,
    status        TEXT NOT NULL DEFAULT 'candidate',
    sample_files  JSONB NOT NULL DEFAULT '[]',
    first_seen    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (name, entity_type)
);
CREATE INDEX IF NOT EXISTS ner_freq_idx   ON ner_candidates(frequency DESC);
CREATE INDEX IF NOT EXISTS ner_status_idx ON ner_candidates(status);

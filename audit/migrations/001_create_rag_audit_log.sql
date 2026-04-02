-- Migration: 001_create_rag_audit_log
-- Append-only audit trail for clinical RAG query events.
-- Do NOT store raw PHI in raw_query — use de-identified query tokens only.

CREATE TABLE IF NOT EXISTS rag_audit_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type          TEXT NOT NULL,
    query_id            TEXT,
    session_id          TEXT,
    raw_query           TEXT,          -- WARNING: do not log raw PHI here
    guideline_sources   TEXT[],        -- source document filenames cited in response
    chunks_retrieved    INTEGER,
    top_score           NUMERIC(6,5),  -- top cosine similarity score (0.0–1.0)
    model_used          TEXT,
    embedding_model     TEXT,
    latency_ms          INTEGER,
    error_detail        TEXT,
    metadata            JSONB
);

CREATE INDEX IF NOT EXISTS idx_rag_audit_event_type  ON rag_audit_log (event_type);
CREATE INDEX IF NOT EXISTS idx_rag_audit_query_id    ON rag_audit_log (query_id);
CREATE INDEX IF NOT EXISTS idx_rag_audit_created_at  ON rag_audit_log (created_at DESC);

COMMENT ON TABLE rag_audit_log IS
    'Append-only audit trail for all clinical RAG query events. Do not store raw PHI in raw_query.';

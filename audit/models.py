"""Audit event models for the Clinical RAG Agent."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RAGAuditEventType(str, Enum):
    QUERY_RECEIVED = "query_received"
    EMBEDDING_GENERATED = "embedding_generated"
    RETRIEVAL_COMPLETED = "retrieval_completed"
    RERANK_COMPLETED = "rerank_completed"
    CONTEXT_ASSEMBLED = "context_assembled"
    LLM_CALL_STARTED = "llm_call_started"
    LLM_CALL_COMPLETED = "llm_call_completed"
    RESPONSE_DELIVERED = "response_delivered"
    NO_RESULTS_FOUND = "no_results_found"
    QUERY_FAILED = "query_failed"


class RAGAuditEvent(BaseModel):
    """Immutable audit record for a single RAG query lifecycle event."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    event_type: RAGAuditEventType
    query_id: Optional[str] = None           # groups all events for one query
    session_id: Optional[str] = None
    raw_query: Optional[str] = None          # never store PHI here
    guideline_sources: Optional[list[str]] = None   # document filenames cited
    chunks_retrieved: Optional[int] = None
    top_score: Optional[float] = None        # top cosine similarity score
    model_used: Optional[str] = None         # e.g. gpt-4o
    embedding_model: Optional[str] = None    # e.g. text-embedding-3-small
    latency_ms: Optional[int] = None
    error_detail: Optional[str] = None
    metadata: Optional[dict] = None


AUDIT_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS rag_audit_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type          TEXT NOT NULL,
    query_id            TEXT,
    session_id          TEXT,
    raw_query           TEXT,
    guideline_sources   TEXT[],
    chunks_retrieved    INTEGER,
    top_score           NUMERIC(6,5),
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
"""

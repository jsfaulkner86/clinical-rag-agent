"""Append-only audit logger for clinical RAG query events."""
import os
import json
import logging
import asyncpg
from typing import Optional
from .models import RAGAuditEvent, RAGAuditEventType

logger = logging.getLogger(__name__)


class RAGAuditLogger:
    """
    Append-only audit logger backed by PostgreSQL.
    Never raises — failed audit writes must not interrupt query delivery.
    """

    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.getenv("DATABASE_URL", "")
        self._pool: Optional[asyncpg.Pool] = None

    async def init(self) -> None:
        self._pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    async def log(self, event: RAGAuditEvent) -> None:
        if not self._pool:
            logger.warning("RAGAuditLogger not initialized — event dropped: %s", event.event_type)
            return
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO rag_audit_log (
                        id, created_at, event_type, query_id, session_id, raw_query,
                        guideline_sources, chunks_retrieved, top_score,
                        model_used, embedding_model, latency_ms, error_detail, metadata
                    ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
                    """,
                    event.id, event.created_at, event.event_type.value,
                    event.query_id, event.session_id, event.raw_query,
                    event.guideline_sources, event.chunks_retrieved, event.top_score,
                    event.model_used, event.embedding_model, event.latency_ms,
                    event.error_detail,
                    json.dumps(event.metadata) if event.metadata else None,
                )
        except Exception as e:
            logger.error("RAG audit write failed [%s]: %s", event.query_id, e)

    async def log_response_delivered(
        self,
        query_id: str,
        raw_query: str,
        guideline_sources: list[str],
        chunks_retrieved: int,
        top_score: float,
        latency_ms: int,
        model_used: str = "gpt-4o",
    ) -> None:
        await self.log(RAGAuditEvent(
            event_type=RAGAuditEventType.RESPONSE_DELIVERED,
            query_id=query_id,
            raw_query=raw_query,
            guideline_sources=guideline_sources,
            chunks_retrieved=chunks_retrieved,
            top_score=top_score,
            latency_ms=latency_ms,
            model_used=model_used,
        ))


audit_logger = RAGAuditLogger()

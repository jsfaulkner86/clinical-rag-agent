"""Read-side analytics for clinical RAG audit data."""
import os
import asyncpg
from datetime import datetime, timedelta
from typing import Optional


class RAGAuditQueryService:

    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.getenv("DATABASE_URL", "")
        self._pool: Optional[asyncpg.Pool] = None

    async def init(self) -> None:
        self._pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=3)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    async def get_query_trail(self, query_id: str) -> list[dict]:
        """Full event chain for a single query lifecycle."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM rag_audit_log WHERE query_id=$1 ORDER BY created_at ASC",
                query_id,
            )
            return [dict(r) for r in rows]

    async def get_top_cited_guidelines(
        self, since: Optional[datetime] = None
    ) -> list[dict]:
        """Most frequently cited guideline documents — use to prioritize corpus maintenance."""
        since = since or (datetime.utcnow() - timedelta(days=30))
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT source, COUNT(*) AS citations
                FROM rag_audit_log,
                     UNNEST(guideline_sources) AS source
                WHERE created_at >= $1
                GROUP BY source ORDER BY citations DESC LIMIT 20
                """,
                since,
            )
            return [dict(r) for r in rows]

    async def get_retrieval_quality_summary(
        self, since: Optional[datetime] = None
    ) -> dict:
        """Avg top score, avg chunks retrieved, no-result rate — RAG quality KPIs."""
        since = since or (datetime.utcnow() - timedelta(days=30))
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) FILTER (WHERE event_type='query_received')     AS total_queries,
                    COUNT(*) FILTER (WHERE event_type='response_delivered') AS delivered,
                    COUNT(*) FILTER (WHERE event_type='no_results_found')   AS no_results,
                    COUNT(*) FILTER (WHERE event_type='query_failed')       AS failed,
                    ROUND(AVG(top_score), 4)                                AS avg_top_score,
                    ROUND(AVG(chunks_retrieved), 1)                         AS avg_chunks,
                    ROUND(AVG(latency_ms))                                  AS avg_latency_ms
                FROM rag_audit_log WHERE created_at >= $1
                """,
                since,
            )
            return dict(row)

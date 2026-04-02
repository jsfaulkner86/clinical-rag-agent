"""Tests for clinical RAG audit layer."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from audit.models import RAGAuditEvent, RAGAuditEventType
from audit.logger import RAGAuditLogger


def test_audit_event_model():
    event = RAGAuditEvent(
        event_type=RAGAuditEventType.RESPONSE_DELIVERED,
        query_id="Q-001",
        raw_query="What is the PPH prevention protocol?",
        guideline_sources=["acog_pph_2024.pdf"],
        chunks_retrieved=4,
        top_score=0.87,
        latency_ms=1240,
    )
    assert event.id is not None
    assert isinstance(event.created_at, datetime)
    assert event.chunks_retrieved == 4


@pytest.mark.asyncio
async def test_logger_never_raises_without_pool():
    logger = RAGAuditLogger(dsn="postgresql://test")
    logger._pool = None
    await logger.log(RAGAuditEvent(
        event_type=RAGAuditEventType.QUERY_FAILED,
        query_id="Q-FAIL",
        error_detail="Test failure",
    ))


@pytest.mark.asyncio
async def test_logger_writes_response_delivered():
    logger = RAGAuditLogger(dsn="postgresql://test")
    mock_conn = AsyncMock()
    mock_pool = AsyncMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    logger._pool = mock_pool
    await logger.log_response_delivered(
        query_id="Q-001",
        raw_query="PPH protocol?",
        guideline_sources=["acog.pdf"],
        chunks_retrieved=3,
        top_score=0.91,
        latency_ms=980,
    )
    mock_conn.execute.assert_called_once()

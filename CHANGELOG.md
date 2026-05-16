# Changelog

All notable changes to the Clinical RAG Agent are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## [1.0.0] — 2026-04-12

### Added
- LangChain RAG pipeline over clinical guideline corpus
  - Query → embed → similarity search → context assembly → GPT-4o synthesis
  - Source citations mandatory on every response
  - Retrieval-grounded output only — LLM does not answer from training data
- Chroma persistent vector store (text-embedding-3-small, cosine similarity)
- Ingest pipeline: PDF/Markdown → RecursiveCharacterTextSplitter (512 tokens, 64 overlap) → embed → upsert
- Append-only `rag_audit_log` (PostgreSQL + asyncpg) — 10 event types
- `audit/models.py` — RAGAuditEvent Pydantic model
- `audit/logger.py` — append-only asyncpg writer
- `audit/queries.py` — `get_top_cited_guidelines()`, `get_retrieval_quality_summary()`, `get_query_trail()`
- `audit/migrations/001_create_rag_audit_log.sql`
- Chunking strategy documentation: 512-token chunks, 64-token overlap, top-k=4
- Corpus recommendations: ACOG Practice Bulletins, SMFM Consult Series, USPSTF, AHA/ACC, institutional protocols
- PHI boundary enforcement: guideline documents only in vector store; patient context injected at query-time
- `get_retrieval_quality_summary()` — avg cosine score, avg chunks retrieved, no-result rate
- `.env.example`

---

## [Unreleased]

### Planned
- Specialty-specific guideline collections (maternal health, cardiology, endocrinology)
- FHIR patient context injection for personalized recommendations via `ehr-mcp`
- Confidence scoring on retrieved chunks with threshold-based fallback
- Re-ranking layer (Cohere Rerank or cross-encoder)
- Hybrid search: BM25 + dense vector for clinical keyword precision
- LangSmith tracing integration

# Clinical RAG Agent

> **LangChain + Chroma** — Clinical guidelines at point of care, retrieved in real time

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)]()
[![LangChain](https://img.shields.io/badge/LangChain-000000?style=flat-square)]()
[![Chroma](https://img.shields.io/badge/Chroma-Vector%20DB-green?style=flat-square)]()
[![Healthcare AI](https://img.shields.io/badge/Healthcare-AI-red?style=flat-square)]()

Built by [The Faulkner Group](https://thefaulknergroupadvisors.com) — informed by clinical workflow design across 12 Epic enterprise health systems.

---

## Problem Statement

Clinicians cannot memorize every clinical guideline, protocol, or evidence update. At the point of care, a literature search takes 45 minutes they don't have. Static EHR-embedded reference tools are outdated, rigid, and not queryable in natural language.

This agent solves that with a RAG pipeline over ingested clinical guideline documents — accepting natural language clinical queries, retrieving relevant guideline sections with source citations, and returning concise, actionable recommendations in seconds.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Guideline Corpus                            │
│      (PDF/Markdown: ACOG, SMFM, ACC, AHA, USPSTF, custom)      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ Ingest pipeline
                              │ chunk → embed → upsert
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Chroma Vector Store                                │
│  text-embedding-3-small · cosine similarity · persistent       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ Retrieval query
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LangChain RAG Pipeline                         │
│                                                                 │
│  [Query] → [Embed Query] → [Similarity Search]                  │
│                                  │                             │
│                          top-k chunks + scores                 │
│                                  │                             │
│                                  ▼                             │
│                     [Context Assembly]                          │
│                                  │                             │
│                     source citations attached                  │
│                                  │                             │
│                                  ▼                             │
│                    [GPT-4o Synthesis]                           │
│                                  │                             │
│                    concise clinical recommendation             │
│                                  │                             │
│                                  ▼                             │
│                      [Audit Log Written]                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PostgreSQL: rag_audit_log (append-only)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Core Design Principles

- **Retrieval-grounded output only** — the LLM synthesizes retrieved chunks; it does not answer from training data. Every response is traceable to a source document.
- **Source citations are mandatory** — every response includes the guideline filenames that contributed to the answer. No citation = the chunk was not used.
- **PHI must never enter the vector store** — guideline documents only. Patient-specific context is injected at query time via FHIR, never indexed.
- **Audit on every query** — `query_id` groups all 10 event types across the full lifecycle from query receipt to response delivery.

---

## Repository Structure

```
clinical-rag-agent/
├── main.py                         # LangChain RAG pipeline + Chroma setup
├── requirements.txt
├── .env.example
│
├── audit/
│   ├── models.py                   # RAGAuditEvent model (10 event types)
│   ├── logger.py                   # Append-only asyncpg writer — never raises
│   ├── queries.py                  # Top cited guidelines, retrieval quality KPIs
│   └── migrations/
│       └── 001_create_rag_audit_log.sql
│
└── tests/
    └── test_audit.py
```

---

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Retrieval Framework** | LangChain | Standard RAG chain primitives; `RetrievalQA` with source documents |
| **Vector Store** | Chroma | Persistent local vector DB; zero infrastructure overhead for development |
| **Embeddings** | OpenAI text-embedding-3-small | Best cost/quality ratio for clinical text; 1536-dimension output |
| **LLM** | OpenAI GPT-4o | Synthesis and clinical reasoning over retrieved context |
| **Audit Store** | PostgreSQL + asyncpg | Append-only query event log with guideline source array indexing |
| **Language** | Python 3.11+ | Async-native; type hints throughout |

---

## RAG Pipeline Configuration

### Chunking Strategy

Clinical guideline documents require specific chunking decisions:

| Parameter | Recommended Value | Rationale |
|---|---|---|
| `chunk_size` | 512 tokens | Preserves clinical recommendation context without splitting dosage/criteria mid-sentence |
| `chunk_overlap` | 64 tokens | Prevents recommendation truncation at chunk boundaries |
| `splitter` | `RecursiveCharacterTextSplitter` | Respects paragraph and sentence structure |
| `top_k` | 4 | Balances context window usage vs. retrieval recall |

### Corpus Recommendations

Priority guideline sources for a maternal health deployment:
- **ACOG Practice Bulletins** — OB/GYN clinical guidelines (PDF)
- **SMFM Consult Series** — Maternal-Fetal Medicine protocols
- **USPSTF Recommendations** — Preventive care thresholds
- **AHA/ACC Guidelines** — Cardiovascular risk in pregnancy
- **Custom institutional protocols** — Exported from Epic as PDFs

---

## Audit Event Lifecycle

```
query_received
    └── embedding_generated
            └── retrieval_completed
                    └── rerank_completed (optional)
                            └── context_assembled
                                    └── llm_call_started
                                            └── llm_call_completed
                                                    └── response_delivered
                                                    └── no_results_found
                                                    └── query_failed
```

**Key audit analytics available:**
- `get_top_cited_guidelines()` — which documents are actually being used; prune or refresh stale ones
- `get_retrieval_quality_summary()` — avg top cosine score, avg chunks retrieved, no-result rate; tracks RAG quality over time
- `get_query_trail()` — full lifecycle trace per query for debugging low-quality responses

---

## Compliance Posture

- **PHI boundary:** Raw clinical queries must never include patient identifiers. The `raw_query` audit field is for de-identified query text only. If integrating with a live EHR for patient-specific context, inject FHIR-retrieved data at synthesis time via a separate prompt layer — never index it.
- **Audit trail:** `rag_audit_log` is append-only. Tracks every query, which guidelines were cited, and whether results were found — satisfying documentation requirements for AI-assisted clinical decision support tools under state medical board guidance.
- **FHIR integration path:** Connect patient context via `ehr-mcp` tools rather than embedding raw FHIR data in the vector store.

---

## Known Failure Modes

| Failure Mode | Impact | Mitigation |
|---|---|---|
| Stale guideline corpus | Outdated recommendations delivered | Schedule quarterly corpus refresh; version-stamp embeddings by ingest date |
| Low cosine score on rare clinical scenarios | No results or low-confidence response | Expand corpus; flag queries with `top_score < 0.70` for manual review |
| PHI accidentally indexed | HIPAA violation | Pre-ingest scan with Presidio; block any document with PHI patterns before embedding |
| LLM ignores retrieved context | Hallucinated clinical guidance | Enforce retrieval-grounded system prompt; log cases where citations are empty |

---

## Local Development

```bash
git clone https://github.com/jsfaulkner86/clinical-rag-agent
cd clinical-rag-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run database migration
psql $DATABASE_URL -f audit/migrations/001_create_rag_audit_log.sql

python main.py
pytest tests/ -v
```

---

## What's Next

- Specialty-specific guideline collections (maternal health, cardiology, endocrinology)
- FHIR patient context injection for personalized recommendations via `ehr-mcp`
- Confidence scoring on retrieved chunks with threshold-based fallback
- Re-ranking layer (Cohere Rerank or cross-encoder)
- Hybrid search: BM25 + dense vector for clinical keyword precision

---

*Part of The Faulkner Group's healthcare agentic AI portfolio → [github.com/jsfaulkner86](https://github.com/jsfaulkner86)*

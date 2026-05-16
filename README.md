<div align="center">

<br />

# 📚 Clinical RAG Agent

**Clinicians can't memorize every guideline.**
**At the point of care, a literature search takes 45 minutes they don't have.**
**Static EHR reference tools are outdated, rigid, and not queryable in natural language.**

This agent solves that with a **LangChain RAG pipeline over ingested clinical guideline documents** —
natural language clinical queries, retrieved guideline sections with source citations,
concise actionable recommendations in seconds.

<br />

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-RAG%20Pipeline-000000?style=flat-square)](https://langchain.com)
[![Chroma](https://img.shields.io/badge/Chroma-Vector%20DB-22c55e?style=flat-square)](https://trychroma.com)
[![ACOG](https://img.shields.io/badge/ACOG%2FSMFM-Guideline%20Corpus-E91E8C?style=flat-square)]()
[![HIPAA](https://img.shields.io/badge/HIPAA-PHI%20Boundary%20Enforced-0EA5E9?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](LICENSE)

<br />

[Architecture](#system-architecture) · [Corpus Setup](#corpus-recommendations) · [Chunking Strategy](#rag-pipeline-configuration) · [Audit Trail](#audit-event-lifecycle) · [Quick Start](#local-development)

<br />

</div>

---

## The Real Problem

I've designed clinical workflow systems across 12 enterprise Epic health systems. The same gap exists at all of them: EHR-embedded clinical reference tools that haven't been updated in years, locked to a search paradigm that requires knowing the exact right term.

When an OB is deciding on PPH prophylaxis at 2am, they need the ACOG recommendation — not a keyword search of a PDF library from 2019. This pipeline makes institutional clinical knowledge queryable, auditable, and grounded — every response traceable to a source document.

---

## What It Does

| Manual Workflow | This Agent |
|---|---|
| Open browser, navigate to ACOG, search keyword | Natural language query — retrieves relevant guideline sections instantly |
| Hope the right document surfaces | Top-k cosine similarity retrieval with score logging |
| Read full PDF section, synthesize recommendation | GPT-4o synthesizes concise recommendation from retrieved context only |
| Citation: none | Source guideline filenames cited on every response |
| Zero audit trail | Append-only `rag_audit_log` — every query, retrieval, and response recorded |
| Stale embedded EHR content | Corpus refresh on your schedule; version-stamped embeddings |

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

## RAG Pipeline Configuration

### Chunking Strategy

Clinical guideline documents require specific chunking decisions:

| Parameter | Value | Rationale |
|---|---|---|
| `chunk_size` | 512 tokens | Preserves clinical recommendation context without splitting dosage/criteria mid-sentence |
| `chunk_overlap` | 64 tokens | Prevents recommendation truncation at chunk boundaries |
| `splitter` | `RecursiveCharacterTextSplitter` | Respects paragraph and sentence structure |
| `top_k` | 4 | Balances context window usage vs. retrieval recall |
| `similarity_threshold` | 0.70 | Queries below this score flagged for manual review |

### Corpus Recommendations

Priority guideline sources for a maternal health deployment:

- **ACOG Practice Bulletins** — OB/GYN clinical guidelines (PDF)
- **SMFM Consult Series** — Maternal-Fetal Medicine protocols
- **USPSTF Recommendations** — Preventive care thresholds
- **AHA/ACC Guidelines** — Cardiovascular risk in pregnancy
- **Custom institutional protocols** — Exported from Epic as PDFs

> ⚠️ Pre-ingest PHI scan required before indexing any institutional document. Use Presidio or AWS Comprehend Medical to screen documents before embedding.

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

**Key audit analytics:**

- `get_top_cited_guidelines()` — which documents are actually being used; prune or refresh stale ones
- `get_retrieval_quality_summary()` — avg top cosine score, avg chunks retrieved, no-result rate
- `get_query_trail(query_id)` — full lifecycle trace per query for debugging low-quality responses

---

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Retrieval Framework** | LangChain | Standard RAG chain primitives; `RetrievalQA` with source documents |
| **Vector Store** | Chroma | Persistent local vector DB; zero infrastructure overhead for development |
| **Embeddings** | OpenAI text-embedding-3-small | Best cost/quality ratio for clinical text; 1536-dimension output |
| **LLM** | OpenAI GPT-4o | Synthesis and clinical reasoning over retrieved context only |
| **Audit Store** | PostgreSQL + asyncpg | Append-only query event log with guideline source array indexing |
| **Language** | Python 3.11+ | Async-native; type hints throughout |

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

## Compliance Posture

- **PHI boundary:** Raw clinical queries must never include patient identifiers. The `raw_query` audit field is for de-identified query text only. If integrating with a live EHR for patient-specific context, inject FHIR-retrieved data at synthesis time via a separate prompt layer — never index it.
- **Audit trail:** `rag_audit_log` is append-only. Tracks every query, which guidelines were cited, and whether results were found — satisfying documentation requirements for AI-assisted clinical decision support tools under state medical board guidance.
- **FHIR integration path:** Connect patient context via [`ehr-mcp`](https://github.com/jsfaulkner86/ehr-mcp) tools rather than embedding raw FHIR data in the vector store.

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

## Roadmap

- [ ] Specialty-specific guideline collections (maternal health, cardiology, endocrinology)
- [ ] FHIR patient context injection for personalized recommendations via `ehr-mcp`
- [ ] Confidence scoring on retrieved chunks with threshold-based fallback
- [ ] Re-ranking layer (Cohere Rerank or cross-encoder)
- [ ] Hybrid search: BM25 + dense vector for clinical keyword precision
- [ ] LangSmith tracing integration

---

## If You're Building Healthcare AI

If this pattern is useful to you, a ⭐ helps others find it.

If you're building clinical AI and need a RAG architecture grounded in real EHR workflow context — this is the kind of system I design at [The Faulkner Group](https://thefaulknergroupadvisors.com).

> ⚠️ See [DISCLAIMER.md](./DISCLAIMER.md) for important limitations on corpus staleness, PHI vector store boundaries, and production deployment requirements.

---

<div align="center">

*Part of The Faulkner Group's healthcare agentic AI portfolio → [github.com/jsfaulkner86](https://github.com/jsfaulkner86)*

*Built from 14 years and 12 Epic enterprise health system deployments.*

</div>

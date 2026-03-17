# Clinical Knowledge RAG Agent

A retrieval-augmented generation pipeline that lets clinicians 
query medical guidelines conversationally — starting with 
ACOG's Endometriosis Clinical Practice Guideline 11.

## The Problem
Clinicians spend 15+ minutes per patient searching fragmented 
clinical guidelines. This agent turns any guideline PDF into 
a queryable, conversational knowledge base in minutes.

## Architecture
| Layer | Tool |
|---|---|
| Document Ingestion | ACOG CPG-11 PDF chunked + embedded |
| Vector Store | Chroma |
| Query Agent | LangChain with clinical context prompting |
| LLM | OpenAI GPT-4 / Claude |

## Why ACOG Endometriosis CPG-11?
Endometriosis affects 1 in 10 women and takes an average 
of 7-10 years to diagnose. ACOG's 2024 guideline introduced 
presumptive diagnosis without surgery — a landmark shift 
most clinicians haven't fully absorbed yet. This agent 
makes that knowledge instantly accessible at the point of care.

## Example Queries This Agent Handles
- "What are the presumptive diagnostic criteria for endometriosis?"
- "When is surgical confirmation required under CPG-11?"
- "What first-line treatments does ACOG recommend?"

## Tech Stack
- LangChain
- Chroma (vector database)
- OpenAI Embeddings
- Python

## Status
🔨 In Progress — target completion April 2026


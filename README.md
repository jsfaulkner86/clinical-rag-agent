# Clinical RAG Agent

> **LangChain + Chroma** — Clinical guidelines delivered at point of care

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)]()
[![LangChain](https://img.shields.io/badge/LangChain-000000?style=flat-square)]()
[![Chroma](https://img.shields.io/badge/Chroma-Vector%20DB-green?style=flat-square)]()
[![Healthcare AI](https://img.shields.io/badge/Healthcare-AI-red?style=flat-square)]()

## The Problem

Clinicians can't memorize every guideline. When making critical decisions at the bedside, they need instant access to evidence-based clinical protocols — not a 45-minute literature search. This agent brings guidelines to the clinician, not the other way around.

## What It Does

A RAG pipeline built with LangChain and Chroma that:
- Ingests and indexes clinical guideline documents into a vector store
- Accepts natural language clinical queries
- Retrieves the most relevant guideline sections with source citations
- Returns concise, actionable clinical recommendations

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | LangChain |
| Vector Store | Chroma |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | OpenAI GPT-4 |
| Language | Python 3.11+ |

## Getting Started

```bash
git clone https://github.com/jsfaulkner86/clinical-rag-agent
cd clinical-rag-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
python main.py
```

## Environment Variables

```
OPENAI_API_KEY=your_key_here
```

## Background

Built by [John Faulkner](https://linkedin.com/in/johnathonfaulkner), Agentic AI Architect and founder of [The Faulkner Group](https://thefaulknergroupadvisors.com). Informed by real clinical workflow design across Epic EHR deployments in 12 health systems.

## What's Next
- Specialty-specific guideline collections (maternal health, cardiology)
- FHIR patient context integration for personalized recommendations
- Confidence scoring on retrieved guideline matches

---
*Part of a portfolio of healthcare agentic AI systems. See all projects at [github.com/jsfaulkner86](https://github.com/jsfaulkner86)*

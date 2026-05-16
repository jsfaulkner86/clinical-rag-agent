# Disclaimer

**Clinical RAG Agent**
The Faulkner Group | Version 1.0.0

---

## Not a Medical Device

This software is a **reference implementation and architectural demonstration** of a retrieval-augmented generation pipeline for clinical guideline retrieval. It is not a cleared or approved medical device, validated clinical decision support tool, or certified diagnostic instrument. It has not been reviewed by the U.S. Food and Drug Administration or any other regulatory authority.

The clinical guideline retrieval, recommendation synthesis, and source citation logic in this repository are for architectural and educational purposes only. Any clinical content surfaced by this agent reflects the source documents ingested — not clinical advice from The Faulkner Group. This system must not be used for actual clinical decision-making without independent clinical validation, regulatory review, and institutional approval.

---

## Not Legal or Clinical Advice

All references to ACOG, SMFM, USPSTF, AHA/ACC, JCAHO, HIPAA, or other clinical and regulatory frameworks are for **architectural and informational reference only**. Clinical guidelines change. The corpus ingested into this agent may be outdated. Always verify recommendations against current authoritative sources and institutional protocols.

---

## PHI Boundary — Vector Store

The vector store in this system is designed to hold **guideline documents only — never patient data**. Specifically:

- Raw patient records, FHIR resources, and clinical notes must never be embedded and stored in the Chroma vector store
- Patient-specific context must be injected at query-time via a separate prompt layer — not indexed
- Pre-ingest PHI scanning (Presidio or equivalent) is required before any institutional document corpus is ingested
- The `rag_audit_log.raw_query` field must contain only de-identified query text — never patient identifiers

Violating this boundary creates a secondary PHI repository and a direct HIPAA exposure path.

---

## Corpus Staleness

Clinical guidelines are updated regularly. ACOG, SMFM, and USPSTF publish revisions that may materially change clinical recommendations. The Faulkner Group assumes no liability for clinical decisions made on the basis of stale guideline content retrieved by this agent. Organizations deploying this system must:

- Establish a corpus refresh schedule (quarterly minimum recommended)
- Version-stamp embeddings by ingest date
- Flag queries where top cosine score < 0.70 for manual review

---

## No Warranty

This software is provided **"as is"**, without warranty of any kind. In no event shall the authors or The Faulkner Group be liable for any claim, damages, or other liability — including but not limited to incorrect clinical guidance, patient harm, PHI exposure, or regulatory penalties — arising from the use of this software.

See [LICENSE](./LICENSE) for full terms.

---

*The Faulkner Group provides healthcare IT architecture advisory services. For production deployment guidance, contact [john@thefaulknergroupadvisors.com](mailto:john@thefaulknergroupadvisors.com).*

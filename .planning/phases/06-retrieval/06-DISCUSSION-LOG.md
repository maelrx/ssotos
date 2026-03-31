# Phase 6: Retrieval - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-31
**Phase:** 06-retrieval
**Areas discussed:** Embedding provider, Hybrid fusion algorithm, Chunking strategy, Context pack structure

---

## Embedding Provider

| Option | Description | Selected |
|--------|-------------|----------|
| text-embedding-3-small (OpenAI) | 1536-dim, good quality/cost | ✓ |
| text-embedding-3-large (OpenAI) | 3072-dim, higher quality, 3x cost | |
| Anthropic embeddings | Not available | |
| Local (BGE) | Privacy, higher latency, more ops | |

**User's choice:** text-embedding-3-small (OpenAI) — auto-selected
**Notes:** Best quality/cost ratio for v1. Local deferred to v2 if privacy needs arise.

---

## Hybrid Fusion Algorithm

| Option | Description | Selected |
|--------|-------------|----------|
| Reciprocal Rank Fusion (RRF) | Standard rank fusion, k=60 | ✓ |
| Weighted sum | Simple weighted combination | |
| Interleaved | Alternate results from each ranker | |

**User's choice:** Reciprocal Rank Fusion (RRF) — auto-selected
**Notes:** Industry-standard approach. k=60 is the common default.

---

## Chunking Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Heading-guided + 512 token max | Split on H1/H2/H3, 50 token overlap | ✓ |
| Fixed 512 token chunks | Simple but breaks headings | |
| Sentence-based | More granular, more noise | |

**User's choice:** Heading-guided + 512 token max with 50 token overlap — auto-selected
**Notes:** Preserves semantic coherence. Configurable per note kind.

---

## Context Pack Structure

| Option | Description | Selected |
|--------|-------------|----------|
| note_ref + snippet + score + why_matched + metadata + neighbors + provenance | Full context pack per spec | ✓ |
| Minimal (note_ref + snippet) | Basic, less overhead | |

**User's choice:** Full context pack (note_ref + snippet + score + why_matched + metadata + neighbors + provenance) — auto-selected
**Notes:** Comprehensive. Neighbors = top-3 related chunks from same note. Provenance includes note_path, heading_path, workspace_id, indexed_at.

---

## Claude's Discretion

All gray areas auto-resolved with recommended defaults per --auto mode flag.


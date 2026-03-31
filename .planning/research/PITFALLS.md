# Domain Pitfalls

**Domain:** Knowledge OS / Agent-aware knowledge management system
**Researched:** 2026-03-31
**Confidence:** MEDIUM

## Critical Pitfalls

Mistakes that cause rewrites or major issues.

### Pitfall 1: Embedding Index Becomes Source of Truth

**What goes wrong:** Over time, users and even the system starts treating vector search results as the canonical knowledge, bypassing the actual Markdown files.

**Why it happens:** Vector retrieval is fast and feels "smart," while reading files is slower. When retrieval quality is good, it is tempting to trust it over source.

**Consequences:**
- If index is lost or corrupted, knowledge appears lost even though files exist
- Chunks drift from source as embeddings do not update immediately
- Users trust retrieved chunks as ground truth without checking sources
- System degrades silently as files and index diverge

**Prevention:**
- Always return provenance (file path, note_id) with retrieval results
- Context packs show "surrounding context" not just matching chunks
- System remains functional with FTS-only mode (embeddings are bonus)
- Explicit UI messaging: "This is derived from your notes"

**Detection:**
- Monitor for queries returning results where source file no longer exists
- Alert when chunk-to-note ratio exceeds reasonable bounds
- Periodic reconciliation job compares index to filesystem

### Pitfall 2: Agent Pollutes User Vault

**What goes wrong:** Agent starts writing directly to User Vault, creating content that mixes with user original knowledge without review.

**Why it happens:** It is easier for the agent to write directly than to create proposals. Without strict policy enforcement, the path of least resistance wins.

**Consequences:**
- User loses sovereignty over their knowledge
- AI content mixes with user knowledge without disclosure
- Hard to distinguish AI-generated from human-written
- Trust in system collapses

**Prevention:**
- Policy Engine explicitly denies vault.write for agent actor in user vault domain
- Agent only has vault.propose_patch capability, never direct write
- Exchange Zone is the only path for agent mutations to user vault
- Every proposal shows origin (agent, crawler, user)

**Detection:**
- Audit logs track all vault mutations by actor
- Alert when agent actor attempts direct vault write (should be blocked)
- Periodic review of mutation sources in audit trail

### Pitfall 3: Exchange Zone Becomes Junk Drawer

**What goes wrong:** Exchange Zone accumulates stale proposals, abandoned research, and unprocessed artifacts with no cleanup.

**Why it happens:** No retention policy. Proposals stay forever. Research outputs pile up. No incentive to close loops.

**Consequences:**
- Users stop reviewing proposals (too many to care about)
- System feels cluttered and untrustworthy
- Performance degrades as Exchange Zone grows
- Proposal workflow collapses

**Prevention:**
- Explicit lifecycle states: draft, generated, awaiting_review, approved, rejected, applied, archived
- Configurable retention: proposals older than X days auto-archive
- Clear UX: show only active proposals by default
- Periodic cleanup job archives stale items
- Proposal count badges to show review burden

**Detection:**
- Monitor Exchange Zone size growth rate
- Alert when proposals older than retention threshold exist
- Track average proposal lifetime

### Pitfall 4: Premature Scale Engineering

**What goes wrong:** Building for 1M users/notes when starting with single user/thousands of notes.

**Why it happens:** Engineers naturally want to "do it right" and avoid rewrites. Kubernetes, microservices, distributed systems feel "serious."

**Consequences:**
- Operational complexity explodes
- Velocity slows dramatically
- Costs multiply
- Solo founder drowns in infrastructure
- System is over-engineered for actual load

**Prevention:**
- Explicit architecture decision: modular monolith + workers for v1
- Define actual scale targets
- Add complexity only when measurement shows need
- Design interfaces for future extraction

**Detection:**
- Review infrastructure decisions against current scale needs
- Alert when adding unnecessary infrastructure

### Pitfall 5: Git Complexity Leaks to Users

**What goes wrong:** Users see branches, worktrees, merges, and git conflicts when they just want to write notes.

**Why it happens:** Git is the revision substrate but surfaces into user-facing UX without abstraction.

**Consequences:**
- Non-technical users feel overwhelmed
- System feels like "developer tool" not "knowledge tool"
- Adoption drops

**Prevention:**
- Git operations happen entirely in background
- Users see: "Note was edited" not "branch was merged"
- Diff/Review UI abstracts Git mechanics
- Emergency rollback is "Restore this version" not "git revert"

**Detection:**
- User research showing confusion about vault operations
- Support tickets about git stuff in UI

## Moderate Pitfalls

### Pitfall 6: Policy Engine Becomes Unmaintainable

Policy rules proliferate with special cases until no one understands what will be allowed.

**Prevention:**
- Policy rules are code, with tests
- Every rule has a clear name and documentation
- Policy simulation tool shows what would be allowed
- Minimal rule surface initially

### Pitfall 7: Retrieval Quality Neglect

Search returns irrelevant results, context packs lack context.

**Prevention:**
- Chunking strategy is explicit design decision
- Hybrid search (FTS + vector) is not optional
- User feedback on retrieval relevance

### Pitfall 8: Note Schema Fragmentation

Frontmatter schemas drift across notes.

**Prevention:**
- Templates are required (enforced by vault config)
- Frontmatter schema validation on note creation/update

### Pitfall 9: Synchronous Heavy Operations

Crawling, embedding, synthesis happen inline in API requests.

**Prevention:**
- ALL operations over ~1 second MUST be async jobs
- API returns job ID immediately
- UI polls for completion

### Pitfall 10: Agent Without Memory Curation

Agent brain accumulates everything, becoming unmanageable.

**Prevention:**
- Explicit curation criteria
- Periodic consolidation runs
- Session summaries rather than full transcripts

## Minor Pitfalls

### Pitfall 11: Over-Engineering Markdown Parsing

Building AST-based Markdown editing when simple text operations suffice.

### Pitfall 12: Ignoring Observability

Structured logging and tracing added as afterthought.

### Pitfall 13: Frontend-Backend Contract Drift

API schema and frontend types get out of sync.

## Phase-Specific Warnings

| Phase | Likely Pitfall | Mitigation |
|-------|---------------|------------|
| Phase 1 | Schema drift | Strict frontmatter validation |
| Phase 2 | Worktree leaks | Worktree lifecycle tied to proposal |
| Phase 3 | Rule proliferation | Minimal rules, tests |
| Phase 4 | Chunking afterthought | Explicit chunking design |
| Phase 5 | Memory accumulation | Curation criteria first |
| Phase 6 | Unbounded crawling | Blueprint scope enforcement |
| Phase 7 | LangGraph overuse | Only where needed |
| Phase 8 | MCP as internal bus | Exposure surface only |

## General Principles

1. Measure before optimizing
2. Policy everything
3. Observable from day one
4. Simple by default
5. Strong boundaries
6. User mental model first

## Sources

- Post-mortems from Obsidian, Logseq, Notion
- Agent safety research (Anthropic, OpenAI)
- Policy engine best practices (OPA, Casbin)
- Modular monolith patterns (Martin Fowler)

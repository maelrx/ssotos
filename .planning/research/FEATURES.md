# Feature Landscape

**Domain:** Knowledge OS / Agent-aware PKM
**Researched:** 2026-03-31
**Confidence:** MEDIUM — Based on competitor analysis, user reviews, and feature studies. Web search had technical issues; used WebFetch from official docs, product pages, and community discussions.

## Table of Contents

1. [Table Stakes](#table-stakes)
2. [Differentiators](#differentiators)
3. [Anti-Features](#anti-features)
4. [Feature Dependencies](#feature-dependencies)
5. [MVP Definition](#mvp-recommendation)
6. [Feature Prioritization Matrix](#feature-prioritization-matrix)

---

## Table Stakes

Features users expect. Missing these = product feels broken or incomplete.

### Core Vault Operations

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Create/Read/Update/Delete notes | Any PKM tool must have this | Low | Core CRUD, no excuse for not having |
| Markdown editor with live preview | Markdown is the format of power users | Low | CodeMirror 6 handles this well |
| Folder/hierarchy navigation | Users organize knowledge spatially | Low | Vault tree is expected |
| Daily notes | Rituals, morning pages, logseq-style outliner | Low | Templates make this powerful |
| Note templates | Consistency, repeatable workflows | Low | Templater pattern (Obsidian) is the gold standard |
| Backlinks | Connects related ideas automatically | Medium | Graph view alone is not enough; inline backlinks expected |
| Search (lexical) | Find what you wrote | Low | Ctrl+P or Cmd+P expected |
| Tags | Lightweight classification | Low | Both inline #tags and frontmatter tags |
| Frontmatter | Structured metadata | Low | YAML frontmatter is table stakes for power users |

### Organization & Structure

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Multiple note types | Different content needs different shapes | Medium | daily, project, resource, area, inbox variants |
| Kanban/task boards | Project management embedded in notes | Medium | Obsidian Kanban has 2.2M downloads |
| Calendar view | Temporal organization | Medium | Obsidian Calendar has 2.5M downloads |
| Multiple workspaces or vaults | Separation of concerns | Medium | Many users maintain multiple vaults |

### Version & Safety

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Git backup/version control | Safety net, audit trail | Medium | Obsidian Git has 2.3M downloads |
| Undo/rollback | Mistakes happen | Low | Should work even without Git |
| Export data | Vendor lock-in fear | Low | Users want their data portable |

### Editor Expectations

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Syntax highlighting | Markdown readability | Low | CodeMirror has this built-in |
| Block references |cite specific content | Medium | `^blockid` style references expected |
| Internal links with autocomplete | Fast linking | Low | `[[` autocomplete is standard |
| Tables | Structured data in notes | Low | Obsidian Table Editor has 2.7M downloads |

---

## Differentiators

Features that set this product apart. Not expected, but highly valued if done well.

### Policy-Gated AI Mutations

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Exchange Zone with patch proposals | Agent writes are reviewed, not applied directly | High | This is the core differentiator |
| Proposal diff view | Users see exactly what changes | Medium | Git diffs are well-understood |
| Approve/reject workflow | Human-in-the-loop for AI outputs | Medium | Makes AI assistance safe |
| Capability model | Fine-grained permissions per action | High | Policy engine must be solid |

**Why valuable:** Every PKM tool fails at this. Obsidian lets AI plugins write anywhere. Notion AI writes directly into pages. This product makes AI assistance governable.

### Domain Separation

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Agent Brain isolated from User Vault | Agent memory is private, not mixed with user knowledge | Medium | Physically separate directories |
| Agent memory persistence | Agent learns across sessions | High | SOUL.md, MEMORY.md, reflections/ |
| Skills and heuristics storage | Agent improves its own procedures | High | skills/ and heuristics/ are the mechanism |

**Why valuable:** No other tool has this. Agent memory pollutes user vaults, or agents have no persistent memory at all.

### Research as Durable Jobs

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Blueprint before job | User defines scope upfront | Medium | Prevents scope creep |
| Raw artifact preservation | Sources are preserved, not just summaries | Medium | Debugging, provenance, reprocessing |
| Synthesis generation | Structured output from research | Medium | Not just a chat answer |
| Ingest proposal bundle | Research becomes canonical knowledge via review | High | Completes the loop |

**Why valuable:** Research in chat is ephemeral. Research as jobs with artifacts is traceable and reviewable.

### Retrieval as Derived Layer

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Hybrid search (FTS + vector) | Best of keyword and semantic | Medium | pgvector handles this |
| Context packs | Retrieval returns surrounding context | Medium | Not just isolated chunks |
| Provenance on results | Users know where results came from | Low | Essential for trust |
| Access domain awareness | Policy determines what's searchable | High | Vault vs Exchange vs Raw |

**Why valuable:** RAG becoming "truth" is a real problem. This product makes retrieval explicitly derived.

### Note Copilot (Scoped AI Assistance)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Explain note | Onboarding, understanding old notes | Low | Constrained to single note |
| Summarize note | Quick comprehension | Low | Constrained to single note |
| Suggest links | Discover connections | Medium | Could generate proposals |
| Propose structural cleanup | Organization suggestions | Medium | Should generate proposals, not direct edits |
| Propose tags | Classification help | Low | Low-risk proposal |

**Why valuable:** Chat with the whole vault is dangerous. Scoped copilot keeps AI accountable.

---

## Anti-Features

Features that seem good but create problems for this type of system.

### AI Writing Directly to Canonical Vault

| Anti-Feature | Why It Creates Problems | What To Do Instead |
|--------------|------------------------|-------------------|
| AI auto-writing to notes | Pollutes user knowledge with unvetted AI content | All mutations go through Exchange Zone as proposals |
| AI modifying notes without review | User loses sovereignty | Patch-first with approval workflow |
| AI absorbing sources directly into canon | No provenance, no review | Sources go to Raw, synthesis goes to Exchange |

### Retrieval as Canonical Truth

| Anti-Feature | Why It Creates Problems | What To Do Instead |
|--------------|------------------------|-------------------|
| Embeddings becoming the source of truth | If index is lost, knowledge is lost | Filesystem is canonical, embeddings are derived |
| RAG answers presented as facts | Users trust vector matches too much | Provenance, domain flags, confidence indicators |
| Search replacing note reading | Surface-level matching over deep reading | Context packs show surrounding structure |

### Unbounded Research Jobs

| Anti-Feature | Why It Creates Problems | What To Do Instead |
|--------------|------------------------|-------------------|
| Research as infinite chat | Outputs are ephemeral | Bounded jobs with fixed outputs (raw + synthesis) |
| Crawling without scope limits | Server overload, endless content | Blueprints define boundaries |
| Auto-ingesting all fetched content | No curation, vault floods | Ingest proposals, user decides |

### Excessive Automation

| Anti-Feature | Why It Creates Problems | What To Do Instead |
|--------------|------------------------|-------------------|
| Auto-linking everything | Graph becomes noise | Suggest links, user approves |
| Auto-tagging | Tags become meaningless | Propose tags, user approves |
| Auto-zettelkasten | Forces structure onto users who dont want it | Provide templates, don't enforce |
| Real-time sync conflicts | Merging AI changes is hard | Worktrees per proposal, explicit merge |

### Enterprise Features Too Early

| Anti-Feature | Why It Creates Problems | What To Do Instead |
|--------------|------------------------|-------------------|
| Full multi-user collaboration | Complexity explosion | Single-user self-host focus |
| SSO/SAML | Implementation burden | Basic auth for v1 |
| Per-seat billing | Not an OSS concern | Self-host, BYOK LLM |
| Organization admin panels | Not relevant to v1 | Simple workspace config |

---

## Feature Dependencies

```
Phase 0: Foundations
├── Canonical filesystem structure ──────────┐
└── Markdown schemas/templates ─────────────┤
                                              │ All later features need this foundation
Phase 1: Vault Core                           │
├── Note CRUD ────────────────────────────────┤
├── Daily notes ──────────────────────────────┤
├── Template instantiation ───────────────────┤
├── Note projection sync ─────────────────────┤
└── Search (lexical) ─────────────────────────┤
                                              │
Phase 2: Git + Exchange ──────────────────────┤
├── Git repo init ────────────────────────────┤
├── Branch/worktree lifecycle ────────────────┤
├── Diff generation ──────────────────────────┤
├── Proposal model ────────────────────────────┤
├── Approval workflow ────────────────────────┤
└── Exchange Zone UI ─────────────────────────┤
                                              │
Phase 3: Policy ───────────────────────────────┤
├── Capability model ─────────────────────────┤
├── Policy rules ─────────────────────────────┤
├── Policy evaluation ─────────────────────────┤
└── Policy checks in sensitive flows ────────┤
                                              │
Phase 4: Retrieval ───────────────────────────┤
├── Chunking ──────────────────────────────────┤
├── Lexical index (Postgres FTS) ─────────────┤
├── Embeddings pipeline ───────────────────────┤
├── Hybrid retrieval ──────────────────────────┤
└── Context packs ────────────────────────────┤
                                              │
Phase 5: Agent Brain + Copilot ───────────────┤
├── Agent Brain filesystem ────────────────────┤
├── Memory curation ──────────────────────────┤
├── Note Copilot (explain, summarize) ─────────┤
├── Note Copilot (suggest links, propose) ─────┤
└── Patch-first proposal generation ──────────┤
                                              │
Phase 6: Research Runtime ─────────────────────┤
├── Research brief ────────────────────────────┤
├── Source fetch ─────────────────────────────┤
├── Raw artifact storage ─────────────────────┤
├── Synthesis generation ──────────────────────┤
└── Ingest proposal bundle ────────────────────┘
```

### Critical Dependency Chains

1. **Exchange Zone requires:** Vault CRUD + Git + Policy
   - Can't have proposals without notes to patch
   - Can't have branches without Git
   - Can't have safe mutations without Policy

2. **Note Copilot requires:** Retrieval + Policy
   - Copilot needs context from retrieval
   - Copilot proposals need policy checks

3. **Research Runtime requires:** Vault + Exchange + Retrieval + Policy
   - Research outputs go to Exchange Zone
   - Research needs retrieval for synthesis context

4. **Agent Brain requires:** Policy + Vault context
   - Agent needs to know what it can/cannot do
   - Agent reads from User Vault for context

---

## MVP Recommendation

Prioritize in this order:

### Must Have (MVP ship criteria)

1. **Canonical filesystem + Vault CRUD**
   - Create, read, update, delete notes
   - Folder hierarchy
   - YAML frontmatter validation

2. **Templates + Daily Notes**
   - At least: daily, project, resource, fleeting, permanent types
   - Template profiles

3. **Lexical search**
   - Postgres FTS
   - Note open latency under 500ms for reasonable corpus

4. **Note Copilot (read-only actions)**
   - Explain note
   - Summarize note
   - Suggest links (read-only suggestion, no mutation)

5. **Exchange Zone (proposal flow)**
   - Create proposal from note edit
   - View diff
   - Approve/reject
   - Apply patch

6. **Policy Engine (basic)**
   - vault.create_note, vault.edit_note, vault.patch_only capabilities
   - At minimum: allow_direct, allow_patch_only, deny

7. **Agent Brain (minimal)**
   - SOUL.md, MEMORY.md, USER.md persistence
   - Agent can write to brain without review

8. **Git ledger (basic)**
   - Commit on note changes
   - View history
   - Diff between versions

### Defer to Post-MVP

| Feature | Reason to Defer |
|---------|----------------|
| Semantic search (embeddings) | Can launch with FTS only; pgvector can be added |
| Research Runtime | Complex, requires full pipeline first |
| Backlinks panel | Nice-to-have, not blocking |
| Graph view | Can be added post-MVP |
| Kanban/task boards | Not blocking core workflow |
| Real-time sync | Out of scope for v1 |
| Multi-workspace | Single workspace is fine for MVP |

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Effort | Risk | Priority |
|---------|------------|---------------------|------|----------|
| Vault CRUD + Templates | Critical | Low | Low | P0 (MVP) |
| Lexical search | Critical | Low | Low | P0 (MVP) |
| Exchange Zone (proposals) | High | Medium | Medium | P0 (MVP) |
| Policy Engine | High | Medium | High | P0 (MVP) |
| Agent Brain (basic) | High | Medium | Medium | P0 (MVP) |
| Git ledger | High | Medium | Low | P0 (MVP) |
| Note Copilot (read-only) | High | Medium | Low | P1 |
| Semantic search | Medium | Medium | Low | P1 |
| Daily notes | Critical | Low | Low | P0 (MVP) |
| Research Runtime | Medium | High | High | P2 |
| Backlinks panel | Medium | Medium | Low | P2 |
| Graph view | Medium | Medium | Low | P2 |
| Context packs | Medium | Medium | Low | P1 |
| Ingest proposals | Medium | High | Medium | P2 |
| Multiple workspaces | Low | Medium | Low | P3 |
| Kanban boards | Low | Medium | Low | P3 |

### Priority Definitions

- **P0 (MVP):** Blocks first usable release. No excuse for missing.
- **P1 (Post-MVP v1):** Important but can ship without. Adds significant value.
- **P2 (Future):** Nice-to-have. Can be added incrementally.
- **P3 (Nice-to-have):** Low urgency. Address if resources allow.

---

## Feature Interaction Map

```
User creates note ──> Template applied ──> Note saved to vault
                                              │
                                              ├──> Lexical index updated
                                              │
                                              └──> Note Copilot available
                                                       │
                                                       ├──> User asks for explanation ──> Retrieval fetches context ──> Copilot explains
                                                       │
                                                       ├──> User asks for summary ──> Copilot summarizes
                                                       │
                                                       └──> User asks for link suggestions ──> Copilot suggests ──> User approves ──> Proposal created

Proposal created ──> Exchange Zone ──> Diff generated ──> User reviews ──> Approve/Reject
                                                                      │
                                                                      ├──> Approve ──> Patch applied ──> Git commit ──> Note updated
                                                                      │
                                                                      └──> Reject ──> Proposal discarded

Agent reads vault ──> Agent Brain updates memory ──> Proposals generated (if needed)
                                                    │
                                                    └──> Proposals go to Exchange, not directly to vault

Research job ──> Blueprint defined ──> Sources fetched ──> Raw artifacts stored
                                                      │
                                                      ├──> Synthesis generated ──> Ingest proposal
                                                      │
                                                      └──> User reviews ──> Approve/Reject ──> Applied to vault (via Exchange)
```

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Table Stakes | HIGH | Based on Obsidian/Logseq/Notion feature analysis, plugin download counts |
| Differentiators | MEDIUM | Based on project architecture docs; unique value proposition is novel |
| Anti-Features | MEDIUM | Based on common PKM pain points and architectural principles stated in PRD |
| Dependencies | HIGH | Dependencies follow logically from phase structure in PRD |
| MVP Definition | MEDIUM | Based on industry patterns and stated MVP criteria in PRD |
| Priority Matrix | MEDIUM | Judgement call based on value/effort/risk analysis |

---

## Sources

- [Obsidian Features](https://obsidian.md/features) — Core feature set
- [Obsidian Community Plugins](https://github.com/obsidianmd/obsidian-releases) — Plugin download stats (Dataview 3.9M, Templater 3.9M, Calendar 2.5M, Table Editor 2.7M, Git 2.3M, Kanban 2.2M, Excalidraw 5.7M)
- [Notion Product](https://www.notion.com/product) — Enterprise knowledge base positioning
- [Logseq Features](https://logseq.com/features) — Privacy-first, open-source positioning
- [Product Hunt Obsidian Reviews](https://www.producthunt.com/products/obsidian/reviews) — User feedback on pain points
- [Elastic Enterprise Search](https://www.elastic.co/enterprise-search) — Hybrid search patterns (BM25 + vector + RRF)

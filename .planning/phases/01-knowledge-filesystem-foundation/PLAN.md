---
phase: 01-knowledge-filesystem-foundation
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - workspace/user-vault/_system/schemas/note-schema.yaml
  - workspace/user-vault/_system/schemas/note-types.yaml
  - workspace/user-vault/_system/vault-config.yaml
  - workspace/_system/vault-config.yaml
  - workspace/user-vault/_system/template-profiles/PARA-like.yaml
  - workspace/user-vault/_system/template-profiles/Daily-first.yaml
  - workspace/user-vault/_system/template-profiles/Zettelkasten-like.yaml
  - workspace/user-vault/_system/template-profiles/Research-Lab.yaml
  - workspace/user-vault/_system/template-profiles/Project-OS.yaml
  - workspace/user-vault/_system/templates/daily.md
  - workspace/user-vault/_system/templates/project.md
  - workspace/user-vault/_system/templates/area.md
  - workspace/user-vault/_system/templates/resource.md
  - workspace/user-vault/_system/templates/fleeting.md
  - workspace/user-vault/_system/templates/permanent.md
  - workspace/user-vault/_system/templates/source.md
  - workspace/user-vault/_system/templates/synthesis.md
  - workspace/user-vault/_system/templates/research-brief.md
  - workspace/agent-brain/SOUL.md
  - workspace/agent-brain/MEMORY.md
  - workspace/agent-brain/USER.md
  - workspace/_system/scripts/create-daily-note.py
  - workspace/_system/scripts/create-workspace.py
  - workspace/user-vault/01-Daily/2026-03-31.md
  - workspace/user-vault/02-Projects/Sample-Project.md
autonomous: true
requirements:
  - F1-01
  - F1-02
  - F1-03
  - F2-01
  - F2-02
  - F2-03
  - F3-01
  - F3-02
  - F3-03

must_haves:
  truths:
    - "All 5 root directories (user-vault, agent-brain, exchange, raw, runtime) exist with correct structure"
    - "Notes with valid frontmatter pass schema validation"
    - "Notes with invalid frontmatter are rejected at write time (strict enforcement)"
    - "All 11 note types have distinct schema definitions"
    - "At least 3 template profiles are selectable (5 created: PARA-like, Daily-first, Zettelkasten-like, Research Lab, Project OS)"
    - "All 9 base templates render correctly with proper frontmatter and body structure"
    - "Daily notes are created on-demand (lazy) with YYYY-MM-DD.md naming"
    - "Daily notes contain configurable sections: Inbox, Focus, Notes, Linked Projects, Decisions, Learnings, Tasks, Review"
  artifacts:
    - path: workspace/user-vault/00-Inbox
      provides: Inbox capture zone
    - path: workspace/user-vault/01-Daily
      provides: Daily notes storage
    - path: workspace/user-vault/02-Projects
      provides: Project notes storage
    - path: workspace/user-vault/03-Areas
      provides: Area notes storage
    - path: workspace/user-vault/04-Resources
      provides: Resource notes storage
    - path: workspace/user-vault/05-Archive
      provides: Archived notes storage
    - path: workspace/user-vault/Templates
      provides: Template instances storage
    - path: workspace/user-vault/Attachments
      provides: File attachments storage
    - path: workspace/user-vault/_system/vault-config.yaml
      provides: Vault-level configuration
      contains: daily_notes, structure, schema
    - path: workspace/user-vault/_system/schemas/note-schema.yaml
      provides: Frontmatter field definitions
      exports: id, kind, status, title, tags, links, source, policy
    - path: workspace/user-vault/_system/schemas/note-types.yaml
      provides: All 11 note type definitions
      exports: daily, project, area, resource, archive-item, fleeting, permanent, research-note, source-note, synthesis-note, index-note, template-instance
    - path: workspace/user-vault/_system/template-profiles
      provides: 5 selectable template profiles
      exports: PARA-like, Daily-first, Zettelkasten-like, Research Lab, Project OS
    - path: workspace/user-vault/_system/templates
      provides: 9 base templates
      exports: daily, project, area, resource, fleeting, permanent, source, synthesis, research-brief
    - path: workspace/agent-brain/SOUL.md
      provides: Agent identity and constitution
    - path: workspace/agent-brain/MEMORY.md
      provides: Consolidated agent memories
    - path: workspace/agent-brain/USER.md
      provides: User operational profile
    - path: workspace/agent-brain/skills
      provides: Reusable agent procedures
    - path: workspace/agent-brain/heuristics
      provides: Agent heuristics
    - path: workspace/agent-brain/reflections
      provides: Post-run reflections
    - path: workspace/agent-brain/sessions
      provides: Session summaries
    - path: workspace/agent-brain/scratchpads
      provides: Temporary agent workspace
    - path: workspace/agent-brain/playbooks
      provides: Agent playbooks
    - path: workspace/agent-brain/traces
      provides: Execution traces
    - path: workspace/exchange/proposals
      provides: Pending proposals storage
    - path: workspace/exchange/research
      provides: Research output storage
    - path: workspace/exchange/imports
      provides: Imported content storage
    - path: workspace/exchange/reviews
      provides: Review bundles storage
    - path: workspace/raw/web
      provides: Raw web artifacts
    - path: workspace/raw/documents
      provides: Raw document artifacts
    - path: workspace/raw/parsed
      provides: Parsed artifacts
    - path: workspace/raw/manifests
      provides: Artifact manifests
    - path: workspace/raw/failed
      provides: Failed artifact storage
    - path: workspace/runtime/worktrees
      provides: Git worktrees
    - path: workspace/runtime/temp
      provides: Temporary runtime files
  key_links:
    - from: workspace/user-vault/_system/vault-config.yaml
      to: workspace/user-vault/_system/template-profiles
      via: template_profile field
    - from: workspace/user-vault/_system/vault-config.yaml
      to: workspace/user-vault/_system/schemas/note-types.yaml
      via: note_types field
    - from: workspace/user-vault/01-Daily
      to: workspace/user-vault/02-Projects
      via: links.project in frontmatter
    - from: workspace/user-vault/01-Daily
      to: workspace/user-vault/03-Areas
      via: links.area in frontmatter
---

<objective>

Establish the canonical filesystem structure, schemas, templates, and daily notes — the sovereign foundation of the entire Knowledge OS Core system. All subsequent phases depend on this foundation.

**Purpose:** Create the directory structure, note schemas, template profiles, and daily note system that form the bedrock of the entire product. The filesystem is sovereign — everything derives from these files.

**Output:** A complete, working workspace scaffold with validated note schemas, selectable template profiles, and functional daily note creation.

</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>

**Downstream Contract (what Phase 2 expects from Phase 1):**
- Phase 2 (Git/Exchange Boundary) requires the directory structure to be in place and stable
- The `_system/` folder contains `vault-config.yaml` that Phase 2 will extend with git settings
- All note types and schemas must be finalized — changes after Phase 2 break compatibility

**Decisions from 01-CONTEXT.md:**
- D-01 to D-06: Directory structure hierarchy
- D-07 to D-09: Note schema (strict validation, rejected at write time)
- D-10: All 11 note types
- D-11 to D-14: Template system (static profiles, minimum 3, all 9 base types)
- D-15 to D-18: Daily notes (lazy creation, YYYY-MM-DD format, configurable sections)
- D-19 to D-20: Workspace structure with `_system/` for config

</context>

<tasks>

<task type="auto">
  <name>Task 1: Create Root Directory Hierarchy</name>
  <files>
    - workspace/user-vault/00-Inbox/
    - workspace/user-vault/01-Daily/
    - workspace/user-vault/02-Projects/
    - workspace/user-vault/03-Areas/
    - workspace/user-vault/04-Resources/
    - workspace/user-vault/05-Archive/
    - workspace/user-vault/Templates/
    - workspace/user-vault/Attachments/
    - workspace/user-vault/_system/schemas/
    - workspace/user-vault/_system/template-profiles/
    - workspace/agent-brain/skills/
    - workspace/agent-brain/heuristics/
    - workspace/agent-brain/reflections/
    - workspace/agent-brain/sessions/
    - workspace/agent-brain/scratchpads/
    - workspace/agent-brain/playbooks/
    - workspace/agent-brain/traces/
    - workspace/exchange/proposals/
    - workspace/exchange/research/
    - workspace/exchange/imports/
    - workspace/exchange/reviews/
    - workspace/raw/web/
    - workspace/raw/documents/
    - workspace/raw/parsed/
    - workspace/raw/manifests/
    - workspace/raw/failed/
    - workspace/runtime/worktrees/
    - workspace/runtime/temp/
    - workspace/_system/scripts/
  </files>
  <action>

Create the following directory structure exactly as specified per D-01 through D-06:

```
workspace/
├── user-vault/
│   ├── 00-Inbox/
│   ├── 01-Daily/
│   ├── 02-Projects/
│   ├── 03-Areas/
│   ├── 04-Resources/
│   ├── 05-Archive/
│   ├── Templates/
│   ├── Attachments/
│   └── _system/
│       ├── schemas/
│       └── template-profiles/
├── agent-brain/
│   ├── skills/
│   ├── heuristics/
│   ├── reflections/
│   ├── sessions/
│   ├── scratchpads/
│   ├── playbooks/
│   └── traces/
├── exchange/
│   ├── proposals/
│   ├── research/
│   ├── imports/
│   └── reviews/
├── raw/
│   ├── web/
│   ├── documents/
│   ├── parsed/
│   ├── manifests/
│   └── failed/
├── runtime/
│   ├── worktrees/
│   └── temp/
└── _system/
    └── scripts/
```

Create empty directories for all paths listed in files.

  </action>
  <verify>
    find workspace -type d | sort | head -40
    echo "Total directories: $(find workspace -type d | wc -l)"
  </verify>
  <done>
    All 5 root directories exist with correct subdirectory structure per D-01, D-02, D-03, D-04, D-05, D-06
  </done>
</task>

<task type="auto">
  <name>Task 2: Create Agent Brain Core Files</name>
  <files>
    - workspace/agent-brain/SOUL.md
    - workspace/agent-brain/MEMORY.md
    - workspace/agent-brain/USER.md
  </files>
  <action>

Create minimal template content for each core brain file:

**SOUL.md** — Agent identity and constitution:
```markdown
# SOUL.md

**Agent Identity:** [To be configured at workspace creation]
**Created:** YYYY-MM-DD
**Version:** 1

## Core Identity

## Operating Principles

## Communication Style

## Constraints

## Self-Improvement Guidelines
```

**MEMORY.md** — Consolidated memories:
```markdown
# MEMORY.md

**Last Updated:** YYYY-MM-DD
**Version:** 1

## Consolidated Memories

### High-Value Learnings

### Patterns Established

### Operational Heuristics
```

**USER.md** — User operational profile:
```markdown
# USER.md

**User Profile**
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD

## User Preferences

## Work Patterns

## Context

## Restrictions

## Communication Style
```

  </action>
  <verify>
    ls -la workspace/agent-brain/*.md
    head -5 workspace/agent-brain/SOUL.md
    head -5 workspace/agent-brain/MEMORY.md
    head -5 workspace/agent-brain/USER.md
  </verify>
  <done>
    Agent Brain core files exist with valid markdown structure
  </done>
</task>

<task type="auto">
  <name>Task 3: Create Note Frontmatter Schema</name>
  <files>
    - workspace/user-vault/_system/schemas/note-schema.yaml
    - workspace/user-vault/_system/schemas/note-types.yaml
  </files>
  <action>

Create **note-schema.yaml** with strict YAML schema for note frontmatter per D-07, D-08, D-09:

```yaml
# Note Frontmatter Schema v1
# Strict validation — invalid frontmatter is REJECTED at write time, not warned

required:
  - id
  - kind
  - status
  - title
  - tags
  - links
  - source
  - policy

fields:
  id:
    type: string
    description: "Stable UUID. Title can change, id cannot."
    pattern: "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
    immutable: true

  kind:
    type: enum
    description: "Note type determining schema"
    values:
      - daily
      - project
      - area
      - resource
      - archive-item
      - fleeting
      - permanent
      - research-note
      - source-note
      - synthesis-note
      - index-note
      - template-instance

  status:
    type: enum
    description: "Note lifecycle status"
    values:
      - draft
      - active
      - archived
      - deleted

  title:
    type: string
    description: "Human-readable title"
    min_length: 1
    max_length: 500

  tags:
    type: list
    description: "Arbitrary string tags"
    items:
      type: string
    default: []

  links:
    type: object
    description: "Structured internal links"
    properties:
      related:
        type: list
        items:
          type: string
        default: []
      project:
        type: string|null
        description: "Parent project ID"
      area:
        type: string|null
        description: "Parent area ID"
    default:
      related: []
      project: null
      area: null

  source:
    type: object
    description: "Origin information for ingested content"
    properties:
      type:
        type: enum
        values:
          - human
          - crawler
          - document
          - research
          - import
          - ai
      provenance:
        type: list
        items:
          type: string
        default: []
    required:
      - type
    default:
      type: human
      provenance: []

  policy:
    type: object
    description: "Mutation policy for this note"
    properties:
      sensitivity:
        type: enum
        values:
          - low
          - normal
          - high
          - critical
        default: normal
      ai_edit_mode:
        type: enum
        values:
          - allow_direct
          - allow_patch_only
          - allow_in_exchange_only
          - deny
        default: allow_patch_only
    default:
      sensitivity: normal
      ai_edit_mode: allow_patch_only

  created_at:
    type: datetime
    description: "ISO 8601 creation timestamp"
    immutable: true

  updated_at:
    type: datetime
    description: "ISO 8601 last modified timestamp"
```

Create **note-types.yaml** — All 11 note types with their specific schemas per D-10:
```yaml
# Note Types Definition v1
# All 11 canonical note types

types:
  daily:
    description: "Contextual daily capture unit"
    icon: "📅"
    color: "#4A90D9"
    default_status: active
    has_date: true
    date_format: "YYYY-MM-DD"
    body_template: daily

  project:
    description: "Time-bound initiative with outcome"
    icon: "🎯"
    color: "#50C878"
    default_status: active
    body_template: project

  area:
    description: "Long-running responsibility area"
    icon: "🏛️"
    color: "#9B59B6"
    default_status: active
    body_template: area

  resource:
    description: "Reference material for ongoing work"
    icon: "📚"
    color: "#F39C12"
    default_status: active
    body_template: resource

  archive-item:
    description: "Archived note no longer active"
    icon: "📦"
    color: "#95A5A6"
    default_status: archived
    body_template: null

  fleeting:
    description: "Transient thought awaiting processing"
    icon: "💨"
    color: "#E74C3C"
    default_status: draft
    body_template: fleeting

  permanent:
    description: "Atomic, durable knowledge nugget"
    icon: "💎"
    color: "#3498DB"
    default_status: active
    body_template: permanent

  research-note:
    description: "Note capturing research findings"
    icon: "🔬"
    color: "#1ABC9C"
    default_status: draft
    body_template: research-note
    links_to:
      - source-note

  source-note:
    description: "Reference to external source with annotation"
    icon: "📄"
    color: "#34495E"
    default_status: active
    body_template: source-note
    has_source_url: true

  synthesis-note:
    description: "Integration of multiple sources/notes"
    icon: "🧬"
    color: "#E91E63"
    default_status: draft
    body_template: synthesis-note

  index-note:
    description: "Entry point or hub connecting related notes"
    icon: "📑"
    color: "#607D8B"
    default_status: active
    body_template: index-note

  template-instance:
    description: "Note created from a template"
    icon: "📝"
    color: "#795548"
    default_status: draft
    body_template: null
    has_template_ref: true
```

  </action>
  <verify>
    python3 -c "import yaml; yaml.safe_load(open('workspace/user-vault/_system/schemas/note-schema.yaml'))" && echo "note-schema.yaml: VALID"
    python3 -c "import yaml; yaml.safe_load(open('workspace/user-vault/_system/schemas/note-types.yaml'))" && echo "note-types.yaml: VALID"
    python3 -c "
import yaml
with open('workspace/user-vault/_system/schemas/note-types.yaml') as f:
    types = yaml.safe_load(f)
note_types = list(types['types'].keys())
print(f'Total note types: {len(note_types)}')
assert len(note_types) == 11, f'Expected 11, got {len(note_types)}'
"
  </verify>
  <done>
    Note schema YAML files exist, are valid YAML, and define all 11 note types plus required frontmatter fields
  </done>
</task>

<task type="auto">
  <name>Task 4: Create Vault Config</name>
  <files>
    - workspace/user-vault/_system/vault-config.yaml
    - workspace/_system/vault-config.yaml
  </files>
  <action>

Create **workspace/_system/vault-config.yaml** — Workspace-level config:
```yaml
# Workspace Configuration v1
version: 1
workspace:
  name: "Knowledge OS Workspace"
  created: "YYYY-MM-DD"
  template_profile: null

system:
  vault_path: "../user-vault"
  brain_path: "../agent-brain"
  exchange_path: "../exchange"
  raw_path: "../raw"
  runtime_path: "../runtime"
```

Create **workspace/user-vault/_system/vault-config.yaml** — Vault-level config:
```yaml
# Vault Configuration v1
version: 1

structure:
  numbering_enabled: true
  folders:
    - "00-Inbox"
    - "01-Daily"
    - "02-Projects"
    - "03-Areas"
    - "04-Resources"
    - "05-Archive"
    - "Templates"
    - "Attachments"

schema:
  strict_mode: true
  auto_fill:
    - created_at
    - updated_at
    - id

daily_notes:
  enabled: true
  folder: "01-Daily"
  format: "YYYY-MM-DD"
  extension: ".md"
  sections:
    - Inbox
    - Focus
    - Notes
    - "Linked Projects"
    - Decisions
    - Learnings
    - Tasks
    - Review

note_types: "schemas/note-types.yaml"
```

  </action>
  <verify>
    python3 -c "import yaml; yaml.safe_load(open('workspace/user-vault/_system/vault-config.yaml'))" && echo "vault-config.yaml: VALID"
    python3 -c "import yaml; yaml.safe_load(open('workspace/_system/vault-config.yaml'))" && echo "workspace-vault-config.yaml: VALID"
  </verify>
  <done>
    Vault config files exist with valid YAML and reference to schema files
  </done>
</task>

<task type="auto">
  <name>Task 5: Create Template Profiles</name>
  <files>
    - workspace/user-vault/_system/template-profiles/PARA-like.yaml
    - workspace/user-vault/_system/template-profiles/Daily-first.yaml
    - workspace/user-vault/_system/template-profiles/Zettelkasten-like.yaml
    - workspace/user-vault/_system/template-profiles/Research-Lab.yaml
    - workspace/user-vault/_system/template-profiles/Project-OS.yaml
  </files>
  <action>

Create 5 template profile definitions per D-11, D-12, D-13:

**PARA-like.yaml:**
```yaml
name: "PARA-like"
description: "Operational organization focused on Projects and Areas"
version: 1

enabled_note_types:
  - project
  - area
  - resource
  - archive-item
  - fleeting
  - permanent
  - daily
  - index-note

structure:
  daily_folder: "01-Daily"
  projects_folder: "02-Projects"
  areas_folder: "03-Areas"
  resources_folder: "04-Resources"
  archive_folder: "05-Archive"

daily_sections:
  - Inbox
  - Focus
  - Notes
  - "Linked Projects"
  - Decisions
  - Learnings
  - Tasks
  - Review
```

**Daily-first.yaml:**
```yaml
name: "Daily-first"
description: "Daily notes as the hub of capture and connection"
version: 1

enabled_note_types:
  - daily
  - project
  - area
  - resource
  - fleeting
  - permanent
  - index-note

structure:
  daily_folder: "01-Daily"
  projects_folder: "02-Projects"
  areas_folder: "03-Areas"
  resources_folder: "04-Resources"
  archive_folder: "05-Archive"

daily_sections:
  - Inbox
  - Focus
  - Notes
  - "Linked Projects"
  - Decisions
  - Learnings
  - Tasks
  - Review
```

**Zettelkasten-like.yaml:**
```yaml
name: "Zettelkasten-like"
description: "Atomic knowledge nuggets with dense linking"
version: 1

enabled_note_types:
  - fleeting
  - permanent
  - daily
  - source-note
  - synthesis-note
  - index-note

structure:
  daily_folder: "01-Daily"
  archive_folder: "05-Archive"

daily_sections:
  - Inbox
  - Notes
  - "Fleeting Notes"
  - "Linked Knowledge"
  - Tasks
```

**Research-Lab.yaml:**
```yaml
name: "Research Lab"
description: "Research-focused with source tracking and synthesis"
version: 1

enabled_note_types:
  - daily
  - project
  - area
  - resource
  - research-note
  - source-note
  - synthesis-note
  - index-note

structure:
  daily_folder: "01-Daily"
  projects_folder: "02-Projects"
  areas_folder: "03-Areas"
  resources_folder: "04-Resources"
  archive_folder: "05-Archive"

daily_sections:
  - Inbox
  - Research Log
  - Notes
  - "Active Sources"
  - Decisions
  - Tasks
  - Review
```

**Project-OS.yaml:**
```yaml
name: "Project OS"
description: "Project management with decisions, specs, and logs"
version: 1

enabled_note_types:
  - project
  - daily
  - area
  - resource
  - archive-item
  - index-note

structure:
  daily_folder: "01-Daily"
  projects_folder: "02-Projects"
  areas_folder: "03-Areas"
  resources_folder: "04-Resources"
  archive_folder: "05-Archive"

daily_sections:
  - Focus
  - Tasks
  - Notes
  - "Project Updates"
  - Decisions
  - Review
```

  </action>
  <verify>
    ls workspace/user-vault/_system/template-profiles/
    echo "Profile count: $(ls workspace/user-vault/_system/template-profiles/*.yaml | wc -l)"
    for f in workspace/user-vault/_system/template-profiles/*.yaml; do
      python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "$f: VALID"
    done
  </verify>
  <done>
    At least 3 template profiles exist (5 total), all with valid YAML syntax
  </done>
</task>

<task type="auto">
  <name>Task 6: Create Base Templates</name>
  <files>
    - workspace/user-vault/_system/templates/daily.md
    - workspace/user-vault/_system/templates/project.md
    - workspace/user-vault/_system/templates/area.md
    - workspace/user-vault/_system/templates/resource.md
    - workspace/user-vault/_system/templates/fleeting.md
    - workspace/user-vault/_system/templates/permanent.md
    - workspace/user-vault/_system/templates/source.md
    - workspace/user-vault/_system/templates/synthesis.md
    - workspace/user-vault/_system/templates/research-brief.md
  </files>
  <action>

Create all 9 base templates per D-14. Each template includes proper YAML frontmatter and structured body.

**daily.md** — with sections: Inbox, Focus, Notes, Linked Projects, Decisions, Learnings, Tasks, Review

**project.md** — with sections: Overview, Goals, Specifications, Tasks, Decisions, Notes, Related

**area.md** — with sections: Responsibility, Scope, Related Projects, Resources, Notes

**resource.md** — with sections: Summary, Key Points, Details, How It Relates, Source

**fleeting.md** — transient notes with processing checklist

**permanent.md** — atomic notes with: Atomic Knowledge, Context, Evidence, Connections, Source

**source.md** — source notes with: Source Information, Summary, Key Findings, Relevant Sections, Notes, Quotes

**synthesis.md** — synthesis notes with: Synthesis, Sources, Key Insights, Conclusions, Implications, Questions, Next Steps

**research-brief.md** — research notes with: Research Goal, Questions, Scope, Methods, Expected Sources, Constraints, Timeline, Output, Status checklist

Each template must include the 8 required frontmatter fields:
- id: {{id}} (UUID placeholder)
- kind: (matching note type)
- status: (appropriate default)
- title: {{title}} or "Daily — {{date}}"
- tags: []
- links: {related: [], project: null, area: null}
- source: {type: human, provenance: []}
- policy: {sensitivity: normal, ai_edit_mode: allow_patch_only}

  </action>
  <verify>
    ls workspace/user-vault/_system/templates/
    echo "Template count: $(ls workspace/user-vault/_system/templates/*.md | wc -l)"
    for f in workspace/user-vault/_system/templates/*.md; do
      # Verify frontmatter has all required fields
      python3 -c "
import re
with open('$f') as file:
    content = file.read()
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        print('$f: has frontmatter')
    else:
        print('$f: MISSING frontmatter')
"
    done
  </verify>
  <done>
    All 9 base templates exist with valid frontmatter and body structure
  </done>
</task>

<task type="auto">
  <name>Task 7: Create Daily Note Creation Script</name>
  <files>
    - workspace/_system/scripts/create-daily-note.py
  </files>
  <action>

Create **create-daily-note.py** that implements:

1. **Lazy creation** (only on access, not at app start) per D-15
2. **YYYY-MM-DD format** for daily note filenames per D-17
3. **Configurable sections** from template profile per D-16
4. **Project/Area linking** via frontmatter `links.project` and `links.area` per D-18

The script should:
- Accept `--vault` path (default: current directory)
- Accept `--date` in YYYY-MM-DD format (default: today)
- Accept `--profile` template profile name
- Check if daily note already exists before creating
- Generate proper UUID for note id
- Use current UTC time for created_at/updated_at
- Render sections from vault-config.yaml daily_notes.sections

Key functions to implement:
- `get_vault_config(vault_path)` — load vault-config.yaml
- `get_daily_config(vault_path)` — extract daily note settings
- `format_date(date_obj, fmt)` — format to YYYY-MM-DD
- `daily_note_exists(vault_path, date_str, extension)` — check existence
- `create_daily_note(vault_path, date_obj, template_profile)` — create note
- `link_project_to_daily(note_path, project_id)` — optional linking

  </action>
  <verify>
    ls -la workspace/_system/scripts/create-daily-note.py
    python3 workspace/_system/scripts/create-daily-note.py --help
    python3 -c "
import sys
sys.path.insert(0, 'workspace/_system/scripts')
from create-daily-note import format_date, daily_note_exists
from datetime import date
print('Date format test:', format_date(date.today(), 'YYYY-MM-DD'))
print('Exists test:', daily_note_exists('workspace/user-vault', '2026-03-31', '.md'))
"
  </verify>
  <done>
    Daily note creation function exists and handles YYYY-MM-DD format, lazy creation, and configurable sections
  </done>
</task>

<task type="auto">
  <name>Task 8: Create Sample Notes and Verify System</name>
  <files>
    - workspace/user-vault/01-Daily/2026-03-31.md
    - workspace/user-vault/02-Projects/Sample-Project.md
  </files>
  <action>

Create sample notes to verify the system works end-to-end.

**2026-03-31.md** — Sample daily note with all 8 required frontmatter fields populated:
- id: valid UUID
- kind: daily
- status: active
- title: "Daily — 2026-03-31"
- tags: with sample tags
- links: with empty related, null project, null area
- source: type: human
- policy: sensitivity: normal, ai_edit_mode: allow_patch_only
- created_at and updated_at: valid ISO 8601 timestamps

Body includes all 8 sections: Inbox, Focus, Notes, Linked Projects, Decisions, Learnings, Tasks, Review

**Sample-Project.md** — Sample project note with all required frontmatter:
- Links to the daily note via links.related

  </action>
  <verify>
    python3 -c "
import yaml
import re

required = ['id', 'kind', 'status', 'title', 'tags', 'links', 'source', 'policy']

for note in ['workspace/user-vault/01-Daily/2026-03-31.md', 'workspace/user-vault/02-Projects/Sample-Project.md']:
    with open(note) as f:
        content = f.read()
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            fm = yaml.safe_load(match.group(1))
            missing = [f for f in required if f not in fm]
            if missing:
                print(f'{note}: MISSING: {missing}')
            else:
                print(f'{note}: VALID')
"
  </verify>
  <done>
    Sample notes exist, frontmatter validates correctly, all 8 required fields present
  </done>
</task>

<task type="auto">
  <name>Task 9: Create Workspace Materialization Script</name>
  <files>
    - workspace/_system/scripts/create-workspace.py
  </files>
  <action>

Create **create-workspace.py** that materializes a complete workspace:

1. Creates full directory structure (same as Task 1)
2. Copies schema files from _system templates
3. Copies template profiles
4. Copies base templates
5. Creates Agent Brain core files
6. Creates vault configuration
7. Accepts `--profile` argument for template profile selection
8. Accepts `--path` for workspace location
9. Accepts `--name` for workspace name

The script should be idempotent — safe to run multiple times.

  </action>
  <verify>
    ls -la workspace/_system/scripts/create-workspace.py
    python3 workspace/_system/scripts/create-workspace.py --help
  </verify>
  <done>
    Workspace materialization script exists and provides full workspace creation with profile selection
  </done>
</task>

</tasks>

<verification>

Execute the following to verify Phase 1 completion:

```bash
# 1. Directory structure
echo "=== Directories ==="
find workspace -type d | sort | head -40

# 2. Schema files
echo "=== Schema Files ==="
ls workspace/user-vault/_system/schemas/

# 3. Template profiles (min 3)
echo "=== Template Profiles ==="
ls workspace/user-vault/_system/template-profiles/
echo "Count: $(ls workspace/user-vault/_system/template-profiles/*.yaml | wc -l)"

# 4. Base templates (9)
echo "=== Base Templates ==="
ls workspace/user-vault/_system/templates/
echo "Count: $(ls workspace/user-vault/_system/templates/*.md | wc -l)"

# 5. Agent Brain files
echo "=== Agent Brain ==="
ls workspace/agent-brain/*.md

# 6. YAML validation
echo "=== YAML Validation ==="
for f in workspace/user-vault/_system/schemas/*.yaml workspace/user-vault/_system/vault-config.yaml workspace/_system/vault-config.yaml workspace/user-vault/_system/template-profiles/*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "$f: VALID" || echo "$f: INVALID"
done

# 7. Note types count
echo "=== Note Types ==="
python3 -c "
import yaml
with open('workspace/user-vault/_system/schemas/note-types.yaml') as f:
    types = yaml.safe_load(f)
print(f'Total types: {len(types[\"types\"])}')
"

# 8. Frontmatter validation on samples
echo "=== Sample Note Validation ==="
python3 -c "
import yaml
import re

required = ['id', 'kind', 'status', 'title', 'tags', 'links', 'source', 'policy']
for note in ['workspace/user-vault/01-Daily/2026-03-31.md', 'workspace/user-vault/02-Projects/Sample-Project.md']:
    with open(note) as f:
        content = f.read()
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            fm = yaml.safe_load(match.group(1))
            missing = [f for f in required if f not in fm]
            print(f'{note}: {\"VALID\" if not missing else \"MISSING: \" + str(missing)}')
"
```

</verification>

<success_criteria>

Phase 1 is complete when:

1. **[DONE]** All 5 root directories exist with correct subdirectory structure
   - `user-vault/` with 00-Inbox, 01-Daily, 02-Projects, 03-Areas, 04-Resources, 05-Archive, Templates, Attachments, _system/
   - `agent-brain/` with SOUL.md, MEMORY.md, USER.md, skills/, heuristics/, reflections/, sessions/, scratchpads/, playbooks/, traces/
   - `exchange/` with proposals/, research/, imports/, reviews/
   - `raw/` with web/, documents/, parsed/, manifests/, failed/
   - `runtime/` with worktrees/, temp/

2. **[DONE]** Note schema validates 8 required frontmatter fields
   - id, kind, status, title, tags, links, source, policy

3. **[DONE]** All 11 note types defined in note-types.yaml
   - daily, project, area, resource, archive-item, fleeting, permanent, research-note, source-note, synthesis-note, index-note, template-instance

4. **[DONE]** At least 3 template profiles selectable (5 created)
   - PARA-like, Daily-first, Zettelkasten-like, Research Lab, Project OS

5. **[DONE]** 9 base templates render correctly
   - daily, project, area, resource, fleeting, permanent, source, synthesis, research-brief

6. **[DONE]** Daily notes created with YYYY-MM-DD format and configurable sections
   - Sections: Inbox, Focus, Notes, Linked Projects, Decisions, Learnings, Tasks, Review

</success_criteria>

<output>

After completion, create `.planning/phases/01-knowledge-filesystem-foundation/01-SUMMARY.md` using the summary template, documenting:
- Files created
- Decisions implemented
- Verification results
- Downstream contract for Phase 2

</output>


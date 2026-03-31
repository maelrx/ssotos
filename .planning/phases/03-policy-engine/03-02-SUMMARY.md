---
phase: 03-policy-engine
plan: 03-02
subsystem: policy-engine
tags:
  - policy
  - rules
  - crud
  - defaults
  - yaml-storage
dependency_graph:
  requires:
    - "03-01 (Wave 1: PolicyEvaluator, models, enums)"
  provides:
    - "PolicyRulesService with CRUD operations"
    - "get_default_rules() with D-41 to D-44 safe defaults"
  affects:
    - "src/core/policy/__init__.py"
    - "Wave 3: Service policy check integration"
tech_stack:
  added:
    - "yaml (PyYAML) for rule persistence"
  patterns:
    - "PolicyRulesService as repository-style data access"
    - "Lazy loading with fallback to default rules"
    - "D-40 priority scoring for rule specificity"
key_files:
  created:
    - "src/core/policy/defaults.py"
    - "src/core/policy/rules.py"
  modified:
    - "src/core/policy/__init__.py"
decisions:
  - "YAML chosen for rule persistence (deferred decision from Phase 3 context)"
  - "Lazy loading pattern — rules loaded only when first accessed"
  - "PolicyRule dataclass is mutable (not frozen) to support CRUD updates"
metrics:
  duration: "~3 minutes"
  completed: "2026-03-31"
  tasks: 3
  commits: 3
---

# Phase 03 Plan 02: Policy Rules CRUD + Default Rules (Wave 2)

Policy rules CRUD service with safe default rules per D-41 to D-44.

## One-liner

PolicyRulesService with YAML-backed CRUD and 22 safe default rules covering read broad, create safe zones, edit patch-first, delete gated.

## What Was Built

### Task 1: Default Policy Rules (`src/core/policy/defaults.py`)

`get_default_rules()` returns 22 rules implementing the four default policies:

- **D-41 Read (broad):** Any actor can read vault, agent, research, exchange domains directly
- **D-42 Create (safe zones):** Inbox, agent-brain, research allow direct creation; vault creation goes through Exchange; agent creation in vault requires exchange flow
- **D-43 Update (patch-first):** Vault updates require patch-only flow; agent can update own brain directly; research updates direct
- **D-44 Delete/move/rename (gated):** User can delete/move/rename with approval; agent denied from all vault mutations; default deny for vault

Exchange rules also added: apply_proposal needs approval, system can create proposals directly.

Priority scoring per D-40: path (+100), note_type (+50), sensitivity (+40), domain (+30), action (+20), capability_group (+10), actor (+5).

### Task 2: PolicyRulesService (`src/core/policy/rules.py`)

CRUD service with YAML persistence to `_system/policy/rules.yaml`:

| Method | Description |
|--------|-------------|
| `list_rules()` | Returns all rules sorted by priority descending |
| `get_rule(id)` | Returns rule or None |
| `create_rule(rule)` | Adds rule with generated UUID, persists |
| `update_rule(id, updates)` | Updates fields, persists, returns updated rule |
| `delete_rule(id)` | Removes rule, persists, returns bool |
| `load_rules()` | Loads from YAML, falls back to defaults if missing |
| `save_rules(rules)` | Serializes rules to YAML |
| `reload_from_defaults()` | Replaces all rules with defaults, saves |

Lazy loading: rules are loaded only when first accessed. If `_system/policy/rules.yaml` does not exist, defaults are loaded and persisted.

### Task 3: Module Exports (`src/core/policy/__init__.py`)

Added `get_default_rules` and `PolicyRulesService` to module exports and `__all__`.

## Verification Results

All checks passed:

1. `from core.policy import PolicyRulesService, get_default_rules` — PASS
2. PolicyRulesService loads 22 default rules on first run — PASS
3. `create_rule()` adds and persists rule with UUID — PASS
4. `update_rule()` modifies and persists, survives reload — PASS
5. `delete_rule()` removes and persists, confirmed by reload — PASS
6. `reload_from_defaults()` restores all 22 default rules — PASS
7. Rules file stored at `_system/policy/rules.yaml` — PASS

## Commits

| Commit | Description |
|--------|-------------|
| `dedb772` | feat(03-policy-engine): add get_default_rules with safe default policies |
| `6f168db` | feat(03-policy-engine): add PolicyRulesService with CRUD operations |
| `1585493` | feat(03-policy-engine): export PolicyRulesService and get_default_rules |

## Deviations from Plan

None — plan executed exactly as written.

## Deferred Issues

None.

## Self-Check

- [x] `src/core/policy/defaults.py` created
- [x] `src/core/policy/rules.py` created
- [x] `src/core/policy/__init__.py` updated with new exports
- [x] Commit `dedb772` exists
- [x] Commit `6f168db` exists
- [x] Commit `1585493` exists
- [x] All verification checks passed

## Self-Check: PASSED

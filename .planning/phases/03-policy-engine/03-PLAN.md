---
phase: 03-policy-engine
plan: 03-01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/core/policy/enums.py
  - src/core/policy/models.py
  - src/core/policy/evaluator.py
  - src/core/policy/__init__.py
autonomous: true
requirements:
  - F6-01
  - F6-02

must_haves:
  truths:
    - "Capability groups (vault, agent, research, exchange) exist with fine-grained actions"
    - "Policy evaluator can determine correct outcome for any mutation request"
    - "All 5 policy outcomes (allow_direct, allow_patch_only, allow_in_exchange_only, allow_with_approval, deny) are defined and used"
  artifacts:
    - path: "src/core/policy/enums.py"
      provides: "CapabilityGroup and CapabilityAction enums"
      exports: ["CapabilityGroup", "CapabilityAction"]
    - path: "src/core/policy/models.py"
      provides: "PolicyRequest, PolicyOutcome, and PolicyResult dataclasses"
      exports: ["PolicyRequest", "PolicyOutcome", "PolicyResult"]
    - path: "src/core/policy/evaluator.py"
      provides: "PolicyEvaluator class with evaluate() method"
      exports: ["PolicyEvaluator"]
  key_links:
    - from: "src/core/policy/evaluator.py"
      to: "src/core/policy/models.py"
      via: "imports PolicyRequest, PolicyOutcome, PolicyResult"
    - from: "src/core/policy/models.py"
      to: "src/core/policy/enums.py"
      via: "imports CapabilityGroup, CapabilityAction"
---

<objective>
Build the core policy engine foundation: capability model and policy evaluator. This is the gatekeeper that prevents unauthorized mutations per D-32, D-33, D-34-D-38.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md §Phase 3
@.planning/REQUIREMENTS.md §F6
@.planning/phases/03-policy-engine/03-CONTEXT.md
@src/core/events.py
@src/core/event_bus.py
</context>

<interfaces>
<!-- Key types and contracts the executor needs. Extracted from codebase. -->

From src/core/events.py:
```python
from core.event_bus import EventBus, Event, EventType

def emit(
    event_type: EventType,
    actor: str = "system",
    domain: str | None = None,
    **metadata
) -> None:
    """Emit an event via the singleton EventBus."""
    EventBus().emit(event_type, actor=actor, domain=domain, **metadata)
```

From src/core/event_bus.py:
```python
class EventType(Enum):
    """Event types for audit logging."""
    GIT_REPO_INITIALIZED = "git.repo.initialized"
    GIT_BRANCH_CREATED = "git.branch.created"
    # ... more events

class Event:
    event_type: EventType
    timestamp: datetime
    actor: str
    domain: str | None
    metadata: dict

class EventBus:
    def emit(self, event_type: EventType, actor: str = "system", domain: str | None = None, **metadata) -> None
    def register_handler(self, handler: Callable[[Event], None]) -> None
```
</interfaces>

<tasks>

<task type="auto">
  <name>Task 1: Create capability model enums</name>
  <files>src/core/policy/enums.py</files>
  <action>
Create `src/core/policy/enums.py` with:

1. **CapabilityGroup** enum (per D-32):
   - `VAULT` = "vault"
   - `AGENT` = "agent"
   - `RESEARCH` = "research"
   - `EXCHANGE` = "exchange"

2. **CapabilityAction** enum (per D-33):
   - `READ` = "read"
   - `CREATE` = "create"
   - `UPDATE` = "update"
   - `DELETE` = "delete"
   - `MOVE` = "move"
   - `RENAME` = "rename"

3. **Domain** enum (for policy context):
   - `USER_VAULT` = "user-vault"
   - `AGENT_BRAIN` = "agent-brain"
   - `EXCHANGE` = "exchange"
   - `RESEARCH` = "research"
   - `RAW` = "raw"
   - `RUNTIME` = "runtime"

Export all enums for use by other modules.
  </action>
  <verify>
python -c "from core.policy import CapabilityGroup, CapabilityAction, Domain; print('OK')"</verify>
  <done>CapabilityGroup has 4 values, CapabilityAction has 6 values, Domain has 6 values</done>
</task>

<task type="auto">
  <name>Task 2: Create policy models</name>
  <files>src/core/policy/models.py</files>
  <action>
Create `src/core/policy/models.py` with:

1. **SensitivityLevel** enum:
   - `PUBLIC` = 0
   - `INTERNAL` = 1
   - `CONFIDENTIAL` = 2
   - `RESTRICTED` = 3

2. **NoteType** enum (from Phase 1 note kinds):
   - `DAILY`, `PROJECT`, `AREA`, `RESOURCE`, `FLEETING`, `PERMANENT`, `RESEARCH_NOTE`, `SOURCE_NOTE`, `SYNTHESIS_NOTE`, `INDEX_NOTE`, `TEMPLATE_INSTANCE`

3. **PolicyOutcome** enum (per D-34-D-38):
   - `ALLOW_DIRECT` = "allow_direct" — operation allowed immediately
   - `ALLOW_PATCH_ONLY` = "allow_patch_only" — requires Exchange Zone patch flow
   - `ALLOW_IN_EXCHANGE_ONLY` = "allow_in_exchange_only" — only via Exchange Zone
   - `ALLOW_WITH_APPROVAL` = "allow_with_approval" — requires human approval
   - `DENY` = "deny" — operation blocked

4. **PolicyRequest** dataclass:
   - `actor: str` — who is performing the action
   - `capability_group: CapabilityGroup`
   - `action: CapabilityAction`
   - `domain: Domain`
   - `path: str | None` — note path being accessed
   - `note_type: NoteType | None` — type of note if known
   - `sensitivity: SensitivityLevel` — sensitivity level

5. **PolicyResult** dataclass:
   - `outcome: PolicyOutcome`
   - `reason: str` — human-readable explanation
   - `matched_rule: str | None` — which rule matched (for audit)

6. **PolicyRule** dataclass:
   - `id: str`
   - `actor: str | None` — None = any actor
   - `capability_group: CapabilityGroup | None`
   - `action: CapabilityAction | None`
   - `domain: Domain | None`
   - `path_pattern: str | None` — glob pattern for path matching
   - `note_type: NoteType | None`
   - `sensitivity: SensitivityLevel | None`
   - `outcome: PolicyOutcome`
   - `priority: int` — higher = more specific (per D-40)

Export all types.
  </action>
  <verify>
python -c "from core.policy.models import PolicyRequest, PolicyOutcome, PolicyResult, PolicyRule; print('OK')"</verify>
  <done>PolicyRequest, PolicyOutcome, PolicyResult, PolicyRule, SensitivityLevel, NoteType all defined</done>
</task>

<task type="auto">
  <name>Task 3: Create policy evaluator</name>
  <files>src/core/policy/evaluator.py</files>
  <action>
Create `src/core/policy/evaluator.py` with **PolicyEvaluator** class:

```python
class PolicyEvaluator:
    def __init__(self, rules: list[PolicyRule] | None = None)
    def add_rule(self, rule: PolicyRule) -> None
    def remove_rule(self, rule_id: str) -> None
    def evaluate(self, request: PolicyRequest) -> PolicyResult
```

**evaluate() logic** (per D-39-D-40):
1. Find all rules that match the request (field is None or equals request field)
2. Sort by priority descending (most specific first)
3. Return first matching rule's outcome
4. If no rules match, return default outcome based on action:
   - READ → ALLOW_DIRECT (per D-41)
   - CREATE → ALLOW_IN_EXCHANGE_ONLY (per D-42)
   - UPDATE → ALLOW_PATCH_ONLY (per D-43)
   - DELETE/MOVE/RENAME → DENY (per D-44)

**Rule matching**:
- None field in rule = wildcard (matches anything)
- path_pattern uses fnmatch-style glob matching
- Compare note_type and sensitivity for exact match

**Priority calculation** (D-40: most specific wins):
- path matches: +100
- note_type matches: +50
- sensitivity matches: +40
- domain matches: +30
- action matches: +20
- capability_group matches: +10
- actor matches: +5

Emit policy evaluation via EventBus using new `POLICY_EVALUATED` event type.

Import CapabilityGroup, CapabilityAction, Domain from enums.
Import PolicyRequest, PolicyOutcome, PolicyResult, PolicyRule from models.
Import emit, EventType from core.events.
  </action>
  <verify>
python -c "
from core.policy import PolicyEvaluator
from core.policy.models import PolicyRequest, PolicyOutcome, PolicyRule, SensitivityLevel, NoteType
from core.policy.enums import CapabilityGroup, CapabilityAction, Domain

evaluator = PolicyEvaluator()
request = PolicyRequest(actor='agent', capability_group=CapabilityGroup.VAULT, action=CapabilityAction.READ, domain=Domain.USER_VAULT, path=None, note_type=None, sensitivity=SensitivityLevel.INTERNAL)
result = evaluator.evaluate(request)
assert result.outcome == PolicyOutcome.ALLOW_DIRECT, f'Expected ALLOW_DIRECT for READ, got {result.outcome}'
print('Policy evaluator basic test passed')
"</verify>
  <done>PolicyEvaluator can evaluate requests and return correct outcomes based on rules and defaults</done>
</task>

<task type="auto">
  <name>Task 4: Create policy module init and event types</name>
  <files>src/core/policy/__init__.py</files>
  <action>
Create `src/core/policy/__init__.py` that re-exports all public types:

```python
from core.policy.enums import CapabilityGroup, CapabilityAction, Domain, SensitivityLevel, NoteType
from core.policy.models import PolicyRequest, PolicyOutcome, PolicyResult, PolicyRule
from core.policy.evaluator import PolicyEvaluator

__all__ = [
    "CapabilityGroup",
    "CapabilityAction",
    "Domain",
    "SensitivityLevel",
    "NoteType",
    "PolicyRequest",
    "PolicyOutcome",
    "PolicyResult",
    "PolicyRule",
    "PolicyEvaluator",
]
```

Also add `POLICY_EVALUATED` event type to `src/core/event_bus.py` EventType enum:

```python
# Policy events
POLICY_EVALUATED = "policy.evaluated"
POLICY_DENIED = "policy.denied"
```
  </action>
  <verify>
python -c "from core.policy import PolicyEvaluator, PolicyRequest, PolicyOutcome, PolicyResult, PolicyRule; print('All exports OK')"</verify>
  <done>Policy module has clean public API exported via __init__.py</done>
</task>

</tasks>

<verification>
1. `from core.policy import CapabilityGroup, CapabilityAction, Domain` works
2. `from core.policy import PolicyEvaluator, PolicyRequest, PolicyOutcome` works
3. PolicyEvaluator with no rules: READ returns ALLOW_DIRECT, CREATE returns ALLOW_IN_EXCHANGE_ONLY, UPDATE returns ALLOW_PATCH_ONLY, DELETE/MOVE/RENAME return DENY
4. PolicyEvaluator with matching rule returns that rule's outcome
5. Higher priority rules win over lower priority rules
</verification>

<success_criteria>
- All 4 capability groups defined (vault, agent, research, exchange)
- All 6 capability actions defined (read, create, update, delete, move, rename)
- All 5 policy outcomes defined
- Policy evaluator returns correct outcomes for all action types
- Policy evaluator matches rules by specificity (path > note_type > sensitivity > domain > actor)
</success_criteria>

<output>
After completion, create `.planning/phases/03-policy-engine/03-01-SUMMARY.md`
</output>

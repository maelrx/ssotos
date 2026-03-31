"""Policy evaluator — matches requests against rules using specificity-based priority."""
import fnmatch
from core.events import emit, EventType
from core.policy.enums import CapabilityAction, CapabilityGroup, Domain
from core.policy.models import PolicyOutcome, PolicyRequest, PolicyResult, PolicyRule


# Priority scoring per D-40: most specific wins
_PRIORITY_PATH = 100
_PRIORITY_NOTE_TYPE = 50
_PRIORITY_SENSITIVITY = 40
_PRIORITY_DOMAIN = 30
_PRIORITY_ACTION = 20
_PRIORITY_CAPABILITY_GROUP = 10
_PRIORITY_ACTOR = 5


def _calculate_rule_priority(rule: PolicyRule, request: PolicyRequest) -> int:
    """Calculate specificity score for a rule given a request."""
    score = 0
    # path matches: +100
    if rule.path_pattern and request.path:
        if fnmatch.fnmatch(request.path, rule.path_pattern):
            score += _PRIORITY_PATH
    # note_type matches: +50
    if rule.note_type is not None and request.note_type is not None:
        if rule.note_type == request.note_type:
            score += _PRIORITY_NOTE_TYPE
    # sensitivity matches: +40
    if rule.sensitivity is not None:
        if rule.sensitivity == request.sensitivity:
            score += _PRIORITY_SENSITIVITY
        elif rule.sensitivity > request.sensitivity:
            score += _PRIORITY_SENSITIVITY // 2
    # domain matches: +30
    if rule.domain is not None and request.domain is not None:
        if rule.domain == request.domain:
            score += _PRIORITY_DOMAIN
    # action matches: +20
    if rule.action is not None and request.action is not None:
        if rule.action == request.action:
            score += _PRIORITY_ACTION
    # capability_group matches: +10
    if rule.capability_group is not None and request.capability_group is not None:
        if rule.capability_group == request.capability_group:
            score += _PRIORITY_CAPABILITY_GROUP
    # actor matches: +5
    if rule.actor is not None and request.actor is not None:
        if rule.actor == request.actor:
            score += _PRIORITY_ACTOR
    return score


def _rule_matches(rule: PolicyRule, request: PolicyRequest) -> bool:
    """Check if a rule matches a request (None = wildcard)."""
    if rule.actor is not None and rule.actor != request.actor:
        return False
    if rule.capability_group is not None and rule.capability_group != request.capability_group:
        return False
    if rule.action is not None and rule.action != request.action:
        return False
    if rule.domain is not None and rule.domain != request.domain:
        return False
    if rule.path_pattern is not None and request.path is not None:
        if not fnmatch.fnmatch(request.path, rule.path_pattern):
            return False
    if rule.note_type is not None and request.note_type is not None:
        if rule.note_type != request.note_type:
            return False
    if rule.sensitivity is not None:
        if rule.sensitivity != request.sensitivity:
            return False
    return True


def _default_outcome(action: CapabilityAction) -> PolicyOutcome:
    """Return default outcome based on action per D-41-D-44."""
    if action == CapabilityAction.READ:
        return PolicyOutcome.ALLOW_DIRECT
    if action == CapabilityAction.CREATE:
        return PolicyOutcome.ALLOW_IN_EXCHANGE_ONLY
    if action == CapabilityAction.UPDATE:
        return PolicyOutcome.ALLOW_PATCH_ONLY
    # DELETE, MOVE, RENAME -> DENY
    return PolicyOutcome.DENY


def _default_reason(action: CapabilityAction) -> str:
    """Human-readable default reason."""
    if action == CapabilityAction.READ:
        return "Read is allowed by default (D-41)"
    if action == CapabilityAction.CREATE:
        return "Create requires Exchange Zone flow (D-42)"
    if action == CapabilityAction.UPDATE:
        return "Update requires patch-first flow (D-43)"
    return "Delete/move/rename are gated (D-44)"


class PolicyEvaluator:
    """Evaluates policy requests against rules using specificity-based priority."""

    def __init__(self, rules: list[PolicyRule] | None = None) -> None:
        self._rules: list[PolicyRule] = list(rules) if rules else []

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a policy rule."""
        self._rules.append(rule)

    def remove_rule(self, rule_id: str) -> None:
        """Remove a policy rule by id."""
        self._rules = [r for r in self._rules if r.id != rule_id]

    def evaluate(self, request: PolicyRequest) -> PolicyResult:
        """Evaluate a policy request and return the outcome.

        Finds all matching rules, sorts by priority descending,
        returns the highest-priority match or a default outcome.
        """
        matching_rules: list[tuple[PolicyRule, int]] = []
        for rule in self._rules:
            if _rule_matches(rule, request):
                priority = _calculate_rule_priority(rule, request)
                matching_rules.append((rule, priority))

        # Sort by priority descending
        matching_rules.sort(key=lambda x: x[1], reverse=True)

        if matching_rules:
            best_rule, best_priority = matching_rules[0]
            result = PolicyResult(
                outcome=best_rule.outcome,
                reason=f"Matched rule '{best_rule.id}' with priority {best_priority}",
                matched_rule=best_rule.id,
            )
        else:
            outcome = _default_outcome(request.action)
            result = PolicyResult(
                outcome=outcome,
                reason=_default_reason(request.action),
                matched_rule=None,
            )

        # Emit audit event via EventBus
        try:
            emit(
                EventType.POLICY_EVALUATED,
                actor=request.actor,
                domain=request.domain.value,
                action=request.action.value,
                capability_group=request.capability_group.value,
                outcome=result.outcome.value,
                matched_rule=result.matched_rule,
                reason=result.reason,
            )
        except Exception:
            # EventBus may not be fully initialized during early bootstrap
            pass

        return result


__all__ = ["PolicyEvaluator"]

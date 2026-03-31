"""Policy service wrapper — single integration point for all services with audit logging.

Per F6-04: All sensitive mutations call policy.check() before execution.
All policy evaluations are logged via EventBus.
"""
from core.events import emit, EventType
from core.policy.enums import CapabilityAction, CapabilityGroup, Domain
from core.policy.evaluator import PolicyEvaluator
from core.policy.models import PolicyOutcome, PolicyRequest, PolicyResult, PolicyRule
from core.policy.rules import PolicyRulesService


class PolicyDeniedException(Exception):
    """Raised when a policy check denies an operation."""

    def __init__(self, result: PolicyResult):
        self.result = result
        super().__init__(f"Policy denied: {result.reason}")


class PolicyService:
    """Policy service wrapper that integrates with EventBus for audit logging.

    All mutations should go through check() before execution.

    Single integration point for GitService, ProposalService, and any other
    service that needs policy enforcement.
    """

    def __init__(self, rules_service: PolicyRulesService | None = None) -> None:
        self._rules_service = rules_service or PolicyRulesService()
        self._evaluator = PolicyEvaluator(rules=self._rules_service.list_rules())

    def check(self, request: PolicyRequest) -> PolicyResult:
        """Evaluate a policy request and return the result.

        Emits POLICY_EVALUATED event for every check.
        Emits POLICY_DENIED event when outcome is DENY.
        """
        result = self._evaluator.evaluate(request)

        # Emit denial event on top of the evaluation event
        if result.outcome == PolicyOutcome.DENY:
            try:
                emit(
                    EventType.POLICY_DENIED,
                    actor=request.actor,
                    domain=request.domain.value if request.domain else None,
                    action=request.action.value if request.action else None,
                    capability_group=request.capability_group.value if request.capability_group else None,
                    outcome=result.outcome.value,
                    matched_rule=result.matched_rule,
                    reason=result.reason,
                )
            except Exception:
                # EventBus may not be fully initialized during early bootstrap
                pass

        return result

    def check_or_raise(self, request: PolicyRequest) -> PolicyResult:
        """Evaluate policy and raise if not ALLOW_DIRECT or ALLOW_PATCH_ONLY.

        Raises:
            PolicyDeniedException: If outcome is DENY or ALLOW_WITH_APPROVAL.
        """
        result = self.check(request)
        if result.outcome in (PolicyOutcome.DENY, PolicyOutcome.ALLOW_WITH_APPROVAL):
            raise PolicyDeniedException(result)
        return result


__all__ = ["PolicyService", "PolicyDeniedException"]

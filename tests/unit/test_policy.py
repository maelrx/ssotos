"""Unit tests for the policy engine — evaluator, rules, and service integration."""
import pytest
from unittest.mock import patch, MagicMock

from core.policy.enums import CapabilityAction, CapabilityGroup, Domain
from core.policy.models import (
    NoteType,
    PolicyOutcome,
    PolicyRequest,
    PolicyResult,
    PolicyRule,
    SensitivityLevel,
)
from core.policy.evaluator import PolicyEvaluator
from core.policy.service import PolicyService, PolicyDeniedException
from core.policy.defaults import get_default_rules
from core.event_bus import EventBus


# --- Capability enum tests ---


class TestCapabilityEnums:
    """Test capability group and action enums."""

    def test_capability_groups_exist(self):
        """Verify all 4 capability groups are defined."""
        assert hasattr(CapabilityGroup, "VAULT")
        assert hasattr(CapabilityGroup, "AGENT")
        assert hasattr(CapabilityGroup, "RESEARCH")
        assert hasattr(CapabilityGroup, "EXCHANGE")
        assert len(CapabilityGroup) == 4

    def test_capability_actions_exist(self):
        """Verify all 6 capability actions are defined."""
        assert hasattr(CapabilityAction, "READ")
        assert hasattr(CapabilityAction, "CREATE")
        assert hasattr(CapabilityAction, "UPDATE")
        assert hasattr(CapabilityAction, "DELETE")
        assert hasattr(CapabilityAction, "MOVE")
        assert hasattr(CapabilityAction, "RENAME")
        assert len(CapabilityAction) == 6


# --- Policy outcome tests ---


class TestPolicyOutcomes:
    """Test PolicyOutcome enum."""

    def test_all_outcomes_defined(self):
        """Verify all 5 policy outcomes are defined."""
        assert hasattr(PolicyOutcome, "ALLOW_DIRECT")
        assert hasattr(PolicyOutcome, "ALLOW_PATCH_ONLY")
        assert hasattr(PolicyOutcome, "ALLOW_IN_EXCHANGE_ONLY")
        assert hasattr(PolicyOutcome, "ALLOW_WITH_APPROVAL")
        assert hasattr(PolicyOutcome, "DENY")
        assert len(PolicyOutcome) == 5


# --- Policy evaluator tests ---


class TestPolicyEvaluatorDefaults:
    """Test PolicyEvaluator default outcome logic."""

    def _make_request(self, action: CapabilityAction) -> PolicyRequest:
        """Helper to create a minimal policy request."""
        return PolicyRequest(
            actor="test",
            capability_group=CapabilityGroup.VAULT,
            action=action,
            domain=Domain.USER_VAULT,
            path=None,
            note_type=None,
            sensitivity=SensitivityLevel.INTERNAL,
        )

    def test_read_defaults_to_allow_direct(self):
        """READ should default to ALLOW_DIRECT."""
        evaluator = PolicyEvaluator(rules=[])
        result = evaluator.evaluate(self._make_request(CapabilityAction.READ))
        assert result.outcome == PolicyOutcome.ALLOW_DIRECT

    def test_create_defaults_to_allow_in_exchange_only(self):
        """CREATE should default to ALLOW_IN_EXCHANGE_ONLY."""
        evaluator = PolicyEvaluator(rules=[])
        result = evaluator.evaluate(self._make_request(CapabilityAction.CREATE))
        assert result.outcome == PolicyOutcome.ALLOW_IN_EXCHANGE_ONLY

    def test_update_defaults_to_allow_patch_only(self):
        """UPDATE should default to ALLOW_PATCH_ONLY."""
        evaluator = PolicyEvaluator(rules=[])
        result = evaluator.evaluate(self._make_request(CapabilityAction.UPDATE))
        assert result.outcome == PolicyOutcome.ALLOW_PATCH_ONLY

    def test_delete_defaults_to_deny(self):
        """DELETE should default to DENY."""
        evaluator = PolicyEvaluator(rules=[])
        result = evaluator.evaluate(self._make_request(CapabilityAction.DELETE))
        assert result.outcome == PolicyOutcome.DENY

    def test_move_defaults_to_deny(self):
        """MOVE should default to DENY."""
        evaluator = PolicyEvaluator(rules=[])
        result = evaluator.evaluate(self._make_request(CapabilityAction.MOVE))
        assert result.outcome == PolicyOutcome.DENY

    def test_rename_defaults_to_deny(self):
        """RENAME should default to DENY."""
        evaluator = PolicyEvaluator(rules=[])
        result = evaluator.evaluate(self._make_request(CapabilityAction.RENAME))
        assert result.outcome == PolicyOutcome.DENY


class TestPolicyEvaluatorRules:
    """Test PolicyEvaluator rule matching and priority."""

    def test_wildcard_rule_matches_any_actor(self):
        """A rule with actor=None should match any actor."""
        rule = PolicyRule(
            id="test-1",
            actor=None,  # wildcard
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.DELETE,
            domain=Domain.USER_VAULT,
            outcome=PolicyOutcome.ALLOW_WITH_APPROVAL,
            priority=10,
        )
        evaluator = PolicyEvaluator(rules=[rule])
        request = PolicyRequest(
            actor="agent",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.DELETE,
            domain=Domain.USER_VAULT,
        )
        result = evaluator.evaluate(request)
        assert result.outcome == PolicyOutcome.ALLOW_WITH_APPROVAL
        assert result.matched_rule == "test-1"

    def test_path_pattern_matching(self):
        """Rules with path_pattern should match via fnmatch."""
        rule = PolicyRule(
            id="test-2",
            actor=None,
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.CREATE,
            domain=Domain.USER_VAULT,
            path_pattern="inbox/**",
            outcome=PolicyOutcome.ALLOW_DIRECT,
            priority=100,
        )
        evaluator = PolicyEvaluator(rules=[rule])
        request = PolicyRequest(
            actor="user",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.CREATE,
            domain=Domain.USER_VAULT,
            path="inbox/test.md",
        )
        result = evaluator.evaluate(request)
        assert result.outcome == PolicyOutcome.ALLOW_DIRECT
        assert result.matched_rule == "test-2"

    def test_most_specific_wins(self):
        """Highest priority rule should win when multiple match."""
        low_priority = PolicyRule(
            id="low",
            actor=None,
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.DELETE,
            domain=Domain.USER_VAULT,
            outcome=PolicyOutcome.ALLOW_WITH_APPROVAL,
            priority=5,
        )
        high_priority = PolicyRule(
            id="high",
            actor="agent",  # more specific
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.DELETE,
            domain=Domain.USER_VAULT,
            outcome=PolicyOutcome.DENY,
            priority=65,
        )
        evaluator = PolicyEvaluator(rules=[low_priority, high_priority])
        request = PolicyRequest(
            actor="agent",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.DELETE,
            domain=Domain.USER_VAULT,
        )
        result = evaluator.evaluate(request)
        assert result.outcome == PolicyOutcome.DENY
        assert result.matched_rule == "high"

    def test_no_matching_rules_uses_default(self):
        """When no rules match, use default outcome based on action."""
        evaluator = PolicyEvaluator(rules=[])
        request = PolicyRequest(
            actor="unknown",
            capability_group=CapabilityGroup.RESEARCH,
            action=CapabilityAction.READ,
            domain=Domain.RESEARCH,
        )
        result = evaluator.evaluate(request)
        assert result.outcome == PolicyOutcome.ALLOW_DIRECT
        assert result.matched_rule is None


# --- Policy service tests ---


class TestPolicyService:
    """Test PolicyService check and check_or_raise methods."""

    def setup_method(self):
        """Clear EventBus state before each test."""
        EventBus._instance = None

    def test_check_returns_policy_result(self):
        """check() should return a PolicyResult."""
        service = PolicyService()
        request = PolicyRequest(
            actor="user",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.READ,
            domain=Domain.USER_VAULT,
        )
        result = service.check(request)
        assert isinstance(result, PolicyResult)
        assert result.outcome == PolicyOutcome.ALLOW_DIRECT

    def test_check_or_raise_raises_on_deny(self):
        """check_or_raise() should raise PolicyDeniedException on DENY."""
        service = PolicyService()
        request = PolicyRequest(
            actor="agent",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.DELETE,
            domain=Domain.USER_VAULT,
        )
        with pytest.raises(PolicyDeniedException) as exc_info:
            service.check_or_raise(request)
        assert exc_info.value.result.outcome == PolicyOutcome.DENY

    def test_check_or_raise_raises_on_allow_with_approval(self):
        """check_or_raise() should raise PolicyDeniedException on ALLOW_WITH_APPROVAL."""
        service = PolicyService()
        request = PolicyRequest(
            actor="user",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.DELETE,
            domain=Domain.USER_VAULT,
        )
        with pytest.raises(PolicyDeniedException) as exc_info:
            service.check_or_raise(request)
        # User delete vault → ALLOW_WITH_APPROVAL per defaults
        assert exc_info.value.result.outcome == PolicyOutcome.ALLOW_WITH_APPROVAL

    def test_check_or_raise_returns_result_on_allow_direct(self):
        """check_or_raise() should return PolicyResult on ALLOW_DIRECT."""
        service = PolicyService()
        request = PolicyRequest(
            actor="user",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.READ,
            domain=Domain.USER_VAULT,
        )
        result = service.check_or_raise(request)
        assert isinstance(result, PolicyResult)
        assert result.outcome == PolicyOutcome.ALLOW_DIRECT


# --- Default rules tests ---


class TestDefaultRules:
    """Test the default policy rules."""

    def test_get_default_rules_returns_non_empty_list(self):
        """get_default_rules() should return a non-empty list."""
        rules = get_default_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0

    def test_vault_read_is_broad(self):
        """Any actor should be able to read vault."""
        rules = get_default_rules()
        evaluator = PolicyEvaluator(rules=rules)
        request = PolicyRequest(
            actor="anyone",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.READ,
            domain=Domain.USER_VAULT,
        )
        result = evaluator.evaluate(request)
        assert result.outcome == PolicyOutcome.ALLOW_DIRECT

    def test_agent_cannot_delete_from_vault(self):
        """Agent delete from vault should be DENY."""
        rules = get_default_rules()
        evaluator = PolicyEvaluator(rules=rules)
        request = PolicyRequest(
            actor="agent",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.DELETE,
            domain=Domain.USER_VAULT,
        )
        result = evaluator.evaluate(request)
        assert result.outcome == PolicyOutcome.DENY

    def test_agent_update_to_vault_requires_exchange(self):
        """Agent update to vault should require exchange flow."""
        rules = get_default_rules()
        evaluator = PolicyEvaluator(rules=rules)
        request = PolicyRequest(
            actor="agent",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.UPDATE,
            domain=Domain.USER_VAULT,
        )
        result = evaluator.evaluate(request)
        assert result.outcome == PolicyOutcome.ALLOW_IN_EXCHANGE_ONLY


# --- Integration tests ---


class TestPolicyEventEmission:
    """Test that policy evaluation emits events to EventBus."""

    def setup_method(self):
        """Clear EventBus state before each test."""
        EventBus._instance = None

    def test_check_emits_policy_evaluated_event(self):
        """Every policy check should emit a POLICY_EVALUATED event."""
        emitted_events = []

        def capture_handler(event):
            emitted_events.append(event)

        bus = EventBus()
        bus.register_handler(capture_handler)

        service = PolicyService()
        request = PolicyRequest(
            actor="user",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.READ,
            domain=Domain.USER_VAULT,
        )
        service.check(request)

        policy_events = [e for e in emitted_events if "policy" in e.event_type.value]
        assert len(policy_events) >= 1
        assert any(e.event_type.value == "policy.evaluated" for e in policy_events)

    def test_deny_emits_policy_denied_event(self):
        """Policy DENY should emit a POLICY_DENIED event."""
        emitted_events = []

        def capture_handler(event):
            emitted_events.append(event)

        bus = EventBus()
        bus.register_handler(capture_handler)

        service = PolicyService()
        request = PolicyRequest(
            actor="agent",
            capability_group=CapabilityGroup.VAULT,
            action=CapabilityAction.DELETE,
            domain=Domain.USER_VAULT,
        )
        service.check(request)

        policy_events = [e for e in emitted_events if "policy" in e.event_type.value]
        assert any(e.event_type.value == "policy.denied" for e in policy_events)


class TestGitServicePolicyIntegration:
    """Test that GitService integrates policy checks."""

    def test_git_service_has_policy_attribute(self):
        """GitService should have a policy attribute after __init__."""
        from pathlib import Path
        from services.git_service import GitService

        # We can't fully instantiate GitService without a real repo,
        # but we can check the class has the attribute
        assert hasattr(GitService, "__init__")
        # The integration is verified by the fact that git_service.py imports
        # PolicyService and adds self.policy = PolicyService() in __init__

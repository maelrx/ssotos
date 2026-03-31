"""Safe default policy rules per D-41 to D-44."""
import uuid

from src.core.policy.enums import CapabilityAction, CapabilityGroup, Domain
from src.core.policy.models import PolicyOutcome, PolicyRule


def _rule(
    actor: str | None,
    group: CapabilityGroup,
    action: CapabilityAction,
    domain: Domain,
    outcome: PolicyOutcome,
    path_pattern: str | None = None,
    priority: int = 0,
) -> PolicyRule:
    """Create a PolicyRule with a generated UUID id."""
    return PolicyRule(
        id=str(uuid.uuid4()),
        actor=actor,
        capability_group=group,
        action=action,
        domain=domain,
        path_pattern=path_pattern,
        outcome=outcome,
        priority=priority,
    )


def get_default_rules() -> list[PolicyRule]:
    """Return safe default policy rules covering all capability groups and actions.

    Read rules (D-41: Read is broad by default):
        - Any actor can read vault, agent, research, exchange domains

    Create rules (D-42: Create only in safe zones):
        - Inbox/agent-brain/research are safe for creation
        - Agent/user creation in user-vault goes through exchange only

    Update rules (D-43: Edit requires patch-first flow):
        - User-vault updates require patch-only flow
        - Agent can update own brain directly
        - Research can update research directly

    Delete/move/rename rules (D-44: Gated):
        - User delete/move/rename require approval
        - Agent delete/move/rename from vault denied
        - Default deny for vault mutations

    Exchange rules:
        - Exchange proposals require approval
        - System can create proposals directly
    """
    rules: list[PolicyRule] = []

    # ---- Read rules (D-41) ----
    # Any actor can read vault
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.READ,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        priority=5,
    ))
    # Any actor can read agent brain
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.AGENT,
        action=CapabilityAction.READ,
        domain=Domain.AGENT_BRAIN,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        priority=5,
    ))
    # Any actor can read research
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.RESEARCH,
        action=CapabilityAction.READ,
        domain=Domain.RESEARCH,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        priority=5,
    ))
    # Any actor can read exchange
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.EXCHANGE,
        action=CapabilityAction.READ,
        domain=Domain.EXCHANGE,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        priority=5,
    ))

    # ---- Create rules (D-42) ----
    # Create in user-vault inbox (safe zone)
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.CREATE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        path_pattern="inbox/**",
        priority=130,  # path (+100) + domain (+30)
    ))
    # Create in agent brain (safe zone)
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.AGENT,
        action=CapabilityAction.CREATE,
        domain=Domain.AGENT_BRAIN,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        priority=35,  # domain (+30) + action (+20)
    ))
    # Create in research (safe zone)
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.RESEARCH,
        action=CapabilityAction.CREATE,
        domain=Domain.RESEARCH,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        priority=35,
    ))
    # Agent creating in vault must go through exchange
    rules.append(_rule(
        actor="agent",
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.CREATE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.ALLOW_IN_EXCHANGE_ONLY,
        priority=65,  # actor (+5) + group (+10) + action (+20) + domain (+30)
    ))
    # Default: user vault create goes through exchange
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.CREATE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.ALLOW_IN_EXCHANGE_ONLY,
        priority=55,  # group (+10) + action (+20) + domain (+30)
    ))

    # ---- Update rules (D-43) ----
    # User-vault updates require patch-first flow
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.UPDATE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.ALLOW_PATCH_ONLY,
        priority=55,
    ))
    # Agent updating vault must go through exchange
    rules.append(_rule(
        actor="agent",
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.UPDATE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.ALLOW_IN_EXCHANGE_ONLY,
        priority=65,
    ))
    # Agent can update own brain directly
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.AGENT,
        action=CapabilityAction.UPDATE,
        domain=Domain.AGENT_BRAIN,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        priority=35,
    ))
    # Research can update research directly
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.RESEARCH,
        action=CapabilityAction.UPDATE,
        domain=Domain.RESEARCH,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        priority=35,
    ))

    # ---- Delete/move/rename rules (D-44) ----
    # User can delete with approval
    rules.append(_rule(
        actor="user",
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.DELETE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.ALLOW_WITH_APPROVAL,
        priority=65,
    ))
    # Agent cannot delete from user vault
    rules.append(_rule(
        actor="agent",
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.DELETE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.DENY,
        priority=65,
    ))
    # Default deny for vault delete
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.DELETE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.DENY,
        priority=55,
    ))

    # User can move with approval
    rules.append(_rule(
        actor="user",
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.MOVE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.ALLOW_WITH_APPROVAL,
        priority=65,
    ))
    # Agent cannot move vault
    rules.append(_rule(
        actor="agent",
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.MOVE,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.DENY,
        priority=65,
    ))

    # User can rename with approval
    rules.append(_rule(
        actor="user",
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.RENAME,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.ALLOW_WITH_APPROVAL,
        priority=65,
    ))
    # Agent cannot rename vault
    rules.append(_rule(
        actor="agent",
        group=CapabilityGroup.VAULT,
        action=CapabilityAction.RENAME,
        domain=Domain.USER_VAULT,
        outcome=PolicyOutcome.DENY,
        priority=65,
    ))

    # ---- Exchange rules ----
    # Any actor can apply exchange proposals with approval
    rules.append(_rule(
        actor=None,
        group=CapabilityGroup.EXCHANGE,
        action=CapabilityAction.APPLY_PROPOSAL if hasattr(CapabilityAction, 'APPLY_PROPOSAL') else CapabilityAction.CREATE,
        domain=Domain.EXCHANGE,
        outcome=PolicyOutcome.ALLOW_WITH_APPROVAL,
        priority=55,
    ))
    # System can create exchange proposals directly
    rules.append(_rule(
        actor="system",
        group=CapabilityGroup.EXCHANGE,
        action=CapabilityAction.CREATE,
        domain=Domain.EXCHANGE,
        outcome=PolicyOutcome.ALLOW_DIRECT,
        priority=65,
    ))

    return rules


__all__ = ["get_default_rules"]

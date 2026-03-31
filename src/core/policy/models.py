"""Policy models — requests, results, rules, and supporting enums."""
from dataclasses import dataclass
from enum import Enum

from src.core.policy.enums import CapabilityAction, CapabilityGroup, Domain


class SensitivityLevel(int, Enum):
    """Sensitivity level for notes."""
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3


class NoteType(str, Enum):
    """Note kinds from Phase 1."""
    DAILY = "daily"
    PROJECT = "project"
    AREA = "area"
    RESOURCE = "resource"
    FLEETING = "fleeting"
    PERMANENT = "permanent"
    RESEARCH_NOTE = "research_note"
    SOURCE_NOTE = "source_note"
    SYNTHESIS_NOTE = "synthesis_note"
    INDEX_NOTE = "index_note"
    TEMPLATE_INSTANCE = "template_instance"


class PolicyOutcome(str, Enum):
    """Policy outcomes per D-34-D-38."""
    ALLOW_DIRECT = "allow_direct"
    ALLOW_PATCH_ONLY = "allow_patch_only"
    ALLOW_IN_EXCHANGE_ONLY = "allow_in_exchange_only"
    ALLOW_WITH_APPROVAL = "allow_with_approval"
    DENY = "deny"


@dataclass(frozen=True)
class PolicyRequest:
    """Request for policy evaluation."""
    actor: str
    capability_group: CapabilityGroup
    action: CapabilityAction
    domain: Domain
    path: str | None = None
    note_type: NoteType | None = None
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL


@dataclass(frozen=True)
class PolicyResult:
    """Result of policy evaluation."""
    outcome: PolicyOutcome
    reason: str
    matched_rule: str | None = None


@dataclass
class PolicyRule:
    """A policy rule with optional match fields (None = wildcard)."""
    id: str
    actor: str | None = None
    capability_group: CapabilityGroup | None = None
    action: CapabilityAction | None = None
    domain: Domain | None = None
    path_pattern: str | None = None
    note_type: NoteType | None = None
    sensitivity: SensitivityLevel | None = None
    outcome: PolicyOutcome = PolicyOutcome.DENY
    priority: int = 0


__all__ = [
    "SensitivityLevel",
    "NoteType",
    "PolicyOutcome",
    "PolicyRequest",
    "PolicyResult",
    "PolicyRule",
]

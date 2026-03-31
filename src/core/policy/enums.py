"""Policy enums — capability groups, actions, and domain types."""
from enum import Enum


class CapabilityGroup(str, Enum):
    """Four capability groups per D-32."""
    VAULT = "vault"
    AGENT = "agent"
    RESEARCH = "research"
    EXCHANGE = "exchange"


class CapabilityAction(str, Enum):
    """Fine-grained actions per D-33."""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    RENAME = "rename"


class Domain(str, Enum):
    """Domain types for policy context."""
    USER_VAULT = "user-vault"
    AGENT_BRAIN = "agent-brain"
    EXCHANGE = "exchange"
    RESEARCH = "research"
    RAW = "raw"
    RUNTIME = "runtime"


__all__ = [
    "CapabilityGroup",
    "CapabilityAction",
    "Domain",
]

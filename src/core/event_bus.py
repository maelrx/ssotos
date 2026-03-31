"""EventBus for audit logging — all service mutations emit events."""
from datetime import datetime
from enum import Enum
from typing import Callable, Any
from dataclasses import dataclass, field


class EventType(Enum):
    """Event types for audit logging."""
    # Git events
    GIT_REPO_INITIALIZED = "git.repo.initialized"
    GIT_BRANCH_CREATED = "git.branch.created"
    GIT_BRANCH_DELETED = "git.branch.deleted"
    GIT_WORKTREE_CREATED = "git.worktree.created"
    GIT_WORKTREE_REMOVED = "git.worktree.removed"
    GIT_COMMIT_CREATED = "git.commit.created"
    GIT_MERGE_COMPLETED = "git.merge.completed"
    GIT_PATCH_APPLIED = "git.patch.applied"

    # Proposal events
    PROPOSAL_CREATED = "proposal.created"
    PROPOSAL_SUBMITTED = "proposal.submitted"
    PROPOSAL_APPROVED = "proposal.approved"
    PROPOSAL_REJECTED = "proposal.rejected"
    PROPOSAL_APPLIED = "proposal.applied"
    PROPOSAL_ROLLBACK = "proposal.rollback"

    # Exchange events
    PATCH_BUNDLE_CREATED = "exchange.patch.created"
    REVIEW_BUNDLE_CREATED = "exchange.review.created"


@dataclass
class Event:
    """Audit event with provenance."""
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    actor: str = "system"
    domain: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "actor": self.actor,
            "domain": self.domain,
            "metadata": self.metadata
        }


class EventBus:
    """Singleton EventBus for audit logging.

    All services emit events via this bus for traceability."""

    _instance: "EventBus | None" = None
    _handlers: list[Callable[[Event], None]] = []
    _event_log: list[Event] = []

    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = []
            cls._instance._event_log = []
        return cls._instance

    def emit(
        self,
        event_type: EventType,
        actor: str = "system",
        domain: str | None = None,
        **metadata
    ) -> None:
        """Emit an event to all handlers."""
        event = Event(
            event_type=event_type,
            actor=actor,
            domain=domain,
            metadata=metadata
        )
        self._event_log.append(event)
        for handler in self._handlers:
            handler(event)

    def register_handler(self, handler: Callable[[Event], None]) -> None:
        """Register an event handler."""
        self._handlers.append(handler)

    def get_events(
        self,
        event_type: EventType | None = None,
        domain: str | None = None,
        limit: int = 100
    ) -> list[Event]:
        """Get recent events, optionally filtered."""
        events = self._event_log
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if domain:
            events = [e for e in events if e.domain == domain]
        return events[-limit:]

    def clear(self) -> None:
        """Clear event log (for testing)."""
        self._event_log.clear()

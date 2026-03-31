"""Events module — re-exports EventType and Event for convenience."""
from core.event_bus import EventBus, Event, EventType

__all__ = ["EventBus", "Event", "EventType", "emit"]


def emit(
    event_type: EventType,
    actor: str = "system",
    domain: str | None = None,
    **metadata
) -> None:
    """Emit an event via the singleton EventBus."""
    EventBus().emit(event_type, actor=actor, domain=domain, **metadata)

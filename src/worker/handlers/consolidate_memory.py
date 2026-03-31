"""Handler for consolidate_memory job type per D-77.

Consolidates agent memory from session summaries.
Input: {workspace_id: UUID, agent_id: UUID, memory_type: "episodic"|"semantic"}
"""
from collections import Counter
from datetime import datetime
from typing import Any

import structlog

from src.schemas.agent import MemoryUpdate
from src.services.agent_brain_service import AgentBrainService

logger = structlog.get_logger(__name__)

# MEMORY_CURATION_CRITERIA per D-77
MEMORY_CURATION_CRITERIA = {
    "recurrence": 3,  # Must appear in at least 3 sessions
    "temporal_stability": 0.7,  # 70% consistency
    "max_per_category": 10,  # Limit to top 10 per category
}


async def handle_consolidate_memory(input_data: dict) -> dict:
    """Handle consolidate_memory job per D-77.

    Args:
        input_data: {
            workspace_id: UUID,
            agent_id: UUID,
            memory_type: "episodic" | "semantic"
        }

    Returns:
        {
            workspace_id: str,
            agent_id: str,
            memory_type: str,
            memories_consolidated: int,
            patterns_found: int,
            status: str
        }
    """
    workspace_id = input_data.get("workspace_id")
    agent_id = input_data.get("agent_id")
    memory_type = input_data.get("memory_type", "episodic")

    logger.info(
        "consolidate_memory_start",
        workspace_id=workspace_id,
        agent_id=agent_id,
        memory_type=memory_type,
    )

    brain_service = AgentBrainService()

    # 1. List all sessions from brain_service
    sessions_response = await brain_service.list_sessions()
    sessions = sessions_response.sessions

    logger.info("sessions_retrieved", count=len(sessions))

    # 2. Read current MEMORY.md
    current_memory = await brain_service.read_memory()
    existing_learnings = set(current_memory.content.high_value_learnings)
    existing_patterns = set(current_memory.content.patterns_established)
    existing_heuristics = set(current_memory.content.operational_heuristics)

    # 3. Extract patterns from session summaries via _extract_patterns()
    patterns = _extract_patterns(sessions, memory_type)

    # 4. Apply curation criteria via _curate_patterns()
    curated = _curate_patterns(patterns, sessions)

    # 5. Update MEMORY.md with curated patterns
    new_high_value_learnings = list(existing_learnings | set(curated["high_value_learnings"]))
    new_patterns_established = list(existing_patterns | set(curated["patterns_established"]))
    new_operational_heuristics = list(existing_heuristics | set(curated["operational_heuristics"]))

    # Limit to max_per_category
    new_high_value_learnings = new_high_value_learnings[: MEMORY_CURATION_CRITERIA["max_per_category"]]
    new_patterns_established = new_patterns_established[: MEMORY_CURATION_CRITERIA["max_per_category"]]
    new_operational_heuristics = new_operational_heuristics[: MEMORY_CURATION_CRITERIA["max_per_category"]]

    # Apply update if we have new patterns
    memories_consolidated = 0
    if curated["high_value_learnings"] or curated["patterns_established"] or curated["operational_heuristics"]:
        update = MemoryUpdate(
            high_value_learnings=new_high_value_learnings,
            patterns_established=new_patterns_established,
            operational_heuristics=new_operational_heuristics,
        )
        await brain_service.update_memory(update)
        memories_consolidated = (
            len(curated["high_value_learnings"])
            + len(curated["patterns_established"])
            + len(curated["operational_heuristics"])
        )
        logger.info("memory_updated", memories_consolidated=memories_consolidated)

    patterns_found = (
        len(curated["high_value_learnings"])
        + len(curated["patterns_established"])
        + len(curated["operational_heuristics"])
    )

    result = {
        "workspace_id": str(workspace_id),
        "agent_id": str(agent_id),
        "memory_type": memory_type,
        "memories_consolidated": memories_consolidated,
        "patterns_found": patterns_found,
        "status": "completed",
    }

    logger.info("consolidate_memory_complete", **result)
    return result


def _extract_patterns(sessions: list, memory_type: str) -> dict[str, list[str]]:
    """Extract patterns from session summaries per D-77.

    Tracks recurring decisions, questions, next_steps using Counter.

    Args:
        sessions: List of SessionResponse objects
        memory_type: "episodic" or "semantic"

    Returns:
        dict with high_value_learnings, patterns_established, operational_heuristics
    """
    decision_counter: Counter[str] = Counter()
    question_counter: Counter[str] = Counter()
    next_step_counter: Counter[str] = Counter()
    learning_counter: Counter[str] = Counter()

    for session in sessions:
        if not session.summary:
            continue

        # Extract key decisions
        for decision in session.summary.key_decisions:
            # Normalize decision text
            normalized = decision.lower().strip()
            if len(normalized) > 5:
                decision_counter[normalized] += 1

        # Extract open questions
        for question in session.summary.open_questions:
            normalized = question.lower().strip()
            if len(normalized) > 5:
                question_counter[normalized] += 1

        # Extract next steps
        for next_step in session.summary.next_steps:
            normalized = next_step.lower().strip()
            if len(normalized) > 5:
                next_step_counter[normalized] += 1

    # Convert to high-value learnings (decisions that appear multiple times)
    high_value_learnings = [
        f"Decided: {decision}" for decision, count in decision_counter.items() if count >= MEMORY_CURATION_CRITERIA["recurrence"]
    ]

    # Patterns established (questions that appear multiple times)
    patterns_established = [
        f"Question recurred: {question}" for question, count in question_counter.items() if count >= MEMORY_CURATION_CRITERIA["recurrence"]
    ]

    # Operational heuristics (next steps that appear multiple times)
    operational_heuristics = [
        f"Often leads to: {next_step}" for next_step, count in next_step_counter.items() if count >= MEMORY_CURATION_CRITERIA["recurrence"]
    ]

    logger.info(
        "patterns_extracted",
        learnings=len(high_value_learnings),
        patterns=len(patterns_established),
        heuristics=len(operational_heuristics),
    )

    return {
        "high_value_learnings": high_value_learnings,
        "patterns_established": patterns_established,
        "operational_heuristics": operational_heuristics,
    }


def _curate_patterns(patterns: dict, sessions: list) -> dict[str, list[str]]:
    """Apply curation criteria per D-77.

    Checks temporal stability across last 10 sessions.
    Filters by stability >= 0.7.

    Args:
        patterns: dict with high_value_learnings, patterns_established, operational_heuristics
        sessions: List of SessionResponse objects for temporal analysis

    Returns:
        Curated patterns dict
    """
    recurrence_threshold = MEMORY_CURATION_CRITERIA["recurrence"]
    stability_threshold = MEMORY_CURATION_CRITERIA["temporal_stability"]

    # Take last 10 sessions for temporal analysis
    recent_sessions = sorted(sessions, key=lambda s: s.updated_at or datetime.min) if sessions else []
    recent_sessions = recent_sessions[-10:]

    curated = {
        "high_value_learnings": [],
        "patterns_established": [],
        "operational_heuristics": [],
    }

    # Calculate temporal stability for each category
    for category in ["high_value_learnings", "patterns_established", "operational_heuristics"]:
        for pattern in patterns.get(category, []):
            # Count how many recent sessions this pattern appears in
            appearances = 0
            for session in recent_sessions:
                if not session.summary:
                    continue
                # Check if pattern text is in any of the summary fields
                summary_text = " ".join(
                    [
                        session.summary.what_happened,
                        " ".join(session.summary.key_decisions),
                        " ".join(session.summary.open_questions),
                        " ".join(session.summary.next_steps),
                    ]
                ).lower()
                if pattern.lower() in summary_text:
                    appearances += 1

            # Calculate temporal stability
            stability = appearances / len(recent_sessions) if recent_sessions else 0

            # Include if meets both recurrence and stability criteria
            if stability >= stability_threshold:
                curated[category].append(pattern)
                logger.debug(
                    "pattern_curated",
                    category=category,
                    pattern=pattern[:50],
                    stability=stability,
                )

    # Apply max per category limit
    for category in curated:
        curated[category] = curated[category][: MEMORY_CURATION_CRITERIA["max_per_category"]]

    logger.info("patterns_curated", ** {f"{k}_count": len(v) for k, v in curated.items()})

    return curated

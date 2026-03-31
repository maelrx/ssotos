"""Handler for reflect_agent job type per D-71, D-82.

Triggers agent self-reflection and memory consolidation.
Input: {workspace_id, agent_id, session_id, session_trace?, brain_mutations?}
"""
from collections import Counter
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import structlog

from src.schemas.agent import (
    MemoryUpdate,
    SessionSummary,
    SkillTrigger,
    SoulUpdate,
    UserProfileUpdate,
)
from src.services.agent_brain_service import AgentBrainService
from src.services.skill_service import SkillService

logger = structlog.get_logger(__name__)


async def handle_reflect_agent(input_data: dict) -> dict:
    """Handle reflect_agent job per D-71, D-82.

    Processes brain mutations, generates session summaries, and extracts heuristics.

    Args:
        input_data: {
            workspace_id: UUID,
            agent_id: UUID,
            session_id: UUID,
            session_trace?: list[dict],
            brain_mutations?: dict with soul_update, memory_update, user_update
        }

    Returns:
        {
            workspace_id: str,
            agent_id: str,
            session_id: str,
            session_summary_id: str | None,
            insights_generated: int,
            skills_created: int,
            brain_mutations_applied: int,
            status: str
        }
    """
    workspace_id = input_data.get("workspace_id")
    agent_id = input_data.get("agent_id")
    session_id = input_data.get("session_id")
    session_trace = input_data.get("session_trace", [])
    brain_mutations = input_data.get("brain_mutations", {})

    logger.info(
        "reflect_agent_start",
        workspace_id=workspace_id,
        agent_id=agent_id,
        session_id=session_id,
        has_trace=bool(session_trace),
        has_mutations=bool(brain_mutations),
    )

    brain_service = AgentBrainService()
    skill_service = SkillService()

    brain_mutations_applied = 0
    session_summary_id = None
    insights_generated = 0
    skills_created = 0

    # 1. Process brain mutations first via _process_brain_mutations()
    if brain_mutations:
        brain_mutations_applied = await _process_brain_mutations(brain_service, brain_mutations)
        logger.info("brain_mutations_processed", count=brain_mutations_applied)

    # 2. Generate session summary from trace if trace provided
    if session_trace:
        summary = _generate_session_summary(str(session_id), session_trace)
        session_response = await brain_service.write_session_summary(str(session_id), summary)
        session_summary_id = str(session_response.session_id)
        logger.info("session_summary_generated", session_id=session_summary_id)

    # 3. Extract heuristics from trace, create skills if occurrence >= 3 (per D-69)
    if session_trace:
        heuristics = _extract_heuristics(session_trace)
        logger.info("heuristics_extracted", count=len(heuristics))

        for heuristic in heuristics:
            if heuristic.get("occurrence_count", 0) >= 3:
                # Create skill per D-69
                skill_name = f"auto-{heuristic['pattern'].lower().replace(' ', '-')[:30]}"
                try:
                    await skill_service.create_skill(
                        skill_name=skill_name,
                        description=f"Auto-created skill from heuristic: {heuristic['pattern']}",
                        procedure=f"# {heuristic['pattern']}\n\n**Pattern:** {heuristic['pattern']}\n**Occurrences:** {heuristic['occurrence_count']}\n\nThis skill was auto-created by reflect_agent when a pattern was observed {heuristic['occurrence_count']} times in a session trace.",
                        triggers=[heuristic["pattern"]],
                    )
                    skills_created += 1
                    logger.info("skill_auto_created", skill_name=skill_name)
                except Exception as e:
                    logger.warning("failed_to_create_skill", skill_name=skill_name, error=str(e))

    # 4. Count insights generated (heuristics that don't meet skill threshold)
    if session_trace:
        heuristics = _extract_heuristics(session_trace)
        insights_generated = sum(1 for h in heuristics if h.get("occurrence_count", 0) < 3)

    result = {
        "workspace_id": str(workspace_id),
        "agent_id": str(agent_id),
        "session_id": str(session_id),
        "session_summary_id": session_summary_id,
        "insights_generated": insights_generated,
        "skills_created": skills_created,
        "brain_mutations_applied": brain_mutations_applied,
        "status": "completed",
    }

    logger.info("reflect_agent_complete", workspace_id=workspace_id, agent_id=agent_id, **result)
    return result


async def _process_brain_mutations(brain_service: AgentBrainService, mutations: dict) -> int:
    """Process brain_mutations dict per D-82.

    Args:
        brain_service: AgentBrainService instance
        mutations: dict with optional soul_update, memory_update, user_update

    Returns:
        Number of mutations applied
    """
    applied = 0

    # Process soul_update
    soul_update_data = mutations.get("soul_update") or mutations.get("update_soul")
    if soul_update_data:
        update = SoulUpdate(
            identity_statement=soul_update_data.get("identity_statement"),
            operating_principles=soul_update_data.get("operating_principles"),
            communication_style=soul_update_data.get("communication_style"),
            constraints=soul_update_data.get("constraints"),
            self_improvement_guidelines=soul_update_data.get("self_improvement_guidelines"),
        )
        # Filter out None values
        update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
        if update_dict:
            filtered_update = SoulUpdate(**update_dict)
            await brain_service.update_soul(filtered_update)
            applied += 1
            logger.info("soul_update_applied")

    # Process memory_update
    memory_update_data = mutations.get("memory_update") or mutations.get("update_memory")
    if memory_update_data:
        update = MemoryUpdate(
            high_value_learnings=memory_update_data.get("high_value_learnings"),
            patterns_established=memory_update_data.get("patterns_established"),
            operational_heuristics=memory_update_data.get("operational_heuristics"),
        )
        update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
        if update_dict:
            filtered_update = MemoryUpdate(**update_dict)
            await brain_service.update_memory(filtered_update)
            applied += 1
            logger.info("memory_update_applied")

    # Process user_update
    user_update_data = mutations.get("user_update") or mutations.get("update_user_profile")
    if user_update_data:
        update = UserProfileUpdate(
            user_preferences=user_update_data.get("user_preferences") or user_update_data.get("preferences"),
            work_patterns=user_update_data.get("work_patterns"),
            context_notes=user_update_data.get("context_notes") or user_update_data.get("context"),
            restrictions=user_update_data.get("restrictions"),
            communication_style=user_update_data.get("communication_style"),
        )
        update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
        if update_dict:
            filtered_update = UserProfileUpdate(**update_dict)
            await brain_service.update_user_profile(filtered_update)
            applied += 1
            logger.info("user_update_applied")

    return applied


def _generate_session_summary(session_id: str, session_trace: list[dict]) -> SessionSummary:
    """Generate session summary from trace per D-72.

    Args:
        session_id: Session identifier
        session_trace: List of trace events

    Returns:
        SessionSummary with what_happened, key_decisions, open_questions, next_steps
    """
    # Extract text content from trace events
    all_text = []
    key_decisions = []
    open_questions = []
    next_steps = []
    dates = []

    for event in session_trace:
        # Extract text content from event
        if isinstance(event, dict):
            content = event.get("content", "") or event.get("text", "") or str(event)
            all_text.append(content)

            # Look for markers
            if event.get("type") == "decision" or "decision" in content.lower():
                key_decisions.append(content)
            if event.get("type") == "question" or "?" in content:
                open_questions.append(content)
            if event.get("type") == "next_step" or event.get("type") == "action":
                next_steps.append(content)
            if event.get("timestamp") or event.get("date"):
                dates.append(event.get("timestamp") or event.get("date"))

    # Generate what_happened from trace summary
    what_happened = ""
    if session_trace:
        first_event = session_trace[0] if session_trace else {}
        last_event = session_trace[-1] if session_trace else {}
        if isinstance(first_event, dict) and isinstance(last_event, dict):
            start = first_event.get("content", "") or first_event.get("text", "")[:100]
            end = last_event.get("content", "") or last_event.get("text", "")[:100]
            what_happened = f"Session started with: {start[:80]}... Completed with: {end[:80]}..."

    # Deduplicate and limit
    key_decisions = list(dict.fromkeys(key_decisions))[:10]
    open_questions = list(dict.fromkeys(open_questions))[:10]
    next_steps = list(dict.fromkeys(next_steps))[:10]

    return SessionSummary(
        session_id=UUID(session_id) if session_id else uuid4(),
        what_happened=what_happened or "Session completed successfully.",
        key_decisions=key_decisions,
        open_questions=open_questions,
        next_steps=next_steps,
        created_at=datetime.utcnow(),
    )


def _extract_heuristics(session_trace: list[dict]) -> list[dict]:
    """Extract recurring patterns from session trace per D-69.

    Counts pattern occurrences and returns patterns with occurrence >= 3.

    Args:
        session_trace: List of trace events

    Returns:
        List of dicts with pattern and occurrence_count
    """
    pattern_counter: Counter[str] = Counter()

    for event in session_trace:
        if isinstance(event, dict):
            content = event.get("content", "") or event.get("text", "") or ""
            # Extract potential patterns (action phrases, decision statements)
            words = content.split()
            # Count n-grams (2-4 word combinations)
            for n in range(2, min(5, len(words) + 1)):
                ngram = " ".join(words[i : i + n] for i in range(len(words) - n + 1))
                if len(ngram) > 10:  # Only meaningful n-grams
                    pattern_counter[ngram] += 1

    # Return patterns with occurrence >= 3
    heuristics = [
        {"pattern": pattern, "occurrence_count": count}
        for pattern, count in pattern_counter.items()
        if count >= 3
    ]

    # Sort by occurrence count descending
    heuristics.sort(key=lambda h: h["occurrence_count"], reverse=True)

    return heuristics[:20]  # Limit to top 20

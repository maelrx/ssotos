"""AgentBrainService — CRUD for SOUL.md, MEMORY.md, USER.md, sessions per D-66, D-73-80."""
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
import yaml

from src.schemas.agent import (
    MemoryResponse,
    MemorySection,
    MemoryUpdate,
    SessionListResponse,
    SessionResponse,
    SessionSummary,
    SoulResponse,
    SoulSection,
    SoulUpdate,
    UserProfileResponse,
    UserProfileSection,
    UserProfileUpdate,
)
from src.services.git_service import GitService

logger = structlog.get_logger()

BRAIN_ROOT = Path("workspace/agent-brain")


class AgentBrainService:
    """Brain file CRUD operations per D-66.

    All brain files live in workspace/agent-brain/ accessible via /agent/brain/* API.
    Git auto-commit on mutations per D-82.
    """

    def __init__(self, brain_root: Path | None = None, git_service: GitService | None = None):
        self.brain_root = brain_root or BRAIN_ROOT
        self.git_service = git_service or GitService(self.brain_root)
        self._ensure_structure()

    def _ensure_structure(self) -> None:
        """Ensure required brain directories exist per D-65."""
        required_dirs = ["skills", "heuristics", "reflections", "sessions", "scratchpads", "playbooks", "traces"]
        for dirname in required_dirs:
            (self.brain_root / dirname).mkdir(parents=True, exist_ok=True)

        # Ensure required files exist as templates
        for filename, template in [
            ("SOUL.md", "# SOUL.md\n\n**Agent Identity:** [To be configured]\n"),
            ("MEMORY.md", "# MEMORY.md\n\n**Last Updated:** \n"),
            ("USER.md", "# USER.md\n\n**Last Updated:** \n"),
        ]:
            filepath = self.brain_root / filename
            if not filepath.exists():
                filepath.write_text(template, encoding="utf-8")

    # =========================================================================
    # Soul operations (F9-02, D-73, D-74)
    # =========================================================================

    def _parse_soul_section(self, content: str) -> SoulSection:
        """Parse sections from SOUL.md content per D-73."""
        return SoulSection(
            identity_statement=self._extract_section(content, "Core Identity"),
            operating_principles=self._extract_list_section(content, "Operating Principles"),
            communication_style=self._extract_section(content, "Communication Style"),
            constraints=self._extract_list_section(content, "Constraints"),
            self_improvement_guidelines=self._extract_list_section(content, "Self-Improvement Guidelines"),
            raw_content=content,
        )

    async def read_soul(self) -> SoulResponse:
        """Read SOUL.md per D-74."""
        try:
            content = (self.brain_root / "SOUL.md").read_text(encoding="utf-8")
            section = self._parse_soul_section(content)
            return SoulResponse(content=section, updated_at=datetime.utcnow())
        except FileNotFoundError:
            logger.warning("SOUL.md not found", path=str(self.brain_root / "SOUL.md"))
            return SoulResponse(
                content=SoulSection(raw_content=""),
                updated_at=None,
            )

    async def update_soul(self, update: SoulUpdate) -> SoulResponse:
        """Update SOUL.md with git auto-commit per D-74, D-82."""
        current = await self.read_soul()
        lines = current.content.raw_content.splitlines() if current.content.raw_content else []

        # Apply updates to content
        content_dict = {
            "Core Identity": update.identity_statement,
            "Operating Principles": update.operating_principles,
            "Communication Style": update.communication_style,
            "Constraints": update.constraints,
            "Self-Improvement Guidelines": update.self_improvement_guidelines,
        }

        # For simplicity, rebuild the content
        new_lines = ["# SOUL.md", "", f"**Agent Identity:** [To be configured]", f"**Updated:** {datetime.utcnow().date()}", ""]

        if update.identity_statement is not None:
            new_lines.extend(["## Core Identity", update.identity_statement, ""])
        if update.operating_principles is not None:
            new_lines.append("## Operating Principles")
            for p in update.operating_principles:
                new_lines.append(f"- {p}")
            new_lines.append("")
        if update.communication_style is not None:
            new_lines.extend(["## Communication Style", update.communication_style, ""])
        if update.constraints is not None:
            new_lines.append("## Constraints")
            for c in update.constraints:
                new_lines.append(f"- {c}")
            new_lines.append("")
        if update.self_improvement_guidelines is not None:
            new_lines.append("## Self-Improvement Guidelines")
            for g in update.self_improvement_guidelines:
                new_lines.append(f"- {g}")
            new_lines.append("")

        new_content = "\n".join(new_lines)
        soul_path = self.brain_root / "SOUL.md"
        soul_path.write_text(new_content, encoding="utf-8")

        # Git auto-commit per D-82
        try:
            self.git_service.add([soul_path])
            self.git_service.commit(f"feat(brain): update SOUL.md")
        except Exception as e:
            logger.warning("Failed to auto-commit SOUL.md", error=str(e))

        return SoulResponse(content=self._parse_soul_section(new_content), updated_at=datetime.utcnow())

    # =========================================================================
    # Memory operations (F9-03, D-75-77)
    # =========================================================================

    def _parse_memory_section(self, content: str) -> MemorySection:
        """Parse sections from MEMORY.md content per D-75."""
        return MemorySection(
            high_value_learnings=self._extract_list_section(content, "High-Value Learnings"),
            patterns_established=self._extract_list_section(content, "Patterns Established"),
            operational_heuristics=self._extract_list_section(content, "Operational Heuristics"),
            raw_content=content,
        )

    async def read_memory(self) -> MemoryResponse:
        """Read MEMORY.md per D-76."""
        try:
            content = (self.brain_root / "MEMORY.md").read_text(encoding="utf-8")
            section = self._parse_memory_section(content)
            return MemoryResponse(content=section, updated_at=datetime.utcnow())
        except FileNotFoundError:
            logger.warning("MEMORY.md not found", path=str(self.brain_root / "MEMORY.md"))
            return MemoryResponse(content=MemorySection(raw_content=""), updated_at=None)

    async def update_memory(self, update: MemoryUpdate) -> MemoryResponse:
        """Update MEMORY.md with git auto-commit per D-77, D-82."""
        current = await self.read_memory()

        new_lines = ["# MEMORY.md", "", f"**Last Updated:** {datetime.utcnow().date()}", "**Version:** 1", "", "## Consolidated Memories", ""]

        if update.high_value_learnings is not None:
            new_lines.append("### High-Value Learnings")
            for item in update.high_value_learnings:
                new_lines.append(f"- {item}")
            new_lines.append("")
        if update.patterns_established is not None:
            new_lines.append("### Patterns Established")
            for item in update.patterns_established:
                new_lines.append(f"- {item}")
            new_lines.append("")
        if update.operational_heuristics is not None:
            new_lines.append("### Operational Heuristics")
            for item in update.operational_heuristics:
                new_lines.append(f"- {item}")
            new_lines.append("")

        new_content = "\n".join(new_lines)
        memory_path = self.brain_root / "MEMORY.md"
        memory_path.write_text(new_content, encoding="utf-8")

        try:
            self.git_service.add([memory_path])
            self.git_service.commit(f"feat(brain): update MEMORY.md")
        except Exception as e:
            logger.warning("Failed to auto-commit MEMORY.md", error=str(e))

        return MemoryResponse(content=self._parse_memory_section(new_content), updated_at=datetime.utcnow())

    # =========================================================================
    # User Profile operations (F9-04, D-78-80)
    # =========================================================================

    def _parse_user_profile_section(self, content: str) -> UserProfileSection:
        """Parse sections from USER.md content per D-78."""
        return UserProfileSection(
            user_preferences=self._extract_list_section(content, "User Preferences"),
            work_patterns=self._extract_list_section(content, "Work Patterns"),
            context_notes=self._extract_list_section(content, "Context"),
            restrictions=self._extract_list_section(content, "Restrictions"),
            communication_style=self._extract_section(content, "Communication Style"),
            raw_content=content,
        )

    async def read_user_profile(self) -> UserProfileResponse:
        """Read USER.md per D-79."""
        try:
            content = (self.brain_root / "USER.md").read_text(encoding="utf-8")
            section = self._parse_user_profile_section(content)
            return UserProfileResponse(content=section, updated_at=datetime.utcnow())
        except FileNotFoundError:
            logger.warning("USER.md not found", path=str(self.brain_root / "USER.md"))
            return UserProfileResponse(content=UserProfileSection(raw_content=""), updated_at=None)

    async def update_user_profile(self, update: UserProfileUpdate) -> UserProfileResponse:
        """Update USER.md with git auto-commit per D-80, D-82."""
        current = await self.read_user_profile()

        new_lines = ["# USER.md", "", f"**Last Updated:** {datetime.utcnow().date()}", ""]

        if update.user_preferences is not None:
            new_lines.append("## User Preferences")
            for item in update.user_preferences:
                new_lines.append(f"- {item}")
            new_lines.append("")
        if update.work_patterns is not None:
            new_lines.append("## Work Patterns")
            for item in update.work_patterns:
                new_lines.append(f"- {item}")
            new_lines.append("")
        if update.context_notes is not None:
            new_lines.append("## Context")
            for item in update.context_notes:
                new_lines.append(f"- {item}")
            new_lines.append("")
        if update.restrictions is not None:
            new_lines.append("## Restrictions")
            for item in update.restrictions:
                new_lines.append(f"- {item}")
            new_lines.append("")
        if update.communication_style is not None:
            new_lines.extend(["## Communication Style", update.communication_style, ""])

        new_content = "\n".join(new_lines)
        user_path = self.brain_root / "USER.md"
        user_path.write_text(new_content, encoding="utf-8")

        try:
            self.git_service.add([user_path])
            self.git_service.commit(f"feat(brain): update USER.md")
        except Exception as e:
            logger.warning("Failed to auto-commit USER.md", error=str(e))

        return UserProfileResponse(content=self._parse_user_profile_section(new_content), updated_at=datetime.utcnow())

    # =========================================================================
    # Session operations (F9-06, D-70-72)
    # =========================================================================

    def _parse_session_summary(self, content: str) -> SessionSummary | None:
        """Parse session summary from markdown content per D-72."""
        if not content.strip():
            return None

        what_happened = self._extract_section(content, "What happened") or ""
        key_decisions = self._extract_list_section(content, "Key decisions")
        open_questions = self._extract_list_section(content, "Open questions")
        next_steps = self._extract_list_section(content, "Next steps")

        return SessionSummary(
            what_happened=what_happened,
            key_decisions=key_decisions,
            open_questions=open_questions,
            next_steps=next_steps,
        )

    async def list_sessions(self) -> SessionListResponse:
        """List all session summaries from sessions/ directory per D-71."""
        sessions_dir = self.brain_root / "sessions"
        if not sessions_dir.exists():
            return SessionListResponse(sessions=[], total=0)

        sessions = []
        for session_file in sorted(sessions_dir.glob("*.md")):
            try:
                content = session_file.read_text(encoding="utf-8")
                summary = self._parse_session_summary(content)
                session_id = session_file.stem  # filename without extension
                stat = session_file.stat()
                sessions.append(
                    SessionResponse(
                        session_id=session_id,
                        content=content,
                        summary=summary,
                        created_at=datetime.fromtimestamp(stat.st_ctime),
                        updated_at=datetime.fromtimestamp(stat.st_mtime),
                    )
                )
            except Exception as e:
                logger.warning("Failed to read session file", file=str(session_file), error=str(e))

        return SessionListResponse(sessions=sessions, total=len(sessions))

    async def get_session(self, session_id: str) -> SessionResponse | None:
        """Get specific session summary per D-71."""
        session_file = self.brain_root / "sessions" / f"{session_id}.md"
        if not session_file.exists():
            return None

        content = session_file.read_text(encoding="utf-8")
        summary = self._parse_session_summary(content)
        stat = session_file.stat()

        return SessionResponse(
            session_id=session_id,
            content=content,
            summary=summary,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            updated_at=datetime.fromtimestamp(stat.st_mtime),
        )

    async def write_session_summary(self, session_id: str, summary: SessionSummary) -> SessionResponse:
        """Write session summary per D-72."""
        content_lines = [
            "# Session Summary",
            "",
            f"**Session ID:** {summary.session_id}",
            f"**Created:** {summary.created_at.isoformat()}",
            "",
            "## What happened",
            summary.what_happened,
            "",
            "## Key decisions",
        ]
        for d in summary.key_decisions:
            content_lines.append(f"- {d}")
        content_lines.extend(["", "## Open questions"])
        for q in summary.open_questions:
            content_lines.append(f"- {q}")
        content_lines.extend(["", "## Next steps"])
        for n in summary.next_steps:
            content_lines.append(f"- {n}")

        content = "\n".join(content_lines)
        session_path = self.brain_root / "sessions" / f"{session_id}.md"
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(content, encoding="utf-8")

        # Git auto-commit per D-82
        try:
            self.git_service.add([session_path])
            self.git_service.commit(f"feat(brain): save session {session_id}")
        except Exception as e:
            logger.warning("Failed to auto-commit session", session_id=session_id, error=str(e))

        stat = session_path.stat()
        return SessionResponse(
            session_id=session_id,
            content=content,
            summary=summary,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            updated_at=datetime.fromtimestamp(stat.st_mtime),
        )

    # =========================================================================
    # Utility methods
    # =========================================================================

    def _extract_section(self, content: str, heading: str) -> str | None:
        """Extract section content between headings."""
        pattern = rf"^##?\s*{re.escape(heading)}\s*\n(.*?)(?=^##|\Z)"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_list_section(self, content: str, heading: str) -> list[str]:
        """Extract bullet list items from a section."""
        section = self._extract_section(content, heading)
        if not section:
            return []
        items = re.findall(r"^\s*-\s+(.+)$", section, re.MULTILINE)
        return items

    def validate_brain_structure(self) -> dict[str, bool]:
        """Validate required dirs and files exist per D-65."""
        required_dirs = ["skills", "heuristics", "reflections", "sessions", "scratchpads", "playbooks", "traces"]
        required_files = ["SOUL.md", "MEMORY.md", "USER.md"]

        result = {}
        for dirname in required_dirs:
            result[f"dir:{dirname}"] = (self.brain_root / dirname).is_dir()
        for filename in required_files:
            result[f"file:{filename}"] = (self.brain_root / filename).is_file()

        result["all_valid"] = all(result.values())
        return result

"""SkillService — Skill manifest loading and invocation per D-67, D-68."""
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import structlog
import yaml

from src.schemas.agent import (
    SkillInvokeRequest,
    SkillInvokeResponse,
    SkillListResponse,
    SkillManifest,
    SkillResponse,
    SkillTrigger,
)

logger = structlog.get_logger()

SKILLS_ROOT = Path("workspace/agent-brain/skills")


class SkillService:
    """Skill manifest and invocation per D-67, D-68.

    Skill format: skills/<skill-name>/manifest.yaml + SKILL.md procedure body.
    Skills invoked via PydanticAI tool calls per D-68.
    """

    def __init__(self, skills_root: Path | None = None):
        self.skills_root = skills_root or SKILLS_ROOT
        self._ensure_skills_dir()

    def _ensure_skills_dir(self) -> None:
        """Ensure skills directory exists."""
        self.skills_root.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Internal helpers
    # =========================================================================

    def _load_manifest(self, skill_dir: Path) -> SkillManifest | None:
        """Load manifest.yaml from skill directory per D-67."""
        manifest_path = skill_dir / "manifest.yaml"
        if not manifest_path.exists():
            return None

        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if data is None:
                return None

            # Parse trigger patterns
            trigger_patterns = []
            for tp in data.get("trigger_patterns", []):
                if isinstance(tp, str):
                    trigger_patterns.append(SkillTrigger(pattern=tp))
                elif isinstance(tp, dict):
                    trigger_patterns.append(SkillTrigger(**tp))

            data["trigger_patterns"] = trigger_patterns
            return SkillManifest(**data)
        except Exception as e:
            logger.warning("Failed to load skill manifest", path=str(manifest_path), error=str(e))
            return None

    def _load_body(self, skill_dir: Path) -> str:
        """Load SKILL.md procedure body from skill directory."""
        body_path = skill_dir / "SKILL.md"
        if not body_path.exists():
            return ""
        return body_path.read_text(encoding="utf-8")

    # =========================================================================
    # Skill listing and retrieval (D-67)
    # =========================================================================

    async def list_skills(self) -> SkillListResponse:
        """List all skills from skills/ directory per D-67."""
        if not self.skills_root.exists():
            return SkillListResponse(skills=[], total=0)

        skills = []
        for skill_dir in self.skills_root.iterdir():
            if not skill_dir.is_dir():
                continue
            manifest = self._load_manifest(skill_dir)
            if manifest:
                skills.append(manifest)

        return SkillListResponse(skills=skills, total=len(skills))

    async def get_skill(self, skill_name: str) -> SkillResponse | None:
        """Get specific skill by name per D-67."""
        skill_dir = self.skills_root / skill_name
        if not skill_dir.exists() or not skill_dir.is_dir():
            return None

        manifest = self._load_manifest(skill_dir)
        if not manifest:
            return None

        procedure_body = self._load_body(skill_dir)
        return SkillResponse(manifest=manifest, procedure_body=procedure_body)

    # =========================================================================
    # Skill invocation (D-68)
    # =========================================================================

    async def invoke_skill(self, skill_name: str, input_data: dict[str, Any]) -> SkillInvokeResponse:
        """Invoke skill per D-68.

        Skill procedure is executed as agent tool.
        This is a placeholder — actual execution requires PydanticAI integration.
        """
        start_time = time.time()

        skill = await self.get_skill(skill_name)
        if not skill:
            return SkillInvokeResponse(
                success=False,
                skill_name=skill_name,
                output_data={},
                error=f"Skill '{skill_name}' not found",
            )

        # Validate inputs against manifest schema
        if skill.manifest.inputs_schema:
            required = skill.manifest.inputs_schema.required
            missing = [f for f in required if f not in input_data]
            if missing:
                return SkillInvokeResponse(
                    success=False,
                    skill_name=skill_name,
                    output_data={},
                    error=f"Missing required inputs: {', '.join(missing)}",
                )

        # Placeholder: In full implementation, this would execute the procedure
        # For now, return the procedure body as "executed"
        execution_time_ms = int((time.time() - start_time) * 1000)

        return SkillInvokeResponse(
            success=True,
            skill_name=skill_name,
            output_data={
                "procedure_executed": True,
                "skill_version": skill.manifest.version,
                "note": "Skill invocation placeholder — full execution requires PydanticAI integration",
            },
            execution_time_ms=execution_time_ms,
        )

    # =========================================================================
    # Skill lifecycle (D-69)
    # =========================================================================

    async def create_skill(
        self,
        skill_name: str,
        description: str,
        procedure: str,
        triggers: list[str] | None = None,
        inputs_schema: dict[str, Any] | None = None,
        outputs_schema: dict[str, Any] | None = None,
    ) -> SkillResponse:
        """Create skill with manifest.yaml and SKILL.md per D-67."""
        skill_dir = self.skills_root / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Create manifest.yaml
        manifest_data = {
            "name": skill_name,
            "description": description,
            "trigger_patterns": [{"pattern": t} for t in (triggers or [])],
            "inputs_schema": inputs_schema or {"type": "object", "properties": {}},
            "outputs_schema": outputs_schema or {"type": "object", "properties": {}},
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
        }

        manifest_path = skill_dir / "manifest.yaml"
        manifest_path.write_text(yaml.dump(manifest_data, default_flow_style=False), encoding="utf-8")

        # Create SKILL.md
        body_path = skill_dir / "SKILL.md"
        body_path.write_text(procedure, encoding="utf-8")

        manifest = self._load_manifest(skill_dir)
        return SkillResponse(manifest=manifest or SkillManifest(name=skill_name, description=description), procedure_body=procedure)

    async def update_skill(
        self,
        skill_name: str,
        description: str | None = None,
        procedure: str | None = None,
        triggers: list[str] | None = None,
        inputs_schema: dict[str, Any] | None = None,
        outputs_schema: dict[str, Any] | None = None,
    ) -> SkillResponse | None:
        """Update existing skill per D-69."""
        skill_dir = self.skills_root / skill_name
        if not skill_dir.exists() or not skill_dir.is_dir():
            return None

        manifest = self._load_manifest(skill_dir)
        if not manifest:
            return None

        # Update manifest
        if description is not None:
            manifest.description = description
        if triggers is not None:
            manifest.trigger_patterns = [SkillTrigger(pattern=t) for t in triggers]
        if inputs_schema is not None:
            manifest.inputs_schema = inputs_schema  # type: ignore
        if outputs_schema is not None:
            manifest.outputs_schema = outputs_schema  # type: ignore

        manifest.updated_at = datetime.utcnow()

        manifest_path = skill_dir / "manifest.yaml"
        manifest_path.write_text(yaml.dump(manifest.model_dump(), default_flow_style=False), encoding="utf-8")

        # Update body if provided
        if procedure is not None:
            body_path = skill_dir / "SKILL.md"
            body_path.write_text(procedure, encoding="utf-8")

        return SkillResponse(manifest=manifest, procedure_body=self._load_body(skill_dir))

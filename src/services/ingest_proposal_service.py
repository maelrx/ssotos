"""Creates ingest proposal for research outputs — per F12-06."""
from uuid import UUID
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


class IngestProposalService:
    """Creates patch bundle for research outputs to go through Exchange Zone."""

    def __init__(self) -> None:
        pass

    async def create_proposal(
        self,
        job_id: UUID,
        workspace_id: UUID,
        synthesis_path: str,
        blueprint_path: str | None,
        source_paths: list[str],
    ) -> str:
        """Create an ingest proposal for research outputs.

        Creates a proposal bundle in exchange/proposals/research-{job_id}/

        Returns:
            The proposal directory path

        Raises:
            Any exception from file/Git operations
        """
        import shutil
        import os

        proposal_dir = f"workspace/exchange/proposals/research-{job_id}"
        os.makedirs(proposal_dir, exist_ok=True)

        # Copy synthesis
        if synthesis_path and os.path.exists(synthesis_path):
            shutil.copy(synthesis_path, f"{proposal_dir}/synthesis.md")

        # Copy blueprint
        if blueprint_path and os.path.exists(blueprint_path):
            shutil.copy(blueprint_path, f"{proposal_dir}/blueprint.md")

        # Copy sources manifest
        manifest = {
            "job_id": str(job_id),
            "synthesis": synthesis_path,
            "blueprint": blueprint_path,
            "sources": source_paths,
        }
        import yaml
        with open(f"{proposal_dir}/manifest.yaml", "w") as f:
            yaml.dump(manifest, f)

        logger.info("ingest_proposal_created", job_id=str(job_id), proposal_dir=proposal_dir)

        return proposal_dir

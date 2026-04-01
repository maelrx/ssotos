"""Job handlers — one module per job type (per D-55)."""
from src.worker.handlers.index_note import handle_index_note
from src.worker.handlers.reindex_scope import handle_reindex_scope
from src.worker.handlers.generate_embeddings import handle_generate_embeddings
from src.worker.handlers.research_job import handle_research_job
from src.worker.handlers.parse_source import handle_parse_source
from src.worker.handlers.apply_patch_bundle import handle_apply_patch_bundle
from src.worker.handlers.reflect_agent import handle_reflect_agent
from src.worker.handlers.consolidate_memory import handle_consolidate_memory
from src.worker.handlers.propose_patch import handle_propose_patch

HANDLERS = {
    "index_note": handle_index_note,
    "reindex_scope": handle_reindex_scope,
    "generate_embeddings": handle_generate_embeddings,
    "research_job": handle_research_job,
    "parse_source": handle_parse_source,
    "apply_patch_bundle": handle_apply_patch_bundle,
    "reflect_agent": handle_reflect_agent,
    "consolidate_memory": handle_consolidate_memory,
    "propose_patch": handle_propose_patch,
}

__all__ = ["HANDLERS"]

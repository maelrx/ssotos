"""Templates REST API - per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/")
async def list_templates():
    """List available templates (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")


@router.get("/{template_name}")
async def get_template(template_name: str):
    """Get template content (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")


@router.post("/render")
async def render_template():
    """Render template with variables (placeholder)."""
    raise HTTPException(status_code=501, detail="Phase 1 feature - not yet implemented")

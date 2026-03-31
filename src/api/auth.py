"""Auth REST API - per D-48 (internal modules)."""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def get_current_actor():
    """Get current actor (placeholder - no auth in v1).

    For v1, returns a default actor 'user'.
    """
    return {"actor": "user", "role": "admin"}

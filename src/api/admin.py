"""Admin REST API — per D-48 (internal modules)."""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime
from typing import Any

from src.db.session import get_db
from src.db.models.workspace import Workspace
from src.db.models.actor import Actor

router = APIRouter(prefix="/admin", tags=["admin"])


class CreateWorkspaceRequest:
    """Request to create a workspace."""
    def __init__(self, name: str, root_path: str, config: dict[str, Any] | None = None):
        self.name = name
        self.root_path = root_path
        self.config = config or {}


@router.get("/workspaces")
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
):
    """List all workspaces."""
    stmt = select(Workspace).order_by(Workspace.created_at.desc())
    result = await db.execute(stmt)
    workspaces = result.scalars().all()

    return {
        "workspaces": [
            {
                "id": str(ws.id),
                "name": ws.name,
                "root_path": ws.root_path,
                "config": ws.config or {},
                "created_at": ws.created_at.isoformat(),
                "updated_at": ws.updated_at.isoformat() if ws.updated_at else None,
            }
            for ws in workspaces
        ],
        "total": len(workspaces),
    }


@router.post("/workspaces")
async def create_workspace(
    name: str,
    root_path: str,
    config: dict[str, Any] | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new workspace."""
    workspace = Workspace(
        name=name,
        root_path=root_path,
        config=config or {},
    )
    db.add(workspace)
    await db.flush()

    return {
        "success": True,
        "message": f"Workspace '{name}' created",
        "workspace": {
            "id": str(workspace.id),
            "name": workspace.name,
            "root_path": workspace.root_path,
        },
    }


@router.get("/actors")
async def list_actors(
    db: AsyncSession = Depends(get_db),
):
    """List all actors (users, agents, services)."""
    stmt = select(Actor).order_by(Actor.created_at.desc())
    result = await db.execute(stmt)
    actors = result.scalars().all()

    return {
        "actors": [
            {
                "id": str(actor.id),
                "name": actor.name,
                "actor_type": actor.actor_type,
                "capabilities": actor.capabilities or [],
                "metadata": actor.metadata or {},
                "created_at": actor.created_at.isoformat(),
            }
            for actor in actors
        ],
        "total": len(actors),
    }

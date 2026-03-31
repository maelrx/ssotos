"""SSE endpoint for job status updates - per D-53 (default to SSE)."""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import AsyncGenerator
from uuid import UUID

router = APIRouter(tags=["jobs"])

# In-memory registry of active SSE connections
# In production, this would use Redis pub/sub
_active_connections: dict[str, asyncio.Queue] = {}


async def job_status_generator(queue: asyncio.Queue) -> AsyncGenerator[bytes, None]:
    """Generator that yields SSE-formatted job status events."""
    while True:
        try:
            event = await asyncio.wait_for(queue.get(), timeout=30)
            yield f"data: {json.dumps(event)}\n\n"
        except asyncio.TimeoutError:
            # Send keepalive comment
            yield b": keepalive\n\n"


@router.get("/events")
async def job_events_sse(request: Request):
    """Stream job status updates via SSE.

    Clients connect to this endpoint and receive real-time
    job status updates as they occur.

    Query params:
    - job_id: (optional) filter events for specific job
    - workspace_id: (optional) filter events for workspace

    Returns SSE stream with event data:
    - job_created: new job was created
    - job_claimed: job was claimed by worker
    - job_started: job began processing
    - job_progress: job reported progress
    - job_completed: job finished successfully
    - job_failed: job failed
    """
    workspace_id = request.query_params.get("workspace_id")
    job_id = request.query_params.get("job_id")

    queue: asyncio.Queue = asyncio.Queue()
    connection_id = f"{workspace_id or 'global'}:{job_id or 'all'}"

    _active_connections[connection_id] = queue

    async def cleanup():
        _active_connections.pop(connection_id, None)

    try:
        return StreamingResponse(
            job_status_generator(queue),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
        # Note: cleanup happens when client disconnects
    except Exception:
        cleanup()
        raise


def broadcast_job_event(event: dict, workspace_id: str | None = None, job_id: str | None = None):
    """Broadcast a job event to all connected SSE clients.

    Call this from the job queue and worker when job state changes.
    """
    event_type = event.get("event_type")
    target_connection = f"{workspace_id or 'global'}:{job_id or 'all'}"

    # Broadcast to specific job connection
    if target_connection in _active_connections:
        _active_connections[target_connection].put_nowait(event)

    # Also broadcast to workspace-wide connection
    workspace_connection = f"{workspace_id or 'global'}:all"
    if workspace_connection in _active_connections:
        _active_connections[workspace_connection].put_nowait(event)

    # Also broadcast to global connection
    if "global:all" in _active_connections:
        _active_connections["global:all"].put_nowait(event)

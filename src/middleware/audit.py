"""Audit middleware — logs all API requests to audit_logs table.

Automatically creates audit entries for:
- All mutating requests (POST, PUT, PATCH, DELETE)
- Sensitive read operations
- Failed requests
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from uuid import uuid4
import time

from src.core.audit import audit_logger
from src.core.audit_events import AuditEventType
from src.core.otel import get_current_trace_id


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that logs audit events for all API requests.

    Skips health check and static file endpoints.
    """

    SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip non-API paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # Only audit API paths
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        start_time = time.time()
        trace_id = get_current_trace_id()

        # Set audit context with actor (from auth header or default to "user")
        actor = request.headers.get("X-Actor", "user")
        audit_logger.set_context(
            workspace_id=request.headers.get("X-Workspace-ID"),
            trace_id=trace_id,
            http_method=request.method,
            http_path=request.url.path,
        )

        try:
            response = await call_next(request)

            # Determine result based on status code
            if response.status_code < 400:
                result = "success"
            elif response.status_code == 401 or response.status_code == 403:
                result = "denied"
            else:
                result = "error"

            # Determine domain from path
            domain = self._extract_domain(request.url.path)

            # Log the audit event via structlog (DB writes handled via EventBus)
            audit_logger.log(
                db=None,
                event_type=AuditEventType.TOOL_CALLED,
                actor=actor,
                result=result,
                domain=domain,
                target=request.url.path,
                action=request.method,
                trace_id=trace_id,
                metadata={
                    "status_code": response.status_code,
                    "duration_ms": int((time.time() - start_time) * 1000),
                    "query_params": dict(request.query_params),
                },
            )

            return response

        except Exception as e:
            audit_logger.log(
                db=None,
                event_type=AuditEventType.TOOL_ERROR,
                actor=actor,
                result="error",
                domain=self._extract_domain(request.url.path),
                target=request.url.path,
                action=request.method,
                reason=str(e),
                trace_id=trace_id,
            )
            raise

        finally:
            audit_logger.clear_context()

    def _extract_domain(self, path: str) -> str:
        """Extract domain from API path (e.g., /api/vault/notes -> vault)."""
        parts = path.split("/")
        if len(parts) >= 3 and parts[1] == "api":
            return parts[2]
        return "unknown"

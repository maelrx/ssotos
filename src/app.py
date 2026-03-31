"""FastAPI application factory - per D-47 (FastAPI with modular routers)."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.api import vault, templates, retrieval, copilot, exchange, approvals, research, jobs, policy, admin, auth, sse, audit, agent
from src.middleware.audit import AuditMiddleware
from src.db.database import engine
from src.core.logging import configure_logging
from src.core.otel import configure_otel

# Configure logging and OTel at startup
configure_logging()
configure_otel()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: verify database connection
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    # Shutdown: dispose engine
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Knowledge OS Core API",
        version="0.1.0",
        description="Backend API for Knowledge OS Core",
        lifespan=lifespan,
    )

    # CORS for frontend SPA (per D-59: React + Vite)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Audit middleware for all API requests (per D-57: F14-01 to F14-05)
    app.add_middleware(AuditMiddleware)

    # OpenTelemetry instrumentation for HTTP requests (per D-58)
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app)

    # Health check
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "healthy", "version": "0.1.0"}

    # Register all API routers (per D-48: internal modules)
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(vault.router, prefix="/api/vault", tags=["vault"])
    app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
    app.include_router(retrieval.router, prefix="/api/retrieval", tags=["retrieval"])
    app.include_router(copilot.router, prefix="/api/copilot", tags=["copilot"])
    app.include_router(exchange.router, prefix="/api/exchange", tags=["exchange"])
    app.include_router(approvals.router, prefix="/api/approvals", tags=["approvals"])
    app.include_router(research.router, prefix="/api/research", tags=["research"])
    app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(sse.router, prefix="/api/jobs", tags=["jobs"])  # SSE at /jobs/events
    app.include_router(policy.router, prefix="/api/policy", tags=["policy"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    app.include_router(audit.router, prefix="/api/admin", tags=["admin"])
    app.include_router(agent.router, prefix="/api", tags=["agent"])

    return app


app = create_app()

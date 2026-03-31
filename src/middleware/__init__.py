"""FastAPI middleware for Knowledge OS Core."""
from src.middleware.audit import AuditMiddleware

__all__ = ["AuditMiddleware"]

"""API routers - per D-48 (internal modules)."""
from fastapi import APIRouter

# Re-export all routers for convenient imports
from src.api import vault, templates, retrieval, copilot, exchange, approvals, research, jobs, policy, admin, auth, sse, agent

__all__ = [
    "vault",
    "templates",
    "retrieval",
    "copilot",
    "exchange",
    "approvals",
    "research",
    "jobs",
    "policy",
    "admin",
    "auth",
    "sse",
    "agent",
]

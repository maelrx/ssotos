"""FastAPI dependency for database sessions."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session_maker


async def get_db() -> AsyncSession:
    """Dependency that provides a database session with auto-commit/rollback."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

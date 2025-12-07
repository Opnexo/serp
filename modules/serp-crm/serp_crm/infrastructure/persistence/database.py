"""
Database configuration and session management for CRM module.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from serp_crm.config import CRMSettings


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, settings: CRMSettings | None = None) -> None:
        self._settings = settings or CRMSettings()
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        """Get or create the database engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                self._settings.database_url,
                echo=self._settings.database_echo,
                pool_size=self._settings.database_pool_size,
                max_overflow=self._settings.database_max_overflow,
            )
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create the session factory."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
        return self._session_factory

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Create a new database session context."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close the database engine."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database manager instance
_db_manager: DatabaseManager | None = None


def get_database_manager(settings: CRMSettings | None = None) -> DatabaseManager:
    """Get or create the global database manager."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(settings)
    return _db_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting a database session."""
    db = get_database_manager()
    async with db.session() as session:
        yield session

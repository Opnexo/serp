"""
Database manager for Project Management module.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from serp_pm.config import PMSettings


class DatabaseManager:
    """
    Database connection and session manager.
    """

    def __init__(self, settings: PMSettings):
        self.settings = settings
        self.engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
        )
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session.

        Yields:
            AsyncSession instance
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        """Close database connections."""
        await self.engine.dispose()


# Global database manager instance
_db_manager: DatabaseManager | None = None


def get_database_manager(settings: PMSettings | None = None) -> DatabaseManager:
    """
    Get or create database manager instance.

    Args:
        settings: Optional settings to create new instance

    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        if settings is None:
            settings = PMSettings()
        _db_manager = DatabaseManager(settings)
    return _db_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting DB session."""
    manager = get_database_manager()
    async for session in manager.get_session():
        yield session

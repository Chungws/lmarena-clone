"""
Database connection and session management for worker

Worker uses async PostgreSQL connection with smaller pool size than backend API.
Configured for batch operations and lower concurrency.
"""

from typing import AsyncGenerator

from llmbattler_shared.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Create async engine with worker-specific pool configuration
# Worker typically uses fewer connections than backend API
engine = create_async_engine(
    settings.postgres_uri,
    echo=False,
    pool_size=2,  # Worker uses fewer connections (backend uses 5)
    max_overflow=3,  # Total max connections: 2 + 3 = 5 (backend: 5 + 5 = 10)
    pool_timeout=10,  # Connection timeout in seconds
)

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for worker operations

    Usage:
        async with get_db() as session:
            result = await session.execute(...)
            await session.commit()

    Yields:
        AsyncSession: Database session instance

    Notes:
        - Automatically commits on success
        - Automatically rolls back on exception
        - Always closes session in finally block
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

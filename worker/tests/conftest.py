"""
Pytest configuration and fixtures for worker tests
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Test database URL (use test PostgreSQL database)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/llmbattler_test"


@pytest_asyncio.fixture(scope="function")
async def test_db_session():
    """Database session fixture for tests"""
    # Create engine per test to avoid connection pool issues
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create session
    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    # Dispose engine
    await engine.dispose()

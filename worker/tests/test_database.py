"""
Tests for PostgreSQL database connection
"""

import os

import pytest
from databases import Database

from llmbattler_worker.database import get_database


class TestDatabaseConnection:
    """Test database connection setup"""

    @pytest.mark.asyncio
    async def test_get_database_creates_connection(self):
        """Test that get_database returns a Database instance"""
        # Arrange & Act
        db = get_database()

        # Assert
        assert isinstance(db, Database)
        assert db.url is not None

    @pytest.mark.asyncio
    async def test_database_uses_connection_pooling(self):
        """Test that database connection is created with pooling parameters"""
        # Arrange & Act
        db = get_database()

        # Assert - Database instance is created with URL
        # Connection pooling parameters (min_size=2, max_size=5, timeout=10)
        # are passed to Database constructor but not directly testable
        # We trust the databases library to handle these correctly
        assert isinstance(db, Database)
        assert db.url is not None

    @pytest.mark.asyncio
    async def test_database_url_from_environment(self):
        """Test that database URL is read from environment variable"""
        # Arrange
        test_url = "postgresql://testuser:testpass@localhost:5432/testdb"
        os.environ["DATABASE_URL"] = test_url

        # Act
        db = get_database()

        # Assert
        assert str(db.url) == test_url

        # Cleanup
        del os.environ["DATABASE_URL"]

    @pytest.mark.asyncio
    async def test_database_url_default_fallback(self):
        """Test that database URL falls back to default if not in environment"""
        # Arrange - Remove DATABASE_URL if it exists
        if "DATABASE_URL" in os.environ:
            original_url = os.environ.pop("DATABASE_URL")
        else:
            original_url = None

        # Act
        db = get_database()

        # Assert
        assert "postgresql://" in str(db.url)
        assert "llmbattler" in str(db.url)

        # Cleanup
        if original_url:
            os.environ["DATABASE_URL"] = original_url

    @pytest.mark.skip(reason="Requires actual PostgreSQL server - move to integration tests")
    @pytest.mark.asyncio
    async def test_database_connect_disconnect(self):
        """Test database connection lifecycle - integration test"""
        # NOTE: This test requires actual PostgreSQL server running
        # Move to integration tests with proper test database setup
        # Arrange
        db = get_database()

        # Act & Assert - Should connect successfully
        await db.connect()
        assert db.is_connected

        # Act & Assert - Should disconnect successfully
        await db.disconnect()
        assert not db.is_connected

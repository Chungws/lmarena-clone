"""
Pytest configuration and fixtures for backend tests
"""

import pytest
from fastapi.testclient import TestClient

from llmbattler_backend.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


# TODO: Add database fixtures
# - Mock MongoDB client
# - Mock PostgreSQL session
# - Test data fixtures

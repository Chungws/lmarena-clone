"""
Tests for model management API endpoints
"""

from fastapi.testclient import TestClient


def test_get_models_returns_list(client: TestClient):
    """Test GET /api/models returns list of available models"""
    response = client.get("/api/models")

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "models" in data
    assert isinstance(data["models"], list)
    assert len(data["models"]) > 0

    # Check first model structure
    model = data["models"][0]
    assert "model_id" in model
    assert "name" in model
    assert "provider" in model
    assert "status" in model
    assert model["status"] in ["active", "inactive"]


def test_get_models_contains_expected_models(client: TestClient):
    """Test GET /api/models contains models from config"""
    response = client.get("/api/models")

    assert response.status_code == 200
    data = response.json()

    model_ids = [m["model_id"] for m in data["models"]]

    # Should contain at least one model
    assert len(model_ids) > 0

    # All models should have valid fields
    for model in data["models"]:
        assert model["model_id"]
        assert model["name"]
        assert model["provider"]


def test_get_models_only_active_models(client: TestClient):
    """Test GET /api/models only returns active models by default"""
    response = client.get("/api/models")

    assert response.status_code == 200
    data = response.json()

    # All models should be active (in MVP, we don't have inactive models)
    for model in data["models"]:
        assert model["status"] == "active"

"""
Tests for session and battle API endpoints
"""

from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient

from llmbattler_backend.services.llm_client import LLMResponse


def test_create_session_success(client: TestClient):
    """
    Test successful session creation with first battle

    Scenario:
    1. User submits initial prompt
    2. System creates session
    3. System selects 2 random models
    4. System calls both LLMs in parallel
    5. System creates battle with conversation
    6. Returns anonymous responses
    """
    # Arrange
    prompt = "What is the capital of France?"

    # Mock model configs
    from llmbattler_backend.services.model_service import ModelConfig

    mock_model_a = ModelConfig({
        "id": "llama-3-1-8b",
        "name": "Llama 3.1 8B",
        "model": "llama3.1:8b",
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,
        "organization": "Meta",
        "license": "open-source",
        "status": "active",
    })

    mock_model_b = ModelConfig({
        "id": "qwen-2-5-7b",
        "name": "Qwen 2.5 7B",
        "model": "qwen2.5:7b",
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,
        "organization": "Alibaba",
        "license": "open-source",
        "status": "active",
    })

    # Mock LLM responses
    mock_left_response = LLMResponse(
        content="The capital of France is Paris.",
        latency_ms=250,
        model_id="llama-3-1-8b",
    )
    mock_right_response = LLMResponse(
        content="Paris is the capital city of France.",
        latency_ms=300,
        model_id="qwen-2-5-7b",
    )

    with patch("llmbattler_backend.services.session_service.get_model_service") as mock_get_model_service, \
         patch("llmbattler_backend.services.session_service.get_llm_client") as mock_get_client:

        # Mock model service (sync, not async)
        mock_model_service = Mock()
        mock_model_service.select_models_for_battle.return_value = (mock_model_a, mock_model_b)
        mock_get_model_service.return_value = mock_model_service

        # Mock LLM client
        mock_client = AsyncMock()
        mock_client.chat_completion.side_effect = [
            mock_left_response,
            mock_right_response,
        ]
        mock_get_client.return_value = mock_client

        # Act
        response = client.post("/api/sessions", json={"prompt": prompt})

    # Assert
    assert response.status_code == 201
    data = response.json()

    # Check response structure
    assert "session_id" in data
    assert "battle_id" in data
    assert "message_id" in data
    assert data["message_id"] == "msg_1"  # First message
    assert "responses" in data
    assert len(data["responses"]) == 2

    # Check response format
    left_response = data["responses"][0]
    right_response = data["responses"][1]

    assert left_response["position"] == "left"
    assert "text" in left_response
    assert "latency_ms" in left_response
    assert len(left_response["text"]) > 0
    assert left_response["latency_ms"] == 250  # Mock value

    assert right_response["position"] == "right"
    assert "text" in right_response
    assert "latency_ms" in right_response
    assert len(right_response["text"]) > 0
    assert right_response["latency_ms"] == 300  # Mock value

    # Verify responses match mock data
    assert left_response["text"] == "The capital of France is Paris."
    assert right_response["text"] == "Paris is the capital city of France."


def test_create_session_empty_prompt(client: TestClient):
    """
    Test session creation with empty prompt fails

    Scenario:
    1. User submits empty prompt
    2. Returns 422 validation error
    """
    # Arrange
    prompt = ""

    # Act
    response = client.post("/api/sessions", json={"prompt": prompt})

    # Assert
    assert response.status_code == 422


def test_create_session_too_long_prompt(client: TestClient):
    """
    Test session creation with excessively long prompt fails

    Scenario:
    1. User submits prompt > 10000 characters
    2. Returns 422 validation error
    """
    # Arrange
    prompt = "A" * 10001

    # Act
    response = client.post("/api/sessions", json={"prompt": prompt})

    # Assert
    assert response.status_code == 422

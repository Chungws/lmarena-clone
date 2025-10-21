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

    mock_model_a = ModelConfig(
        {
            "id": "llama-3-1-8b",
            "name": "Llama 3.1 8B",
            "model": "llama3.1:8b",
            "base_url": "http://localhost:11434/v1",
            "api_key_env": None,
            "organization": "Meta",
            "license": "open-source",
            "status": "active",
        }
    )

    mock_model_b = ModelConfig(
        {
            "id": "qwen-2-5-7b",
            "name": "Qwen 2.5 7B",
            "model": "qwen2.5:7b",
            "base_url": "http://localhost:11434/v1",
            "api_key_env": None,
            "organization": "Alibaba",
            "license": "open-source",
            "status": "active",
        }
    )

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

    with (
        patch(
            "llmbattler_backend.services.session_service.get_model_service"
        ) as mock_get_model_service,
        patch("llmbattler_backend.services.session_service.get_llm_client") as mock_get_client,
    ):
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


def test_create_new_battle_in_session_success(client: TestClient):
    """
    Test creating a new battle in existing session

    Scenario:
    1. User has existing session with one battle
    2. User submits new prompt for second battle
    3. System selects 2 NEW random models (different from first battle)
    4. System calls both LLMs in parallel
    5. System creates new battle in same session
    6. System updates session.last_active_at
    7. Returns anonymous responses
    """
    # Arrange
    session_id = "session_abc123"
    prompt = "Tell me about Python programming"

    # Mock existing session in database
    from datetime import UTC, datetime

    from llmbattler_shared.models import Session

    mock_session = Session(
        id=1,
        session_id=session_id,
        title="What is the capital of France?",
        user_id=None,
        created_at=datetime.now(UTC),
        last_active_at=datetime.now(UTC),
    )

    # Mock model configs
    from llmbattler_backend.services.model_service import ModelConfig

    mock_model_c = ModelConfig(
        {
            "id": "gpt-4o-mini",
            "name": "GPT-4o Mini",
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1",
            "api_key_env": "OPENAI_API_KEY",
            "organization": "OpenAI",
            "license": "proprietary",
            "status": "active",
        }
    )

    mock_model_d = ModelConfig(
        {
            "id": "claude-3-5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "model": "claude-3-5-sonnet-20241022",
            "base_url": "https://api.anthropic.com/v1",
            "api_key_env": "ANTHROPIC_API_KEY",
            "organization": "Anthropic",
            "license": "proprietary",
            "status": "active",
        }
    )

    # Mock LLM responses
    from llmbattler_backend.services.llm_client import LLMResponse

    mock_left_response = LLMResponse(
        content="Python is a high-level programming language...",
        latency_ms=320,
        model_id="gpt-4o-mini",
    )
    mock_right_response = LLMResponse(
        content="Python is an interpreted language...",
        latency_ms=280,
        model_id="claude-3-5-sonnet",
    )

    # Mock battle to be created
    from llmbattler_shared.models import Battle

    mock_battle = Battle(
        id=1,
        battle_id="battle_xyz789",
        session_id=session_id,
        left_model_id="gpt-4o-mini",
        right_model_id="claude-3-5-sonnet",
        conversation=[],
        status="ongoing",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with (
        patch(
            "llmbattler_backend.services.session_service.SessionRepository"
        ) as mock_session_repo_class,
        patch(
            "llmbattler_backend.services.session_service.BattleRepository"
        ) as mock_battle_repo_class,
        patch(
            "llmbattler_backend.services.session_service.get_model_service"
        ) as mock_get_model_service,
        patch("llmbattler_backend.services.session_service.get_llm_client") as mock_get_client,
    ):
        # Mock session repository
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_session_id.return_value = mock_session
        mock_session_repo.update.return_value = mock_session
        mock_session_repo_class.return_value = mock_session_repo

        # Mock battle repository
        mock_battle_repo = AsyncMock()
        mock_battle_repo.create.return_value = mock_battle
        mock_battle_repo_class.return_value = mock_battle_repo

        # Mock model service
        mock_model_service = Mock()
        mock_model_service.select_models_for_battle.return_value = (mock_model_c, mock_model_d)
        mock_get_model_service.return_value = mock_model_service

        # Mock LLM client
        mock_client = AsyncMock()
        mock_client.chat_completion.side_effect = [
            mock_left_response,
            mock_right_response,
        ]
        mock_get_client.return_value = mock_client

        # Act
        response = client.post(f"/api/sessions/{session_id}/battles", json={"prompt": prompt})

    # Assert
    assert response.status_code == 201
    data = response.json()

    # Check response structure (BattleResponse schema)
    assert "battle_id" in data
    assert "message_id" in data
    assert data["message_id"] == "msg_1"  # First message of new battle
    assert "responses" in data
    assert len(data["responses"]) == 2

    # Check response format
    left_response = data["responses"][0]
    right_response = data["responses"][1]

    assert left_response["position"] == "left"
    assert left_response["text"] == "Python is a high-level programming language..."
    assert left_response["latency_ms"] == 320

    assert right_response["position"] == "right"
    assert right_response["text"] == "Python is an interpreted language..."
    assert right_response["latency_ms"] == 280

    # Verify session.last_active_at was updated
    mock_session_repo.update.assert_called_once()


def test_create_new_battle_session_not_found(client: TestClient):
    """
    Test creating battle with non-existent session ID fails

    Scenario:
    1. User provides invalid session_id
    2. Returns 404 not found error
    """
    # Arrange
    session_id = "session_nonexistent"
    prompt = "Test prompt"

    with patch(
        "llmbattler_backend.services.session_service.SessionRepository"
    ) as mock_session_repo_class:
        # Mock session not found
        mock_session_repo = AsyncMock()
        mock_session_repo.get_by_session_id.return_value = None
        mock_session_repo_class.return_value = mock_session_repo

        # Act
        response = client.post(f"/api/sessions/{session_id}/battles", json={"prompt": prompt})

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

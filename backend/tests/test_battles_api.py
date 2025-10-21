"""
Tests for battle API endpoints
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient
from llmbattler_shared.models import Battle

from llmbattler_backend.services.llm_client import LLMResponse


def test_add_follow_up_message_success(client: TestClient):
    """
    Test adding follow-up message to existing battle

    Scenario:
    1. User has existing battle with 1 user message + 2 assistant responses
    2. User submits follow-up prompt
    3. System retrieves conversation history from battle (JSONB)
    4. System calls LLM APIs with full message history (OpenAI chat format)
    5. System appends new messages to battle.conversation using || operator
    6. Returns anonymous responses with message_count
    """
    # Arrange
    battle_id = "battle_xyz789"
    follow_up_prompt = "What about its population?"

    # Mock existing battle with conversation history
    existing_conversation = [
        {
            "role": "user",
            "content": "What is the capital of France?",
            "timestamp": "2025-01-21T10:00:00Z",
        },
        {
            "role": "assistant",
            "model_id": "gpt-4o-mini",
            "position": "left",
            "content": "The capital of France is Paris.",
            "latency_ms": 250,
            "timestamp": "2025-01-21T10:00:01Z",
        },
        {
            "role": "assistant",
            "model_id": "llama-3-1-8b",
            "position": "right",
            "content": "Paris is the capital city of France.",
            "latency_ms": 300,
            "timestamp": "2025-01-21T10:00:01Z",
        },
    ]

    mock_battle = Battle(
        id=1,
        battle_id=battle_id,
        session_id="session_abc123",
        left_model_id="gpt-4o-mini",
        right_model_id="llama-3-1-8b",
        conversation=existing_conversation,
        status="ongoing",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # Mock model configs
    from llmbattler_backend.services.model_service import ModelConfig

    mock_model_left = ModelConfig(
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

    mock_model_right = ModelConfig(
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

    # Mock LLM responses
    mock_left_response = LLMResponse(
        content="Paris has approximately 2.1 million people in the city proper.",
        latency_ms=280,
        model_id="gpt-4o-mini",
    )
    mock_right_response = LLMResponse(
        content="The population of Paris is around 2.2 million inhabitants.",
        latency_ms=310,
        model_id="llama-3-1-8b",
    )

    with (
        patch(
            "llmbattler_backend.services.session_service.BattleRepository"
        ) as mock_battle_repo_class,
        patch(
            "llmbattler_backend.services.session_service.get_model_service"
        ) as mock_get_model_service,
        patch("llmbattler_backend.services.session_service.get_llm_client") as mock_get_client,
    ):
        # Mock battle repository
        mock_battle_repo = AsyncMock()
        mock_battle_repo.get_by_battle_id.return_value = mock_battle
        mock_battle_repo.update.return_value = mock_battle
        mock_battle_repo_class.return_value = mock_battle_repo

        # Mock model service
        mock_model_service = Mock()
        mock_model_service.get_model.side_effect = lambda model_id: (
            mock_model_left if model_id == "gpt-4o-mini" else mock_model_right
        )
        mock_get_model_service.return_value = mock_model_service

        # Mock LLM client
        mock_client = AsyncMock()
        mock_client.chat_completion.side_effect = [
            mock_left_response,
            mock_right_response,
        ]
        mock_get_client.return_value = mock_client

        # Act
        response = client.post(
            f"/api/battles/{battle_id}/messages", json={"prompt": follow_up_prompt}
        )

    # Assert
    assert response.status_code == 201
    data = response.json()

    # Check response structure (FollowUpResponse schema)
    assert "battle_id" in data
    assert data["battle_id"] == battle_id
    assert "message_id" in data
    assert data["message_id"] == "msg_2"  # Second user message
    assert "responses" in data
    assert len(data["responses"]) == 2
    assert "message_count" in data
    assert data["message_count"] == 2  # 2 user messages total (initial + follow-up)
    assert "max_messages" in data
    assert data["max_messages"] == 6

    # Check response format
    left_response = data["responses"][0]
    right_response = data["responses"][1]

    assert left_response["position"] == "left"
    assert left_response["text"] == "Paris has approximately 2.1 million people in the city proper."
    assert left_response["latency_ms"] == 280

    assert right_response["position"] == "right"
    assert right_response["text"] == "The population of Paris is around 2.2 million inhabitants."
    assert right_response["latency_ms"] == 310

    # Verify LLM client was called with full conversation history
    mock_client.chat_completion.assert_any_call(
        mock_model_left,
        [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."},
            {"role": "user", "content": follow_up_prompt},
        ],
    )
    mock_client.chat_completion.assert_any_call(
        mock_model_right,
        [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "Paris is the capital city of France."},
            {"role": "user", "content": follow_up_prompt},
        ],
    )

    # Verify battle.conversation was updated
    mock_battle_repo.update.assert_called_once()


def test_add_follow_up_message_battle_not_found(client: TestClient):
    """
    Test adding follow-up message to non-existent battle fails

    Scenario:
    1. User provides invalid battle_id
    2. Returns 404 not found error
    """
    # Arrange
    battle_id = "battle_nonexistent"
    prompt = "Follow-up question"

    with patch(
        "llmbattler_backend.services.session_service.BattleRepository"
    ) as mock_battle_repo_class:
        # Mock battle not found
        mock_battle_repo = AsyncMock()
        mock_battle_repo.get_by_battle_id.return_value = None
        mock_battle_repo_class.return_value = mock_battle_repo

        # Act
        response = client.post(f"/api/battles/{battle_id}/messages", json={"prompt": prompt})

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_add_follow_up_message_battle_already_voted(client: TestClient):
    """
    Test adding follow-up message to voted battle fails

    Scenario:
    1. User tries to add message to battle that has been voted
    2. Returns 400 bad request error
    """
    # Arrange
    battle_id = "battle_voted123"
    prompt = "Follow-up question"

    mock_battle = Battle(
        id=1,
        battle_id=battle_id,
        session_id="session_abc123",
        left_model_id="gpt-4o-mini",
        right_model_id="llama-3-1-8b",
        conversation=[],
        status="voted",  # Battle already voted
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with patch(
        "llmbattler_backend.services.session_service.BattleRepository"
    ) as mock_battle_repo_class:
        # Mock battle found but voted
        mock_battle_repo = AsyncMock()
        mock_battle_repo.get_by_battle_id.return_value = mock_battle
        mock_battle_repo_class.return_value = mock_battle_repo

        # Act
        response = client.post(f"/api/battles/{battle_id}/messages", json={"prompt": prompt})

    # Assert
    assert response.status_code == 400
    assert (
        "voted" in response.json()["detail"].lower()
        or "cannot add" in response.json()["detail"].lower()
    )


def test_vote_on_battle_success(client: TestClient):
    """
    Test voting on battle successfully

    Scenario:
    1. User submits vote on ongoing battle
    2. System creates vote record with denormalized model IDs
    3. System updates battle.status to 'voted'
    4. System updates session.last_active_at
    5. Returns vote confirmation with revealed model identities
    """
    # Arrange
    battle_id = "battle_abc123"
    vote_choice = "left_better"

    mock_battle = Battle(
        id=1,
        battle_id=battle_id,
        session_id="session_xyz789",
        left_model_id="gpt-4o-mini",
        right_model_id="llama-3-1-8b",
        conversation=[
            {
                "role": "user",
                "content": "What is Python?",
                "timestamp": "2025-10-21T10:00:00Z",
            },
            {
                "role": "assistant",
                "model_id": "gpt-4o-mini",
                "position": "left",
                "content": "Python is a programming language.",
                "latency_ms": 250,
                "timestamp": "2025-10-21T10:00:01Z",
            },
            {
                "role": "assistant",
                "model_id": "llama-3-1-8b",
                "position": "right",
                "content": "Python is a high-level language.",
                "latency_ms": 280,
                "timestamp": "2025-10-21T10:00:01Z",
            },
        ],
        status="ongoing",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with patch(
        "llmbattler_backend.services.session_service.BattleRepository"
    ) as mock_battle_repo_class, patch(
        "llmbattler_backend.services.session_service.SessionRepository"
    ) as mock_session_repo_class, patch(
        "llmbattler_backend.services.session_service.VoteRepository"
    ) as mock_vote_repo_class:
        # Mock repositories
        mock_battle_repo = AsyncMock()
        mock_session_repo = AsyncMock()
        mock_vote_repo = AsyncMock()

        mock_battle_repo.get_by_battle_id.return_value = mock_battle
        mock_battle_repo.update_status.return_value = None
        mock_session_repo.update_last_active_at.return_value = None
        mock_vote_repo.create.return_value = None

        mock_battle_repo_class.return_value = mock_battle_repo
        mock_session_repo_class.return_value = mock_session_repo
        mock_vote_repo_class.return_value = mock_vote_repo

        # Act
        response = client.post(
            f"/api/battles/{battle_id}/vote",
            json={"vote": vote_choice},
        )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["battle_id"] == battle_id
    assert data["vote"] == vote_choice
    assert data["revealed_models"]["left"] == "gpt-4o-mini"
    assert data["revealed_models"]["right"] == "llama-3-1-8b"


def test_vote_on_battle_not_found(client: TestClient):
    """
    Test voting on non-existent battle fails

    Scenario:
    1. User submits vote on non-existent battle
    2. Returns 404 not found error
    """
    # Arrange
    battle_id = "battle_nonexistent"
    vote_choice = "left_better"

    with patch(
        "llmbattler_backend.services.session_service.BattleRepository"
    ) as mock_battle_repo_class:
        # Mock battle not found
        mock_battle_repo = AsyncMock()
        mock_battle_repo.get_by_battle_id.return_value = None
        mock_battle_repo_class.return_value = mock_battle_repo

        # Act
        response = client.post(
            f"/api/battles/{battle_id}/vote",
            json={"vote": vote_choice},
        )

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_vote_on_battle_already_voted(client: TestClient):
    """
    Test voting on already-voted battle fails

    Scenario:
    1. User tries to vote on battle that has already been voted
    2. Returns 400 bad request error
    """
    # Arrange
    battle_id = "battle_already_voted"
    vote_choice = "left_better"

    mock_battle = Battle(
        id=1,
        battle_id=battle_id,
        session_id="session_xyz789",
        left_model_id="gpt-4o-mini",
        right_model_id="llama-3-1-8b",
        conversation=[],
        status="voted",  # Already voted
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    with patch(
        "llmbattler_backend.services.session_service.BattleRepository"
    ) as mock_battle_repo_class:
        # Mock battle found but already voted
        mock_battle_repo = AsyncMock()
        mock_battle_repo.get_by_battle_id.return_value = mock_battle
        mock_battle_repo_class.return_value = mock_battle_repo

        # Act
        response = client.post(
            f"/api/battles/{battle_id}/vote",
            json={"vote": vote_choice},
        )

    # Assert
    assert response.status_code == 400
    detail = response.json()["detail"].lower()
    assert ("already" in detail and "voted" in detail) or "been voted" in detail

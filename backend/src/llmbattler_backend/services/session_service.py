"""
Session and battle business logic service
"""

import asyncio
import logging
import random
import uuid
from datetime import datetime
from typing import Dict, List

from llmbattler_shared.models import Battle, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .llm_client import get_llm_client
from .model_service import ModelConfig, get_model_service

logger = logging.getLogger(__name__)


async def create_session_with_battle(
    prompt: str,
    db: AsyncSession,
) -> Dict:
    """
    Create new session with first battle

    Flow:
    1. Create session record
    2. Select 2 random models
    3. Call LLMs in parallel
    4. Create battle with conversation
    5. Return anonymous responses

    Args:
        prompt: User's initial prompt
        db: Database session

    Returns:
        Dict with session_id, battle_id, message_id, responses

    Raises:
        Exception: If LLM API fails or model selection fails
    """
    logger.info(f"Creating session with prompt: {prompt[:50]}...")

    # 1. Create session
    session_id = f"session_{uuid.uuid4().hex[:12]}"
    session = Session(
        session_id=session_id,
        title=prompt[:200],  # Use first 200 chars as title
        user_id=None,  # Anonymous in MVP
        created_at=datetime.utcnow(),
        last_active_at=datetime.utcnow(),
    )
    db.add(session)
    await db.flush()  # Get session.id

    logger.info(f"Session created: {session_id}")

    # 2. Select 2 random models
    model_service = get_model_service()
    model_a, model_b = model_service.select_models_for_battle()

    # 3. Randomly assign left/right positions (prevent position bias)
    if random.random() < 0.5:
        left_model, right_model = model_a, model_b
    else:
        left_model, right_model = model_b, model_a

    logger.info(f"Models selected: left={left_model.id}, right={right_model.id}")

    # 4. Call LLMs in parallel
    llm_client = get_llm_client()

    messages = [{"role": "user", "content": prompt}]

    try:
        # Parallel API calls
        left_task = llm_client.chat_completion(left_model, messages)
        right_task = llm_client.chat_completion(right_model, messages)

        left_response, right_response = await asyncio.gather(
            left_task, right_task
        )

        logger.info(
            f"LLM responses received: "
            f"left={left_response.latency_ms}ms, "
            f"right={right_response.latency_ms}ms"
        )

    except Exception as e:
        logger.error(f"LLM API call failed: {e}")
        # Rollback session creation
        await db.rollback()
        raise Exception(f"Failed to get LLM responses: {str(e)}")

    # 5. Create battle with conversation
    battle_id = f"battle_{uuid.uuid4().hex[:12]}"

    conversation = [
        {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.utcnow().isoformat(),
        },
        {
            "role": "assistant",
            "model_id": left_model.id,
            "position": "left",
            "content": left_response.content,
            "latency_ms": left_response.latency_ms,
            "timestamp": datetime.utcnow().isoformat(),
        },
        {
            "role": "assistant",
            "model_id": right_model.id,
            "position": "right",
            "content": right_response.content,
            "latency_ms": right_response.latency_ms,
            "timestamp": datetime.utcnow().isoformat(),
        },
    ]

    battle = Battle(
        battle_id=battle_id,
        session_id=session_id,
        left_model_id=left_model.id,
        right_model_id=right_model.id,
        conversation=conversation,
        status="ongoing",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(battle)

    # Commit both session and battle
    await db.commit()

    logger.info(f"Battle created: {battle_id}")

    # 6. Return anonymous responses
    return {
        "session_id": session_id,
        "battle_id": battle_id,
        "message_id": "msg_1",  # First message
        "responses": [
            {
                "position": "left",
                "text": left_response.content,
                "latency_ms": left_response.latency_ms,
            },
            {
                "position": "right",
                "text": right_response.content,
                "latency_ms": right_response.latency_ms,
            },
        ],
    }

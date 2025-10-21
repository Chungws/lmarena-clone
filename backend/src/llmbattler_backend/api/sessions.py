"""
Session API endpoints
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from llmbattler_shared.schemas import BattleCreate, BattleResponse, SessionCreate, SessionResponse
from sqlalchemy.ext.asyncio import AsyncSession

from llmbattler_backend.database import get_db
from llmbattler_backend.services.session_service import (
    create_battle_in_session,
    create_session_with_battle,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create new session with first battle

    Flow:
    1. User submits initial prompt
    2. System creates session
    3. System selects 2 random models
    4. System calls both LLMs in parallel
    5. System creates battle with conversation
    6. Returns anonymous responses (model IDs hidden)

    Args:
        data: Session creation request with prompt
        db: Database session

    Returns:
        SessionResponse with session_id, battle_id, and anonymous responses

    Raises:
        HTTPException 500: If LLM API fails or internal error occurs
    """
    try:
        result = await create_session_with_battle(data.prompt, db)
        return result

    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}",
        )


@router.post(
    "/sessions/{session_id}/battles",
    response_model=BattleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_battle(
    session_id: str,
    data: BattleCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create new battle in existing session

    Flow:
    1. User submits new prompt for second battle
    2. System verifies session exists
    3. System updates session.last_active_at
    4. System selects 2 NEW random models (different from previous battle)
    5. System calls both LLMs in parallel
    6. System creates new battle in same session
    7. Returns anonymous responses (model IDs hidden)

    Args:
        session_id: Existing session ID
        data: Battle creation request with prompt
        db: Database session

    Returns:
        BattleResponse with battle_id and anonymous responses

    Raises:
        HTTPException 404: If session not found
        HTTPException 500: If LLM API fails or internal error occurs
    """
    try:
        result = await create_battle_in_session(session_id, data.prompt, db)
        return result

    except ValueError:
        logger.error(f"Session not found: {session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )

    except Exception as e:
        logger.error(f"Failed to create battle in session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create battle: {str(e)}",
        )

"""
Battle API endpoints
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from llmbattler_shared.schemas import FollowUpCreate, FollowUpResponse
from sqlalchemy.ext.asyncio import AsyncSession

from llmbattler_backend.database import get_db
from llmbattler_backend.services.session_service import add_follow_up_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/battles/{battle_id}/messages",
    response_model=FollowUpResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_message_to_battle(
    battle_id: str,
    data: FollowUpCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Add follow-up message to existing battle

    Flow:
    1. User submits follow-up prompt
    2. System retrieves conversation history from battle (JSONB)
    3. System calls LLM APIs with full message history (OpenAI chat format)
    4. System appends new messages to battle.conversation using || operator
    5. Returns anonymous responses with message_count

    Args:
        battle_id: Existing battle ID
        data: Follow-up message request with prompt
        db: Database session

    Returns:
        FollowUpResponse with battle_id, message_id, responses, message_count

    Raises:
        HTTPException 404: If battle not found
        HTTPException 400: If battle status is not 'ongoing' (e.g., already voted)
        HTTPException 500: If LLM API fails or internal error occurs
    """
    try:
        result = await add_follow_up_message(battle_id, data.prompt, db)
        return result

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            logger.error(f"Battle not found: {battle_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Battle not found: {battle_id}",
            )
        elif "status" in error_msg or "voted" in error_msg:
            logger.error(f"Cannot add message to battle {battle_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    except Exception as e:
        logger.error(f"Failed to add message to battle {battle_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add message: {str(e)}",
        )

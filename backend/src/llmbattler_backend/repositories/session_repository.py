"""
Session repository for database operations
"""

from typing import Optional

from llmbattler_shared.models import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """Repository for Session model operations"""

    def __init__(self, db: AsyncSession):
        super().__init__(Session, db)

    async def get_by_session_id(self, session_id: str) -> Optional[Session]:
        """
        Get session by session_id string

        Args:
            session_id: Unique session identifier (e.g., "session_abc123")

        Returns:
            Session instance or None if not found
        """
        return await self.get_by_field("session_id", session_id)

    async def get_by_user_id(self, user_id: int, limit: Optional[int] = None) -> list[Session]:
        """
        Get all sessions for a user

        Args:
            user_id: User ID
            limit: Optional limit on number of sessions

        Returns:
            List of session instances
        """
        stmt = select(Session).where(Session.user_id == user_id).order_by(Session.last_active_at.desc())
        if limit:
            stmt = stmt.limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

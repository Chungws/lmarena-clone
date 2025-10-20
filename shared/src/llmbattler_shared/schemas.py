"""
Pydantic schemas for API requests/responses (shared between backend and frontend)
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ==================== Battle Schemas ====================


class BattleCreate(BaseModel):
    """Request schema for creating a new battle"""
    prompt: str = Field(..., min_length=1, max_length=10000)


class Response(BaseModel):
    """Single model response in a battle"""
    position: Literal["left", "right"]
    text: str
    latency_ms: int


class BattleResponse(BaseModel):
    """Response schema for battle creation"""
    battle_id: str
    message_id: str
    responses: List[Response]


class FollowUpCreate(BaseModel):
    """Request schema for follow-up message"""
    prompt: str = Field(..., min_length=1, max_length=10000)


class FollowUpResponse(BaseModel):
    """Response schema for follow-up message"""
    battle_id: str
    message_id: str
    responses: List[Response]
    message_count: int  # Total messages in conversation (1-6)
    max_messages: int = 6  # Maximum allowed messages


# ==================== Vote Schemas ====================


class VoteCreate(BaseModel):
    """Request schema for submitting a vote"""
    vote: Literal["left_better", "right_better", "tie", "both_bad"]


class RevealedModels(BaseModel):
    """Model identities revealed after voting"""
    left: str  # model_id
    right: str  # model_id


class VoteResponse(BaseModel):
    """Response schema for vote submission"""
    battle_id: str
    vote: str
    revealed_models: RevealedModels


# ==================== Model Schemas ====================


class ModelInfo(BaseModel):
    """Single model information"""
    model_id: str
    name: str
    provider: str
    status: Literal["active", "inactive"]


class ModelsListResponse(BaseModel):
    """Response schema for GET /api/models"""
    models: List[ModelInfo]


# ==================== Leaderboard Schemas ====================


class ModelStatsResponse(BaseModel):
    """Single model statistics in leaderboard"""
    rank: int
    model_id: str
    model_name: str
    elo_score: int
    elo_ci: float
    vote_count: int
    win_rate: float
    organization: str
    license: str


class LeaderboardMetadata(BaseModel):
    """Leaderboard metadata"""
    total_models: int
    total_votes: int
    last_updated: datetime


class LeaderboardResponse(BaseModel):
    """Response schema for GET /api/leaderboard"""
    leaderboard: List[ModelStatsResponse]
    metadata: LeaderboardMetadata


# ==================== Error Schemas ====================


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    status_code: int

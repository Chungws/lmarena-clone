"""
SQLModel models for PostgreSQL (shared between backend and worker)
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ModelStats(SQLModel, table=True):
    """
    Leaderboard model statistics (PostgreSQL)

    Updated by worker hourly based on MongoDB votes
    """
    __tablename__ = "model_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    model_id: str = Field(unique=True, index=True, max_length=255)
    elo_score: int = Field(default=1500, index=True)
    elo_ci: float = Field(default=200.0)  # 95% confidence interval
    vote_count: int = Field(default=0, index=True)
    win_count: int = Field(default=0)
    loss_count: int = Field(default=0)
    tie_count: int = Field(default=0)
    win_rate: float = Field(default=0.0)
    organization: str = Field(max_length=255)
    license: str = Field(max_length=50)  # 'proprietary', 'open-source', etc.
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkerStatus(SQLModel, table=True):
    """
    Worker execution status tracking (PostgreSQL)

    Stores last successful worker run timestamp
    """
    __tablename__ = "worker_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    worker_name: str = Field(unique=True, max_length=100)  # e.g., "elo_aggregator"
    last_run_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(max_length=50)  # 'success', 'failed', 'running'
    votes_processed: int = Field(default=0)
    error_message: Optional[str] = Field(default=None, max_length=1000)

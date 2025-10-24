"""
Worker main entry point

Runs hourly cron job to aggregate votes from PostgreSQL
and update ELO ratings.
"""

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict

import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from llmbattler_shared.config import settings
from llmbattler_shared.logging_config import setup_logging
from llmbattler_shared.models import WorkerStatus

from .aggregators.elo_aggregator import ELOAggregator
from .database import async_session_maker


# Configure package-level logging
# Child modules (e.g., llmbattler_worker.*) will inherit this configuration
logger = setup_logging("llmbattler_worker")


def load_model_configs() -> Dict[str, Dict[str, str]]:
    """
    Load model configurations from YAML file

    Returns:
        Dict mapping model_id -> {organization, license}
    """
    config_path = Path(settings.models_config_path)

    if not config_path.exists():
        logger.warning(f"Model config not found: {config_path}, using defaults")
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not config or "models" not in config:
            logger.warning("Invalid model config: missing 'models' key")
            return {}

        # Extract organization and license for each model
        model_configs = {}
        for model_dict in config["models"]:
            model_id = model_dict.get("id")
            if model_id:
                model_configs[model_id] = {
                    "organization": model_dict.get("organization", "Unknown"),
                    "license": model_dict.get("license", "Unknown"),
                }

        logger.info(f"Loaded configs for {len(model_configs)} models")
        return model_configs

    except Exception as e:
        logger.error(f"Failed to load model config: {e}")
        return {}


async def run_aggregation(session: AsyncSession | None = None):
    """
    Main aggregation task

    Steps:
    1. Read pending votes from PostgreSQL
    2. Calculate ELO ratings for each model
    3. Update model_stats in PostgreSQL
    4. Update worker_status with execution metadata

    Args:
        session: Optional database session (for testing). If None, creates own session.
    """
    logger.info("Starting vote aggregation...")

    # Use provided session or create new one
    if session is not None:
        # Testing mode: use provided session
        await _run_aggregation_with_session(session)
    else:
        # Production mode: create own session
        async with async_session_maker() as session:
            try:
                await _run_aggregation_with_session(session)
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


async def _run_aggregation_with_session(session: AsyncSession):
    """
    Run aggregation with provided session

    Args:
        session: Database session to use
    """
    votes_processed = 0
    status = "success"
    error_message = None

    try:
        # Load model configs for organization and license info
        model_configs = load_model_configs()

        # Run ELO aggregation
        aggregator = ELOAggregator(session, model_configs=model_configs)
        votes_processed = await aggregator.process_pending_votes()

        # Update worker_status
        await _update_worker_status(
            session,
            votes_processed=votes_processed,
            status=status,
            error_message=error_message,
        )

        logger.info(f"Vote aggregation complete: {votes_processed} votes processed")

    except Exception as e:
        logger.error(f"Aggregation failed: {e}", exc_info=True)
        # Try to update worker_status with error
        try:
            await _update_worker_status(
                session,
                votes_processed=0,
                status="failed",
                error_message=str(e)[:1000],
            )
        except Exception as inner_e:
            logger.error(f"Failed to update worker_status: {inner_e}", exc_info=True)
        raise


async def _update_worker_status(
    session,
    votes_processed: int,
    status: str,
    error_message: str | None,
):
    """
    Update worker_status table with execution metadata

    Args:
        session: Database session
        votes_processed: Number of votes processed in this run
        status: 'success' or 'failed'
        error_message: Error message if failed, None otherwise
    """
    # Get or create worker_status
    result = await session.execute(
        select(WorkerStatus).where(WorkerStatus.worker_name == "elo_aggregator")
    )
    worker_status = result.scalar_one_or_none()

    if worker_status is None:
        # Create new status
        worker_status = WorkerStatus(
            worker_name="elo_aggregator",
            last_run_at=datetime.now(UTC),
            status=status,
            votes_processed=votes_processed,
            error_message=error_message,
        )
        session.add(worker_status)
    else:
        # Update existing status
        worker_status.last_run_at = datetime.now(UTC)
        worker_status.status = status
        worker_status.votes_processed = votes_processed
        worker_status.error_message = error_message

    await session.commit()
    logger.info(f"Updated worker_status: {status}, {votes_processed} votes")


async def main():
    """
    Start worker with scheduler

    Runs hourly at :00 UTC by default
    Configurable via WORKER_INTERVAL_HOURS environment variable
    """
    logger.info("Starting llmbattler-worker...")
    logger.info(f"Scheduler: Every {settings.worker_interval_hours} hour(s) at :00")

    # Create async scheduler
    scheduler = AsyncIOScheduler(timezone=settings.worker_timezone)

    # Schedule hourly aggregation
    # Note: For interval=1, use CronTrigger for precise :00 execution
    # For other intervals, CronTrigger with hour="*" still works (runs every hour)
    if settings.worker_interval_hours == 1:
        # Run every hour at :00
        trigger = CronTrigger(
            hour="*",
            minute="0",
            timezone=settings.worker_timezone,
        )
    else:
        # For intervals > 1 hour, use IntervalTrigger
        # This runs every N hours from the start time
        from apscheduler.triggers.interval import IntervalTrigger

        trigger = IntervalTrigger(
            hours=settings.worker_interval_hours,
            timezone=settings.worker_timezone,
        )
        logger.info(f"Using IntervalTrigger: every {settings.worker_interval_hours} hours")

    scheduler.add_job(
        run_aggregation,
        trigger=trigger,
        id="elo_aggregation",
        name="ELO Rating Aggregation",
        replace_existing=True,
    )

    # Start scheduler
    scheduler.start()
    logger.info("Worker started. Press Ctrl+C to exit.")

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down worker...")
        scheduler.shutdown()
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())

"""
Worker main entry point

Runs hourly cron job to aggregate votes from MongoDB
and update ELO ratings in PostgreSQL.
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from llmbattler_shared.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


async def run_aggregation():
    """
    Main aggregation task

    Steps:
    1. Read new votes from MongoDB (since last run)
    2. Calculate ELO ratings for each model
    3. Update model_stats in PostgreSQL
    4. Update worker_status with last run timestamp
    """
    logger.info("Starting vote aggregation...")

    try:
        # TODO: Initialize database connections
        # - MongoDB (Motor) for reading votes
        # - PostgreSQL (asyncpg) for writing model_stats

        # TODO: Get last run timestamp from worker_status

        # TODO: Read new votes from MongoDB

        # TODO: Calculate ELO ratings

        # TODO: Update PostgreSQL model_stats

        # TODO: Update worker_status

        logger.info("Vote aggregation complete")

    except Exception as e:
        logger.error(f"Aggregation failed: {e}", exc_info=True)
        raise


def main():
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
    scheduler.add_job(
        run_aggregation,
        trigger=CronTrigger(
            hour=f"*/{settings.worker_interval_hours}",
            minute="0",
            timezone=settings.worker_timezone,
        ),
        id="elo_aggregation",
        name="ELO Rating Aggregation",
        replace_existing=True,
    )

    # Start scheduler
    scheduler.start()
    logger.info("Worker started. Press Ctrl+C to exit.")

    # Keep running
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down worker...")
        scheduler.shutdown()
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    main()

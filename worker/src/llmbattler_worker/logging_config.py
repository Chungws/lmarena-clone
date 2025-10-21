"""
Logging configuration for worker

Re-exports shared logging functions for worker use.
"""

from llmbattler_shared.logging_config import setup_logging

# Worker-specific logger instance
logger = setup_logging("llmbattler_worker")

__all__ = ["setup_logging", "logger"]

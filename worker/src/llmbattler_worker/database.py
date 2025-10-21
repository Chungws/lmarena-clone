"""
PostgreSQL database connection for worker

Worker uses connection pooling with smaller pool size than backend API.
Configured for batch operations and lower concurrency.
"""

import os

from databases import Database


def get_database() -> Database:
    """
    Get PostgreSQL database instance with connection pooling

    Returns:
        Database: Configured Database instance

    Pool Configuration:
        - min_size: 2 (worker typically uses fewer connections)
        - max_size: 5 (sufficient for batch operations)
        - timeout: 10 (seconds to wait for connection)

    Environment Variables:
        DATABASE_URL: PostgreSQL connection string
                     Default: postgresql://localhost/llmbattler
    """
    database_url = os.getenv("DATABASE_URL", "postgresql://localhost/llmbattler")

    return Database(
        database_url,
        min_size=2,  # Worker typically uses fewer connections
        max_size=5,  # Sufficient for batch operations
        timeout=10,  # Connection timeout in seconds
    )


# Global database instance (singleton pattern)
database = get_database()

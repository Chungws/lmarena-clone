# Worker Dockerfile for llmbattler

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy workspace root files
COPY pyproject.toml uv.lock ./

# Copy shared package
COPY shared/ ./shared/

# Copy worker package
COPY worker/ ./worker/

# Sync workspace dependencies (includes shared package)
RUN uv sync --frozen

# Copy entrypoint script
COPY worker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set entrypoint to wait for database before starting worker
ENTRYPOINT ["/app/entrypoint.sh"]

# Run worker
CMD ["uv", "run", "--package", "llmbattler-worker", "python", "-m", "llmbattler_worker.main"]

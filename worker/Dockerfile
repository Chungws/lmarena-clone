# Worker Dockerfile for llmbattler

FROM python:3.11-slim

WORKDIR /app

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

# Run worker
CMD ["uv", "run", "--package", "llmbattler-worker", "python", "-m", "llmbattler_worker.main"]

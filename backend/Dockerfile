# Backend Dockerfile for llmbattler

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy workspace root files
COPY pyproject.toml uv.lock ./

# Copy shared package
COPY shared/ ./shared/

# Copy backend package
COPY backend/ ./backend/

# Sync workspace dependencies (includes shared package)
RUN uv sync --frozen

# Copy entrypoint script
COPY backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint to run migrations before starting server
ENTRYPOINT ["/app/entrypoint.sh"]

# Run FastAPI with uvicorn
CMD ["uv", "run", "--package", "llmbattler-backend", "uvicorn", "llmbattler_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

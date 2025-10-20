# Backend Dockerfile for llmbattler

FROM python:3.11-slim

WORKDIR /app

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

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uv", "run", "--package", "llmbattler-backend", "uvicorn", "llmbattler_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

.PHONY: help setup dev dev-infra dev-backend dev-frontend dev-worker stop clean test lint

help:
	@echo "llmbattler Development Commands"
	@echo ""
	@echo "  make setup        - Initial setup (install dependencies)"
	@echo "  make dev          - Start infrastructure and show service commands"
	@echo "  make dev-infra    - Start PostgreSQL + Ollama"
	@echo "  make dev-backend  - Start Backend API (port 8000)"
	@echo "  make dev-frontend - Start Frontend (port 3000)"
	@echo "  make dev-worker   - Start Worker (manual run)"
	@echo ""
	@echo "  make stop         - Stop Docker services"
	@echo "  make clean        - Stop and remove all data (WARNING: deletes DB)"
	@echo "  make test         - Run all tests"
	@echo "  make lint         - Run all linters"

# Initial setup
setup:
	@echo "📦 Installing dependencies..."
	@echo ""
	@echo "🐍 Syncing Python workspace (backend + worker + shared)..."
	@uv sync --all-extras
	@echo ""
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "📝 Next steps:"
	@echo "  1. Copy environment file: cp .env.example .env"
	@echo "  2. Start services: make dev"

# Start infrastructure (PostgreSQL + Ollama)
dev-infra:
	@echo "🚀 Starting infrastructure (PostgreSQL + Ollama)..."
	docker compose --profile dev up -d
	@echo "✅ PostgreSQL started on localhost:5432"
	@echo "✅ Ollama started on localhost:11434"

# Start Backend (requires PostgreSQL)
dev-backend:
	@echo "🚀 Starting Backend API on http://localhost:8000..."
	@echo "🔄 Running database migrations..."
	@cd backend && uv run alembic upgrade head
	@cd backend && uv run uvicorn llmbattler_backend.main:app --reload --port 8000

# Start Frontend
dev-frontend:
	@if [ ! -d "frontend/node_modules" ]; then \
		echo "⚠️  node_modules not found. Running npm install..."; \
		cd frontend && npm install; \
	fi
	@echo "🎨 Starting Frontend on http://localhost:3000..."
	@cd frontend && npm run dev

# Start Worker (manual run)
dev-worker:
	@echo "⚙️  Running Worker (vote aggregation)..."
	@cd worker && uv run python -m llmbattler_worker.main

# Start all services (convenience command)
dev:
	@make dev-infra
	@sleep 3
	@echo ""
	@echo "✅ Infrastructure started!"
	@echo ""
	@echo "📝 Now run in separate terminals:"
	@echo "  Terminal 1: make dev-backend"
	@echo "  Terminal 2: make dev-frontend"
	@echo "  Terminal 3: make dev-worker (optional)"
	@echo ""

# Stop Docker services
stop:
	@echo "🛑 Stopping Docker services..."
	@docker compose --profile dev down
	@echo "✅ Services stopped"

# Clean all data (WARNING)
clean:
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose --profile dev down -v; \
		echo "✅ All data deleted"; \
	else \
		echo "❌ Cancelled"; \
	fi

# Run tests
test:
	@echo "🧪 Running backend tests..."
	@cd backend && uv run pytest -s
	@echo ""
	@echo "🧪 Running worker tests..."
	@cd worker && uv run pytest -s
	@echo ""
	@echo "✅ All tests completed"

# Run linters
lint:
	@echo "🔍 Running backend linters..."
	@uvx ruff check && uvx ruff format --check && uvx isort --check --profile black .
	@echo ""
	@echo "🔍 Running frontend linter..."
	@cd frontend && npm run lint
	@echo ""
	@echo "✅ All linters passed"

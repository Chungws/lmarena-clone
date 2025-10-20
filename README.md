# llmbattler - AI Language Model Battle Arena

> Compare and evaluate LLM responses through blind side-by-side testing

![Project Status](https://img.shields.io/badge/status-initial%20setup-yellow)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Next.js](https://img.shields.io/badge/next.js-15-black)
![FastAPI](https://img.shields.io/badge/fastapi-0.115+-green)

**llmbattler** is an open-source platform for comparing and evaluating Large Language Models through blind A/B testing. Users submit prompts to two randomly selected models, vote on the better response, and contribute to comprehensive ELO-based leaderboards.

Inspired by [LM Arena](https://lmarena.ai), built with modern web technologies.

---

## ✨ Features

- **Blind Testing**: Compare responses from two LLMs side-by-side without knowing which model is which
- **Multi-Turn Conversations**: Up to 6 messages per battle (1 initial + 5 follow-ups)
- **ELO Rankings**: Fair model comparison using chess-style ELO ratings
- **Comprehensive Leaderboards**: Track model performance with confidence intervals
- **Flexible LLM Integration**: OpenAI-compatible API for easy model additions
- **Vote Aggregation**: Hourly worker updates leaderboards from user votes

---

## 🛠️ Tech Stack

### Backend
- **API Server**: FastAPI with async/await
- **Worker**: Python cron job (APScheduler) for data aggregation
- **Databases**:
  - PostgreSQL: Read-optimized aggregated data (leaderboards, statistics)
  - MongoDB: Write-optimized log data (battles, responses, votes)

### Frontend
- **Framework**: Next.js 15 with App Router
- **React**: v19 with React Server Components
- **UI Library**: shadcn/ui (Radix UI + Tailwind CSS)
- **Styling**: Tailwind CSS v4 with dark mode

### Infrastructure
- **Package Manager**: uv (Python), npm (Frontend)
- **Containerization**: Docker + Docker Compose
- **Workspace**: uv workspace for monorepo Python packages

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (required)
- **Node.js 18+** (for frontend development)
- **Python 3.11+** (for backend/worker development)
- **uv** (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Option 1: Full Stack with Docker Compose

```bash
# Clone repository
git clone https://github.com/Chungws/lmarena-clone.git
cd lmarena-clone

# Optional: Customize environment variables
cp .env.example .env

# Start all services (PostgreSQL, MongoDB, Backend, Worker, Frontend)
docker compose up -d

# View logs
docker compose logs -f
```

**Endpoints:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Stop services:**
```bash
docker compose down
```

### Option 2: Local Development (Recommended for Contributors)

```bash
# Clone repository
git clone https://github.com/Chungws/lmarena-clone.git
cd lmarena-clone

# Start databases only
docker compose -f docker-compose.dev.yml up -d

# Install workspace dependencies
uv sync

# Backend (terminal 1)
cd backend
uv run alembic upgrade head  # Run migrations
uv run uvicorn llmbattler_backend.main:app --reload --port 8000

# Frontend (terminal 2)
cd frontend
npm install
npm run dev  # Port 3000

# Worker (terminal 3, optional for local dev)
cd worker
uv run python -m llmbattler_worker.main
```

**Endpoints:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📁 Project Structure

```
lmarena-clone/
├── backend/                  # FastAPI application
│   ├── src/
│   │   └── llmbattler_backend/
│   │       ├── main.py       # FastAPI app entry
│   │       ├── api/          # API routes
│   │       ├── services/     # Business logic
│   │       └── mongodb/      # MongoDB operations
│   ├── tests/                # pytest tests
│   ├── alembic/              # Database migrations
│   └── Dockerfile
│
├── worker/                   # Data aggregation worker
│   ├── src/
│   │   └── llmbattler_worker/
│   │       ├── main.py       # Worker entry (cron job)
│   │       └── aggregators/  # ELO calculation
│   ├── tests/
│   └── Dockerfile
│
├── shared/                   # Shared code (models, schemas, config)
│   └── src/
│       └── llmbattler_shared/
│           ├── models.py     # SQLModel models
│           ├── schemas.py    # Pydantic schemas
│           └── config.py     # Settings
│
├── frontend/                 # Next.js application
│   ├── app/                  # App Router pages
│   │   ├── battle/           # Battle mode page
│   │   └── leaderboard/      # Leaderboard page
│   ├── components/           # React components
│   ├── lib/                  # Utilities
│   └── Dockerfile
│
├── WORKSPACE/                # Documentation
│   ├── 00_PROJECT.md         # Project overview
│   ├── 00_ROADMAP.md         # Development roadmap
│   ├── CONVENTIONS/          # Coding standards
│   ├── ARCHITECTURE/         # Architecture Decision Records
│   └── FEATURES/             # Feature specifications
│
├── docker-compose.dev.yml    # DB only (development)
├── docker-compose.yml        # Full stack
├── pyproject.toml            # uv workspace root
├── uv.lock                   # Unified Python lockfile
└── README.md                 # This file
```

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│ Next.js Client  │ (Battle UI, Leaderboard)
└────────┬────────┘
         │
    ┌────▼─────────┐
    │ FastAPI API  │ (Battle, Leaderboard, Models)
    └────┬─────────┘
         │
         ├──► External LLM APIs (OpenAI, Anthropic, etc.)
         │
         ├──► MongoDB (battles, responses, votes)
         │        │
         │   ┌────▼────────┐
         │   │   Worker    │ (Hourly ELO aggregation)
         │   └────┬────────┘
         │        │
         └──────► PostgreSQL (leaderboards, model_stats)
```

**Key Design Decisions:**
- **No Foreign Keys**: Application-level relationships only ([ADR-001](WORKSPACE/ARCHITECTURE/ADR_001-No_Foreign_Keys.md))
- **Blind Testing**: Model identities hidden until after voting
- **Dual Database**: MongoDB for write-heavy logs, PostgreSQL for read-heavy leaderboards
- **ELO Rankings**: Fair model comparison using chess-style ratings

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [WORKSPACE/00_PROJECT.md](WORKSPACE/00_PROJECT.md) | Comprehensive project overview, policies, setup guide |
| [WORKSPACE/00_ROADMAP.md](WORKSPACE/00_ROADMAP.md) | Development roadmap and milestones |
| [WORKSPACE/CONVENTIONS/](WORKSPACE/CONVENTIONS/) | Coding standards, Git workflow, PR guidelines |
| [WORKSPACE/ARCHITECTURE/](WORKSPACE/ARCHITECTURE/) | Architecture Decision Records (ADRs) |
| [WORKSPACE/FEATURES/](WORKSPACE/FEATURES/) | Feature specifications and phase tracking |
| [CLAUDE.md](CLAUDE.md) | Guidelines for AI assistants working on this project |

**For Contributors:**
- New to the project? Start with [WORKSPACE/00_PROJECT.md](WORKSPACE/00_PROJECT.md)
- Check current status: [WORKSPACE/00_ROADMAP.md](WORKSPACE/00_ROADMAP.md)
- Read coding standards: [WORKSPACE/CONVENTIONS/](WORKSPACE/CONVENTIONS/)

---

## 🧪 Development

### Pre-Commit Checks

Before creating a PR, run these checks:

**Backend/Worker:**
```bash
cd backend  # or worker
uvx ruff check
uvx ruff format --check
uvx isort --check --profile black .
uv run pytest -s
```

**Frontend:**
```bash
cd frontend
npm run lint
# UI changes: Run Playwright MCP for manual verification
```

### Git Workflow

This project uses Git Flow:

1. Create feature branch: `git checkout -b feature/your-feature-name` from `develop`
2. Make changes and commit
3. Push and create PR targeting `develop`
4. After review and merge, delete feature branch

See [WORKSPACE/CONVENTIONS/GIT_FLOW.md](WORKSPACE/CONVENTIONS/GIT_FLOW.md) for details.

### Package Management

**Python (Backend/Worker):**
- Use `uv` for all package operations
- Install: `uv add <package>`
- Run: `uv run <command>`
- Sync workspace: `uv sync` (from root)

**Frontend:**
- Use `npm` for package management
- Install: `npm install`
- Add package: `npm install <package>`

---

## 🎯 Roadmap

**Phase 0: Project Structure Setup** ✅ (Completed)
- Backend, Worker, Frontend boilerplate
- Docker Compose configurations
- Documentation structure

**Phase 1: Battle MVP** (In Progress)
- Battle API endpoints
- LLM integration
- Battle UI

**Phase 2: Leaderboard MVP**
- ELO calculation
- Leaderboard API
- Leaderboard UI

See [WORKSPACE/00_ROADMAP.md](WORKSPACE/00_ROADMAP.md) for full roadmap.

---

## 🤝 Contributing

Contributions are welcome! Please read our documentation before starting:

1. Read [WORKSPACE/00_PROJECT.md](WORKSPACE/00_PROJECT.md) for project overview and policies
2. Check [WORKSPACE/CONVENTIONS/](WORKSPACE/CONVENTIONS/) for coding standards
3. Follow the Git Flow workflow in [WORKSPACE/CONVENTIONS/GIT_FLOW.md](WORKSPACE/CONVENTIONS/GIT_FLOW.md)
4. Write PRs in English following [WORKSPACE/CONVENTIONS/PR_GUIDELINES.md](WORKSPACE/CONVENTIONS/PR_GUIDELINES.md)

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🔗 Resources

- **LM Arena (Inspiration)**: https://lmarena.ai
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Next.js Documentation**: https://nextjs.org/docs
- **shadcn/ui**: https://ui.shadcn.com
- **uv**: https://docs.astral.sh/uv
- **ELO Rating System**: https://en.wikipedia.org/wiki/Elo_rating_system

---

**Built with ❤️ by [Chungws](https://github.com/Chungws)**

**Last Updated:** 2025-01-20

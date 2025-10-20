# llmbattler - Project Overview

**AI Language Model Battle Arena**

Compare and evaluate LLM responses through blind side-by-side testing. Users submit prompts, receive anonymous responses from two randomly selected models, and vote on the better response. Build comprehensive leaderboards using ELO-based rankings.

---

## 📋 Project Information

| Category | Details |
|----------|---------|
| **Project Name** | llmbattler |
| **Repository** | [Chungws/lmarena-clone](https://github.com/Chungws/lmarena-clone) |
| **Tech Stack** | FastAPI, Next.js 15, PostgreSQL, MongoDB, Python Worker |
| **Development Start** | 2025-01-20 |
| **Status** | Initial Setup |

---

## 🔴 Project Policies

This project follows specific policies. **Always check before starting work.**

| Policy | This Project | Reference |
|--------|--------------|-----------|
| **Foreign Keys** | ❌ **NOT used** | [ADR-001](./ARCHITECTURE/ADR_001-No_Foreign_Keys.md) |
| **Main Branch** | ✅ `develop` | [GIT_FLOW.md](./CONVENTIONS/GIT_FLOW.md) |
| **PR Language** | ✅ **English** | [CLAUDE.md](../CLAUDE.md) |
| **PR Assignee** | ✅ **Chungws** | [CLAUDE.md](../CLAUDE.md) |
| **PR Reviewer** | ✅ **Chungws** | [CLAUDE.md](../CLAUDE.md) |
| **Git Host** | ✅ **GitHub** | - |
| **Package Manager (Backend)** | ✅ **uv** | [BACKEND.md](./CONVENTIONS/BACKEND.md) |
| **Package Manager (Worker)** | ✅ **uv** | [BACKEND.md](./CONVENTIONS/BACKEND.md) |
| **Package Manager (Frontend)** | ✅ **npm** | package.json |

### 🚨 Key Policies to Remember

1. **No Foreign Keys (ADR-001)**
   - Do NOT use database-level FK constraints
   - Handle referential integrity in application code with transactions
   - Reason: Flexibility, horizontal scalability, microservice readiness

2. **PRs Always in English**
   - Title, description, checklist all in English
   - Follow GitHub PR best practices

3. **develop Branch is Primary**
   - `feature/*` → `develop` merge

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- uv (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Setup

```bash
# Clone repository
git clone https://github.com/Chungws/lmarena-clone.git
cd lmarena-clone

# Start infrastructure (PostgreSQL + MongoDB)
docker compose up -d

# Backend setup
cd backend
uv sync                       # Install dependencies
uv run alembic upgrade head  # Run migrations
uv run uvicorn app.main:app --reload --port 8000

# Frontend setup (in new terminal)
cd frontend
npm install
npm run dev  # Port 3000

# Worker setup (optional for local dev)
cd worker
uv sync
uv run python -m app.main  # Run aggregation manually
```

**Endpoints:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Pre-Commit Checks

**Backend changes:**
```bash
cd backend
uvx ruff check
uvx ruff format --check
uvx isort --check --profile black .
uv run pytest -s
```

**Frontend changes:**
```bash
cd frontend
npm run lint
# UI changes: Playwright MCP manual verification required! (See CONVENTIONS/FRONTEND.md)
```

**Worker changes:**
```bash
cd worker
uvx ruff check
uvx ruff format --check
uvx isort --check --profile black .
uv run pytest -s
```

---

## 🏗️ Project Structure

```
lmarena-clone/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py      # FastAPI app entry
│   │   ├── api/         # API routes (battle, leaderboard, models)
│   │   ├── models/      # SQLModel models (PostgreSQL)
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── mongodb/     # MongoDB operations
│   ├── tests/           # pytest tests
│   ├── alembic/         # Database migrations
│   └── pyproject.toml
├── frontend/            # Next.js application
│   ├── src/
│   │   ├── app/         # App Router pages
│   │   │   ├── battle/  # Battle mode page
│   │   │   └── leaderboard/  # Leaderboard page
│   │   ├── components/  # React components
│   │   └── lib/         # Utilities
│   └── package.json
├── worker/              # Data aggregation worker
│   ├── app/
│   │   ├── main.py      # Worker entry (cron job)
│   │   └── aggregators/ # Aggregation logic
│   ├── tests/
│   └── pyproject.toml
├── WORKSPACE/           # Documentation
│   ├── 00_PROJECT.md    # This file
│   ├── 00_ROADMAP.md    # Development roadmap
│   ├── CONVENTIONS/     # Coding standards
│   ├── ARCHITECTURE/    # ADRs
│   └── FEATURES/        # Feature specs
├── docker-compose.yml   # Local infrastructure
├── CLAUDE.md            # AI assistant guidelines
└── README.md
```

---

## 🏗️ Architecture Overview

### Component Flow

```
┌─────────┐
│ Client  │ (Next.js 15)
│         │ - Battle UI (blind side-by-side)
│         │ - Leaderboard UI (ELO rankings)
└────┬────┘
     │
┌────▼────────────────┐
│ Backend (FastAPI)   │
│                     │
│ - Battle API        │
│ - Leaderboard API   │
│ - Model Management  │
└────┬────────────────┘
     │
     ├─────► ┌──────────────────┐
     │       │ External LLM API │ (OpenAI, Anthropic, etc.)
     │       └──────────────────┘
     │
     ├─────► ┌──────────────────────────┐
     │       │   GPU Pool (Ollama)      │
     │       │  ┌────────┬────────┐     │
     │       │  │Model 1 │Model 2 │...  │
     │       │  └────────┴────────┘     │
     │       └──────────────────────────┘
     │
     ├─────► ┌────────────┐
     │       │  MongoDB   │ (Write-optimized)
     │       │            │ - battles
     │       │            │ - responses
     │       │            │ - votes
     │       └─────┬──────┘
     │             │
     │       ┌─────▼──────┐
     │       │   Worker   │ (Hourly cron)
     │       │            │ - ELO calculation
     │       │            │ - Statistics aggregation
     │       └─────┬──────┘
     │             │
     └───────────► ┌────────────┐
                   │ PostgreSQL │ (Read-optimized)
                   │            │ - leaderboards
                   │            │ - model_stats
                   └────────────┘
```

### Key Design Decisions

1. **No Foreign Keys (ADR-001)**: Application-level relationships only
2. **Blind Testing**: Model identities hidden until after voting
3. **Dual Database**: MongoDB for logs (write-heavy), PostgreSQL for aggregated data (read-heavy)
4. **ELO Rankings**: Fair model comparison across different match counts
5. **OpenAI-Compatible API**: Easy integration with any LLM provider

---

## 📚 Core Documentation

| Document | Description |
|----------|-------------|
| **[00_ROADMAP.md](./00_ROADMAP.md)** | Development roadmap, MVP milestones |
| **[CONVENTIONS/](./CONVENTIONS/)** | Coding standards, Git workflow, PR guidelines |
| **[ARCHITECTURE/](./ARCHITECTURE/)** | Architecture Decision Records (ADRs) |
| **[FEATURES/](./FEATURES/)** | Feature specifications and phase tracking |

### 💡 Quick Navigation

- **New to the project?** Read this document → [CONVENTIONS/README.md](./CONVENTIONS/README.md)
- **Current development status?** Check [00_ROADMAP.md](./00_ROADMAP.md)
- **Implementing a feature?** Read corresponding `FEATURES/*.md`

---

## 🎯 Role-Specific Documentation

This section guides you to the right documents based on your role. **.claude/ agents and commands reference this section.**

### Backend Developer

Read these documents **in order** before starting work:

1. **This document (00_PROJECT.md)** - Check project policies table
2. **[CONVENTIONS/backend/README.md](./CONVENTIONS/backend/README.md)** - Backend coding standards
3. **[CONVENTIONS/GIT_FLOW.md](./CONVENTIONS/GIT_FLOW.md)** - Git branch strategy
4. **[CONVENTIONS/PR_GUIDELINES.md](./CONVENTIONS/PR_GUIDELINES.md)** - PR writing rules
5. **FEATURES/<feature-name>.md** (if working on a specific feature)

### Frontend Developer

Read these documents **in order** before starting work:

1. **This document (00_PROJECT.md)** - Check project policies table
2. **[CONVENTIONS/frontend/README.md](./CONVENTIONS/frontend/README.md)** - Frontend coding standards
3. **[CONVENTIONS/GIT_FLOW.md](./CONVENTIONS/GIT_FLOW.md)** - Git branch strategy
4. **[CONVENTIONS/PR_GUIDELINES.md](./CONVENTIONS/PR_GUIDELINES.md)** - PR writing rules
5. **FEATURES/<feature-name>.md** (if working on a specific feature)

### Worker Developer

Read these documents **in order** before starting work:

1. **This document (00_PROJECT.md)** - Check project policies table
2. **[CONVENTIONS/backend/README.md](./CONVENTIONS/backend/README.md)** - Python coding standards (same as backend)
3. **[CONVENTIONS/GIT_FLOW.md](./CONVENTIONS/GIT_FLOW.md)** - Git branch strategy
4. **[CONVENTIONS/PR_GUIDELINES.md](./CONVENTIONS/PR_GUIDELINES.md)** - PR writing rules
5. **FEATURES/<feature-name>.md** (if working on aggregation logic)

### Convention Reviewer

Read these documents before code review:

1. **This document (00_PROJECT.md)** - Check project policies table
2. **[CONVENTIONS/README.md](./CONVENTIONS/README.md)** - Full conventions index
3. **Depending on changes:**
   - Backend/Worker: [CONVENTIONS/backend/README.md](./CONVENTIONS/backend/README.md)
   - Frontend: [CONVENTIONS/frontend/README.md](./CONVENTIONS/frontend/README.md)
4. **[CONVENTIONS/CODE_REVIEW.md](./CONVENTIONS/CODE_REVIEW.md)** - Code review checklist

### PR Creator

Read these documents before creating PR:

1. **This document (00_PROJECT.md)** - PR policies (English, main branch, assignee/reviewer)
2. **[CONVENTIONS/PR_GUIDELINES.md](./CONVENTIONS/PR_GUIDELINES.md)** - PR template and format
3. **[CONVENTIONS/COMMIT_GUIDELINES.md](./CONVENTIONS/COMMIT_GUIDELINES.md)** - Commit message format

---

## 🔗 External Resources

- **LM Arena (Inspiration)**: https://lmarena.ai
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Next.js Documentation**: https://nextjs.org/docs
- **Ollama**: https://ollama.ai
- **vLLM**: https://github.com/vllm-project/vllm
- **ELO Rating System**: https://en.wikipedia.org/wiki/Elo_rating_system

---

**💡 This document is the "configuration file" of the project.**
- Check the **policies table** before starting work
- Curious about **current development status**? → [00_ROADMAP.md](./00_ROADMAP.md)
- Want to know **how to implement a feature**? → [CONVENTIONS/](./CONVENTIONS/)

**Last Updated:** 2025-01-20

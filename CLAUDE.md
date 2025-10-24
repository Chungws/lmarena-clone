# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## 📖 Project Overview

**llmbattler** - AI Language Model Battle Arena

Compare and evaluate LLM responses through blind side-by-side testing. Users submit prompts, receive anonymous responses from two randomly selected models, and vote on the better response. Build comprehensive leaderboards using ELO-based rankings.

**Repository:** [Chungws/lmarena-clone](https://github.com/Chungws/lmarena-clone)

---

## 🔴 CRITICAL RULES

### 1. Branch Safety
**BEFORE doing ANY work, ALWAYS check current branch:**
```bash
git branch --show-current
```

**Rules:**
- ❌ NEVER work on `main` branch directly
- ✅ ALWAYS switch to feature branch FIRST
- ✅ Create feature branch: `git checkout -b feature/your-feature-name`

### 2. Project Policies ⚠️

| Policy | This Project | Reference |
|--------|--------------|-----------|
| Foreign Keys | ❌ **NOT used** | [ADR-001](./WORKSPACE/ARCHITECTURE/ADR_001-No_Foreign_Keys.md) |
| Main Branch | ✅ `develop` | - |
| PR Language | ✅ **English** | [PR Guidelines](./WORKSPACE/CONVENTIONS/PR_GUIDELINES.md) |
| PR Assignee | ✅ **Chungws** | - |
| PR Reviewer | ✅ **Chungws** | - |
| Git Host | ✅ **GitHub** | - |

**🚨 ALWAYS check WORKSPACE/00_PROJECT.md for complete policies**

### 3. Pre-Commit Checklist (Must Pass)

**Quick check (all services):**
```bash
make lint  # Run all linters
make test  # Run all tests
```

**Backend changes:**
```bash
cd backend
uvx ruff check
uvx ruff format --check
uv run pytest -s
```

**Frontend changes:**
```bash
cd frontend
npm run lint
# UI changes: Playwright MCP manual verification REQUIRED! (See WORKSPACE/CONVENTIONS/FRONTEND.md)
```

**Worker changes:**
```bash
cd worker
uvx ruff check
uvx ruff format --check
uv run pytest -s
```

**All checks must pass before creating PR.**

---

## 📚 Documentation (상세 내용은 WORKSPACE 참조)

**⭐ 모든 상세 규칙과 컨벤션은 WORKSPACE에 있습니다:**

| Category | Location | Description |
|----------|----------|-------------|
| **Project Info** | [WORKSPACE/00_PROJECT.md](./WORKSPACE/00_PROJECT.md) | Project overview, policies, Quick Start |
| **Roadmap** | [WORKSPACE/00_ROADMAP.md](./WORKSPACE/00_ROADMAP.md) | Development roadmap and milestones |
| **Conventions** | [WORKSPACE/CONVENTIONS/](./WORKSPACE/CONVENTIONS/) | Git Flow, PR, code review guidelines |
| **Architecture** | [WORKSPACE/ARCHITECTURE/](./WORKSPACE/ARCHITECTURE/) | Architecture Decision Records (ADRs) |
| **Features** | [WORKSPACE/FEATURES/](./WORKSPACE/FEATURES/) | Feature specifications and phase checklists |

---

## 🚀 Quick Start

### Initial Setup (First Time)
```bash
# Install dependencies
make setup

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

### Development Workflow

**Makefile Commands (Recommended):**
```bash
# Start infrastructure (PostgreSQL + Ollama)
make dev-infra

# Run services in separate terminals
Terminal 1: make dev-backend   # Backend API (port 8000)
Terminal 2: make dev-frontend  # Frontend (port 3000)
Terminal 3: make dev-worker    # Worker (optional for local dev)

# Stop infrastructure
make stop

# Run tests and linters
make test
make lint
```

**Alternative: Manual Commands**

Infrastructure:
```bash
docker compose --profile dev up -d   # Start PostgreSQL + Ollama
```

Backend:
```bash
cd backend
uv run alembic upgrade head          # Run migrations
uv run uvicorn llmbattler_backend.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm run dev  # Port 3000
```

Worker:
```bash
cd worker
uv run python -m llmbattler_worker.main  # Run aggregation manually
```

🔗 **Full setup guide:** [WORKSPACE/00_PROJECT.md#quick-start](./WORKSPACE/00_PROJECT.md)

---

## 🤖 Workflow Commands

**Makefile Commands:**
```bash
make help         # Show all available commands
make setup        # Install dependencies (first time only)
make dev          # Start infrastructure and show instructions
make dev-infra    # Start PostgreSQL + Ollama
make dev-backend  # Start Backend API
make dev-frontend # Start Frontend
make dev-worker   # Run Worker (vote aggregation)
make stop         # Stop Docker services
make clean        # Stop and remove all data (WARNING: deletes DB)
make test         # Run all tests
make lint         # Run all linters
```

**Custom slash commands will be configured later.**

Common workflow:
1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Start infrastructure: `make dev-infra`
3. Develop and test locally
4. Run pre-commit checks: `make lint && make test`
5. Commit and push
6. Create GitHub Pull Request

---

## 🤖 Available Agents

**Specialized agents will be configured later.**

Planned agents:
- **backend-developer** - Backend development (FastAPI, TDD, SQLModel)
- **frontend-developer** - Frontend development (Next.js, RSC)
- **worker-developer** - Worker development (Python, data aggregation)
- **convention-reviewer** - Code review and convention checks
- **pr-creator** - PR creation (English format, GitHub)

---

## 🏗️ Architecture Summary

- **Client:** Next.js 15 with App Router + React Server Components
- **Backend (API Server):** FastAPI with OpenAI-compatible LLM routing
- **AI Inference:** vLLM/Ollama servers (OpenAI-compatible API)
- **Database:** PostgreSQL (sessions, battles, votes, model_stats, worker_status)
  - JSONB for conversation storage
  - Denormalized vote data for performance
- **Worker:** Hourly cron job for vote aggregation and ELO calculation
- **Testing:** TDD with pytest (backend/worker), Playwright MCP (frontend)

**Key Architectural Decisions:**
- NO Foreign Keys (ADR-001) - use application-level relationships
- PostgreSQL-only architecture (no MongoDB) - simplified operations
- Session-based battle flow - multi-turn conversations
- Blind testing - model identities hidden until after voting
- ELO-based ranking system with Bradley-Terry confidence intervals

🔗 **Details:** [WORKSPACE/ARCHITECTURE/](./WORKSPACE/ARCHITECTURE/)

---

## 📊 Current Status

**Project Phase:** ✅ **Phase 3: Session Management UI - COMPLETED (2025-10-23)**
**Current Branch:** `develop`
**Latest Feature Branch:** `feature/simplify-configuration-structure`

**Development Progress:**

- ✅ **Phase 0: Project Initialization** - COMPLETED (2025-01-21)
  - Architecture design, tech stack selection
  - WORKSPACE documentation
  - Database design (PostgreSQL-only, no FK)
  - Project structure (uv workspace)

- ✅ **Phase 1: Battle MVP** - COMPLETED (2025-10-21)
  - Session & Battle Creation API (PR #18, #19, #21)
  - Voting API (PR #22)
  - Model Management System (PR #17)
  - Frontend Battle UI (PR #23)

- ✅ **Phase 2: Leaderboard MVP** - COMPLETED (2025-10-21)
  - Worker ELO Calculation (PR #27, #28)
  - Leaderboard API (PR #29)
  - Frontend Leaderboard UI (PR #30)

- ✅ **Phase 3: Session Management UI** - COMPLETED (2025-10-23)
  - Backend Session List API (PR #33)
  - Sidebar & User Management (PR #34)
  - Session Context & API Integration (PR #35)
  - Vote Button Hover Effects & Auto-scroll (PR #36, #37)
  - E2E Testing & Integration (Completed)

**Next Steps:**
- Production deployment preparation
- User authentication (replace anonymous UUID)
- Performance optimization & monitoring

🔗 **Full roadmap:** [WORKSPACE/00_ROADMAP.md](./WORKSPACE/00_ROADMAP.md)
🔗 **Feature details:** [WORKSPACE/FEATURES/](./WORKSPACE/FEATURES/)

---

## 🔧 MCP Tools

**Available MCP servers:**
- `@context7` - Library documentation (FastAPI, Next.js, etc.)
- `@playwright` - Browser automation for UI testing
- `@github` - GitHub repository management (PRs, issues)

🔗 **Setup:** [`.mcp.json`](./.mcp.json)

---

**Last Updated:** 2025-10-25

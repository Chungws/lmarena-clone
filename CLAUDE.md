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
# UI changes: Playwright MCP manual verification REQUIRED! (See WORKSPACE/CONVENTIONS/FRONTEND.md)
```

**Worker changes:**
```bash
cd worker
uvx ruff check
uvx ruff format --check
uvx isort --check --profile black .
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

### Infrastructure (Docker Compose)
```bash
docker compose up -d                     # Start PostgreSQL + MongoDB
```

### Backend (FastAPI)
```bash
cd backend
uv sync                                  # Install dependencies
uv run alembic upgrade head             # Run migrations (PostgreSQL)
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js 15)
```bash
cd frontend
npm install
npm run dev  # Port 3000
```

### Worker (Data Aggregation)
```bash
cd worker
uv sync                                  # Install dependencies
uv run python -m app.main               # Run hourly aggregation worker
```

🔗 **Full setup guide:** [WORKSPACE/00_PROJECT.md#quick-start](./WORKSPACE/00_PROJECT.md)

---

## 🤖 Workflow Commands

**Custom slash commands will be configured later.**

Common workflow:
1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Develop and test locally
3. Run pre-commit checks (linting, tests)
4. Commit and push
5. Create GitHub Pull Request

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
- **Databases:**
  - MongoDB: Log data (battles, responses, votes) - write-optimized
  - PostgreSQL: Aggregated data (leaderboards, statistics) - read-optimized
- **Worker:** Hourly cron job for MongoDB → PostgreSQL aggregation
- **Testing:** TDD with pytest (backend/worker), Playwright MCP (frontend)

**Key Architectural Decisions:**
- NO Foreign Keys (ADR-001) - use application-level relationships
- Blind testing - model identities hidden until after voting
- ELO-based ranking system for leaderboards

🔗 **Details:** [WORKSPACE/ARCHITECTURE/](./WORKSPACE/ARCHITECTURE/)

---

## 📊 Current Status

**Project Phase:** Initial Setup & Documentation
**Current Branch:** `develop`

**Initialization Progress:**
- ✅ Architecture design completed
- ✅ Tech stack selected
- 🔄 WORKSPACE documentation in progress
- ⏳ Project structure setup pending
- ⏳ MVP features implementation pending

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

**Last Updated:** 2025-01-20

# Project Roadmap: llmbattler

This document defines the **vision, completed/in-progress/planned features** for llmbattler.

**💡 Other Documents:**
- **Project setup/policies?** → [00_PROJECT.md](./00_PROJECT.md)
- **Development conventions?** → [CONVENTIONS/](./CONVENTIONS/)
- **Feature details?** → [FEATURES/](./FEATURES/)

---

## 🔭 Project Vision

llmbattler is an **AI Language Model Battle Arena** that enables unbiased evaluation of LLMs through blind side-by-side testing.

### Core Values
1. **Objectivity**: Blind testing eliminates model bias
2. **Data-Driven**: Collect real user preferences to improve LLM evaluation
3. **Transparency**: Open leaderboards show fair, ELO-based rankings
4. **Flexibility**: Support any OpenAI-compatible LLM (local or external)

### Tech Stack

**Frontend:**
- Next.js 15 (App Router, React Server Components)
- React 19
- Tailwind CSS (or shadcn/ui)
- TypeScript 5
- Playwright MCP (UI testing)

**Backend (API Server):**
- FastAPI (async ASGI)
- SQLModel + SQLAlchemy 2.0 (PostgreSQL ORM)
- Motor or PyMongo (MongoDB driver)
- Alembic (migrations)
- pytest (TDD)
- httpx (LLM API client)

**Worker (Data Aggregation):**
- Python 3.11+
- APScheduler (hourly jobs)
- databases + asyncpg (PostgreSQL async driver)

**Database:**
- PostgreSQL 16 (single database for all data)
  - sessions, battles (JSONB), votes, model_stats, worker_status

**AI Inference:**
- Ollama (local models)
- vLLM (GPU inference)
- External APIs: OpenAI, Anthropic, etc.

**Infrastructure:**
- Docker + Docker Compose (local dev)
- GitHub Actions (CI/CD)
- Uvicorn (ASGI server)

---

## 🗺️ Development Roadmap

### ✅ Phase 0: Project Initialization (Completed)

**Status:** ✅ Completed (2025-01-21)
**Goal:** Set up project structure and documentation

**Tasks:**
- ✅ Architecture design (completed)
- ✅ Tech stack selection (completed)
- ✅ WORKSPACE documentation initialization
  - ✅ CLAUDE.md
  - ✅ 00_PROJECT.md
  - ✅ 00_ROADMAP.md (this file)
  - ✅ CONVENTIONS/ (completed)
  - ✅ ARCHITECTURE/ (completed)
  - ✅ FEATURES/ (completed)
- ✅ **MVP Design Decisions finalized** - **PR #4 (2025-01-21)**
  - All 12 implementation decisions documented
  - Battle MVP: 9 decisions (position randomization, timeout/retry, CORS, logging, etc.)
  - Leaderboard MVP: 5 decisions (worker scheduling, CI calculation, minimum votes, etc.)
- ✅ **Database Design completed** - **2025-01-21**
  - PostgreSQL-only architecture finalized (no MongoDB)
  - Session-based schema: sessions → battles → votes
  - JSONB conversation storage (OpenAI-compatible)
  - Foreign Keys NOT used (ADR-001)
  - Repository pattern for abstraction
  - 4-phase scalability path defined (10 QPS → 10,000+ QPS)
  - Complete Alembic migration spec (DATABASE_DESIGN.md)
- ✅ **Project structure setup (backend, frontend, worker)** - Already defined in uv workspace
- ✅ **Docker Compose configuration (PostgreSQL only)** - **PR #14 (2025-01-21)**
  - Removed MongoDB service from docker-compose.yml and docker-compose.dev.yml
  - PostgreSQL-only architecture implemented
- ✅ **Repository README.md** - **PR #15 (2025-01-21)**
  - Updated to reflect PostgreSQL-only architecture
  - Removed MongoDB references
  - Updated architecture diagram and tech stack
- ✅ **MongoDB removal** - **PR #13 (2025-01-21)**
  - Removed motor dependency from backend and worker
  - Deleted mongodb/ directory
  - Removed MongoDB configuration settings
- ✅ **Alembic migrations implemented** - **PR #16 (2025-01-21)**
  - Initial migration (001_initial_schema.py) created
  - All 5 tables: sessions, battles, votes, model_stats, worker_status
  - JSONB support, indexes, CHECK constraints
  - Async SQLAlchemy support configured

**Details:** Phase 0 completed with 4 PRs (#13, #14, #15, #16) successfully merged

---

### ⏳ Phase 1: MVP - Battle Mode (Text-to-Text)

**Status:** In Progress
**Goal:** Enable users to compare two LLM responses in blind side-by-side testing with session-based conversations

**Progress:**
- ✅ **Phase 1.3: Model Management System** - **PR #17 (2025-01-21)**
  - config/models.yaml configuration
  - LLM API client with timeout/retry
  - GET /api/models endpoint
- 🔄 **Phase 1.1: Session & Battle Creation API** - **In Progress**
  - ✅ SQLModel models (Session, Battle, Vote) - **PR #18 (2025-01-21)**
  - ✅ Alembic migration for database tables - **PR #18 (2025-01-21)**
  - ⏳ POST /api/sessions endpoint (pending)
  - ⏳ POST /api/sessions/{session_id}/battles endpoint (pending)
  - ⏳ POST /api/battles/{battle_id}/messages endpoint (pending)

**Key Features:**
1. **Battle UI (Frontend)**
   - Session-based design (multiple battles per session like LM Arena)
   - Prompt input field for creating session/battle
   - Side-by-side response display (Assistant A vs Assistant B)
   - Multi-turn conversation support with follow-up messages
   - Model identities hidden until vote
   - Voting buttons: "Left is Better", "Tie", "Both are bad", "Right is Better"
   - Reveal model names after voting
   - "New Battle" button to start new battle with different models in same session

2. **Battle API (Backend)**
   - `POST /api/sessions` - Create session + first battle
     - Accept user prompt
     - Randomly select 2 models from available pool
     - Call LLM APIs (parallel requests)
     - Store session and battle in PostgreSQL (JSONB conversation)
     - Return anonymous responses (model IDs hidden)
   - `POST /api/sessions/{session_id}/battles` - New battle in session
     - Randomly select 2 NEW models
     - Create new battle in same session
   - `POST /api/battles/{battle_id}/messages` - Follow-up message
     - Append to JSONB conversation array
     - Call LLMs with full conversation history
   - `POST /api/battles/{battle_id}/vote` - Submit vote
     - Transaction: INSERT vote (denormalized model_ids) + UPDATE battle status
     - Reveal model identities
   - `GET /api/models` - List available models

3. **Model Management (Backend)**
   - Configure LLM endpoints (Ollama, vLLM, OpenAI, etc.)
   - Support OpenAI-compatible API format
   - Environment-based configuration (dev/prod)

4. **PostgreSQL Tables**
   - `sessions`: session_id, title, user_id (NULL in MVP), created_at, last_active_at
   - `battles`: battle_id, session_id, left_model_id, right_model_id, conversation (JSONB), status
   - `votes`: vote_id, battle_id, session_id, vote, left_model_id (denorm), right_model_id (denorm), processing_status

**Estimated Time:** 2-3 weeks

**Details:** [FEATURES/001_BATTLE_MVP.md](./FEATURES/001_BATTLE_MVP.md)

---

### ⏳ Phase 2: MVP - Leaderboard

**Status:** Not Started
**Goal:** Display ELO-based rankings for all models

**Key Features:**
1. **Leaderboard UI (Frontend)**
   - Table view with columns:
     - Rank (UB) - Universal Bracket rank
     - Model Name (with icon)
     - Score (ELO rating)
     - 95% CI (±confidence interval)
     - Votes (total vote count)
     - Organization (model provider)
     - License (proprietary/open-source)
   - Search by model name
   - Sort by score, votes, organization
   - Filter by category (Overall, Text, etc.)
   - Metadata display (Last Updated, Total Votes, Total Models)

2. **Leaderboard API (Backend)**
   - `GET /api/leaderboard` - Get current leaderboard
     - Query params: category, sort_by, order
     - Return rankings from PostgreSQL
     - Filter models with < 5 votes
   - Serve aggregated data (ELO scores, statistics)

3. **Worker (Data Aggregation)**
   - Hourly cron job (APScheduler) to process pending votes
   - Read from PostgreSQL `votes` table (`processing_status = 'pending'`)
   - Denormalized model_ids in votes (avoids N+1 queries)
   - Calculate ELO ratings using Bradley-Terry confidence intervals
   - Update PostgreSQL `model_stats` table
   - Mark votes as processed (`processing_status = 'processed'`)
   - Store execution metadata in `worker_status` table

4. **PostgreSQL Tables** (already defined in Phase 1)
   - `model_stats`: model_id, elo_score, elo_ci, vote_count, win_rate, organization, license
   - `worker_status`: worker_name, last_run_at, status, votes_processed

**Estimated Time:** 1-2 weeks

**Details:** [FEATURES/002_LEADERBOARD_MVP.md](./FEATURES/002_LEADERBOARD_MVP.md)

---

### 💡 Future Features (Post-MVP)

#### 1. Multi-Modal Support
- **Goal:** Support image-to-text, text-to-image, etc.
- **Priority:** Medium
- **Estimated Time:** 3-4 weeks

#### 2. User Authentication
- **Goal:** Track user votes, prevent spam
- **Priority:** High (for production)
- **Estimated Time:** 1-2 weeks

#### 3. Advanced Leaderboard Categories
- **Goal:** Rankings by task type (coding, creative writing, etc.)
- **Priority:** Medium
- **Estimated Time:** 1 week

#### 4. Real-Time Leaderboard Updates
- **Goal:** Live ELO updates using WebSocket or SSE
- **Priority:** Low
- **Estimated Time:** 1-2 weeks

#### 5. Model Comparison Page
- **Goal:** Head-to-head statistics between two specific models
- **Priority:** Low
- **Estimated Time:** 1 week

#### 6. Historical Battle Replay
- **Goal:** View past battles and votes
- **Priority:** Low
- **Estimated Time:** 1 week

#### 7. Admin Dashboard
- **Goal:** Manage models, view analytics, moderate content
- **Priority:** High (for production)
- **Estimated Time:** 2-3 weeks

#### 8. API Rate Limiting
- **Goal:** Prevent abuse with rate limiting (per IP or user)
- **Priority:** High (for production)
- **Estimated Time:** 1 week

---

## 📊 Current Status

**Active Phase:** ✅ Phase 0 Completed → 🚀 Ready for Phase 1
**Current Branch:** `develop`
**Latest Update:** 2025-01-21

**Progress:**
- ✅ **Phase 0: Project Initialization - COMPLETED**
  - Architecture designed
  - Tech stack finalized
  - WORKSPACE documentation completed
  - Database design completed (PostgreSQL-only, session-based schema, no FK)
  - Project structure defined (uv workspace)
  - Docker Compose configured (PostgreSQL only)
  - Repository README.md updated
  - MongoDB removed from codebase
  - Alembic migrations implemented and tested

**Completed PRs (Phase 0):**
- PR #13: Remove MongoDB dependencies and code
- PR #14: Update Docker Compose to PostgreSQL-only
- PR #15: Update README.md to reflect PostgreSQL-only architecture
- PR #16: Implement Alembic migrations from DATABASE_DESIGN.md

**Next Steps:**
1. 🚀 Begin Phase 1 (Battle MVP) implementation
2. Set up model configuration (config/models.yaml)
3. Implement backend API endpoints
4. Create frontend Battle UI
5. Develop LLM integration layer

---

## 🎯 Success Metrics

### MVP Goals
- [ ] Users can battle 2+ models in blind testing
- [ ] Leaderboard displays ELO rankings
- [ ] At least 2 models supported (e.g., Ollama models)
- [ ] 100+ test battles conducted

### Long-Term Goals
- [ ] 10+ models supported (local + external)
- [ ] 1,000+ user votes collected
- [ ] Accurate ELO rankings (95% CI < ±10)
- [ ] Multi-modal support (text, image, code)

---

**Last Updated:** 2025-01-20

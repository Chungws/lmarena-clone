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

### ✅ Phase 1: MVP - Battle Mode (Text-to-Text)

**Status:** ✅ Completed (2025-10-21)
**Goal:** Enable users to compare two LLM responses in blind side-by-side testing with session-based conversations

**Progress:**
- ✅ **Phase 1.1: Session & Battle Creation API** - **PR #18, #19, #21 (2025-01-21 ~ 2025-10-21)**
  - SQLModel models (Session, Battle, Vote)
  - Alembic migration for database tables
  - POST /api/sessions endpoint (session + first battle)
  - POST /api/sessions/{session_id}/battles endpoint (new battle in session)
  - POST /api/battles/{battle_id}/messages endpoint (follow-up messages)
  - Repository pattern implementation
  - Timezone-aware timestamps (TIMESTAMPTZ)
  - Multi-turn conversation support with JSONB
  - Comprehensive tests (7/7 passing)
- ✅ **Phase 1.2: Voting API** - **PR #22 (2025-10-21)**
  - POST /api/battles/{battle_id}/vote endpoint
  - Vote validation (prevent duplicate votes)
  - Transaction-based vote handling
  - Model reveal after voting
  - Tests for voting (3/3 passing)
- ✅ **Phase 1.3: Model Management System** - **PR #17 (2025-01-21)**
  - config/models.yaml configuration
  - LLM API client with timeout/retry
  - GET /api/models endpoint
  - OpenAI-compatible API support
  - CORS and logging setup
- ✅ **Phase 1.4: Frontend - Battle UI** - **PR #23 (2025-10-21)**
  - /battle page with session-based flow
  - Side-by-side response display
  - Follow-up message support
  - Voting interface with model reveal
  - New Battle button
  - shadcn/ui components integration
  - Responsive mobile design
  - Tailwind CSS v4 migration
- ✅ **Phase 1.5: Frontend - API Integration** - **Merged into Phase 1.4**
  - API client service (lib/apiClient.ts)
  - Custom hooks (use-battle.ts)
  - TypeScript types (_types.ts)
  - Error handling and loading states

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

### ✅ Phase 2: MVP - Leaderboard

**Status:** ✅ Completed (2025-10-21)
**Goal:** Display ELO-based rankings for all models

**Progress:**
- ✅ **Phase 2.1: PostgreSQL Schema** - **PR #24 (2025-10-21)**
  - Tables created: sessions, battles, votes, model_stats, worker_status
  - Indexes added for fast queries
  - Schema tests written
- ✅ **Phase 2.2: Worker ELO Calculation** - **PR #27, #28 (2025-10-21)**
  - ELO calculator module with Bradley-Terry CI
  - Vote aggregation script with error handling
  - 24 comprehensive tests (17 unit + 7 integration)
  - APScheduler integration complete
  - Worker status tracking implemented
- ✅ **Phase 2.3: Backend - Leaderboard API** - **PR #29 (2025-10-21)**
  - GET /api/leaderboard endpoint with sorting
  - Model stats repository
  - Leaderboard service layer
  - 355 lines of comprehensive tests
- ✅ **Phase 2.4: Frontend - Leaderboard UI** - **PR #30 (2025-10-21)**
  - Complete leaderboard table with 8 columns
  - Search and sorting functionality
  - Metadata display with relative timestamps
  - shadcn/ui components integration
  - Responsive mobile design
- ✅ **Phase 2.5: Frontend - API Integration** - **Merged into Phase 2.4**
  - API service layer (service.ts)
  - Custom React hook (use-leaderboard.ts)
  - TypeScript types (_types.ts)
  - Loading and error states

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

### ✅ Phase 3: Session Management UI (Completed)

**Status:** ✅ Completed (2025-10-23)
**Goal:** ChatGPT-like session sidebar with conversation history

**Progress:**
- ✅ Feature specification created - [FEATURES/004_SESSION_MANAGEMENT.md](./FEATURES/004_SESSION_MANAGEMENT.md)
- ✅ **Phase 3.1: Backend - Session List API** - **PR #33 (2025-10-23)**
  - GET /api/sessions endpoint with pagination
  - GET /api/sessions/{session_id}/battles endpoint
  - Session.user_id type change (int → varchar)
  - Repository and service layer enhancements
  - 6 comprehensive tests (26 total tests passing)
- ✅ **Phase 3.2+3.3: Frontend - Sidebar & User Management** - **PR #34 (2025-10-23)**
  - Session list component (no date grouping - MVP)
  - Session item component (hover + active highlight)
  - Anonymous user ID management (localStorage + UUID)
  - useUser hook implementation
  - Battle service integration (user_id parameter)
  - Playwright MCP UI verification completed
- ✅ **Phase 3.4: Frontend - Session Context & API Integration** - **PR #35 (2025-10-23)**
  - SessionContext implementation (global state management)
  - useSessionDetail hook (battle list loading)
  - SessionProvider integration in layout
  - session-list.tsx refactored to use SessionContext
  - ESLint and Playwright MCP verification completed
- ✅ **Phase 3.5: Frontend - Battle UI Enhancement** - **PR #36, #37 (2025-10-23)**
  - Vote button hover effects with color-coded card borders
  - Client-side state updates (removed page refresh)
  - Auto-scroll functionality
  - Sticky vote buttons
  - Theme toggle fix
- ✅ **Phase 3.6: Integration & E2E Testing** - **Completed (2025-10-23)**
  - End-to-end flow testing
  - Playwright MCP UI verification
  - All features integrated and working

**Key Features:**
1. **Session Sidebar (Frontend)**
   - "New Chat" button for starting fresh sessions
   - Session list grouped by date (Today, Yesterday, Previous 7 Days, etc.)
   - Click session to view conversation history
   - Active session highlighting
   - Responsive design (mobile hamburger menu)

2. **Anonymous User Management (Frontend)**
   - Generate UUID v4 for anonymous users
   - Store in localStorage (`llmbattler_user_id`)
   - Associate sessions with anonymous user ID

3. **Session List API (Backend)**
   - `GET /api/sessions` - List user's sessions
     - Filter by user_id (anonymous UUID)
     - Sort by last_active_at DESC
     - Pagination support
   - `GET /api/sessions/{session_id}/battles` - Get all battles in session
     - Return conversation history for each battle
     - Include vote information if available

4. **Enhanced Battle UI (Frontend)**
   - Vote button hover effects:
     - "Left is Better" → Left card green border
     - "Right is Better" → Right card green border
     - "Tie" → Both cards green border
     - "Both are bad" → Both cards red border
   - Smooth CSS transitions
   - Keyboard navigation support

5. **Post-Vote Conversation Flow**
   - Vote reveals model names
   - Continue conversation after voting
   - New vote becomes available for follow-up messages

**Estimated Time:** 1.5-2 weeks (7-8 days)

**Details:** [FEATURES/004_SESSION_MANAGEMENT.md](./FEATURES/004_SESSION_MANAGEMENT.md)

---

### 💡 Future Features (Post-MVP)

#### 1. Multi-Modal Support
- **Goal:** Support image-to-text, text-to-image, etc.
- **Priority:** Medium
- **Estimated Time:** 3-4 weeks

#### 2. User Authentication
- **Goal:** Track user votes, prevent spam, replace anonymous UUID with real accounts
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

**Active Phase:** ✅ **Phase 3: Session Management UI - COMPLETED (2025-10-23)**
**Current Branch:** `develop`
**Latest Update:** 2025-10-23

**Progress:**
- ✅ **Phase 0: Project Initialization - COMPLETED (2025-01-21)**
  - Architecture designed
  - Tech stack finalized
  - WORKSPACE documentation completed
  - Database design completed (PostgreSQL-only, session-based schema, no FK)
  - Project structure defined (uv workspace)
  - Docker Compose configured (PostgreSQL only)
  - Repository README.md updated
  - MongoDB removed from codebase

- ✅ **Phase 1: Battle MVP - COMPLETED (2025-10-21)**
  - ✅ Phase 1.1: Session & Battle Creation API - **PR #18, #19, #21**
  - ✅ Phase 1.2: Voting API - **PR #22**
  - ✅ Phase 1.3: Model Management System - **PR #17**
  - ✅ Phase 1.4: Frontend - Battle UI - **PR #23**
  - ✅ Phase 1.5: Frontend - API Integration - **Merged into 1.4**

- ✅ **Phase 2: Leaderboard MVP - COMPLETED (2025-10-21)**
  - ✅ Phase 2.1: PostgreSQL Schema - **PR #24**
  - ✅ Phase 2.2: Worker ELO Calculation - **PR #27, #28**
  - ✅ Phase 2.3: Backend - Leaderboard API - **PR #29**
  - ✅ Phase 2.4: Frontend - Leaderboard UI - **PR #30**
  - ✅ Phase 2.5: Frontend - API Integration - **Merged into 2.4**

- ✅ **Phase 3: Session Management UI - COMPLETED (2025-10-23)**
  - ✅ Feature specification completed - **FEATURES/004_SESSION_MANAGEMENT.md**
  - ✅ Phase 3.1: Backend - Session List API - **PR #33 (2025-10-23)**
  - ✅ Phase 3.2+3.3: Frontend - Sidebar & User Management - **PR #34 (2025-10-23)**
  - ✅ Phase 3.4: Frontend - Session Context & API Integration - **PR #35 (2025-10-23)**
  - ✅ Phase 3.5: Frontend - Battle UI Enhancement - **PR #36, #37 (2025-10-23)**
  - ✅ Phase 3.6: Integration & E2E Testing - **Completed (2025-10-23)**

**Completed PRs (Phases 0-3):**
- **Phase 0:** PR #13, #14, #15, #16
- **Phase 1:** PR #17, #18, #19, #21, #22, #23
- **Phase 2:** PR #24, #27, #28, #29, #30
- **Phase 3:** PR #33, #34, #35, #36, #37

**🎯 MVP Status:**
- ✅ Battle Mode: Users can compare LLM responses in blind testing
- ✅ Leaderboard: ELO-based rankings displayed
- ✅ Worker: Automated vote aggregation and ELO calculation
- ✅ Session Management: ChatGPT-like sidebar with user history
- ✅ Full-stack implementation (Backend + Frontend + Worker)

**Next Steps:**
1. 🎨 **UI/UX Polish & Testing** - Manual testing with real LLM models, bug fixes
2. 📊 **Analytics & Monitoring** - Add detailed logging and performance monitoring
3. 🌐 **Production Deployment** - Deploy to staging/production environment
4. 🔐 **User Authentication** - Replace anonymous UUID with real accounts
5. 🚀 **Advanced Features** - Multi-modal support, model comparison, admin dashboard

---

## 🎯 Success Metrics

### MVP Goals
- [x] Users can battle 2+ models in blind testing ✅
- [x] Leaderboard displays ELO rankings ✅
- [x] At least 2 models supported (e.g., Ollama models) ✅
- [ ] 100+ test battles conducted (In Progress - Ready for testing)
- [ ] Production deployment complete (Next step)

### Long-Term Goals
- [ ] 10+ models supported (local + external)
- [ ] 1,000+ user votes collected
- [ ] Accurate ELO rankings (95% CI < ±10)
- [ ] Multi-modal support (text, image, code)

---

**Last Updated:** 2025-10-23

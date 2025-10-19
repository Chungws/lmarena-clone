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
- APScheduler or cron (hourly jobs)
- Motor or PyMongo (MongoDB reader)
- SQLModel (PostgreSQL writer)

**Databases:**
- PostgreSQL 16 (aggregated data: leaderboards, statistics)
- MongoDB (log data: battles, responses, votes)

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

### 🚧 Phase 0: Project Initialization (In Progress)

**Status:** In Progress
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
- ⏳ Project structure setup (backend, frontend, worker)
- ⏳ Docker Compose configuration (PostgreSQL + MongoDB)
- ⏳ Repository README.md

**Details:** N/A (initialization phase)

---

### ⏳ Phase 1: MVP - Battle Mode (Text-to-Text)

**Status:** Not Started
**Goal:** Enable users to compare two LLM responses in blind side-by-side testing

**Key Features:**
1. **Battle UI (Frontend)**
   - Chat-like input field for user prompt
   - Side-by-side response display (Assistant A vs Assistant B)
   - Model identities hidden until vote
   - Voting buttons: "Left is Better", "Tie", "Both are bad", "Right is Better"
   - Reveal model names after voting
   - Follow-up prompt support (optional MVP feature)

2. **Battle API (Backend)**
   - `POST /api/battles` - Create new battle
     - Accept user prompt
     - Randomly select 2 models from available pool
     - Call LLM APIs (parallel requests)
     - Store battle, responses in MongoDB
     - Return anonymous responses (model IDs hidden)
   - `POST /api/battles/{battle_id}/vote` - Submit vote
     - Accept vote (left_better, tie, both_bad, right_better)
     - Store vote in MongoDB
     - Reveal model identities
   - `GET /api/models` - List available models

3. **Model Management (Backend)**
   - Configure LLM endpoints (Ollama, vLLM, OpenAI, etc.)
   - Support OpenAI-compatible API format
   - Environment-based configuration (dev/prod)

4. **MongoDB Collections**
   - `battles`: battle_id, prompt, model_a_id, model_b_id, created_at
   - `responses`: response_id, battle_id, model_id, response_text, latency_ms, created_at
   - `votes`: vote_id, battle_id, user_id (optional), vote, voted_at

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
   - Serve aggregated data (ELO scores, statistics)

3. **Worker (Data Aggregation)**
   - Hourly cron job to process new votes
   - Calculate ELO ratings from MongoDB votes
   - Update PostgreSQL tables:
     - `model_stats`: model_id, elo_score, elo_ci, vote_count, win_rate, organization, license
     - `leaderboards`: snapshot of rankings (optional for history tracking)

4. **PostgreSQL Tables**
   - `model_stats`: Aggregated statistics per model
   - `leaderboards` (optional): Historical snapshots

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

**Active Phase:** Phase 0 - Project Initialization
**Current Branch:** `develop`
**Latest Update:** 2025-01-20

**Progress:**
- ✅ Architecture designed
- ✅ Tech stack finalized
- ✅ WORKSPACE documentation completed
- ⏳ MVP implementation pending

**Next Steps:**
1. Set up project structure (backend, frontend, worker)
2. Configure Docker Compose
3. Create repository README.md
4. Begin Phase 1 (Battle MVP) implementation

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

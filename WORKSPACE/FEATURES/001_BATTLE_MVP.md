# Feature: Battle Mode (Text-to-Text) - MVP

**Status:** Not Started
**Priority:** High (MVP Core Feature)
**Estimated Time:** 2-3 weeks

---

## Overview

Enable users to compare two LLM responses through blind side-by-side testing in **session-based** conversations. Users can have multiple battles in one session, where each battle involves multi-turn conversations with two randomly selected models, followed by voting.

**Goals:**
- Unbiased LLM evaluation through blind testing
- Session-based UI like LM Arena (multiple battles per session)
- Multi-turn conversations with conversation history
- Collect user preference data for model ranking
- Support any OpenAI-compatible LLM endpoint

---

## Architecture

```
User → Frontend (Next.js)
         ↓
    Backend (FastAPI)
         ↓
    ┌────┴────┐
    ↓         ↓
  Model A   Model B (parallel API calls)
    ↓         ↓
    └────┬────┘
         ↓
    PostgreSQL (sessions → battles → votes)
```

**Database Strategy** (see [DATABASE_DESIGN.md](../ARCHITECTURE/DATABASE_DESIGN.md)):
- **PostgreSQL only** (no MongoDB)
- **Session-based hierarchy:** sessions → battles → votes
- **JSONB conversation storage:** OpenAI-compatible format
- **Foreign Keys:** Used for data integrity (ADR-001 reversed)

---

## Design Decisions

### Session-Based Architecture
**Decision:** Session contains multiple battles
- User creates a **session** on first prompt
- Each **battle** = 1 conversation between 2 random models
- After voting, user can start a **new battle** in same session with different models
- Session has title (first prompt) and last_active_at timestamp

**UI Flow:**
```
Session Start
  ↓
Battle 1: Model A vs Model B
  - Multi-turn conversation
  - User votes → Models revealed
  ↓
Battle 2: Model C vs Model D (new random models)
  - Multi-turn conversation
  - User votes → Models revealed
  ↓
... (repeat in same session)
```

### Model Selection Algorithm
**Decision:** Uniform random selection (Option A)
- Select 2 different models randomly from active pool
- All models have equal probability
- `model_a != model_b` guaranteed
- **New random models selected for each battle** (even in same session)
- **Implementation:** Isolated in `select_models_for_battle()` function for easy algorithm upgrade

### Model Configuration
**Decision:** YAML + Environment Variables (Hybrid)
```yaml
# config/models.yaml
models:
  - id: gpt-4o-mini                      # System internal ID
    name: GPT-4o Mini                    # Display name
    model: gpt-4o-mini                   # Model name for API call
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY          # Env var reference
    organization: OpenAI
    license: proprietary

  - id: llama-3.1-8b
    name: Llama 3.1 8B
    model: llama3.1:8b                   # Ollama model name
    base_url: http://localhost:11434/v1
    api_key_env: null                    # No API key for local
    organization: Meta
    license: open-source
```

**Security:** API keys stored in environment variables only (`.env` in `.gitignore`)

### Conversation History Storage
**Decision:** JSONB in PostgreSQL (Option C)
- Store conversation as JSONB array in `battles.conversation` column
- **OpenAI-compatible message format** with roles (user, assistant)
- Each assistant message includes `model_id`, `position`, `latency_ms`
- Append-only operations using `conversation || $1::jsonb`
- No hard limit on messages (backend can enforce soft limit like 20)

**JSONB Structure:**
```json
[
  {
    "role": "user",
    "content": "안녕하세요",
    "timestamp": "2025-01-21T10:00:00Z"
  },
  {
    "role": "assistant",
    "model_id": "gpt-4o-mini",
    "position": "left",
    "content": "안녕하세요! 무엇을 도와드릴까요?",
    "latency_ms": 234,
    "timestamp": "2025-01-21T10:00:01Z"
  },
  {
    "role": "assistant",
    "model_id": "claude-3.5-sonnet",
    "position": "right",
    "content": "반갑습니다!",
    "latency_ms": 189,
    "timestamp": "2025-01-21T10:00:01Z"
  }
]
```

### Vote Handling: "both_bad"
**Decision:** Small penalty (0.25, 0.25) - LM Arena approach
- `left_better` → A: 1.0, B: 0.0
- `right_better` → A: 0.0, B: 1.0
- `tie` → A: 0.5, B: 0.5
- **`both_bad` → A: 0.25, B: 0.25** (both receive small ELO penalty)
- Reflects negative feedback while minimizing rank volatility

### Model Position Randomization
**Decision:** Random left/right placement
- Randomly assign model_a to "left" or "right" position
- Prevents position bias in voting
- Store `left_model_id` and `right_model_id` in battles table
- Example: If model_a is "gpt-4o", it might appear as "Assistant A" on left OR "Assistant B" on right

### Vote Duplicate Prevention
**Decision:** Not implemented in MVP
- Will be implemented with user authentication in Phase 3
- MVP allows multiple votes from same user (acceptable for testing phase)

### Rate Limiting
**Decision:** Not implemented in MVP
- Will be implemented with user authentication in Phase 3
- User-based rate limiting more effective than IP-based
- MVP focuses on feature validation, not production security

### LLM API Timeout & Retry
**Decision:** Timeouts and exponential backoff retry
- **Timeouts:** Connect 5s, Read 30s, Write 5s, Pool 5s
- **Retry:** 3 attempts with exponential backoff (1s, 2s, 4s)
- Prevents hanging requests and improves reliability

### Error Logging
**Decision:** Python logging to stdout
- Use standard `logging` module with StreamHandler
- Docker logs capture stdout automatically
- Log levels: INFO (normal operations), ERROR (failures)
- Key events: LLM API failures, battle creation, vote submission, database errors

### CORS Configuration
**Decision:** Environment-based origins
```python
# .env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
- Production: Set `CORS_ORIGINS` to actual frontend domain

### Database Indexes
**Decision:** Strategic indexes for query performance
```python
# Indexes (defined in Alembic migration)
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX idx_battles_session_id ON battles(session_id);
CREATE INDEX idx_battles_status ON battles(status);
CREATE INDEX idx_battles_session_status ON battles(session_id, status);  # Compound
```
- All queries use `session_id` (partition-friendly for future sharding)

### Database Connection
**Decision:** Async PostgreSQL with connection pooling
```python
# PostgreSQL (databases + asyncpg)
from databases import Database

POSTGRES_URI = os.getenv("DATABASE_URL", "postgresql://localhost/llmbattler")
database = Database(
    POSTGRES_URI,
    min_size=5,
    max_size=10,
    timeout=5
)
```
- **Note:** Backend uses ONLY PostgreSQL (no MongoDB)

---

## Implementation Phases

### Phase 1.1: Backend - Session & Battle Creation API

**Tasks:**
- [x] Setup PostgreSQL connection and models - **PR #18 (2025-01-21)**
  - [x] Create async Database client with connection pooling
  - [x] Load SQLModel models from `shared/` package (sessions, battles, votes)
  - [x] Run Alembic migrations to create tables
- [ ] Implement `POST /api/sessions` endpoint
  - [ ] Accept user prompt (text)
  - [ ] Create new session (session_id, title=prompt[:200])
  - [ ] Randomly select 2 models using `select_models_for_battle()`
  - [ ] **Randomly assign left/right positions** (prevent position bias)
  - [ ] Call LLM APIs in parallel (async) with timeout and retry logic
  - [ ] Create battle with JSONB conversation (user message + 2 assistant messages)
  - [ ] Return anonymous responses (model IDs hidden, positions randomized)
- [ ] Implement `POST /api/sessions/{session_id}/battles` endpoint
  - [ ] Accept user prompt
  - [ ] Update session.last_active_at
  - [ ] Randomly select 2 NEW models (different from previous battle)
  - [ ] Create new battle in same session
  - [ ] Return anonymous responses
- [ ] Implement `POST /api/battles/{battle_id}/messages` endpoint
  - [ ] Accept follow-up prompt
  - [ ] Retrieve conversation history from battle (JSONB)
  - [ ] Call LLM APIs with full message history (OpenAI chat format)
  - [ ] Append new messages to battle.conversation using `||` operator
  - [ ] Return anonymous responses
- [ ] Add error handling (API failures, timeouts)
- [ ] Add logging for key events (session/battle creation, API failures, errors)
- [ ] Write tests for session creation and multi-turn conversations

**API Spec (Create Session):**
```
POST /api/sessions
Request:
{
  "prompt": "What is the capital of France?"
}

Response:
{
  "session_id": "session_abc123",
  "battle_id": "battle_001",
  "message_id": "msg_1",
  "responses": [
    {
      "position": "left",
      "text": "The capital of France is Paris.",
      "latency_ms": 234
    },
    {
      "position": "right",
      "text": "Paris is the capital city of France.",
      "latency_ms": 189
    }
  ]
}
```

**API Spec (New Battle in Session):**
```
POST /api/sessions/session_abc123/battles
Request:
{
  "prompt": "Tell me about Python programming"
}

Response:
{
  "session_id": "session_abc123",
  "battle_id": "battle_002",  // NEW battle with different models
  "message_id": "msg_1",
  "responses": [
    {
      "position": "left",
      "text": "Python is a high-level...",
      "latency_ms": 312
    },
    {
      "position": "right",
      "text": "Python is an interpreted...",
      "latency_ms": 245
    }
  ]
}
```

**API Spec (Follow-up Message):**
```
POST /api/battles/battle_001/messages
Request:
{
  "prompt": "What about its population?"
}

Response:
{
  "battle_id": "battle_001",
  "message_id": "msg_2",
  "responses": [
    {
      "position": "left",
      "text": "Paris has approximately 2.1 million people...",
      "latency_ms": 287
    },
    {
      "position": "right",
      "text": "The population of Paris is around 2.2 million...",
      "latency_ms": 201
    }
  ],
  "message_count": 3,  // Total messages in conversation (user + 2 assistants counted as 1)
  "max_messages": 20   // Backend enforced limit (optional)
}
```

---

### Phase 1.2: Backend - Voting API

**Tasks:**
- [ ] Implement `POST /api/battles/{battle_id}/vote` endpoint
  - [ ] Accept vote: `left_better`, `tie`, `both_bad`, `right_better`
  - [ ] **Transaction:**
    - [ ] SELECT left_model_id, right_model_id FROM battles
    - [ ] INSERT INTO votes (battle_id, vote, left_model_id, right_model_id) -- Denormalized
    - [ ] UPDATE battles SET status = 'voted'
    - [ ] UPDATE sessions SET last_active_at = NOW()
  - [ ] Return model identities (reveal after vote)
- [ ] Add vote validation (prevent duplicate votes - optional for MVP)
- [ ] Write tests for voting

**API Spec:**
```
POST /api/battles/battle_001/vote
Request:
{
  "vote": "left_better"
}

Response:
{
  "battle_id": "battle_001",
  "vote": "left_better",
  "revealed_models": {
    "left": "gpt-4o-mini",
    "right": "llama-3.1-8b"
  }
}
```

---

### Phase 1.3: Backend - Model Management ✅

**Status:** ✅ Completed - **PR #17 (2025-01-21)**

**Tasks:**
- [x] Create model configuration system (YAML + Environment Variables)
  - [x] **MVP: OpenAI-compatible endpoints only** (Ollama, vLLM, OpenAI, etc.)
  - [x] Load models from `config/models.yaml` (see Design Decisions)
  - [x] Resolve API keys from environment variables
  - [x] Validate configuration on startup
- [x] Implement `GET /api/models` endpoint
  - [x] Return list of available models (name, provider, status)
- [x] Create LLM API client (httpx-based)
  - [x] **OpenAI chat completion format** (`/v1/chat/completions`)
  - [x] Support conversation history for multi-turn battles
  - [x] **Timeout configuration:** Connect 5s, Read 30s, Write 5s, Pool 5s
  - [x] **Retry logic:** 3 attempts with exponential backoff (1s, 2s, 4s)
  - [x] Error handling and logging for API failures
  - [x] Use `model` field from config for API calls
- [x] Setup CORS middleware (environment-based origins)
- [x] Setup logging (Python logging to stdout)
- [x] Write tests for model management

**Note:** MVP only supports OpenAI-compatible API endpoints to simplify implementation. All models must expose `/v1/chat/completions` endpoint compatible with OpenAI's API specification.

**API Spec:**
```
GET /api/models

Response:
{
  "models": [
    {
      "model_id": "gpt-4o-mini",
      "name": "GPT-4o Mini",
      "provider": "OpenAI",
      "status": "active"
    },
    {
      "model_id": "llama-3.1-8b",
      "name": "Llama 3.1 8B",
      "provider": "Ollama",
      "status": "active"
    }
  ]
}
```

---

### Phase 1.4: Frontend - Battle UI

**Tasks:**
- [ ] Create `/battle` page (Next.js App Router)
- [ ] Implement session-based battle flow
  - [ ] **Session creation** (first prompt)
    - Prompt input field (textarea)
    - "Submit" button to create session
    - Loading state during API calls
  - [ ] **Side-by-side response display** (Assistant A vs Assistant B)
    - Conversation history display (scrollable)
    - Each message shows timestamp
  - [ ] **Follow-up message input**
    - "Send Follow-up" button
    - Available only before voting
  - [ ] **Voting buttons** (ends current battle)
    - "Left is Better", "Tie", "Both are bad", "Right is Better"
    - Reveal model names after voting
  - [ ] **New Battle button** (after voting)
    - "Start New Battle" to begin new comparison in same session
    - Keeps session title and history sidebar
  - [ ] **Session sidebar** (optional MVP feature)
    - Show session title
    - List all battles in session
    - Click to view past battles
- [ ] Add error handling (API failures, network errors)
- [ ] Use shadcn/ui components (Button, Card, Textarea, Alert, ScrollArea)
- [ ] Add responsive design (mobile-friendly)

**UI Flow:**
```
1. User enters initial prompt
2. Click "Submit" → Session created, first battle starts
3. Display two responses side-by-side (anonymous)
4. [Optional] User enters follow-up prompt
5. Click "Send Follow-up" → Append to conversation
6. Repeat steps 4-5 as needed
7. User clicks voting button → Models revealed, battle status = 'voted'
8. Show "New Battle" button
9. Click "New Battle" → New random models selected, new battle starts in same session
10. Repeat 3-9 (multiple battles in one session)
```

---

### Phase 1.5: Frontend - API Integration

**Tasks:**
- [ ] Create API client service (`src/lib/api/battles.ts`)
  - [ ] `createSession(prompt: string)` → Create session + first battle
  - [ ] `createBattle(sessionId: string, prompt: string)` → New battle in session
  - [ ] `sendFollowUp(battleId: string, prompt: string)` → Add message to conversation
  - [ ] `submitVote(battleId: string, vote: string)` → Submit vote
- [ ] Create custom hooks
  - [ ] `useSession()` for session state management
  - [ ] `useBattle()` for battle state management (including conversation history)
  - [ ] `useVote()` for voting actions
- [ ] Handle loading and error states
- [ ] Add TypeScript types for API responses (Session, Battle, Message, Response, Vote)

---

## Data Models

### PostgreSQL Tables

See complete schema in [DATABASE_DESIGN.md](../ARCHITECTURE/DATABASE_DESIGN.md)

**sessions:**
```typescript
interface Session {
  id: number;
  session_id: string;          // UUID v4
  title: string;               // First prompt (max 200 chars)
  user_id: number | null;      // NULL in MVP (anonymous)
  created_at: Date;
  last_active_at: Date;
}
```

**battles:**
```typescript
interface Battle {
  id: number;
  battle_id: string;           // UUID v4
  session_id: string;          // FK to sessions
  left_model_id: string;
  right_model_id: string;
  conversation: MessageArray;  // JSONB array
  status: 'ongoing' | 'voted' | 'abandoned';
  created_at: Date;
  updated_at: Date;
}

// JSONB structure
type MessageArray = Array<UserMessage | AssistantMessage>;

interface UserMessage {
  role: 'user';
  content: string;
  timestamp: string;  // ISO 8601
}

interface AssistantMessage {
  role: 'assistant';
  model_id: string;
  position: 'left' | 'right';
  content: string;
  latency_ms: number;
  timestamp: string;  // ISO 8601
}
```

**votes:**
```typescript
interface Vote {
  id: number;
  vote_id: string;               // UUID v4
  battle_id: string;             // UNIQUE (1:1 with battle)
  session_id: string;            // FK to sessions
  vote: 'left_better' | 'right_better' | 'tie' | 'both_bad';
  left_model_id: string;         // Denormalized (avoid N+1)
  right_model_id: string;        // Denormalized
  processing_status: 'pending' | 'processed' | 'failed';
  processed_at: Date | null;
  error_message: string | null;
  voted_at: Date;
}
```

---

## Testing Strategy

**Backend:**
- Unit tests for session creation logic
- Unit tests for battle creation logic
- Unit tests for voting logic
- Integration tests for LLM API calls (mocked)
- Test cases: happy path, API failures, invalid votes

**Frontend:**
- Playwright MCP for UI flow verification
  1. Enter prompt and create session
  2. Verify responses displayed
  3. Send follow-up message
  4. Click vote button
  5. Verify model names revealed
  6. Click "New Battle" button
  7. Verify new battle with different models

**Test Data Generation:**
- Python script for seeding test data (`scripts/seed_test_data.py`)
- Generate 5-10 sessions with 2-3 battles each
- Generate realistic prompts and responses
- Generate random votes per battle
- Use for development and manual testing
- Run before worker to populate leaderboard data

---

## Success Criteria

- [ ] Users can create sessions with initial prompt
- [ ] Two random models are selected and called in parallel
- [ ] Responses are displayed anonymously
- [ ] Users can send follow-up prompts and continue multi-turn conversations
- [ ] Conversation history is maintained in JSONB and sent to LLMs for context
- [ ] Users can vote and see model identities revealed
- [ ] After voting, users can start new battle in same session with different models
- [ ] All API endpoints tested and working
- [ ] Frontend UI is responsive and error-free
- [ ] At least 2 OpenAI-compatible models configured (e.g., Ollama models)

---

## Future Enhancements (Post-MVP)

- User authentication (track votes per user)
- Rate limiting (prevent spam)
- Model filtering by category (coding, creative, etc.)
- Share battle results (URL sharing)
- Session history sidebar (view past battles)
- Multi-modal battles (image, audio, video)

---

**Related Documents:**
- [DATABASE_DESIGN.md](../ARCHITECTURE/DATABASE_DESIGN.md) - Complete database schema
- [002_LEADERBOARD_MVP.md](./002_LEADERBOARD_MVP.md) - Leaderboard feature
- [00_ROADMAP.md](../00_ROADMAP.md) - Overall project roadmap
- [CONVENTIONS/backend/](../CONVENTIONS/backend/) - Backend conventions
- [CONVENTIONS/frontend/](../CONVENTIONS/frontend/) - Frontend conventions

**Last Updated:** 2025-01-21

# Feature: Battle Mode (Text-to-Text) - MVP

**Status:** Not Started
**Priority:** High (MVP Core Feature)
**Estimated Time:** 2-3 weeks

---

## Overview

Enable users to compare two LLM responses through blind side-by-side testing. Users submit a prompt, receive anonymous responses from two randomly selected models, vote on the better response, and see model identities revealed after voting.

**Goals:**
- Unbiased LLM evaluation through blind testing
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
    MongoDB (store battle, responses, votes)
```

---

## Design Decisions

### Model Selection Algorithm
**Decision:** Uniform random selection (Option A)
- Select 2 different models randomly from active pool
- All models have equal probability
- `model_a != model_b` guaranteed
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

### Conversation History Limit
**Decision:** Maximum 5 follow-ups (Option B)
- Initial message + 5 follow-ups = **6 total messages per battle**
- Prevents context window overflow and excessive API costs
- Error returned when limit exceeded
- UI disables input after 5 follow-ups

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
- Store `model_a_position` and `model_b_position` in battle document
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

### MongoDB Indexes
**Decision:** Minimal indexes for MVP
```python
# Indexes to create on startup
db.battles.create_index("battle_id", unique=True)
db.battles.create_index("created_at")  # For worker aggregation
db.votes.create_index("vote_id", unique=True)
db.votes.create_index("voted_at")  # For worker aggregation
```
- Additional indexes can be added based on query patterns

### Database Connections
**Decision:** Async connections for both databases
```python
# MongoDB (Motor)
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/llmbattler")
mongo_client = AsyncIOMotorClient(
    MONGODB_URI,
    maxPoolSize=10,
    minPoolSize=2,
    serverSelectionTimeoutMS=5000
)

# PostgreSQL (SQLAlchemy + asyncpg) - for leaderboard read
from sqlalchemy.ext.asyncio import create_async_engine

POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql+asyncpg://localhost/llmbattler")
engine = create_async_engine(
    POSTGRES_URI,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
```
- **Note:** Backend needs BOTH databases - MongoDB for battles/votes write, PostgreSQL for leaderboard read

---

## Implementation Phases

### Phase 1.1: Backend - Battle Creation API

**Tasks:**
- [ ] Setup MongoDB connection and indexes
  - [ ] Create async Motor client with connection pooling
  - [ ] Create indexes on startup (battle_id unique, created_at, vote_id unique, voted_at)
- [ ] Create MongoDB collections schema
  - [ ] `battles` collection (battle_id, model_a_id, model_b_id, model_a_position, model_b_position, messages[], created_at)
  - [ ] `messages` subdocument: (message_id, prompt, responses[], timestamp)
  - [ ] `responses` subdocument: (model_id, response_text, latency_ms)
  - [ ] `votes` collection (vote_id, battle_id, vote, voted_at)
- [ ] Implement `POST /api/battles` endpoint
  - [ ] Accept user prompt (text)
  - [ ] Randomly select 2 models from available pool using `select_models_for_battle()`
  - [ ] **Randomly assign left/right positions** (prevent position bias)
  - [ ] Call LLM APIs in parallel (async) with timeout and retry logic
  - [ ] Store battle with first message in MongoDB (include position fields)
  - [ ] Return anonymous responses (model IDs hidden, positions randomized)
- [ ] Implement `POST /api/battles/{battle_id}/messages` endpoint
  - [ ] Accept follow-up prompt
  - [ ] **Check conversation history limit (MAX_FOLLOW_UPS = 5)**
  - [ ] Retrieve conversation history from battle
  - [ ] Call LLM APIs with full message history (OpenAI chat format)
  - [ ] Append new message to battle
  - [ ] Return anonymous responses
- [ ] Add error handling (API failures, timeouts, history limit exceeded)
- [ ] Add logging for key events (battle creation, API failures, errors)
- [ ] Write tests for battle creation and multi-turn conversations

**API Spec (Initial Battle):**
```
POST /api/battles
Request:
{
  "prompt": "What is the capital of France?"
}

Response:
{
  "battle_id": "battle_123",
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

**API Spec (Follow-up Message):**
```
POST /api/battles/battle_123/messages
Request:
{
  "prompt": "What about its population?"
}

Response:
{
  "battle_id": "battle_123",
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
  ]
}
```

---

### Phase 1.2: Backend - Voting API

**Tasks:**
- [ ] Implement `POST /api/battles/{battle_id}/vote` endpoint
  - [ ] Accept vote: `left_better`, `tie`, `both_bad`, `right_better`
  - [ ] Store vote in MongoDB
  - [ ] Return model identities (reveal after vote)
- [ ] Add vote validation (prevent duplicate votes - optional for MVP)
- [ ] Write tests for voting

**API Spec:**
```
POST /api/battles/battle_123/vote
Request:
{
  "vote": "left_better"
}

Response:
{
  "battle_id": "battle_123",
  "vote": "left_better",
  "revealed_models": {
    "left": "gpt-4o-mini",
    "right": "llama-3.1-8b"
  }
}
```

---

### Phase 1.3: Backend - Model Management

**Tasks:**
- [ ] Create model configuration system (YAML + Environment Variables)
  - [ ] **MVP: OpenAI-compatible endpoints only** (Ollama, vLLM, OpenAI, etc.)
  - [ ] Load models from `config/models.yaml` (see Design Decisions)
  - [ ] Resolve API keys from environment variables
  - [ ] Validate configuration on startup
- [ ] Implement `GET /api/models` endpoint
  - [ ] Return list of available models (name, provider, status)
- [ ] Create LLM API client (httpx-based)
  - [ ] **OpenAI chat completion format** (`/v1/chat/completions`)
  - [ ] Support conversation history for multi-turn battles
  - [ ] **Timeout configuration:** Connect 5s, Read 30s, Write 5s, Pool 5s
  - [ ] **Retry logic:** 3 attempts with exponential backoff (1s, 2s, 4s)
  - [ ] Error handling and logging for API failures
  - [ ] Use `model` field from config for API calls
- [ ] Setup CORS middleware (environment-based origins)
- [ ] Setup logging (Python logging to stdout)
- [ ] Write tests for model management

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
- [ ] Implement battle flow
  - [ ] Prompt input field (textarea)
  - [ ] "Submit" button to create battle
  - [ ] Loading state during API calls
  - [ ] Side-by-side response display (Assistant A vs Assistant B)
  - [ ] Conversation history display (scrollable)
  - [ ] Follow-up prompt input (available before voting)
  - [ ] "Send Follow-up" button
  - [ ] **Message counter (e.g., "3/6 messages")**
  - [ ] **Disable follow-up input after 5 follow-ups (6 total messages)**
  - [ ] Voting buttons: "Left is Better", "Tie", "Both are bad", "Right is Better"
  - [ ] Reveal model names after voting
  - [ ] Disable follow-up input after voting
- [ ] Add error handling (API failures, network errors)
- [ ] Use shadcn/ui components (Button, Card, Textarea, Alert, ScrollArea)
- [ ] Add responsive design (mobile-friendly)

**UI Flow:**
```
1. User enters initial prompt
2. Click "Submit" → Show loading spinner
3. Display two responses side-by-side (anonymous)
4. [Optional] User enters follow-up prompt (max 5 follow-ups)
5. Click "Send Follow-up" → Show loading spinner
6. Append new responses to conversation history
7. Repeat steps 4-6 as needed (until 6 total messages or user votes)
8. Show message counter (e.g., "3/6 messages")
9. Disable follow-up input after 6 messages or voting
10. User clicks voting button (ends conversation)
11. Reveal model names below entire conversation
12. Show "New Battle" button to restart
```

---

### Phase 1.5: Frontend - API Integration

**Tasks:**
- [ ] Create API client service (`src/lib/api/battles.ts`)
  - [ ] `createBattle(prompt: string)`
  - [ ] `sendFollowUp(battleId: string, prompt: string)`
  - [ ] `submitVote(battleId: string, vote: string)`
- [ ] Create custom hooks
  - [ ] `useBattle()` for battle state management (including conversation history)
  - [ ] `useVote()` for voting actions
- [ ] Handle loading and error states
- [ ] Add TypeScript types for API responses (Battle, Message, Response, Vote)

---

## Data Models

### MongoDB Collections

**battles:**
```json
{
  "_id": "ObjectId",
  "battle_id": "battle_123",
  "model_a_id": "gpt-4o-mini",
  "model_b_id": "llama-3.1-8b",
  "model_a_position": "left",
  "model_b_position": "right",
  "messages": [
    {
      "message_id": "msg_1",
      "prompt": "What is the capital of France?",
      "responses": [
        {
          "model_id": "gpt-4o-mini",
          "response_text": "The capital of France is Paris.",
          "latency_ms": 234
        },
        {
          "model_id": "llama-3.1-8b",
          "response_text": "Paris is the capital city of France.",
          "latency_ms": 189
        }
      ],
      "timestamp": "2025-01-20T10:30:05Z"
    },
    {
      "message_id": "msg_2",
      "prompt": "What about its population?",
      "responses": [
        {
          "model_id": "gpt-4o-mini",
          "response_text": "Paris has approximately 2.1 million people...",
          "latency_ms": 287
        },
        {
          "model_id": "llama-3.1-8b",
          "response_text": "The population of Paris is around 2.2 million...",
          "latency_ms": 201
        }
      ],
      "timestamp": "2025-01-20T10:31:12Z"
    }
  ],
  "created_at": "2025-01-20T10:30:00Z"
}
```

**votes:**
```json
{
  "_id": "ObjectId",
  "vote_id": "vote_789",
  "battle_id": "battle_123",
  "vote": "left_better",
  "voted_at": "2025-01-20T10:32:00Z"
}
```

---

## Testing Strategy

**Backend:**
- Unit tests for battle creation logic
- Unit tests for voting logic
- Integration tests for LLM API calls (mocked)
- Test cases: happy path, API failures, invalid votes, history limit exceeded

**Frontend:**
- Playwright MCP for UI flow verification
  1. Enter prompt and submit
  2. Verify responses displayed
  3. Click vote button
  4. Verify model names revealed

**Test Data Generation:**
- Python script for seeding test data (`scripts/seed_test_data.py`)
- Generate 20-30 battles with realistic prompts and responses
- Generate 5-15 random votes per battle
- Use for development and manual testing
- Run before worker to populate leaderboard data

---

## Success Criteria

- [ ] Users can create battles with any prompt
- [ ] Two random models are selected and called in parallel
- [ ] Responses are displayed anonymously
- [ ] Users can send follow-up prompts and continue multi-turn conversations (max 5 follow-ups)
- [ ] Conversation history is maintained and sent to LLMs for context
- [ ] Follow-up input is disabled after 6 total messages or voting
- [ ] Message counter displayed in UI
- [ ] Users can vote and see model identities revealed
- [ ] All API endpoints tested and working
- [ ] Frontend UI is responsive and error-free
- [ ] At least 2 OpenAI-compatible models configured (e.g., Ollama models)

---

## Future Enhancements (Post-MVP)

- User authentication (track votes per user)
- Rate limiting (prevent spam)
- Model filtering by category (coding, creative, etc.)
- Share battle results (URL sharing)
- Multi-modal battles (image, audio, video)

---

**Related Documents:**
- [00_ROADMAP.md](../00_ROADMAP.md) - Overall project roadmap
- [CONVENTIONS/backend/](../CONVENTIONS/backend/) - Backend conventions
- [CONVENTIONS/frontend/](../CONVENTIONS/frontend/) - Frontend conventions
- [002_LEADERBOARD_MVP.md](./002_LEADERBOARD_MVP.md) - Leaderboard feature

**Last Updated:** 2025-10-20

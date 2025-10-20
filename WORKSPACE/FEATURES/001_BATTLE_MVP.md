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

## Implementation Phases

### Phase 1.1: Backend - Battle Creation API

**Tasks:**
- [ ] Create MongoDB collections schema
  - [ ] `battles` collection (battle_id, model_a_id, model_b_id, messages[], created_at)
  - [ ] `messages` subdocument: (message_id, prompt, responses[], timestamp)
  - [ ] `responses` subdocument: (model_id, response_text, latency_ms)
  - [ ] `votes` collection (vote_id, battle_id, vote, voted_at)
- [ ] Implement `POST /api/battles` endpoint
  - [ ] Accept user prompt (text)
  - [ ] Randomly select 2 models from available pool
  - [ ] Call LLM APIs in parallel (async)
  - [ ] Store battle with first message in MongoDB
  - [ ] Return anonymous responses (model IDs hidden)
- [ ] Implement `POST /api/battles/{battle_id}/messages` endpoint
  - [ ] Accept follow-up prompt
  - [ ] Retrieve conversation history from battle
  - [ ] Call LLM APIs with full message history (OpenAI chat format)
  - [ ] Append new message to battle
  - [ ] Return anonymous responses
- [ ] Add error handling (API failures, timeouts)
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
- [ ] Create model configuration system (environment-based)
  - [ ] **MVP: OpenAI-compatible endpoints only** (Ollama, vLLM, OpenAI, etc.)
  - [ ] Configuration via environment variables (model name, base URL, API key)
- [ ] Implement `GET /api/models` endpoint
  - [ ] Return list of available models (name, provider, status)
- [ ] Create LLM API client (httpx-based)
  - [ ] **OpenAI chat completion format** (`/v1/chat/completions`)
  - [ ] Support conversation history for multi-turn battles
  - [ ] Error handling and retry logic
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
4. [Optional] User enters follow-up prompt
5. Click "Send Follow-up" → Show loading spinner
6. Append new responses to conversation history
7. Repeat steps 4-6 as needed
8. User clicks voting button (ends conversation)
9. Reveal model names below entire conversation
10. Show "New Battle" button to restart
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
- Test cases: happy path, API failures, invalid votes

**Frontend:**
- Playwright MCP for UI flow verification
  1. Enter prompt and submit
  2. Verify responses displayed
  3. Click vote button
  4. Verify model names revealed

---

## Success Criteria

- [ ] Users can create battles with any prompt
- [ ] Two random models are selected and called in parallel
- [ ] Responses are displayed anonymously
- [ ] Users can send follow-up prompts and continue multi-turn conversations
- [ ] Conversation history is maintained and sent to LLMs for context
- [ ] Users can vote and see model identities revealed
- [ ] Follow-up input is disabled after voting
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

**Last Updated:** 2025-01-20

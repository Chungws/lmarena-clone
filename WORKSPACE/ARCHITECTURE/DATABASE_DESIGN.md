# Database Design: llmbattler

**Status:** Final Design for MVP with Scalability Path
**Last Updated:** 2025-01-21

---

## Table of Contents

1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [PostgreSQL Schema](#postgresql-schema)
4. [Data Flow](#data-flow)
5. [Repository Pattern](#repository-pattern)
6. [Scalability Path](#scalability-path)
7. [Implementation Guide](#implementation-guide)

---

## Overview

llmbattler uses a **single PostgreSQL database** for MVP, designed with clear scalability path to handle growth from 10 QPS to 10,000+ QPS.

### Database Strategy

```
PostgreSQL (Single DB)
  ├── sessions          # Session 컨테이너
  ├── battles           # Battle with conversation (JSONB)
  ├── votes             # Vote with denormalized model IDs
  ├── model_stats       # Aggregated ELO rankings
  └── worker_status     # Worker execution tracking
```

### Why PostgreSQL Only?

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Traffic** | 10 QPS (MVP) | PostgreSQL handles 10,000+ QPS easily |
| **Complexity** | Single DB | Simpler operations, no sync issues |
| **Joins** | Minimal | Denormalization avoids N+1 queries |
| **ACID** | Required | Vote integrity, transaction safety |
| **Analytics** | SQL | Complex aggregations and filtering |
| **Scalability** | Read replicas → Sharding | Clear upgrade path |

**Alternative Rejected:**
- ❌ MongoDB: No benefit at this scale, harder analytics
- ❌ Dual DB: Over-engineering for 10 QPS
- ❌ Cassandra: Designed for 100,000+ QPS

---

## Design Philosophy

### 1. Start Simple, Scale Smart

```
Phase 1 (MVP): Single PostgreSQL
  → 10-100 QPS

Phase 2 (Growth): Add Read Replicas
  → 100-1,000 QPS

Phase 3 (Viral): Add Redis Cache
  → 1,000-10,000 QPS

Phase 4 (Hypergrowth): Horizontal Sharding
  → 10,000+ QPS
```

### 2. Partition-Ready Design

**All queries use `session_id` as partition key:**
```sql
-- Good (partition-friendly)
SELECT * FROM battles WHERE session_id = ?;

-- Bad (requires full scan)
SELECT * FROM battles WHERE left_model_id = ?;
```

**Future sharding:**
```python
shard_id = hash(session_id) % num_shards
# All data for a session stays in one shard
```

### 3. Repository Pattern (Abstraction Layer)

**Database is hidden behind repositories:**
```python
# Easy to replace PostgreSQL → Cassandra
battles = await battle_repo.get_by_session(session_id)
```

---

## PostgreSQL Schema

### 1. sessions

**Purpose:** Container for multiple battles in one user session

```sql
CREATE TABLE sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,

    -- Metadata
    title VARCHAR(200) NOT NULL,  -- First prompt (e.g., "안녕?")
    user_id BIGINT,  -- NULL for anonymous (MVP)

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    last_active_at TIMESTAMP DEFAULT NOW() NOT NULL,

    -- Indexes
    CONSTRAINT sessions_session_id_unique UNIQUE (session_id)
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);
```

**Field Details:**

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `session_id` | VARCHAR(50) | Unique identifier | UUID v4 |
| `title` | VARCHAR(200) | First user prompt | For sidebar display |
| `user_id` | BIGINT | User reference | NULL in MVP (anonymous) |
| `last_active_at` | TIMESTAMP | Last battle/vote time | For session cleanup |

**Sample Data:**
```sql
INSERT INTO sessions (session_id, title, user_id, created_at, last_active_at)
VALUES
    ('session_abc123', '안녕하세요 👋', NULL, '2025-01-21 10:00:00', '2025-01-21 10:30:00'),
    ('session_xyz789', 'What is ELO rating?', NULL, '2025-01-21 11:00:00', '2025-01-21 11:05:00');
```

**Business Logic:**
- Session created on first battle
- `last_active_at` updated on every battle/vote
- Cleanup: Delete sessions older than 30 days with no votes

---

### 2. battles

**Purpose:** Single battle with conversation history between two models

```sql
CREATE TABLE battles (
    id BIGSERIAL PRIMARY KEY,
    battle_id VARCHAR(50) UNIQUE NOT NULL,
    session_id VARCHAR(50) NOT NULL,

    -- Models (randomly selected)
    left_model_id VARCHAR(255) NOT NULL,
    right_model_id VARCHAR(255) NOT NULL,

    -- Conversation (OpenAI-compatible format)
    conversation JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'ongoing',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT battles_battle_id_unique UNIQUE (battle_id),
    CONSTRAINT battles_status_check CHECK (status IN ('ongoing', 'voted', 'abandoned'))
    -- Note: No FK constraint (ADR-001) - application-level referential integrity
);

-- Indexes
CREATE INDEX idx_battles_session_id ON battles(session_id);
CREATE INDEX idx_battles_status ON battles(status);
CREATE INDEX idx_battles_session_status ON battles(session_id, status);  -- Compound
CREATE INDEX idx_battles_created_at ON battles(created_at DESC);
```

**Field Details:**

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `battle_id` | VARCHAR(50) | Unique identifier | UUID v4 |
| `session_id` | VARCHAR(50) | Parent session | FK to sessions |
| `left_model_id` | VARCHAR(255) | Left model | From config/models.yaml |
| `right_model_id` | VARCHAR(255) | Right model | Randomly selected |
| `conversation` | JSONB | Message array | OpenAI chat format |
| `status` | VARCHAR(20) | Battle state | ongoing → voted |

**Conversation JSONB Structure:**
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
    "content": "반갑습니다! 어떻게 도와드릴까요?",
    "latency_ms": 189,
    "timestamp": "2025-01-21T10:00:01Z"
  }
]
```

**JSONB Operations:**
```sql
-- Append new message
UPDATE battles
SET conversation = conversation || $1::jsonb,
    updated_at = NOW()
WHERE battle_id = $2;

-- Query messages by role
SELECT battle_id, conversation
FROM battles
WHERE conversation @> '[{"role": "user"}]'::jsonb;

-- Count messages
SELECT battle_id, jsonb_array_length(conversation) as message_count
FROM battles;
```

**Sample Data:**
```sql
INSERT INTO battles (battle_id, session_id, left_model_id, right_model_id, conversation, status)
VALUES (
    'battle_001',
    'session_abc123',
    'gpt-4o-mini',
    'claude-3.5-sonnet',
    '[
        {"role": "user", "content": "안녕하세요", "timestamp": "2025-01-21T10:00:00Z"},
        {"role": "assistant", "model_id": "gpt-4o-mini", "position": "left", "content": "...", "latency_ms": 234},
        {"role": "assistant", "model_id": "claude-3.5-sonnet", "position": "right", "content": "...", "latency_ms": 189}
    ]'::jsonb,
    'ongoing'
);
```

**Business Logic:**
- Battle created when user submits first prompt
- Conversation appended on follow-up messages
- Status: `ongoing` (can add messages) → `voted` (frozen)
- Max messages: No limit in DB, enforced by backend (e.g., 20 messages)

---

### 3. votes

**Purpose:** User vote on battle outcome (denormalized for worker performance)

```sql
CREATE TABLE votes (
    id BIGSERIAL PRIMARY KEY,
    vote_id VARCHAR(50) UNIQUE NOT NULL,
    battle_id VARCHAR(50) UNIQUE NOT NULL,  -- 1:1 relationship
    session_id VARCHAR(50) NOT NULL,

    -- Vote
    vote VARCHAR(20) NOT NULL,

    -- Denormalized model IDs (避免 JOIN)
    left_model_id VARCHAR(255) NOT NULL,
    right_model_id VARCHAR(255) NOT NULL,

    -- Worker processing status
    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    processed_at TIMESTAMP,
    error_message TEXT,

    -- Timestamp
    voted_at TIMESTAMP DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT votes_vote_id_unique UNIQUE (vote_id),
    CONSTRAINT votes_battle_id_unique UNIQUE (battle_id),  -- 1:1
    CONSTRAINT votes_vote_check CHECK (vote IN ('left_better', 'right_better', 'tie', 'both_bad')),
    CONSTRAINT votes_processing_status_check CHECK (processing_status IN ('pending', 'processed', 'failed'))
    -- Note: No FK constraints (ADR-001) - application-level CASCADE deletion
);

-- Indexes
CREATE INDEX idx_votes_processing_status ON votes(processing_status);
CREATE INDEX idx_votes_session_id ON votes(session_id);
CREATE INDEX idx_votes_voted_at ON votes(voted_at);
```

**Field Details:**

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `vote_id` | VARCHAR(50) | Unique identifier | UUID v4 |
| `battle_id` | VARCHAR(50) | Parent battle | UNIQUE (1:1) |
| `session_id` | VARCHAR(50) | Parent session | For analytics |
| `vote` | VARCHAR(20) | Vote choice | 4 options |
| `left_model_id` | VARCHAR(255) | Left model | **Denormalized** |
| `right_model_id` | VARCHAR(255) | Right model | **Denormalized** |
| `processing_status` | VARCHAR(20) | Worker status | pending → processed |

**Why Denormalized?**
```python
# Without denormalization (BAD)
votes = await db.fetch_all("SELECT * FROM votes WHERE processing_status = 'pending'")
for vote in votes:
    battle = await db.fetch_one("SELECT * FROM battles WHERE battle_id = $1", vote["battle_id"])
    # N+1 queries!

# With denormalization (GOOD)
votes = await db.fetch_all("SELECT * FROM votes WHERE processing_status = 'pending'")
for vote in votes:
    # model_id already in vote!
    winner = vote["left_model_id"] if vote["vote"] == "left_better" else ...
```

**Vote Types & ELO Scores:**

| Vote | UI Label | ELO Score (Left, Right) | Description |
|------|----------|------------------------|-------------|
| `left_better` | "Left is Better" | (1.0, 0.0) | Left wins |
| `right_better` | "Right is Better" | (0.0, 1.0) | Right wins |
| `tie` | "It's a tie" | (0.5, 0.5) | Equal quality |
| `both_bad` | "Both are bad" | (0.25, 0.25) | Both poor (small penalty) |

**Sample Data:**
```sql
INSERT INTO votes (vote_id, battle_id, session_id, vote, left_model_id, right_model_id, processing_status)
VALUES (
    'vote_001',
    'battle_001',
    'session_abc123',
    'left_better',
    'gpt-4o-mini',
    'claude-3.5-sonnet',
    'pending'
);
```

**Business Logic:**
- Vote created when user clicks vote button
- Immediately updates battle.status = 'voted'
- Worker processes pending votes hourly
- Processing status: `pending` → `processed` (success) or `failed` (error)

---

### 4. model_stats

**Purpose:** Aggregated ELO rankings and statistics (updated by worker)

```sql
CREATE TABLE model_stats (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(255) UNIQUE NOT NULL,

    -- ELO Rating
    elo_score INTEGER NOT NULL DEFAULT 1500,
    elo_ci FLOAT NOT NULL DEFAULT 200.0,  -- 95% confidence interval

    -- Statistics
    vote_count INTEGER NOT NULL DEFAULT 0,
    win_count INTEGER NOT NULL DEFAULT 0,
    loss_count INTEGER NOT NULL DEFAULT 0,
    tie_count INTEGER NOT NULL DEFAULT 0,
    win_rate FLOAT NOT NULL DEFAULT 0.0,

    -- Metadata
    organization VARCHAR(255) NOT NULL,
    license VARCHAR(50) NOT NULL,  -- 'proprietary', 'open-source'

    -- Timestamp
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT model_stats_model_id_unique UNIQUE (model_id),
    CONSTRAINT model_stats_elo_score_positive CHECK (elo_score >= 0),
    CONSTRAINT model_stats_vote_count_positive CHECK (vote_count >= 0),
    CONSTRAINT model_stats_win_rate_range CHECK (win_rate >= 0.0 AND win_rate <= 1.0)
);

-- Indexes
CREATE INDEX idx_model_stats_elo_score ON model_stats(elo_score DESC);
CREATE INDEX idx_model_stats_vote_count ON model_stats(vote_count DESC);
CREATE INDEX idx_model_stats_organization ON model_stats(organization);
CREATE INDEX idx_model_stats_license ON model_stats(license);
```

**Field Details:**

| Field | Default | Description | Formula |
|-------|---------|-------------|---------|
| `elo_score` | 1500 | Current ELO rating | Standard ELO formula |
| `elo_ci` | 200.0 | 95% confidence interval | `1.96 * 400 / sqrt(vote_count)` |
| `vote_count` | 0 | Total votes | win + loss + tie |
| `win_rate` | 0.0 | Win percentage | `win_count / (win_count + loss_count)` |

**Sample Data:**
```sql
INSERT INTO model_stats (model_id, elo_score, elo_ci, vote_count, win_count, loss_count, tie_count, win_rate, organization, license)
VALUES
    ('gpt-4o', 1654, 12.3, 1234, 839, 295, 100, 0.74, 'OpenAI', 'proprietary'),
    ('claude-3.5-sonnet', 1632, 15.7, 987, 632, 305, 50, 0.67, 'Anthropic', 'proprietary'),
    ('llama-3.1-8b', 1487, 28.4, 456, 218, 198, 40, 0.52, 'Meta', 'open-source');
```

**Business Logic:**
- Worker updates hourly based on new votes
- Leaderboard filters: `vote_count >= 5` (minimum votes)
- ELO calculation: K-factor = 32, Initial = 1500

---

### 5. worker_status

**Purpose:** Worker execution tracking for incremental processing

```sql
CREATE TABLE worker_status (
    id SERIAL PRIMARY KEY,
    worker_name VARCHAR(100) UNIQUE NOT NULL,

    -- Execution tracking
    last_run_at TIMESTAMP DEFAULT NOW() NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'idle',
    votes_processed INTEGER NOT NULL DEFAULT 0,
    error_message VARCHAR(1000),

    -- Constraints
    CONSTRAINT worker_status_worker_name_unique UNIQUE (worker_name),
    CONSTRAINT worker_status_votes_processed_positive CHECK (votes_processed >= 0),
    CONSTRAINT worker_status_status_check CHECK (status IN ('idle', 'running', 'success', 'failed'))
);
```

**Sample Data:**
```sql
INSERT INTO worker_status (worker_name, last_run_at, status, votes_processed)
VALUES ('elo_aggregator', '2025-01-21 15:00:00', 'success', 127);
```

---

## Data Flow

### 1. User Flow (Session → Battle → Vote)

```
┌─────────────────────────────────────────────────────┐
│ Step 1: Create Session & First Battle              │
├─────────────────────────────────────────────────────┤
│ POST /api/sessions                                  │
│ Body: {"prompt": "안녕하세요"}                        │
│                                                     │
│ Backend:                                            │
│   1. INSERT INTO sessions (session_id, title)       │
│   2. SELECT 2 random models                         │
│   3. Call LLM APIs (parallel)                       │
│   4. INSERT INTO battles (session_id, conversation) │
│                                                     │
│ Response:                                           │
│   {"session_id": "...", "battle_id": "...",        │
│    "responses": [...]}                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 2: Follow-up Message (Same Battle)            │
├─────────────────────────────────────────────────────┤
│ POST /api/battles/{battle_id}/messages             │
│ Body: {"prompt": "계속 질문"}                        │
│                                                     │
│ Backend:                                            │
│   1. SELECT conversation FROM battles               │
│   2. Call LLMs with history                        │
│   3. UPDATE battles SET conversation = conversation │
│         || new_messages                             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 3: Vote                                        │
├─────────────────────────────────────────────────────┤
│ POST /api/battles/{battle_id}/vote                 │
│ Body: {"vote": "left_better"}                      │
│                                                     │
│ Backend (Transaction):                              │
│   BEGIN;                                            │
│   1. SELECT left_model_id, right_model_id          │
│        FROM battles WHERE battle_id = ?             │
│   2. INSERT INTO votes (battle_id, vote,           │
│        left_model_id, right_model_id)  -- Denorm   │
│   3. UPDATE battles SET status = 'voted'           │
│   4. UPDATE sessions SET last_active_at = NOW()    │
│   COMMIT;                                           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 4: New Battle (After Vote)                    │
├─────────────────────────────────────────────────────┤
│ POST /api/sessions/{session_id}/battles            │
│ Body: {"prompt": "새로운 질문"}                      │
│                                                     │
│ Backend:                                            │
│   1. SELECT 2 NEW random models                    │
│   2. INSERT INTO battles (session_id, ...)         │
└─────────────────────────────────────────────────────┘
```

---

### 2. Worker Flow (ELO Aggregation)

```python
async def run_aggregation():
    """
    Hourly worker to process pending votes and update ELO ratings
    """
    async with db.transaction():
        # 1. Get pending votes (with denormalized model IDs)
        pending_votes = await db.fetch_all("""
            SELECT vote_id, vote, left_model_id, right_model_id
            FROM votes
            WHERE processing_status = 'pending'
            ORDER BY voted_at
        """)

        for vote in pending_votes:
            try:
                # 2. Determine winner/loser
                if vote["vote"] == "left_better":
                    winner, loser = vote["left_model_id"], vote["right_model_id"]
                    winner_score, loser_score = 1.0, 0.0
                elif vote["vote"] == "right_better":
                    winner, loser = vote["right_model_id"], vote["left_model_id"]
                    winner_score, loser_score = 1.0, 0.0
                elif vote["vote"] == "tie":
                    # Both get 0.5
                    await update_elo(vote["left_model_id"], vote["right_model_id"], 0.5)
                    await update_elo(vote["right_model_id"], vote["left_model_id"], 0.5)
                    await mark_vote_processed(vote["vote_id"])
                    continue
                elif vote["vote"] == "both_bad":
                    # Both get 0.25 (small penalty)
                    await update_elo(vote["left_model_id"], vote["right_model_id"], 0.25)
                    await update_elo(vote["right_model_id"], vote["left_model_id"], 0.25)
                    await mark_vote_processed(vote["vote_id"])
                    continue

                # 3. Calculate new ELO
                await update_elo(winner, loser, winner_score)
                await update_elo(loser, winner, loser_score)

                # 4. Mark as processed
                await mark_vote_processed(vote["vote_id"])

            except Exception as e:
                # 5. Mark as failed
                await db.execute("""
                    UPDATE votes
                    SET processing_status = 'failed',
                        error_message = $1
                    WHERE vote_id = $2
                """, str(e), vote["vote_id"])

        # 6. Update worker status
        await db.execute("""
            UPDATE worker_status
            SET last_run_at = NOW(),
                status = 'success',
                votes_processed = $1
            WHERE worker_name = 'elo_aggregator'
        """, len(pending_votes))


async def update_elo(model_a: str, model_b: str, score: float):
    """
    Update ELO for model_a based on match against model_b

    Args:
        model_a: Model to update
        model_b: Opponent model
        score: Result (1.0=win, 0.5=tie, 0.25=both_bad, 0.0=loss)
    """
    # Get current ratings
    stats_a = await db.fetch_one(
        "SELECT elo_score, vote_count FROM model_stats WHERE model_id = $1",
        model_a
    )
    stats_b = await db.fetch_one(
        "SELECT elo_score FROM model_stats WHERE model_id = $1",
        model_b
    )

    # Calculate expected score
    rating_a = stats_a["elo_score"]
    rating_b = stats_b["elo_score"]
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    # Calculate new rating
    K_FACTOR = 32
    new_rating = rating_a + K_FACTOR * (score - expected_a)

    # Calculate new confidence interval
    new_vote_count = stats_a["vote_count"] + 1
    if new_vote_count > 0:
        se = 400 / (new_vote_count ** 0.5)
        new_ci = 1.96 * se
    else:
        new_ci = 200.0

    # Update stats
    await db.execute("""
        UPDATE model_stats
        SET elo_score = $1,
            elo_ci = $2,
            vote_count = vote_count + 1,
            win_count = win_count + CASE WHEN $3 >= 0.75 THEN 1 ELSE 0 END,
            loss_count = loss_count + CASE WHEN $3 <= 0.25 THEN 1 ELSE 0 END,
            tie_count = tie_count + CASE WHEN $3 > 0.25 AND $3 < 0.75 THEN 1 ELSE 0 END,
            win_rate = (win_count + CASE WHEN $3 >= 0.75 THEN 1 ELSE 0 END)::float /
                      NULLIF(win_count + loss_count + CASE WHEN $3 >= 0.75 OR $3 <= 0.25 THEN 1 ELSE 0 END, 0),
            updated_at = NOW()
        WHERE model_id = $4
    """, int(new_rating), new_ci, score, model_a)
```

---

## Repository Pattern

### Why Repository Pattern?

**Benefits:**
- ✅ Database abstraction (easy to replace PostgreSQL → Cassandra)
- ✅ Testable (mock repositories)
- ✅ Consistent interface
- ✅ Future-proof (add caching, events easily)

### Example: BattleRepository

```python
# backend/app/repositories/battle_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas import Battle, BattleCreate

class BattleRepositoryInterface(ABC):
    """Abstract interface for battle storage"""

    @abstractmethod
    async def get_by_id(self, battle_id: str) -> Optional[Battle]:
        pass

    @abstractmethod
    async def get_by_session(self, session_id: str) -> List[Battle]:
        pass

    @abstractmethod
    async def create(self, battle: BattleCreate) -> Battle:
        pass

    @abstractmethod
    async def append_message(self, battle_id: str, messages: List[dict]) -> None:
        pass

    @abstractmethod
    async def update_status(self, battle_id: str, status: str) -> None:
        pass


class PostgresBattleRepository(BattleRepositoryInterface):
    """PostgreSQL implementation"""

    def __init__(self, db):
        self.db = db

    async def get_by_id(self, battle_id: str) -> Optional[Battle]:
        row = await self.db.fetch_one(
            "SELECT * FROM battles WHERE battle_id = $1",
            battle_id
        )
        return Battle(**row) if row else None

    async def get_by_session(self, session_id: str) -> List[Battle]:
        """
        Get all battles for a session

        This query is partition-friendly (uses session_id)
        Future: When sharding, this will hit only one shard
        """
        rows = await self.db.fetch_all(
            "SELECT * FROM battles WHERE session_id = $1 ORDER BY created_at",
            session_id
        )
        return [Battle(**row) for row in rows]

    async def create(self, battle: BattleCreate) -> Battle:
        row = await self.db.fetch_one("""
            INSERT INTO battles (battle_id, session_id, left_model_id, right_model_id, conversation)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
        """, battle.battle_id, battle.session_id, battle.left_model_id,
            battle.right_model_id, battle.conversation)
        return Battle(**row)

    async def append_message(self, battle_id: str, messages: List[dict]) -> None:
        """
        Append new messages to conversation (JSONB array)
        """
        await self.db.execute("""
            UPDATE battles
            SET conversation = conversation || $1::jsonb,
                updated_at = NOW()
            WHERE battle_id = $2
        """, json.dumps(messages), battle_id)

    async def update_status(self, battle_id: str, status: str) -> None:
        await self.db.execute(
            "UPDATE battles SET status = $1, updated_at = NOW() WHERE battle_id = $2",
            status, battle_id
        )


# Usage in router
@router.post("/battles/{battle_id}/vote")
async def submit_vote(
    battle_id: str,
    vote_data: VoteCreate,
    battle_repo: BattleRepositoryInterface = Depends(get_battle_repo),
    vote_repo: VoteRepositoryInterface = Depends(get_vote_repo)
):
    # Easy to test with mock repositories
    battle = await battle_repo.get_by_id(battle_id)
    if not battle:
        raise HTTPException(404, "Battle not found")

    # Create vote
    vote = await vote_repo.create(vote_data)

    # Update battle status
    await battle_repo.update_status(battle_id, "voted")

    return vote
```

---

## Scalability Path

### Phase 1: MVP (10-100 QPS)

```
┌─────────────────────────┐
│  PostgreSQL (단일 DB)    │
│  - sessions             │
│  - battles              │
│  - votes                │
│  - model_stats          │
└─────────────────────────┘
         ↑
      Backend
```

**Capacity:**
- Handles: 10-100 QPS
- Storage: 1-10 GB/year
- Cost: $50-100/month

**Monitoring Triggers:**
- DB CPU > 70% → Move to Phase 2
- Query latency > 500ms → Add indexes
- Storage > 100 GB → Archive old sessions

---

### Phase 2: Growth (100-1,000 QPS)

```
┌────────────────────────────┐
│  PostgreSQL Primary (Write)│
│  - sessions, battles, votes│
└───────────┬────────────────┘
            │ Streaming replication
    ┌───────┴─────────┐
    ↓                 ↓
┌─────────┐      ┌─────────┐
│Replica 1│      │Replica 2│
│ (Read)  │      │ (Read)  │
└─────────┘      └─────────┘

Backend:
  Write → Primary
  Read → Replicas (load balanced)
```

**Changes:**
```python
# backend/app/db.py
class Database:
    def __init__(self):
        self.primary = create_pool(PRIMARY_URL)  # Write
        self.replicas = [
            create_pool(REPLICA1_URL),
            create_pool(REPLICA2_URL)
        ]  # Read

    async def execute(self, query: str, *args):
        # Write goes to primary
        return await self.primary.execute(query, *args)

    async def fetch_all(self, query: str, *args):
        # Read from random replica
        replica = random.choice(self.replicas)
        return await replica.fetch_all(query, *args)
```

**Capacity:**
- Handles: 100-1,000 QPS
- Cost: $200-500/month

---

### Phase 3: Viral (1,000-10,000 QPS)

```
┌────────────────────────────┐
│  PostgreSQL Primary (Write)│
└───────────┬────────────────┘
            │
    ┌───────┴─────────┐
    ↓                 ↓
┌─────────┐      ┌───────────────┐
│Replica  │      │  Redis Cache  │ 👈 NEW!
│ (Read)  │      │  - Leaderboard│
└─────────┘      │  - Hot battles│
                 └───────────────┘

Worker:
  PostgreSQL → Redis (every 1 min)
```

**Cache Strategy:**
```python
# backend/app/services/leaderboard_service.py
class LeaderboardService:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis

    async def get_leaderboard(self) -> List[ModelStats]:
        # 1. Check cache
        cached = await self.redis.get("leaderboard:latest")
        if cached:
            return json.loads(cached)

        # 2. Query DB
        rows = await self.db.fetch_all("""
            SELECT * FROM model_stats
            WHERE vote_count >= 5
            ORDER BY elo_score DESC
            LIMIT 100
        """)

        # 3. Cache for 5 minutes
        await self.redis.setex("leaderboard:latest", 300, json.dumps(rows))

        return rows
```

**Capacity:**
- Handles: 1,000-10,000 QPS
- Cost: $500-1,000/month

---

### Phase 4: Hypergrowth (10,000+ QPS)

```
              ┌─────────────┐
              │API Gateway  │
              └──────┬──────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │  PG #1   │ │  PG #2   │ │  PG #3   │
  │session_id│ │session_id│ │session_id│
  │% 3 = 0   │ │% 3 = 1   │ │% 3 = 2   │
  └──────────┘ └──────────┘ └──────────┘
```

**Sharding by session_id:**
```python
# backend/app/db_router.py
class ShardedDatabase:
    def __init__(self):
        self.shards = [
            create_pool(SHARD_0_URL),
            create_pool(SHARD_1_URL),
            create_pool(SHARD_2_URL)
        ]

    def get_shard(self, session_id: str):
        shard_id = int(hashlib.md5(session_id.encode()).hexdigest(), 16) % len(self.shards)
        return self.shards[shard_id]

    async def execute(self, session_id: str, query: str, *args):
        shard = self.get_shard(session_id)
        return await shard.execute(query, *args)

# Usage (no code change in repositories!)
await db.execute(session_id, "INSERT INTO battles ...")
```

**Capacity:**
- Handles: 10,000+ QPS
- Cost: $2,000-5,000/month

---

## Implementation Guide

### 1. Alembic Migration

```python
# backend/alembic/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Create Date: 2025-01-21
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # sessions
    op.create_table('sessions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('last_active_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_created_at', 'sessions', ['created_at'], postgresql_ops={'created_at': 'DESC'})

    # battles
    op.create_table('battles',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('battle_id', sa.String(length=50), nullable=False),
        sa.Column('session_id', sa.String(length=50), nullable=False),
        sa.Column('left_model_id', sa.String(length=255), nullable=False),
        sa.Column('right_model_id', sa.String(length=255), nullable=False),
        sa.Column('conversation', sa.dialects.postgresql.JSONB(), nullable=False, server_default="'[]'::jsonb"),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='ongoing'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('battle_id'),
        sa.CheckConstraint("status IN ('ongoing', 'voted', 'abandoned')", name='battles_status_check')
        # Note: No FK constraint (ADR-001) - application-level referential integrity
    )
    op.create_index('idx_battles_session_id', 'battles', ['session_id'])
    op.create_index('idx_battles_status', 'battles', ['status'])
    op.create_index('idx_battles_session_status', 'battles', ['session_id', 'status'])

    # votes
    op.create_table('votes',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('vote_id', sa.String(length=50), nullable=False),
        sa.Column('battle_id', sa.String(length=50), nullable=False),
        sa.Column('session_id', sa.String(length=50), nullable=False),
        sa.Column('vote', sa.String(length=20), nullable=False),
        sa.Column('left_model_id', sa.String(length=255), nullable=False),
        sa.Column('right_model_id', sa.String(length=255), nullable=False),
        sa.Column('processing_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('processed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('voted_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vote_id'),
        sa.UniqueConstraint('battle_id'),
        sa.CheckConstraint("vote IN ('left_better', 'right_better', 'tie', 'both_bad')", name='votes_vote_check'),
        sa.CheckConstraint("processing_status IN ('pending', 'processed', 'failed')", name='votes_processing_status_check')
        # Note: No FK constraints (ADR-001) - application-level CASCADE deletion
    )
    op.create_index('idx_votes_processing_status', 'votes', ['processing_status'])
    op.create_index('idx_votes_session_id', 'votes', ['session_id'])
    op.create_index('idx_votes_voted_at', 'votes', ['voted_at'])

    # model_stats
    op.create_table('model_stats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('model_id', sa.String(length=255), nullable=False),
        sa.Column('elo_score', sa.Integer(), nullable=False, server_default='1500'),
        sa.Column('elo_ci', sa.Float(), nullable=False, server_default='200.0'),
        sa.Column('vote_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('win_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('loss_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tie_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('win_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('organization', sa.String(length=255), nullable=False),
        sa.Column('license', sa.String(length=50), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_id')
    )
    op.create_index('idx_model_stats_elo_score', 'model_stats', ['elo_score'], postgresql_ops={'elo_score': 'DESC'})
    op.create_index('idx_model_stats_vote_count', 'model_stats', ['vote_count'], postgresql_ops={'vote_count': 'DESC'})

    # worker_status
    op.create_table('worker_status',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('worker_name', sa.String(length=100), nullable=False),
        sa.Column('last_run_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='idle'),
        sa.Column('votes_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('worker_name')
    )

def downgrade():
    op.drop_table('worker_status')
    op.drop_table('model_stats')
    op.drop_table('votes')
    op.drop_table('battles')
    op.drop_table('sessions')
```

### 2. Database Connection

```python
# backend/app/db.py
from databases import Database

DATABASE_URL = "postgresql://user:pass@localhost/llmbattler"

database = Database(DATABASE_URL)

async def get_db():
    return database
```

### 3. Initial Model Stats

```python
# backend/scripts/seed_models.py
import asyncio
from app.db import database

async def seed_models():
    """Seed initial model_stats from config/models.yaml"""
    models = [
        {"model_id": "gpt-4o-mini", "organization": "OpenAI", "license": "proprietary"},
        {"model_id": "claude-3.5-sonnet", "organization": "Anthropic", "license": "proprietary"},
        {"model_id": "llama-3.1-8b", "organization": "Meta", "license": "open-source"},
    ]

    for model in models:
        await database.execute("""
            INSERT INTO model_stats (model_id, organization, license)
            VALUES ($1, $2, $3)
            ON CONFLICT (model_id) DO NOTHING
        """, model["model_id"], model["organization"], model["license"])

    print(f"Seeded {len(models)} models")

if __name__ == "__main__":
    asyncio.run(seed_models())
```

---

## Summary

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Database** | PostgreSQL only | 10 QPS doesn't need MongoDB, simpler ops |
| **Schema** | Relational + JSONB | Structured data + flexible conversation |
| **Partitioning** | session_id | Natural sharding key, 1 session = 1 shard |
| **Denormalization** | votes.model_ids | Avoid N+1 queries in worker |
| **Status Tracking** | processing_status | Accurate worker progress, retry safe |
| **Abstraction** | Repository pattern | Easy to replace DB, testable |
| **Scalability** | Phase-based upgrades | Start simple, scale on demand |

### When to Scale

| Trigger | Action | Timeline |
|---------|--------|----------|
| DB CPU > 70% | Add read replicas | Phase 2 (100 QPS) |
| Leaderboard slow | Add Redis cache | Phase 3 (1,000 QPS) |
| Storage > 1 TB | Archive old sessions | Anytime |
| Single DB limit | Horizontal sharding | Phase 4 (10,000 QPS) |
| Global users | Multi-region | Phase 5 (100,000 QPS) |

### Next Steps

1. ✅ Run Alembic migration
2. ✅ Seed initial model_stats
3. ✅ Implement repositories
4. ✅ Build API endpoints
5. ⏳ Monitor and scale

---

**Related Documents:**
- [ADR-001: No Foreign Keys](./ADR_001-No_Foreign_Keys.md) - Application-level referential integrity
- [001_BATTLE_MVP.md](../FEATURES/001_BATTLE_MVP.md) - Battle feature spec
- [002_LEADERBOARD_MVP.md](../FEATURES/002_LEADERBOARD_MVP.md) - Leaderboard spec
- [00_ROADMAP.md](../00_ROADMAP.md) - Project roadmap

**Last Updated:** 2025-01-21

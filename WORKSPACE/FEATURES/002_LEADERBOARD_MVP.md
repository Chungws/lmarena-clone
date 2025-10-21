# Feature: Leaderboard - MVP

**Status:** In Progress (Phase 2.2 - Infrastructure Complete)
**Priority:** High (MVP Core Feature)
**Estimated Time:** 1-2 weeks

---

## Overview

Display ELO-based rankings for all models based on user votes collected from battle mode. Leaderboard shows fair model comparisons using statistical rankings with confidence intervals.

**Goals:**
- Transparent model rankings based on real user votes
- ELO rating system for fair comparison across different match counts
- Fast leaderboard queries (PostgreSQL with strategic indexes)
- Accurate worker aggregation with retry-safe status tracking

---

## Architecture

```
PostgreSQL (single database)
  ├── votes (pending)
  ↓
Worker (hourly cron)
  - Read pending votes
  - Calculate ELO ratings
  - Update model_stats
  - Mark votes as processed
  ↓
PostgreSQL (model_stats updated)
  ↓
Backend API
  ↓
Frontend (Leaderboard UI)
```

**Database Strategy** (see [DATABASE_DESIGN.md](../ARCHITECTURE/DATABASE_DESIGN.md)):
- **PostgreSQL only** (no MongoDB)
- Worker reads from `votes` table (filtering by `processing_status = 'pending'`)
- **Denormalized votes:** `left_model_id` and `right_model_id` stored in votes (avoids N+1 queries)
- **Status tracking:** `processing_status` field for retry safety (pending → processed/failed)

---

## Design Decisions

### Worker Scheduling
**Decision:** Hourly execution with configurable interval
- **Default:** Run every hour at :00 (e.g., 00:00, 01:00, 02:00, ...)
- **Timezone:** UTC
- **Scheduler:** APScheduler
- **Configuration:** Interval configurable via environment variable (e.g., `WORKER_INTERVAL_HOURS=1`)
- Store execution metadata in `worker_status` table

### Confidence Interval Calculation
**Decision:** Bradley-Terry Model (Option B)
- Formula: `CI = 1.96 * SE` where `SE = 400 / sqrt(n)`
- 95% confidence interval using standard error
- More statistically accurate than simple heuristics
- Default CI = 200.0 when vote_count = 0

```python
def calculate_ci(vote_count: int) -> float:
    """Calculate 95% CI using Bradley-Terry model"""
    if vote_count == 0:
        return 200.0
    se = 400 / math.sqrt(vote_count)
    ci = 1.96 * se
    return round(ci, 1)
```

### Minimum Vote Requirement
**Decision:** Minimum 5 votes to appear on leaderboard
- Models with < 5 votes are excluded from leaderboard display
- Prevents unreliable rankings from insufficient data
- Note: Will be upgraded with more sophisticated criteria in future (e.g., Bayesian rating)

### Vote Denormalization Strategy
**Decision:** Store model_ids in votes table
- **Problem:** Worker needs model IDs to calculate ELO, but querying battles table for each vote causes N+1 queries
- **Solution:** Denormalize `left_model_id` and `right_model_id` into votes table
- **Trade-off:** Slight data redundancy for significant performance gain

**Without Denormalization (N+1 queries):**
```python
votes = await db.fetch_all("SELECT * FROM votes WHERE processing_status = 'pending'")
for vote in votes:
    battle = await db.fetch_one("SELECT * FROM battles WHERE battle_id = $1", vote["battle_id"])
    # N+1 queries! (1 + N)
```

**With Denormalization (single query):**
```python
votes = await db.fetch_all("SELECT * FROM votes WHERE processing_status = 'pending'")
for vote in votes:
    # model_ids already in vote! (1 query)
    winner = vote["left_model_id"] if vote["vote"] == "left_better" else ...
```

### Processing Status Tracking
**Decision:** Use `processing_status` field instead of timestamp
- **Field:** `processing_status` with values: 'pending', 'processed', 'failed'
- **Why not timestamp?** Timestamp-based tracking (e.g., `voted_at > last_run_at`) has race conditions and requires careful timezone handling
- **Benefits:**
  - Retry-safe: Failed votes can be retried without duplicate processing
  - Clear state: Easy to identify pending, completed, and failed votes
  - Debugging: Error messages stored in `error_message` field

### Database Connection (Worker)
**Decision:** Shared database module with separate connection pools
```python
# shared/src/llmbattler_shared/database.py
# Central database code shared by backend and worker

# Backend database (higher concurrency for API requests)
backend_engine, backend_session_maker = _create_engine_and_session_maker(
    pool_size=settings.postgres_pool_size,      # 5
    max_overflow=settings.postgres_max_overflow, # 5 (total: 10)
)

# Worker database (lower concurrency for batch operations)
worker_engine, worker_session_maker = _create_engine_and_session_maker(
    pool_size=settings.worker_pool_size,        # 2
    max_overflow=settings.worker_max_overflow,  # 3 (total: 5)
    pool_timeout=settings.worker_pool_timeout,  # 10 seconds
)
```
- **Why shared module:** Eliminates code duplication, centralized configuration
- **Separate engines:** Backend and worker use different connection pools with appropriate sizing
- **Re-export pattern:** Both `backend/database.py` and `worker/database.py` re-export from shared
- **Note:** Worker uses ONLY PostgreSQL (no MongoDB)

### Error Logging (Worker)
**Decision:** Shared logging module with Python logging to stdout
```python
# shared/src/llmbattler_shared/logging_config.py
# Central logging configuration shared by backend and worker

def setup_logging(logger_name: str = "llmbattler") -> logging.Logger:
    """Setup logging with stdout handler and standardized format"""
    # Format: [YYYY-MM-DD HH:MM:SS] [LEVEL] message
    # LOG_LEVEL environment variable support (default: INFO)
```
- **Why shared module:** Consistent logging across backend and worker
- **Re-export pattern:** Both `backend/main.py` and `worker/logging_config.py` use shared
- **Log levels:** INFO (normal operations), ERROR (failures)
- **Docker-compatible:** Logs to stdout for container log collection

---

## Implementation Phases

### Phase 2.1: PostgreSQL Schema ✅

**Tasks:**
- [x] Create PostgreSQL tables (already in DATABASE_DESIGN.md)
  - [x] `sessions` table
  - [x] `battles` table
  - [x] `votes` table (with denormalized model_ids and processing_status)
  - [x] `model_stats` table (elo_score, elo_ci, vote_count, win_rate, etc.)
  - [x] `worker_status` table
- [x] Create Alembic migration (based on DATABASE_DESIGN.md)
- [x] Add indexes for fast queries (elo_score, vote_count, processing_status)
- [x] Write tests for schema

**Schema Reference:** See [DATABASE_DESIGN.md](../ARCHITECTURE/DATABASE_DESIGN.md) for complete schema

**Completed:** 2025-01-21 (Phase 2.1 완료)

---

### Phase 2.2: Worker - ELO Calculation

**Tasks:**
- [x] Set up worker project structure (`worker/src/llmbattler_worker/`) - **PR #24 (2025-10-21)** ✅
- [x] Setup database connection - **PR #24 (2025-10-21)** ✅
  - [x] PostgreSQL async client (SQLAlchemy AsyncSession)
  - [x] Connection pooling configuration (pool_size=2, max_overflow=3, timeout=10s)
  - [x] **Shared database module** (`llmbattler_shared.database`) with separate engines for backend/worker
  - [x] **Code deduplication:** Backend 69→21 lines, Worker 60→15 lines (72-75% reduction)
- [x] Setup logging (Python logging to stdout) - **PR #24 (2025-10-21)** ✅
  - [x] **Shared logging module** (`llmbattler_shared.logging_config`) for consistent logging
  - [x] **Package-level logging pattern:** Backend/Worker inherit from package logger
  - [x] **Code deduplication:** Worker logging 64→12 lines (81% reduction)
- [x] Create vote aggregation script - **PR #27 (2025-10-21)** ✅
  - [x] Read pending votes from PostgreSQL (`processing_status = 'pending'`)
  - [x] Calculate ELO ratings using vote results
  - [x] **Calculate confidence intervals using Bradley-Terry model** (SE = 400/sqrt(n), CI = 1.96 * SE)
  - [x] Update `model_stats` in PostgreSQL
  - [x] **Mark votes as processed** (`processing_status = 'processed'`, `processed_at = NOW()`)
  - [x] **Handle errors:** Mark failed votes with `processing_status = 'failed'`, store error in `error_message`
  - [x] **Update `worker_status` table with execution metadata** - **PR #28 (2025-10-21)** ✅
- [x] Implement ELO calculation algorithm - **PR #27 (2025-10-21)** ✅
  - [x] Use standard ELO formula (K-factor = 32, Initial ELO = 1500)
  - [x] Handle ties appropriately (score = 0.5)
  - [x] **Handle "both_bad" votes (score = 0.25 for both models)**
- [x] Add scheduler (APScheduler) - **PR #28 (2025-10-21)** ✅
  - [x] **Default: Run every hour at :00 (UTC)** (already in main.py)
  - [x] **Configurable interval via WORKER_INTERVAL_HOURS environment variable** (already in main.py)
  - [x] **Integrate with ELOAggregator** (connect scheduler to aggregation logic) - **PR #28 (2025-10-21)** ✅
  - [x] **Store last run timestamp in PostgreSQL** (`worker_status` table) - **PR #28 (2025-10-21)** ✅
- [x] Add error handling and logging - **PR #27 (2025-10-21)** ✅
  - [x] Log aggregation start/complete
  - [x] Log votes processed and ELO updates
  - [x] Handle database connection errors
  - [x] Handle invalid vote types and other errors
- [x] Write tests for ELO calculation and CI calculation - **PR #27 (2025-10-21)** ✅
  - [x] 17 unit tests for ELO calculator (win/loss/tie/both_bad, CI calculation)
  - [x] 7 integration tests for ELO aggregator (vote processing, error handling)
  - [x] **4 integration tests for scheduler integration** (worker_status tracking) - **PR #28 (2025-10-21)** ✅

**ELO Formula:**
```python
# Standard ELO calculation
INITIAL_ELO = 1500
K_FACTOR = 32

def calculate_elo(rating_a, rating_b, result, k=K_FACTOR):
    """
    Calculate new ELO rating for model A

    Args:
        rating_a: Current ELO rating of model A
        rating_b: Current ELO rating of model B
        result: Score for model A (0.0 to 1.0)
                - 1.0 = A wins
                - 0.5 = tie
                - 0.25 = both_bad
                - 0.0 = B wins
        k: K-factor (rating sensitivity)

    Returns:
        float: New ELO rating for model A
    """
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    new_rating_a = rating_a + k * (result - expected_a)
    return new_rating_a

def get_score_from_vote(vote: str, is_left: bool) -> float:
    """
    Convert vote to ELO score for a specific model

    Args:
        vote: "left_better", "right_better", "tie", "both_bad"
        is_left: True if calculating for left model, False for right

    Returns:
        float: Score (S) for ELO calculation
    """
    if vote == "both_bad":
        return 0.25  # Small penalty for both models (LM Arena approach)
    elif vote == "tie":
        return 0.5
    elif (vote == "left_better" and is_left) or \
         (vote == "right_better" and not is_left):
        return 1.0
    else:
        return 0.0
```

**Worker Implementation Reference:**
See [DATABASE_DESIGN.md - Worker Flow](../ARCHITECTURE/DATABASE_DESIGN.md#2-worker-flow-elo-aggregation) for complete implementation

---

### Phase 2.3: Backend - Leaderboard API

**Tasks:**
- [ ] Setup PostgreSQL connection (already configured for battles/votes)
  - [ ] Use same Database client as Battle API
- [ ] Implement `GET /api/leaderboard` endpoint
  - [ ] Query PostgreSQL `model_stats` table
  - [ ] **Filter out models with < 5 votes** (minimum vote requirement)
  - [ ] Support sorting (by score, votes, organization)
  - [ ] Support filtering (by category - optional for MVP)
  - [ ] Return rankings with metadata (total models, total votes, last updated)
- [ ] Add pagination (optional for MVP)
- [ ] Write tests for leaderboard API (including minimum vote filter)

**API Spec:**
```
GET /api/leaderboard?sort_by=elo_score&order=desc

Response:
{
  "leaderboard": [
    {
      "rank": 1,
      "model_id": "gpt-4o",
      "model_name": "GPT-4o",
      "elo_score": 1654,
      "elo_ci": 12.3,
      "vote_count": 1234,
      "win_rate": 0.68,
      "organization": "OpenAI",
      "license": "proprietary"
    },
    {
      "rank": 2,
      "model_id": "claude-3.5-sonnet",
      "model_name": "Claude 3.5 Sonnet",
      "elo_score": 1632,
      "elo_ci": 15.7,
      "vote_count": 987,
      "win_rate": 0.64,
      "organization": "Anthropic",
      "license": "proprietary"
    }
  ],
  "metadata": {
    "total_models": 12,
    "total_votes": 5432,
    "last_updated": "2025-01-20T15:00:00Z"
  }
}
```

---

### Phase 2.4: Frontend - Leaderboard UI ✅

**Status:** Completed - **PR #TBD (2025-10-21)**

**Tasks:**
- [x] Create `/leaderboard` page (Next.js App Router)
- [x] Implement leaderboard table
  - [x] Columns: Rank, Model Name, Score (ELO), 95% CI, Votes, Win Rate, Organization, License
  - [x] Use shadcn/ui Table component
  - [x] Add sorting functionality (ELO Score, Vote Count, Organization)
  - [x] Add search/filter by model name, ID, and organization
- [x] Display metadata (Total Votes, Total Models, Last Updated with relative time)
- [x] Add responsive design (mobile-friendly with horizontal scroll)
- [x] Add loading and error states

**Implementation Details:**
- Created TypeScript types (`_types.ts`)
- API service layer (`service.ts`)
- Custom React hook (`use-leaderboard.ts`) with sorting and client-side filtering
- Leaderboard client component with shadcn/ui components (Table, Input, Select, Badge)
- Dynamic Rank calculation after sorting
- RSC pattern: `page.tsx` (server) + `leaderboard-client.tsx` (client)

**UI Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Leaderboard                                         │
│ Total Votes: 5,432 | Models: 12 | Updated: 1h ago  │
├─────────────────────────────────────────────────────┤
│ Search: [__________] Sort by: [Score ▼]            │
├──────┬─────────────────┬───────┬─────┬───────┬─────┤
│ Rank │ Model           │ Score │ CI  │ Votes │ Org │
├──────┼─────────────────┼───────┼─────┼───────┼─────┤
│  1   │ GPT-4o          │ 1654  │ ±12 │ 1234  │ ... │
│  2   │ Claude 3.5      │ 1632  │ ±16 │  987  │ ... │
│ ...  │ ...             │ ...   │ ... │  ...  │ ... │
└──────┴─────────────────┴───────┴─────┴───────┴─────┘
```

---

### Phase 2.5: Frontend - API Integration

**Tasks:**
- [ ] Create API client service (`src/lib/api/leaderboard.ts`)
  - [ ] `getLeaderboard(sortBy?, order?)`
- [ ] Create custom hook `useLeaderboard()`
- [ ] Handle loading and error states
- [ ] Add TypeScript types for API responses

---

## Data Models

### PostgreSQL Tables

See complete schema in [DATABASE_DESIGN.md](../ARCHITECTURE/DATABASE_DESIGN.md)

**votes (with denormalization):**
```typescript
interface Vote {
  id: number;
  vote_id: string;
  battle_id: string;             // UNIQUE (1:1)
  session_id: string;
  vote: 'left_better' | 'right_better' | 'tie' | 'both_bad';

  // Denormalized fields (avoid N+1 queries)
  left_model_id: string;
  right_model_id: string;

  // Worker processing status
  processing_status: 'pending' | 'processed' | 'failed';
  processed_at: Date | null;
  error_message: string | null;

  voted_at: Date;
}
```

**model_stats:**
```typescript
interface ModelStats {
  id: number;
  model_id: string;
  elo_score: number;
  elo_ci: number;  // 95% confidence interval
  vote_count: number;
  win_count: number;
  loss_count: number;
  tie_count: number;
  win_rate: number;
  organization: string;
  license: string;
  updated_at: Date;
}
```

**worker_status:**
```typescript
interface WorkerStatus {
  id: number;
  worker_name: string;           // e.g., "elo_aggregator"
  last_run_at: Date;
  status: 'idle' | 'running' | 'success' | 'failed';
  votes_processed: number;
  error_message: string | null;
}
```

---

## Testing Strategy

**Worker:**
- Unit tests for ELO calculation logic (including both_bad handling)
- Unit tests for CI calculation (Bradley-Terry model)
- Integration tests for vote aggregation
- Test cases: new votes, ties, both_bad, edge cases (0 votes), status tracking (pending → processed/failed)

**Backend:**
- Unit tests for leaderboard query logic
- Test cases: sorting, filtering, empty results, minimum vote requirement (< 5 votes)

**Frontend:**
- Playwright MCP for UI verification
  1. Verify leaderboard table renders
  2. Check sorting functionality
  3. Verify search/filter works

**Test Data Generation:**
- Use `scripts/seed_test_data.py` to generate sessions and battles in PostgreSQL
- Insert votes with `processing_status = 'pending'`
- Run worker manually to process votes and populate model_stats
- Verify leaderboard displays correctly with test data

---

## Success Criteria

- [ ] Worker runs hourly and calculates ELO ratings
- [ ] PostgreSQL stores accurate model statistics
- [ ] Denormalized votes table avoids N+1 queries
- [ ] processing_status field ensures retry-safe aggregation
- [ ] Leaderboard API returns sorted rankings
- [ ] Frontend displays leaderboard with all columns
- [ ] Confidence intervals displayed correctly
- [ ] Models with < 5 votes excluded from leaderboard
- [ ] At least 10 test battles conducted to populate leaderboard

---

## Future Enhancements (Post-MVP)

- Real-time leaderboard updates (WebSocket or SSE)
- Historical leaderboard snapshots (track ELO over time)
- Category-based rankings (coding, creative writing, etc.)
- Model comparison page (head-to-head stats)
- Export leaderboard data (CSV, JSON)
- Bayesian rating system (more sophisticated than minimum 5 votes)

---

**Related Documents:**
- [DATABASE_DESIGN.md](../ARCHITECTURE/DATABASE_DESIGN.md) - Complete database schema and worker implementation
- [001_BATTLE_MVP.md](./001_BATTLE_MVP.md) - Battle mode feature
- [00_ROADMAP.md](../00_ROADMAP.md) - Overall project roadmap
- [CONVENTIONS/backend/](../CONVENTIONS/backend/) - Backend conventions

**Last Updated:** 2025-10-21

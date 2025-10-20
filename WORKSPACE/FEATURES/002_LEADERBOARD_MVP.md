# Feature: Leaderboard - MVP

**Status:** Not Started
**Priority:** High (MVP Core Feature)
**Estimated Time:** 1-2 weeks

---

## Overview

Display ELO-based rankings for all models based on user votes collected from battle mode. Leaderboard shows fair model comparisons using statistical rankings with confidence intervals.

**Goals:**
- Transparent model rankings based on real user votes
- ELO rating system for fair comparison across different match counts
- Fast leaderboard queries (read-optimized PostgreSQL)

---

## Architecture

```
MongoDB (battles, votes)
    ↓
  Worker (hourly cron)
    - Read new votes from MongoDB
    - Calculate ELO ratings
    - Update PostgreSQL
    ↓
PostgreSQL (model_stats, leaderboards)
    ↓
Backend API
    ↓
Frontend (Leaderboard UI)
```

---

## Design Decisions

### Worker Scheduling
**Decision:** Hourly execution with configurable interval
- **Default:** Run every hour at :00 (e.g., 00:00, 01:00, 02:00, ...)
- **Timezone:** UTC
- **Scheduler:** APScheduler or system cron
- **Configuration:** Interval configurable via environment variable (e.g., `WORKER_INTERVAL_HOURS=1`)
- Store last run timestamp in PostgreSQL `worker_status` table

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

### Database Connections (Worker)
**Decision:** Async connections to both databases
- **MongoDB (Motor):** Read battles and votes
- **PostgreSQL (asyncpg):** Write model_stats
- Connection pooling for efficiency
- Same configuration as Backend (see 001_BATTLE_MVP.md)

### Error Logging (Worker)
**Decision:** Python logging to stdout
- Same strategy as Backend
- Log levels: INFO (aggregation start/complete), ERROR (failures)
- Key events: Worker start, votes processed, ELO updates, database errors

---

## Implementation Phases

### Phase 2.1: PostgreSQL Schema

**Tasks:**
- [ ] Create PostgreSQL tables
  - [ ] `model_stats` table (model_id, elo_score, elo_ci, vote_count, win_rate, organization, license, updated_at)
  - [ ] `leaderboards` table (optional, for historical snapshots)
- [ ] Create Alembic migration (auto-generate)
- [ ] Add indexes for fast queries (elo_score, vote_count)
- [ ] Write tests for schema

**Schema:**
```sql
-- model_stats table
CREATE TABLE model_stats (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(255) UNIQUE NOT NULL,
    elo_score INTEGER DEFAULT 1500,
    elo_ci FLOAT,  -- 95% confidence interval
    vote_count INTEGER DEFAULT 0,
    win_count INTEGER DEFAULT 0,
    loss_count INTEGER DEFAULT 0,
    tie_count INTEGER DEFAULT 0,
    win_rate FLOAT,
    organization VARCHAR(255),
    license VARCHAR(50),  -- 'proprietary', 'open-source', etc.
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_elo_score ON model_stats(elo_score DESC);
CREATE INDEX idx_vote_count ON model_stats(vote_count DESC);
```

---

### Phase 2.2: Worker - ELO Calculation

**Tasks:**
- [ ] Set up worker project structure (`worker/app/`)
- [ ] Setup database connections
  - [ ] MongoDB async client (Motor) for reading battles/votes
  - [ ] PostgreSQL async client (asyncpg) for writing model_stats
  - [ ] Connection pooling configuration
- [ ] Setup logging (Python logging to stdout)
- [ ] Create MongoDB → PostgreSQL aggregation script
  - [ ] Read new votes from MongoDB (since last run timestamp)
  - [ ] Retrieve battle documents to get model positions
  - [ ] Calculate ELO ratings using vote results
  - [ ] **Calculate confidence intervals using Bradley-Terry model** (SE = 400/sqrt(n), CI = 1.96 * SE)
  - [ ] Update `model_stats` in PostgreSQL
  - [ ] Update last run timestamp in `worker_status` table
- [ ] Implement ELO calculation algorithm
  - [ ] Use standard ELO formula (K-factor = 32, Initial ELO = 1500)
  - [ ] Handle ties appropriately
  - [ ] **Handle "both_bad" votes (score = 0.25 for both models)**
  - [ ] Use model positions from battle document to determine vote outcome
- [ ] Add scheduler (APScheduler or cron)
  - [ ] **Default: Run every hour at :00 (UTC)**
  - [ ] **Configurable interval via WORKER_INTERVAL_HOURS environment variable**
  - [ ] Store last run timestamp in PostgreSQL (`worker_status` table)
- [ ] Add error handling and logging
  - [ ] Log aggregation start/complete
  - [ ] Log votes processed and ELO updates
  - [ ] Handle database connection errors
- [ ] Write tests for ELO calculation and CI calculation

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

def get_score_from_vote(vote: str, position: str) -> float:
    """
    Convert vote to ELO score

    Args:
        vote: "left_better", "right_better", "tie", "both_bad"
        position: "left" or "right"

    Returns:
        float: Score (S) for ELO calculation
    """
    if vote == "both_bad":
        return 0.25  # Small penalty for both models (LM Arena approach)
    elif vote == "tie":
        return 0.5
    elif (vote == "left_better" and position == "left") or \
         (vote == "right_better" and position == "right"):
        return 1.0
    else:
        return 0.0
```

---

### Phase 2.3: Backend - Leaderboard API

**Tasks:**
- [ ] Setup PostgreSQL connection (async with asyncpg)
  - [ ] Use same connection configuration as Backend (see 001_BATTLE_MVP.md)
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

### Phase 2.4: Frontend - Leaderboard UI

**Tasks:**
- [ ] Create `/leaderboard` page (Next.js App Router)
- [ ] Implement leaderboard table
  - [ ] Columns: Rank, Model Name, Score (ELO), 95% CI, Votes, Organization, License
  - [ ] Use shadcn/ui Table component
  - [ ] Add sorting functionality (client-side or server-side)
  - [ ] Add search/filter by model name
- [ ] Display metadata (Total Votes, Total Models, Last Updated)
- [ ] Add responsive design (mobile-friendly)
- [ ] Add loading and error states

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

---

## Testing Strategy

**Worker:**
- Unit tests for ELO calculation logic (including both_bad handling)
- Unit tests for CI calculation (Bradley-Terry model)
- Integration tests for MongoDB → PostgreSQL aggregation
- Test cases: new votes, ties, both_bad, edge cases (0 votes), position randomization

**Backend:**
- Unit tests for leaderboard query logic
- Test cases: sorting, filtering, empty results, minimum vote requirement (< 5 votes)

**Frontend:**
- Playwright MCP for UI verification
  1. Verify leaderboard table renders
  2. Check sorting functionality
  3. Verify search/filter works

**Test Data Generation:**
- Use `scripts/seed_test_data.py` to generate battles and votes in MongoDB
- Run worker manually to populate PostgreSQL with model_stats
- Verify leaderboard displays correctly with test data

---

## Success Criteria

- [ ] Worker runs hourly and calculates ELO ratings
- [ ] PostgreSQL stores accurate model statistics
- [ ] Leaderboard API returns sorted rankings
- [ ] Frontend displays leaderboard with all columns
- [ ] Confidence intervals displayed correctly
- [ ] At least 10 test battles conducted to populate leaderboard

---

## Future Enhancements (Post-MVP)

- Real-time leaderboard updates (WebSocket or SSE)
- Historical leaderboard snapshots (track ELO over time)
- Category-based rankings (coding, creative writing, etc.)
- Model comparison page (head-to-head stats)
- Export leaderboard data (CSV, JSON)

---

**Related Documents:**
- [00_ROADMAP.md](../00_ROADMAP.md) - Overall project roadmap
- [CONVENTIONS/backend/](../CONVENTIONS/backend/) - Backend conventions
- [001_BATTLE_MVP.md](./001_BATTLE_MVP.md) - Battle mode feature

**Last Updated:** 2025-10-20

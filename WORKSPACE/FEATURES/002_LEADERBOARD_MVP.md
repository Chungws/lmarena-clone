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
- [ ] Create MongoDB → PostgreSQL aggregation script
  - [ ] Read new votes from MongoDB (since last run)
  - [ ] Calculate ELO ratings using vote results
  - [ ] Calculate confidence intervals (95% CI)
  - [ ] Update `model_stats` in PostgreSQL
- [ ] Implement ELO calculation algorithm
  - [ ] Use standard ELO formula (K-factor = 32)
  - [ ] Handle ties appropriately
- [ ] Add scheduler (APScheduler or cron)
  - [ ] Run hourly
  - [ ] Store last run timestamp
- [ ] Write tests for ELO calculation

**ELO Formula:**
```python
# Standard ELO calculation
def calculate_elo(rating_a, rating_b, result, k=32):
    """
    result: 1.0 (A wins), 0.5 (tie), 0.0 (B wins)
    """
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    new_rating_a = rating_a + k * (result - expected_a)
    return new_rating_a
```

---

### Phase 2.3: Backend - Leaderboard API

**Tasks:**
- [ ] Implement `GET /api/leaderboard` endpoint
  - [ ] Query PostgreSQL `model_stats` table
  - [ ] Support sorting (by score, votes, organization)
  - [ ] Support filtering (by category - optional for MVP)
  - [ ] Return rankings with metadata
- [ ] Add pagination (optional for MVP)
- [ ] Write tests for leaderboard API

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
- Unit tests for ELO calculation logic
- Integration tests for MongoDB → PostgreSQL aggregation
- Test cases: new votes, ties, edge cases (0 votes)

**Backend:**
- Unit tests for leaderboard query logic
- Test cases: sorting, filtering, empty results

**Frontend:**
- Playwright MCP for UI verification
  1. Verify leaderboard table renders
  2. Check sorting functionality
  3. Verify search/filter works

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

**Last Updated:** 2025-01-20

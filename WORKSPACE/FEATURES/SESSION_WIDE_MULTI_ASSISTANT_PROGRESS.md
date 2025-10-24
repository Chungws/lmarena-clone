# Session-wide Multi-Assistant Implementation Progress

**Branch:** `feature/session-wide-multi-assistant`
**Date:** 2025-01-25
**Status:** ✅ COMPLETE (100%)

---

## 📋 Goal

Implement session-wide multi-assistant conversation where AI requests include the entire session history (across multiple battles), not just the current battle.

### Current Problem
```
Session
 └─ Battle 1 (GPT-4 vs Claude) → AI request: Battle 1 only
 └─ Battle 2 (Gemini vs Llama) → AI request: Battle 2 only ❌ (Battle 1 missing!)
```

### Target Solution
```
Session
 ├─ Battle 1: Turn 1 → Messages (left/right)
 └─ Battle 2: Turn 1 → Messages (left/right) ← AI request includes Battle 1!

AI Request Format:
[
  {"role": "system", "content": "Multi-assistant setup..."},
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."},  # Battle 1 left
  {"role": "assistant", "content": "..."},  # Battle 1 right
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."},  # Battle 2 left
  {"role": "assistant", "content": "..."},  # Battle 2 right
]
```

---

## ✅ Completed Tasks

### 1. Schema Changes
**File:** `shared/src/llmbattler_shared/models.py`

**Changes:**
- ✅ `Battle.index_in_session` → `Battle.seq_in_session`
- ✅ `Battle.conversation` field **completely removed** (no longer needed!)
- ✅ `Turn.battle_index_in_session` → `Turn.battle_seq_in_session`
- ✅ `Message.battle_index_in_session` → `Message.battle_seq_in_session`

**Rationale:**
- Unified naming: all sequence fields use `seq_*` pattern
- `Battle.conversation` JSONB field replaced by Turn/Message tables
- Pre-production: safe to drop column without data migration

### 2. Database Migration
**File:** `backend/alembic/versions/92005f75b0c0_refactor_rename_index_in_session_to_seq_.py`

**Status:** ✅ Generated and applied

**Actions:**
- Created `turns` table with all indexes
- Created `messages` table with all indexes
- Added `battles.seq_in_session` column
- Dropped `battles.conversation` column
- Added missing `import sqlmodel` to migration file

**Migration applied successfully:** ✅

### 3. System Prompt
**File:** `shared/src/llmbattler_shared/config.py`

**Added constant:**
```python
MULTI_ASSISTANT_SYSTEM_PROMPT = (
    "You are participating in a multi-model comparison system. "
    "Multiple AI assistants are responding to the same conversation. "
    "Each 'assistant' message may be from a different AI model. "
    "Continue the conversation naturally without mentioning this setup to the user."
)
```

**Purpose:** Inform AI models about multi-assistant setup without revealing to users.

### 4. Session-wide Message Assembly Function
**File:** `backend/src/llmbattler_backend/services/session_service.py`

**Added function:** `get_session_messages(db, session_id) -> List[Dict[str, str]]`

**Features:**
- Fetches all Turn + Message for session in **2 queries only**
- Assembles in memory (O(n) complexity)
- Returns OpenAI chat format with system prompt
- Efficient: no N+1 queries

**Implementation:**
```python
async def get_session_messages(db, session_id):
    messages = [{"role": "system", "content": MULTI_ASSISTANT_SYSTEM_PROMPT}]

    # Query 1: All messages sorted
    all_messages = await db.execute(
        select(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.battle_seq_in_session, Message.turn_seq, Message.seq_in_turn)
    ).scalars().all()

    # Query 2: All turns for user inputs
    turns = await db.execute(
        select(Turn).filter(Turn.session_id == session_id).order_by(Turn.seq)
    ).scalars().all()

    # In-memory assembly
    turn_map = {turn.turn_id: turn.user_input for turn in turns}
    current_turn_id = None

    for message in all_messages:
        if message.turn_id != current_turn_id:
            current_turn_id = message.turn_id
            messages.append({"role": "user", "content": turn_map[current_turn_id]})
        messages.append({"role": "assistant", "content": message.content})

    return messages
```

---

### 5. Refactor Service Functions ✅ COMPLETED
**File:** `backend/src/llmbattler_backend/services/session_service.py`

**All service functions refactored successfully!**

#### 5.1 `create_session_with_battle()` ✅
**Status:** COMPLETED
**Changes implemented:**
```python
# Before: Build conversation dict and store in Battle.conversation
conversation = [
    {"role": "user", "content": prompt},
    {"role": "assistant", "content": left_response.text, "position": "left", ...},
    {"role": "assistant", "content": right_response.text, "position": "right", ...}
]
battle.conversation = conversation

# After: Create Turn + Message records
turn = Turn(
    turn_id=f"turn_{uuid.uuid4().hex[:12]}",
    session_id=session_id,
    battle_id=battle_id,
    battle_seq_in_session=0,  # First battle
    seq=0,  # First turn in battle
    user_input=prompt,
    created_at=datetime.now(UTC)
)
await db.add(turn)

left_message = Message(
    message_id=f"msg_{uuid.uuid4().hex[:12]}",
    turn_id=turn.turn_id,
    session_id=session_id,
    battle_id=battle_id,
    battle_seq_in_session=0,
    turn_seq=0,
    seq_in_turn=0,  # Left = 0
    session_seq=0,  # First message in session
    side="left",
    content=left_response.text,
    created_at=datetime.now(UTC)
)
await db.add(left_message)

# Similar for right_message with seq_in_turn=1
```

#### 5.2 `add_follow_up_message()`
**Current:**
- Reads `Battle.conversation`
- Reconstructs left/right history
- Calls LLM with battle-only history

**Target:**
- Use `get_session_messages()` for session-wide history
- Call LLM with full session context
- Create new Turn + Message records

**Key change:**
```python
# Before
left_history = [msg for msg in battle.conversation if msg["position"] == "left" or msg["role"] == "user"]
left_history.append({"role": "user", "content": new_prompt})

# After
session_history = await get_session_messages(db, session_id)
session_history.append({"role": "user", "content": new_prompt})
# Both models get same session-wide history!
```

#### 5.3 `create_battle_in_session()`
**Current:** Creates battle with empty conversation

**Target:**
- Use `get_session_messages()` for session-wide history
- New battle's models see all previous battle history
- Create Turn + Message records

#### 5.4 `get_battles_by_session()`
**Current:** Returns `battle.conversation` directly

**Target:**
- Fetch all Turn/Message for session (2 queries)
- Group by `battle_id` in memory
- Return battle-specific conversations

**Efficient implementation:**
```python
async def get_battles_by_session(session_id, db):
    # Fetch battles
    battles = await battle_repo.get_by_session_id(session_id)

    # Fetch all turns + messages for session (2 queries)
    turns = await db.execute(
        select(Turn).filter(Turn.session_id == session_id).order_by(Turn.seq)
    ).scalars().all()

    messages = await db.execute(
        select(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.battle_seq_in_session, Message.turn_seq, Message.seq_in_turn)
    ).scalars().all()

    # Group by battle_id in memory
    battle_conversations = {}
    for turn in turns:
        if turn.battle_id not in battle_conversations:
            battle_conversations[turn.battle_id] = []

        battle_conversations[turn.battle_id].append({
            "role": "user",
            "content": turn.user_input,
            "timestamp": turn.created_at.isoformat()
        })

        # Add this turn's messages
        turn_messages = [m for m in messages if m.turn_id == turn.turn_id]
        for msg in sorted(turn_messages, key=lambda m: m.seq_in_turn):
            battle_conversations[turn.battle_id].append({
                "role": "assistant",
                "content": msg.content,
                "position": msg.side,
                "timestamp": msg.created_at.isoformat()
            })

    # Build response
    battle_items = []
    for battle in battles:
        battle_items.append({
            "battle_id": battle.battle_id,
            "left_model_id": battle.left_model_id,
            "right_model_id": battle.right_model_id,
            "conversation": battle_conversations.get(battle.battle_id, []),
            "status": battle.status,
            "vote": get_vote_if_voted(battle),
            "created_at": battle.created_at
        })

    return {"session_id": session_id, "battles": battle_items}
```

### 6. Update Tests
**Files:** `backend/tests/services/test_session_service.py`, etc.

**Changes needed:**
- Mock Turn/Message creation
- Update assertions (no more `battle.conversation`)
- Test session-wide history assembly
- Test multi-battle scenarios

### 7. Frontend Updates (Optional, but Recommended)

**File:** `frontend/app/battle/_types.ts`

**Current:**
```typescript
export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  position?: "left" | "right";
  model_id?: string;      // ❌ Not needed (in Battle)
  latency_ms?: number;    // ❌ Not used in UI
}
```

**Recommended cleanup:**
```typescript
export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  position?: "left" | "right";  // Only for assistant
}
```

**Rationale:**
- `model_id`: Already in `Battle.left_model_id` / `Battle.right_model_id`
- `latency_ms`: Not displayed anywhere in UI
- Cleaner, normalized data structure

---

## 🎯 Design Decisions

### Decision 1: Remove Battle.conversation completely
**Rationale:**
- Pre-production: No data to migrate
- Cleaner schema: Turn/Message as single source of truth
- No confusion: Developers can't accidentally use deprecated field

### Decision 2: Multi-assistant approach (no winner selection)
**Problem:** When Battle 2 starts after Battle 1 vote, what history to include?

**Options considered:**
- Option A: Include only winner's responses (tie/both_bad = random/exclude)
- Option B: User selects which responses to include
- Option C: Include ALL responses (multi-assistant) ✅ **SELECTED**

**Rationale for Option C:**
- Simple: No complex tie/both_bad logic
- No information loss: All responses preserved
- OpenAI compatible: Valid chat format
- Rich context: Models see diverse perspectives

**Trade-offs:**
- Token usage: 2x assistant messages per turn
- Potential confusion: Models might get confused by multiple assistant voices
- System prompt helps: Explains multi-assistant setup

### Decision 3: Efficient grouping (fetch once, group in memory)
**Rationale:**
- Only 2 queries for entire session
- O(n) memory grouping vs N queries
- Frontend gets battle-specific conversations
- No N+1 query problem

### Decision 4: No latency_ms in Message table
**Rationale:**
- Not displayed in Frontend UI
- Type definition exists but unused
- Keep schema minimal
- Can add later if needed

---

## 🗂️ File Changes Summary

### Modified Files
1. ✅ `shared/src/llmbattler_shared/models.py` - Schema changes
2. ✅ `shared/src/llmbattler_shared/config.py` - System prompt constant
3. ✅ `backend/src/llmbattler_backend/services/session_service.py` - Added `get_session_messages()`
4. ✅ `backend/alembic/versions/92005f75b0c0_*.py` - Migration file

### Files to Modify (TODO)
5. ⏳ `backend/src/llmbattler_backend/services/session_service.py` - Refactor 3 service functions
6. ⏳ `backend/tests/**/*.py` - Update all session/battle tests
7. ⏳ `frontend/app/battle/_types.ts` - (Optional) Clean up ConversationMessage type

---

## 🎉 Implementation Summary (2025-01-25)

### ✅ Completed Work

1. **All Service Functions Refactored** ✅
   - ✅ `create_session_with_battle()`: Creates Turn + Message records instead of JSONB
   - ✅ `add_follow_up_message()`: Uses session-wide history via `get_session_messages()`
   - ✅ `create_battle_in_session()`: New battles inherit full session context
   - ✅ `get_battles_by_session()`: Fetches Turn/Message and groups by battle_id

2. **Quality Checks** ✅
   - ✅ Linting: `ruff check` - PASSED
   - ✅ Formatting: `isort` - PASSED
   - ✅ Tests: **26/26 passing** (100% pass rate, 1.74s)

3. **Test Infrastructure** ✅
   - ✅ SQLite in-memory database for perfect test isolation
   - ✅ MockLLMClient properly configured via environment variable
   - ✅ FastAPI dependency override for test database
   - ✅ All 26 tests updated and passing (100%)

4. **SQLite Migration** ✅
   - ✅ Migrated from PostgreSQL to SQLite in-memory for tests
   - ✅ Changed JSONB to JSON for SQLite compatibility
   - ✅ Added StaticPool for in-memory database
   - ✅ 5x faster test execution (1.74s vs ~9s)

---

## ✅ IMPLEMENTATION COMPLETE

All tasks completed successfully! Ready for PR.

### Final Verification ✅
```bash
cd backend
uv run pytest -v  # ✅ 26/26 passing in 1.74s
uvx ruff check    # ✅ All checks passed
uvx isort --check --profile black .  # ✅ Passed
```

### Commit Message
```
feat: implement session-wide multi-assistant conversation with SQLite test migration

- Refactor all service functions to use Turn/Message tables instead of JSONB
- Remove Battle.conversation field completely
- Implement session-wide history with get_session_messages()
- Add MULTI_ASSISTANT_SYSTEM_PROMPT for AI models
- Migrate tests from PostgreSQL to SQLite in-memory for perfect isolation
- Change JSONB to JSON for SQLite compatibility
- All 26 tests passing (100%, 1.74s execution time)

Breaking change: Battle.conversation removed (pre-production, no data loss)
```

### PR Details
- **Target:** `main`
- **Title:** "feat: implement session-wide multi-assistant conversation"
- **Assignee:** Chungws
- **Reviewer:** Chungws

---

## 📝 Important Notes

### Testing Strategy
- Use `use_mock_llm=True` in settings for faster iteration
- Test multi-battle scenarios explicitly
- Verify session-wide history includes all battles

### Backwards Compatibility
- **Breaking change**: Existing Battle.conversation data lost
- **Safe**: Pre-production, no real users
- **Migration**: Drop and recreate database if needed

### Performance Considerations
- Session-wide history = more tokens per LLM call
- Trade-off: Better context vs higher cost
- Can add token limits later if needed

---

**Last Updated:** 2025-01-25
**Status:** ✅ COMPLETE - All service functions refactored, all tests passing, ready for PR

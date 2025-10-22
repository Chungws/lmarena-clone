# Session Management UI

## Overview

- **Goal:** Provide a UI for saving sessions and browsing past conversations in a sidebar, similar to ChatGPT
- **Background:**
  - Session functionality is currently implemented in the backend, but the frontend cannot view the session list
  - Users cannot revisit or continue past conversations
  - Anonymous users should be able to manage their own sessions through browser localStorage

## UI/UX Requirements

### Reference Images (LM Arena)
- `session.png`: Session list grouped by date in the sidebar
- `walkthrough-1.png` ~ `walkthrough-6.png`: Complete user flow

### Key Flows

1. **Click New Chat (walkthrough-1.png)**
   - Click "New Chat" button in the sidebar
   - Main area is initialized to an empty screen
   - Display "Ask anything..." placeholder in the bottom input field

2. **Send First Message (walkthrough-2.png)**
   - User enters and sends a message
   - Responses from Assistant A and B are displayed on both sides
   - Display Vote buttons at the bottom: "Left is Better", "Tie", "Both are bad", "Right is Better"
   - Display "Ask followup..." input field

3. **Send Additional Messages (walkthrough-3.png)**
   - Same models continue to answer
   - Conversation history accumulates in the scroll area

4. **Vote Button Hover Effects (walkthrough-4-1.png ~ walkthrough-4-4.png)**
   - "Left is Better" hover: Left card and button border turn green
   - "Tie" hover: Both cards and button border turn green
   - "Both are bad" hover: Both cards and button border turn red
   - "Right is Better" hover: Right card and button border turn green

5. **Submit Vote (walkthrough-5.png)**
   - Click Vote button reveals model names (Assistant A → model_name_1, Assistant B → model_name_2)
   - Vote buttons become disabled

6. **Continue Conversation After Vote (walkthrough-6.png)**
   - Can continue sending messages in the input field after voting
   - Existing conversation continues without starting a new battle
   - Vote becomes available again

7. **Sidebar Session List (session.png)**
   - Grouped by date: "Today", "Yesterday", "Previous 7 Days", "Previous 30 Days", etc.
   - Each session is displayed with the first message (title)
   - Click session to display its conversation content
   - Currently active session is highlighted

## Phase-by-Phase Implementation Plan

### Phase 1: Backend - Session List API

**Goal:** Implement APIs for retrieving session lists and battle lists for specific sessions

**Checklist:**
- [x] GET `/api/sessions` - Retrieve session list (user_id based)
  - Query params: `user_id` (optional, for anonymous users), `limit`, `offset`
  - Response: Session list (session_id, title, created_at, last_active_at)
  - Sort: `last_active_at DESC` (most recent activity)
- [x] GET `/api/sessions/{session_id}/battles` - Retrieve all battles for a specific session
  - Response: Battle list (battle_id, conversation, status, left_model_id, right_model_id)
  - Check vote information inclusion (when status === 'voted')
- [x] Modify POST `/api/sessions` - Add `user_id` parameter
  - Add optional `user_id` to request body
  - Save user_id when creating session
- [x] Implement `SessionRepository`
  - `get_sessions_by_user_id()` - Retrieve session list based on user_id
  - `get_battles_by_session_id()` - Retrieve battle list based on session_id
- [x] Tests
  - Session list retrieval test (empty list, multiple sessions)
  - Specific session battle retrieval test
  - user_id filtering test

**Estimated Time:** 1 day
**Status:** ✅ **Completed** (2025-10-23)

**Files Changed:**
- `backend/src/llmbattler_backend/api/sessions.py`
- `backend/src/llmbattler_backend/services/session_service.py`
- `backend/src/llmbattler_backend/repositories/session_repository.py`
- `backend/tests/api/test_sessions.py`
- `shared/src/llmbattler_shared/schemas.py` (Add SessionListResponse)

---

### Phase 2: Frontend - Sidebar Component Implementation

**Goal:** Develop sidebar component displaying session list

**Checklist:**
- [x] Update existing `Sidebar` component
  - "New Chat" button (already exists)
  - "Leaderboard" link (already exists)
  - Session list integration (completed)
- [x] Session list item component
  - Session title (first message)
  - Load corresponding session on click
  - Active session highlight
  - Hover effect
- [x] Responsive design
  - Mobile: Toggle sidebar with hamburger menu (already exists)
  - Desktop: Always displayed (already exists)
- [x] Utilize shadcn/ui components
  - `Button`, `ScrollArea`, `Separator`, etc.
- [x] Anonymous user ID management (Phase 3 integrated)
  - localStorage-based UUID generation
  - useUser hook
- [x] Battle service integration
  - Pass user_id when creating sessions

**Note:** Date grouping logic was skipped for MVP simplicity as requested by the user.

**Estimated Time:** 2 days
**Actual Time:** 1 day

**Status:** ✅ **Completed** (2025-10-23)

**Files Changed:**
- `frontend/components/sidebar.tsx` (modified)
- `frontend/components/sidebar/session-list.tsx` (new)
- `frontend/components/sidebar/session-item.tsx` (new)
- `frontend/lib/storage.ts` (new)
- `frontend/lib/hooks/use-user.ts` (new)
- `frontend/lib/services/session-service.ts` (new)
- `frontend/app/battle/service.ts` (modified)
- `frontend/app/battle/use-battle.ts` (modified)

---

### Phase 3: Frontend - Anonymous User ID Management

**Goal:** Generate and manage anonymous user IDs using localStorage

**Checklist:**
- [x] Anonymous user ID generation logic
  - Generate UUID v4
  - Save to localStorage (`llmbattler_user_id`)
  - Check on app load, generate if not present
- [x] Implement `useUser` hook
  - `userId` state management
  - `isAnonymous` flag
  - localStorage synchronization
- [x] Automatically include user_id in API requests
  - Modified battle service to pass user_id
  - Add user_id to all session creation requests

**Note:** This phase was integrated with Phase 2 implementation.

**Estimated Time:** 0.5 days
**Actual Time:** Integrated with Phase 2

**Status:** ✅ **Completed** (2025-10-23)

**Files Changed:**
- `frontend/lib/hooks/use-user.ts` (new)
- `frontend/lib/storage.ts` (new)
- `frontend/app/battle/service.ts` (modified - added user_id parameter)
- `frontend/app/battle/use-battle.ts` (modified - integrated useUser hook)

---

### Phase 4: Frontend - Session Context and API Integration

**Goal:** Implement session list loading and specific session selection functionality

**Checklist:**
- [x] Implement `SessionContext`
  - Global session list state management
  - Current active session state
  - Session list load function (refetchSessions)
  - Session select function (selectSession)
- [x] Implement `useSessionDetail` hook
  - API call: GET `/api/sessions/{session_id}/battles`
  - Load all battles for specific session
  - Restore conversation state
- [x] Modify Layout
  - Wrap with SessionProvider in `app/layout.tsx`
- [x] Update `session-list.tsx` to use SessionContext
  - Removed local state management
  - Use SessionContext for session list and active session

**Note:** `useSessionList` hook was not needed as SessionContext handles session list management directly. Date grouping logic was already skipped in Phase 2 for MVP simplicity.

**Estimated Time:** 2 days
**Actual Time:** 1 day

**Status:** ✅ **Completed** (2025-10-23)

**Files Changed:**
- `frontend/lib/contexts/session-context.tsx` (new)
- `frontend/lib/hooks/use-session-detail.ts` (new)
- `frontend/app/layout.tsx` (modified)
- `frontend/components/sidebar/session-list.tsx` (modified)

---

### Phase 5: Frontend - Battle UI Enhancement (Vote Hover Effects)

**Goal:** Implement card border change effects when hovering over Vote buttons

**Checklist:**
- [x] Separate Vote button component
  - Create `VoteButton` component
  - Manage hover state
- [x] Link hover effect to card component
  - "Left is Better" hover → left card green border
  - "Right is Better" hover → right card green border
  - "Tie" hover → both cards green border
  - "Both are bad" hover → both cards red border
- [x] Add CSS animations
  - Use `transition-colors`
  - Smooth border color transitions
- [x] Accessibility improvements
  - Support keyboard navigation
  - Add ARIA labels

**Estimated Time:** 1 day
**Actual Time:** 1 day

**Status:** ✅ **Completed** (2025-10-23)

**Files Changed:**
- `frontend/app/battle/battle-client.tsx` (modified)
- `frontend/components/battle/vote-button.tsx` (new)
- `frontend/components/battle/response-card.tsx` (new)

---

### Phase 6: Integration and End-to-End Testing

**Goal:** Integrate and test complete flow

**Checklist:**
- [ ] End-to-End flow test
  - New Chat → Send message → Vote → Continue conversation → Select from session list
- [ ] Playwright MCP tests (UI changes)
  - Verify sidebar rendering
  - Verify session click action
  - Verify vote hover effects
- [ ] Error handling
  - Fallback UI on API failure
  - Retry on network errors
- [ ] Performance optimization
  - Session list infinite scroll (optional)
  - Apply React.memo
- [ ] Documentation update
  - Mark FEATURES/004_SESSION_MANAGEMENT.md checklist as complete
  - Update README.md (new feature description)

**Estimated Time:** 1 day

**Files Changed:**
- All previous files
- `README.md`

---

## Tech Stack

### Backend
- **FastAPI** - Add session list API
- **SQLModel** - Session, Battle models (already implemented)
- **PostgreSQL** - Store session and battle data

### Frontend
- **Next.js 15** - App Router and React Server Components
- **React Context API** - Global session state management
- **localStorage** - Store anonymous user ID
- **shadcn/ui** - UI components (Sidebar, Button, ScrollArea, etc.)
- **date-fns** - Date grouping logic
- **Tailwind CSS** - Vote hover effect styling

---

## Data Models

### Existing Models (No Changes)

```python
class Session(SQLModel, table=True):
    id: Optional[int]
    session_id: str  # UUID
    title: str  # First message
    user_id: Optional[int]  # For anonymous users (store UUID string)
    created_at: datetime
    last_active_at: datetime
```

```python
class Battle(SQLModel, table=True):
    id: Optional[int]
    battle_id: str  # UUID
    session_id: str  # FK to sessions
    left_model_id: str
    right_model_id: str
    conversation: List[Dict[str, Any]]  # JSONB
    status: str  # ongoing, voted, abandoned
    created_at: datetime
    updated_at: datetime
```

### localStorage Structure

```typescript
{
  "llmbattler_user_id": "550e8400-e29b-41d4-a716-446655440000"  // UUID v4
}
```

---

## API Specification

### GET `/api/sessions`

**Request:**
```
GET /api/sessions?user_id=550e8400-e29b-41d4-a716-446655440000&limit=50&offset=0
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "abc123...",
      "title": "Hello! How can I help you?",
      "created_at": "2025-10-22T10:00:00Z",
      "last_active_at": "2025-10-22T11:30:00Z"
    },
    ...
  ],
  "total": 42
}
```

### GET `/api/sessions/{session_id}/battles`

**Request:**
```
GET /api/sessions/abc123/battles
```

**Response:**
```json
{
  "session_id": "abc123...",
  "battles": [
    {
      "battle_id": "def456...",
      "left_model_id": "gpt-4",
      "right_model_id": "claude-3",
      "conversation": [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hello! How can I help you?", "position": "left"},
        {"role": "assistant", "content": "Nice to meet you! What questions do you have?", "position": "right"}
      ],
      "status": "voted",
      "vote": "left_better",
      "created_at": "2025-10-22T10:00:00Z"
    },
    ...
  ]
}
```

### POST `/api/sessions` (Modified)

**Request:**
```json
{
  "prompt": "Hello!",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"  // Optional
}
```

**Response:** (Same as existing)

---

## UI Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  [LMArena ▼]  [📋 Battle ▼]                          [Login] [⋮] │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                   │
│ [✏ New Chat] │  Battle Mode                                     │
│              │  Compare responses from two randomly...          │
│ 🏆 Leaderboard│                                                   │
│              │  ┌─────────────────┐  ┌─────────────────┐        │
│ Today        │  │ Assistant A     │  │ Assistant B     │        │
│ ✕ Hello?     │  │                 │  │                 │        │
│              │  │ You: Hello?     │  │ You: Hello?     │        │
│ Yesterday    │  │ A: Hello!       │  │ B: Nice to meet!│        │
│ ✕ Capital?   │  └─────────────────┘  └─────────────────┘        │
│              │                                                   │
│              │  ┌────────────────────────────────────────────┐  │
│              │  │ Ask followup...                       [Send]│  │
│              │  ├────────────────────────────────────────────┤  │
│              │  │ [◀ A is Better] [🤝 Tie] [👎 Both Bad]      │  │
│              │  │                          [B is Better ▶]    │  │
│              │  └────────────────────────────────────────────┘  │
└──────────────┴──────────────────────────────────────────────────┘
```

---

## Important Notes

### Project Policy Compliance
- ❌ **NO Foreign Keys** (ADR-001)
  - Session ↔ Battle relationship managed at application level
- ✅ **PRs written in English**
- ✅ **Main branch is `develop`**
- ✅ **Each Phase in separate PR** (target 300 lines or less)

### localStorage Security
- Anonymous user ID is not sensitive information, so localStorage usage is acceptable
- Future authentication system will migrate to JWT, etc.

### Performance Considerations
- Session list paginated in batches of 50 (infinite scroll optional)
- Battle list loads all at once (typically 1-5 battles per session)

---

## Next Steps

After writing the specification, start development with:
```bash
/start-phase
```

Develop sequentially from Phase 1, with each Phase submitted as a separate PR.

---

---

## Clarifications

**Date:** 2025-10-23

### 🔴 Critical Decisions

#### 1. Edge Cases

**Q1: Handling localStorage initialization?**
- **A:** Generate new user_id, existing sessions remain orphaned (cannot recover)

**Q2: Multi-tab handling?**
- **A:** user_id shared across tabs (localStorage), each tab creates independent sessions

**Q3: Session count limit?**
- **A:** Display maximum 100 (API limit=100), no automatic deletion

**Q4: Restoring past session state on click?**
- **A:** Display all battles as read-only
  - Selective display based on vote results:
    - "Left is Better" → Show only left response by default
    - "Right is Better" → Show only right response by default
    - "Tie" → Show both responses (green border)
    - "Both are bad" → Show both responses (red border)
  - "See other response" button to view unselected response
  - New message in bottom input → Create new battle

**Q5: Restoring voted battles?**
- **A:** Model names already revealed, Vote buttons disabled

#### 2. Error Handling

**Q6: GET `/api/sessions` failure?**
- **A:** Display error message + provide "Retry" button

**Q7: GET `/api/sessions/{session_id}/battles` failure?**
- **A:** "Cannot load session" toast message, maintain sidebar sessions

**Q8: Session list loading timeout?**
- **A:** Display 3 skeleton UIs + 15 second timeout

#### 3. Integration Points

**Q9: "New Chat" button behavior?**
- **A:** Initialize Battle page (sessionId = null), display empty input → First message creates new session

**Q10: Sidebar display scope?**
- **A:** Add to global layout, display on all pages (`/battle`, `/leaderboard`)

**Q11: Sidebar update on new session creation?**
- **A:** SessionContext auto refetches (re-calls GET `/api/sessions`)

### 🟡 Important Decisions

#### 4. Backward Compatibility

**Q12: Handling existing sessions (user_id=NULL)?**
- **A:** Ignore and start fresh (no migration needed)

**Q13: Session model user_id type?**
- **A:** Change to `user_id: Optional[str]` (VARCHAR(50)) + Alembic migration
  - Anonymous: Store UUID
  - Future auth: Convert user.id to string and store

#### 5. Performance & Scale

**Q14: Session list pagination?**
- **A:** Load initial 20 + "Load More" button (add 20 at a time)

**Q15: Battle list loading strategy?**
- **A:** Load all battles for one session at once (no pagination)

### 🟢 Optional Decisions

#### 6. Design Preferences

**Q16: Sidebar width?**
- **A:** Keep same as current. Do not change.

**Q17: Session title display?**
- **A:** First message maximum 60 characters + ellipsis (...), not editable (Phase 1)

**Q18: Vote hover animation time?**
- **A:** 150ms transition (smooth transition)

**Q19: Border color and thickness?**
- **A:** `border-green-500`, `border-red-500`, 2px

#### 7. Security & Permissions

**Q20: Anonymous user ID security?**
- **A:** UUID v4 is sufficiently random (2^122 possibilities), no additional measures in MVP, naturally resolved when adding future authentication

#### 8. Testing & Validation

**Q21: Playwright MCP test scope?**
- **A:** Basic rendering + session click test (core functionality only)
  - Verify sidebar rendering
  - "New Chat" button click
  - Click one from session list → Verify main area change

---

## Architecture Design

**Selected Option:** Option C (Pragmatic Balance)
**Decision Date:** 2025-10-23

### Design Rationale

1. **Feature Complexity**: Medium level (CRUD + state management)
2. **Existing Pattern Consistency**: Maintain Backend 3-layer, Frontend page/client/hook/service
3. **Future Extensibility**: Easy to add auth with `use-user` hook, sidebar isolation allows reuse
4. **Phase-by-Phase Implementation**: Each Phase can be developed independently

### Backend Structure

```
backend/src/llmbattler_backend/
├── api/
│   └── sessions.py (modified)
│       - GET /api/sessions (new)
│       - GET /api/sessions/{session_id}/battles (new)
├── services/
│   └── session_service.py (modified)
│       - get_sessions_by_user_id() (new)
│       - get_battles_by_session_id() (new)
└── repositories/
    └── session_repository.py (modified)
        - find_by_user_id() (new)
        - find_battles_by_session() (new)

shared/src/llmbattler_shared/
└── schemas.py (modified)
    - SessionListResponse (new)
    - SessionItem (new)
    - BattleListResponse (new)
```

### Frontend Structure

```
frontend/
├── lib/
│   ├── storage.ts (new)
│   │   - getAnonymousUserId()
│   │   - setAnonymousUserId()
│   │   - clearAnonymousUserId()
│   ├── hooks/
│   │   └── use-user.ts (new)
│   │       - userId state management
│   │       - isAnonymous flag
│   │       - localStorage synchronization
│   ├── contexts/
│   │   └── session-context.tsx (new)
│   │       - Global session list state
│   │       - refetchSessions()
│   │       - selectSession()
│   └── services/
│       └── session-service.ts (new)
│           - fetchSessions()
│           - fetchSessionBattles()
├── components/
│   └── sidebar/
│       ├── sidebar.tsx (new)
│       │   - Sidebar container
│       │   - New Chat button
│       │   - Leaderboard link
│       ├── session-list.tsx (new)
│       │   - Date grouping logic
│       │   - Load More button
│       └── session-item.tsx (new)
│           - Session item rendering
│           - Active session highlight
├── app/
│   ├── layout.tsx (modified)
│   │   - Wrap with SessionProvider
│   │   - Add sidebar (all pages)
│   └── battle/
│       ├── battle-client.tsx (modified)
│       │   - Add vote hover effects
│       │   - Integrate SessionContext
│       └── _types.ts (modified)
│           - Add vote result types
```

### Key Decisions

1. **Backend API Addition**
   - GET `/api/sessions?user_id={uuid}&limit=20&offset=0`
   - GET `/api/sessions/{session_id}/battles`
   - Add `user_id` parameter to existing POST `/api/sessions`

2. **Database Migration**
   - Change Session model `user_id` type: `Optional[int]` → `Optional[str]` (VARCHAR(50))
   - Ignore existing user_id=NULL sessions

3. **Frontend State Management**
   - SessionContext: Manage global session list
   - useUser: Manage anonymous user ID (localStorage)
   - Auto refetch on new session creation

4. **Vote Result-Based Display**
   - "Left is Better": Show only left
   - "Right is Better": Show only right
   - "Tie": Show both (green border)
   - "Both are bad": Show both (red border)
   - "See other response" button to view rest

5. **Sidebar Behavior**
   - Display on all pages
   - Fixed width (maintain current design)
   - Load initial 20 + "Load More" button
   - 15 second timeout + skeleton UI

### Implementation Priority

**Phase 3.1: Backend - Session List API**
- Implement GET `/api/sessions`
- Implement GET `/api/sessions/{session_id}/battles`
- Alembic migration (user_id type change)

**Phase 3.2: Frontend - Sidebar Component**
- Develop sidebar UI components
- Date grouping logic

**Phase 3.3: Frontend - Anonymous User ID Management**
- localStorage utils
- use-user hook

**Phase 3.4: Frontend - Session Context & API Integration**
- Implement SessionContext
- session-service.ts
- layout.tsx integration

**Phase 3.5: Frontend - Battle UI Enhancement**
- Vote hover effects
- Vote result-based display logic

**Phase 3.6: Integration & E2E Testing**
- Playwright MCP tests
- Verify complete flow

---

**Last Updated:** 2025-10-23

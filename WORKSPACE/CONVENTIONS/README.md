# CONVENTIONS - Development Conventions

This folder defines development rules for the llmbattler project.

## 📚 Document Structure

```
CONVENTIONS/
├── README.md                 # This file (full index)
│
├── # Common Conventions
├── GIT_FLOW.md              # Git branch strategy
├── PR_GUIDELINES.md         # PR writing rules
├── COMMIT_GUIDELINES.md     # Commit message format
├── CODE_REVIEW.md           # Self code review
│
├── # Backend Conventions
└── backend/
    ├── README.md            # Backend index
    ├── CODE_STYLE.md        # Python code style
    ├── TESTING.md           # TDD, pytest
    ├── UV.md                # uv package management
    ├── SQLMODEL.md          # DB modeling, ⚠️ NO FK
    ├── ALEMBIC.md           # DB migrations, ⚠️ auto-generate
    └── FASTAPI.md           # FastAPI patterns
│
└── # Frontend Conventions
    └── frontend/
        ├── README.md        # Frontend index
        ├── NEXTJS.md        # RSC patterns
        ├── SHADCN.md        # shadcn/ui
        └── TESTING.md       # Playwright E2E
```

## 🎯 Documents to Read Before Starting Work

### Backend Work
```
1. WORKSPACE/00_PROJECT.md - Project policies
2. backend/README.md - Backend overview
3. backend/TESTING.md - TDD
4. backend/SQLMODEL.md - ⚠️ NO FK usage
5. GIT_FLOW.md - Branch strategy
```

### Frontend Work
```
1. WORKSPACE/00_PROJECT.md - Project policies
2. frontend/README.md - Frontend overview
3. frontend/NEXTJS.md - RSC patterns
4. GIT_FLOW.md - Branch strategy
```

### Worker Work
```
1. WORKSPACE/00_PROJECT.md - Project policies
2. backend/README.md - Python conventions (same as backend)
3. backend/TESTING.md - TDD
4. GIT_FLOW.md - Branch strategy
```

### Before Creating PR
```
1. CODE_REVIEW.md - Self-review checklist
2. PR_GUIDELINES.md - PR writing rules
```

## 🔴 CRITICAL Checklist

### Common
```
[ ] Git Flow: Work on feature/* branches
[ ] Target Branch: PR to main
[ ] PR Language: English
[ ] Commit Format: <type>: <subject>
[ ] PR Size: 300 lines or less
```

### Backend/Worker
```
[ ] TDD: Write tests first
[ ] ❌ NO FK: Foreign Keys absolutely prohibited
[ ] uv add: pip install prohibited
[ ] Alembic: Auto-generate migrations (--autogenerate)
[ ] Import: Only at top of file
[ ] English comments: No Korean comments
```

### Frontend
```
[ ] RSC Pattern: page.tsx vs *-client.tsx separation
[ ] Reference structure: Follow existing patterns
[ ] shadcn/ui: Use components instead of raw HTML
[ ] Playwright MCP: Manual verification required for UI changes!
```

## 📝 How to Add Rules

### When Adding New Rules

**Step 1: Decide which file to update**

| Rule Type | File |
|-----------|------|
| Git branches, PR workflow | `GIT_FLOW.md`, `PR_GUIDELINES.md` |
| Commit message format | `COMMIT_GUIDELINES.md` |
| Backend code style, libraries | `backend/*.md` |
| Frontend code style, libraries | `frontend/*.md` |
| Project-specific policies (NO FK, etc.) | Relevant file (e.g., `backend/SQLMODEL.md`) |

**Step 2: Rule format**

All convention documents follow this format:

```markdown
# Title

## 🔴 Required Rules (MUST)

✅ **What to do**
❌ **What NOT to do**

```bash/python/typescript
# Simple DO/DON'T examples
```

## ⚠️ Recommendations (SHOULD)

```bash
# Useful commands or tips
```

---

💬 **Ask if you have specific questions**
```

**Step 3: Keep it concise (10-60 lines)**

- ✅ Only specify required/prohibited rules
- ✅ Minimal DO/DON'T examples
- ❌ Remove usage tutorials
- ❌ Remove reference links
- ❌ Remove verbose explanations

**Step 4: Add "Ask questions" message**

Add this at the end of every document:
```markdown
💬 **Ask if you have specific [topic] questions**
```

## 🔍 Quick Reference

| Question | Document | Answer |
|----------|----------|--------|
| Can I use Foreign Keys? | backend/SQLMODEL.md | ❌ Absolutely prohibited |
| Can I use pip install? | backend/UV.md | ❌ Use uv add only |
| Manual migration writing? | backend/ALEMBIC.md | ❌ --autogenerate required |
| Import in middle of file? | backend/CODE_STYLE.md | ❌ Top of file only |
| Can I use Korean comments? | backend/CODE_STYLE.md | ❌ English only |
| useState in Server Component? | frontend/NEXTJS.md | ❌ Separate to Client Component |
| Use raw HTML? | frontend/SHADCN.md | ❌ Use shadcn components |
| Can I skip Playwright? | frontend/TESTING.md | ❌ Required! |
| PR over 300 lines? | PR_GUIDELINES.md | ⚠️ Split recommended |
| Commit message format? | COMMIT_GUIDELINES.md | `<type>: <subject>` |

## 📋 Pre-Commit Checklist

### Backend/Worker
```bash
cd backend  # or cd worker
uvx ruff check
uvx isort --check --profile black .
uv run pytest -s
git diff --stat  # 300 lines or less recommended
```

### Frontend
```bash
cd frontend
npm run lint
# For UI changes: Manual Playwright MCP verification required! (see frontend/TESTING.md)
git diff --stat  # 300 lines or less recommended
```

---

**Parent Document:** [00_PROJECT.md](../00_PROJECT.md)

💬 **Ask if you have convention-related questions**

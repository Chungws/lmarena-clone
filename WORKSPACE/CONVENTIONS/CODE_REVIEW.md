# Self Code Review Rules

## 🔴 Required Rules (MUST)

### Self-Review Before PR Creation
✅ **MUST self-review after phase completion**
✅ **Run `/check-pr` command** (automated checks - to be configured)
❌ **DO NOT create PR without review**

### Checklist

**Common:**
```
[ ] Git Flow compliance (feature/* branch)
[ ] Conventional Commits (<type>: <subject>)
[ ] PR size 300 lines or less
[ ] NO Foreign Keys (Backend/Worker)
[ ] Target branch: main
[ ] PR language: English
[ ] Comments: English
```

**Backend/Worker Changes:**
```
[ ] TDD: Write tests first
[ ] uvx ruff check passed
[ ] uvx isort --check passed
[ ] uv run pytest -s passed
[ ] Use uv add for dependencies
[ ] Use alembic revision --autogenerate
```

**Frontend Changes:**
```
[ ] RSC pattern (page.tsx vs *-client.tsx)
[ ] shadcn/ui components used
[ ] API client used correctly
[ ] npm run lint passed
[ ] Playwright MCP verification completed for UI changes (required!)
```

## ⚠️ Recommendations (SHOULD)

```bash
# Self-review (automated - to be configured)
/review-phase

# Manual checks
git diff main --stat
cd backend && uvx ruff check && uv run pytest -s
cd frontend && npm run lint
# For UI changes: Manual Playwright MCP verification (see frontend/TESTING.md)
```

---

💬 **Ask if you have specific review criteria questions**

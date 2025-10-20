# Alembic Migration Rules

## 🔴 Required Rules (MUST)

### Migration Creation
✅ `uv run alembic revision --autogenerate -m "description"` (auto-generate only)
❌ **NEVER manually create/edit migration files**
❌ **NEVER directly modify generated files** (except data migrations)

### Workflow
✅ 1. Modify models (`app/*/models.py`)
✅ 2. Run PostgreSQL (`docker compose up -d`)
✅ 3. Auto-generate (`alembic revision --autogenerate`)
✅ 4. Apply (`alembic upgrade head`)

### Git Commits
✅ Commit model files + migration files together
✅ On revision conflict: regenerate (delete file and re-run --autogenerate)

## ⚠️ Recommendations (SHOULD)

```bash
# Test downgrade
uv run alembic downgrade -1
uv run alembic upgrade head

# Check current version
uv run alembic current

# Check history
uv run alembic history
```

## 💡 Exception: Data Migrations

**Only allowed manual editing case:**
- When existing data transformation is needed
- First generate with --autogenerate, then modify
- Document reason for modification in comments

---

💬 **Ask if you have specific Alembic questions**

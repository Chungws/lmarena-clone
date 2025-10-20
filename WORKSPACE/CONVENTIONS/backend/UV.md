# UV Package Management Rules

## 🔴 Required Rules (MUST)

### Package Management
✅ `uv add <package>` (production)
✅ `uv add <package> --dev` (development)
❌ **NEVER use pip install**
❌ **NEVER manually edit pyproject.toml**

### Command Execution
✅ `uv run <command>` (pytest, uvicorn, alembic, etc.)
✅ `uvx <tool>` (one-time tools like ruff, isort)

### Git Commits
✅ `uv.lock` must be committed
❌ `.venv/` must NOT be committed (add to .gitignore)

## ⚠️ Recommendations (SHOULD)

```bash
# Initial project setup
uv sync

# Remove package
uv remove <package>

# Verify dependencies
uv sync --locked
```

---

💬 **Ask if you have specific uv usage questions**

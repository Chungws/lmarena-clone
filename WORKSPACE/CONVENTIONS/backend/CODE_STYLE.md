# Backend Code Style Rules

## 🔴 Required Rules (MUST)

### Import Location
✅ Write imports only at the top of file
❌ **NEVER import in the middle of functions/classes**

### Comments
✅ **Write in English only**
❌ **NO Korean comments allowed**

### Type Hints
✅ Add type hints to all function parameters and return values
```python
def get_user(user_id: int, db: Session) -> User | None:
    pass
```

## ⚠️ Recommendations (SHOULD)

- Import order: Standard library → External packages → Internal modules (isort auto-sorts)
- Black formatting (automatic)
- Ruff linting must pass

## 🛠️ Automated Checks

```bash
cd backend
uvx ruff check
uvx ruff format --check
uvx isort --check --profile black .
```

---

💬 **Ask if you have specific style questions**

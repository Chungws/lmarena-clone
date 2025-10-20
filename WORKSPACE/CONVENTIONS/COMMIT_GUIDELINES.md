# Commit Message Guidelines

## 🔴 Required Rules (MUST)

### Format
✅ **MUST use `<type>: <subject>` format**

```bash
feat: add battle mode API endpoints
fix: resolve authentication bug
chore: update dependencies
```

### Commit Types

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Build, config, documentation |
| `refactor` | Refactoring (no functional changes) |
| `test` | Add/modify tests |
| `perf` | Performance improvements |
| `docs` | Documentation only |
| `style` | Code formatting (no functional changes) |

### Subject Rules
✅ **Imperative mood** (`add`, `fix`, not `added`, `fixing`)
✅ **Lowercase first letter** (`add user`, not `Add user`)
✅ **No period at the end**
✅ **50 characters or less**

```bash
# ✅ CORRECT
feat: add LLM judge evaluation
fix: resolve cache invalidation

# ❌ WRONG
feat: Added LLM Judge evaluation feature  # past tense, uppercase, too long
fix: resolve cache invalidation.  # period at end
```

### Granular Commits
✅ **Split by logical units** (models → schemas → service → router → tests)
❌ **DO NOT bundle multiple features in one commit**

## ⚠️ Recommendations (SHOULD)

```bash
# Check commit messages
git log --oneline -n 10

# Fix incorrect message (last commit)
git commit --amend -m "feat: correct message"
```

---

💬 **Ask if you have specific commit message questions**

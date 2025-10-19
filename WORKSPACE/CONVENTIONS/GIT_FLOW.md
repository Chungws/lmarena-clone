# Git Branching Rules (Git Flow)

## 🔴 Required Rules (MUST)

### Branch Verification
✅ **MUST verify branch before commit**
❌ **NEVER work directly on `main` branch**
✅ **ALWAYS create `feature/*` branch first**

```bash
# ALWAYS check before work!
git branch --show-current

# If on main, immediately create feature branch
git checkout -b feature/feature-name
```

### Branch Types

| Branch | Purpose | Branch From | Merge To |
|--------|---------|-------------|----------|
| `main` | Production (Main branch) | - | - |
| `feature/*` | Feature development | `main` | `main` |
| `release/*` | Release preparation | `main` | `main` |
| `hotfix/*` | Urgent fixes | `main` | `main` |

### Feature Workflow

```bash
# 1. Update main and create branch
git checkout main
git pull origin main
git checkout -b feature/feature-name-phase-1

# 2. Work and commit
git add .
git commit -m "feat: add feature"
git push -u origin feature/feature-name-phase-1

# 3. Create PR (target: main)
# 4. After merge, clean up local branch
git checkout main
git pull origin main
git branch -d feature/feature-name-phase-1
```

### Branch Naming
✅ `feature/battle-mode-phase-1`
✅ `feature/fix-login-bug`
❌ `bugfix/issue-123` (use feature/ for all)
❌ `refactor/cleanup` (use feature/ for all)

## ⚠️ Recommendations (SHOULD)

```bash
# If accidentally worked on main (before commit)
git stash
git checkout -b feature/new-feature
git stash pop

# If accidentally worked on main (after commit)
git checkout -b feature/new-feature  # Create branch with current state
git checkout main
git reset --hard origin/main  # Reset main
```

---

💬 **Ask if you have specific Git Flow questions**

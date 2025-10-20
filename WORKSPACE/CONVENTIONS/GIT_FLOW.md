# Git Branching Rules (Git Flow)

## 🔴 Required Rules (MUST)

### Branch Verification
✅ **MUST verify branch before commit**
❌ **NEVER work directly on `develop` branch**
✅ **ALWAYS create `feature/*` branch first**

```bash
# ALWAYS check before work!
git branch --show-current

# If on develop, immediately create feature branch
git checkout -b feature/feature-name
```

### Branch Types

| Branch | Purpose | Branch From | Merge To |
|--------|---------|-------------|----------|
| `develop` | Development (Main branch) | - | - |
| `feature/*` | Feature development | `develop` | `develop` |
| `release/*` | Release preparation | `develop` | `develop` |
| `hotfix/*` | Urgent fixes | `develop` | `develop` |

### Feature Workflow

```bash
# 1. Update develop and create branch
git checkout develop
git pull origin develop
git checkout -b feature/feature-name-phase-1

# 2. Work and commit
git add .
git commit -m "feat: add feature"
git push -u origin feature/feature-name-phase-1

# 3. Create PR (target: develop)
# 4. After merge, clean up local branch
git checkout develop
git pull origin develop
git branch -d feature/feature-name-phase-1
```

### Branch Naming
✅ `feature/battle-mode-phase-1`
✅ `feature/fix-login-bug`
❌ `bugfix/issue-123` (use feature/ for all)
❌ `refactor/cleanup` (use feature/ for all)

## ⚠️ Recommendations (SHOULD)

```bash
# If accidentally worked on develop (before commit)
git stash
git checkout -b feature/new-feature
git stash pop

# If accidentally worked on develop (after commit)
git checkout -b feature/new-feature  # Create branch with current state
git checkout develop
git reset --hard origin/develop  # Reset develop
```

---

💬 **Ask if you have specific Git Flow questions**

# Pull Request (PR) Guidelines

## 🔴 Required Rules (MUST)

### PR Size
✅ **300 lines or less** (recommended)
✅ **Focus on single feature/fix**
❌ **DO NOT include multiple features in one PR**

```bash
# Check changed lines
git diff develop --shortstat
```

### Granular Commits
✅ **Split commits by logical units** (models → schemas → service → router → tests)
❌ **DO NOT bundle entire feature in one commit**

### Project Policies

| Item | Setting |
|------|---------|
| **Target Branch** | `develop` (required) |
| **PR Language** | **English** |
| **Assignee** | **Chungws** |
| **Reviewer** | **Chungws** |
| **Delete Source Branch** | `true` |

### PR Description Structure

```markdown
## Summary
[Describe changes in 1-3 sentences]

## Changes
### Backend/Frontend/Worker
- Key file changes and details

## Test Plan
- [x] Backend/Frontend/Worker tests passed
- [ ] Manual testing required

## Impact
- Breaking Changes: None/Yes (details)
- Database Changes: Migration required? (Yes/No)
- Dependencies: New packages added

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Documentation Changes
✅ **WORKSPACE documentation changes in separate PR**
❌ **DO NOT mix code + documentation in one PR**

## ⚠️ Recommendations (SHOULD)

```bash
# Self-review before PR creation (automated)
/check-pr  # (to be configured)

# Check PR size
git diff develop --stat

# If over 300 lines: Split into smaller phases or multiple PRs
```

### PR Creation Timing
✅ Create PR immediately after completing each work unit
❌ Create one PR after completing entire phase (too large)

---

💬 **Ask if you have specific PR-related questions**

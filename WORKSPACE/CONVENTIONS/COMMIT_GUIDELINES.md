# 커밋 메시지 규칙

## 🔴 필수 규칙 (MUST)

### 형식
✅ **`<type>: <subject>` 형식 필수**

```bash
feat: add translation evaluation models
fix: resolve authentication bug
chore: update dependencies
```

### Commit Types

| Type | 용도 |
|------|------|
| `feat` | 새로운 기능 |
| `fix` | 버그 수정 |
| `chore` | 빌드, 설정, 문서 |
| `refactor` | 리팩토링 (기능 변경 없음) |
| `test` | 테스트 추가/수정 |
| `perf` | 성능 개선 |
| `docs` | 문서만 수정 |
| `style` | 코드 포매팅 (기능 변경 없음) |

### Subject 규칙
✅ **명령형** (`add`, `fix`, not `added`, `fixing`)
✅ **소문자 시작** (`add user`, not `Add user`)
✅ **마침표 없이**
✅ **50자 이내**

```bash
# ✅ CORRECT
feat: add LLM Judge evaluation
fix: resolve cache invalidation

# ❌ WRONG
feat: Added LLM Judge evaluation feature  # 과거형, 대문자, 너무 김
fix: resolve cache invalidation.  # 마침표
```

### Granular Commits
✅ **논리적 단위로 분리** (models → schemas → service → router → tests)
❌ **한 커밋에 여러 기능 포함 금지**

## ⚠️ 권장 사항 (SHOULD)

```bash
# 커밋 메시지 확인
git log --oneline -n 10

# 잘못된 메시지 수정 (마지막 커밋)
git commit --amend -m "feat: correct message"
```

---

💬 **구체적인 커밋 메시지 질문이 있으면 물어보세요**

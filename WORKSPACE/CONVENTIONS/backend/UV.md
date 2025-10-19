# UV 패키지 관리 규칙

## 🔴 필수 규칙 (MUST)

### 패키지 관리
✅ `uv add <package>` (production)
✅ `uv add <package> --dev` (development)
❌ **pip install 절대 사용 금지**
❌ **pyproject.toml 직접 수정 금지**

### 명령어 실행
✅ `uv run <command>` (pytest, uvicorn, alembic 등)
✅ `uvx <tool>` (ruff, isort 같은 일회성 도구)

### Git 커밋
✅ `uv.lock` 반드시 커밋
❌ `.venv/` 커밋 금지 (.gitignore에 추가)

## ⚠️ 권장 사항 (SHOULD)

```bash
# 프로젝트 초기 설정
uv sync

# 패키지 제거
uv remove <package>

# 의존성 검증
uv sync --locked
```

---

💬 **구체적인 uv 사용법 질문이 있으면 물어보세요**

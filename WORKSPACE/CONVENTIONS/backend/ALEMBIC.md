# Alembic 마이그레이션 규칙

## 🔴 필수 규칙 (MUST)

### 마이그레이션 생성
✅ `uv run alembic revision --autogenerate -m "description"` (자동 생성만 사용)
❌ **마이그레이션 파일 수동 생성/편집 절대 금지**
❌ **이미 생성된 파일 직접 수정 금지** (data migration 예외)

### 워크플로우
✅ 1. 모델 수정 (`app/*/models.py`)
✅ 2. PostgreSQL 실행 (`docker compose up -d`)
✅ 3. 자동 생성 (`alembic revision --autogenerate`)
✅ 4. 적용 (`alembic upgrade head`)

### Git 커밋
✅ 모델 파일 + 마이그레이션 파일 함께 커밋
✅ Revision conflict 시 재생성 (파일 삭제 후 다시 --autogenerate)

## ⚠️ 권장 사항 (SHOULD)

```bash
# Downgrade 테스트
uv run alembic downgrade -1
uv run alembic upgrade head

# 현재 버전 확인
uv run alembic current

# 히스토리 확인
uv run alembic history
```

## 💡 예외: Data Migration

**유일한 수동 편집 허용 케이스:**
- 기존 데이터 변환 필요 시
- 먼저 --autogenerate로 파일 생성 후 수정
- 수정 사유를 주석으로 명시

---

💬 **구체적인 Alembic 사용법 질문이 있으면 물어보세요**

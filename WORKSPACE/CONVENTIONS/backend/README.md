# Backend Conventions

이 폴더는 Backend (FastAPI + SQLModel + PostgreSQL) 개발 컨벤션을 정의합니다.

## 📚 문서 목록

| 문서 | 규칙 요약 |
|------|---------|
| **[CODE_STYLE.md](./CODE_STYLE.md)** | Import 위치, 영어 주석, Type Hints |
| **[FASTAPI.md](./FASTAPI.md)** | Service Layer 패턴, Router 규칙 |
| **[SQLMODEL.md](./SQLMODEL.md)** | ⚠️ FK 미사용, Index 사용, 관계 정의 |
| **[ALEMBIC.md](./ALEMBIC.md)** | ⚠️ 자동 생성 필수, 수동 작성 금지 |
| **[UV.md](./UV.md)** | uv add 사용, pip 금지 |
| **[TESTING.md](./TESTING.md)** | TDD 필수, AAA 패턴 |

## 🔴 CRITICAL 체크리스트

Backend 작업 전 반드시 확인:

```
[ ] TDD: 테스트 먼저 작성 (TESTING.md)
[ ] FK 미사용: Foreign Keys 절대 사용 금지 (SQLMODEL.md)
[ ] uv add: pip install 사용 금지 (UV.md)
[ ] Alembic: 마이그레이션 자동 생성 필수 (ALEMBIC.md)
[ ] Import: 파일 맨 위에 위치 (CODE_STYLE.md)
[ ] 영어 주석: 한글 주석 금지 (CODE_STYLE.md)
```

## ⚡ Quick Start

```bash
cd backend

# 환경 설정
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# TDD 워크플로우 (새 기능 추가)
vim tests/test_feature.py              # 1. 테스트 작성
uv run pytest -s                       # 2. 실패 확인 (Red)
vim app/feature/service.py             # 3. 구현 (Green)
uv run pytest -s                       # 4. 통과 확인
uv run alembic revision --autogenerate # 5. 마이그레이션 (모델 변경 시)

# 커밋 전 체크
uvx ruff check
uvx isort --check --profile black .
uv run pytest -s
```

## 📋 언제 읽어야 하나?

| 상황 | 문서 |
|------|------|
| 새 기능 구현 시작 | TESTING.md → CODE_STYLE.md |
| 모델 정의 | SQLMODEL.md → ALEMBIC.md |
| API 엔드포인트 추가 | FASTAPI.md |
| 패키지 추가/제거 | UV.md |

---

**상위 문서:** CONVENTIONS/README.md

💬 **구체적인 질문이 있으면 물어보세요 (context7 활용 가능)**

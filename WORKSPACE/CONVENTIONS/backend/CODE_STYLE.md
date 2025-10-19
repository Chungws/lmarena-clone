# Backend 코드 스타일 규칙

## 🔴 필수 규칙 (MUST)

### Import 위치
✅ 파일 맨 위에만 작성
❌ 함수/클래스 중간에 import 절대 금지

### 주석
✅ **영어로만 작성** (English only)
❌ **한글 주석 절대 금지** (No Korean comments)

### Type Hints
✅ 모든 함수 파라미터와 리턴값에 타입 명시
```python
def get_user(user_id: int, db: Session) -> User | None:
    pass
```

## ⚠️ 권장 사항 (SHOULD)

- Import 순서: 표준 라이브러리 → 외부 패키지 → 내부 모듈 (isort 자동 정렬)
- Black 포매팅 (자동)
- Ruff 린트 통과 필수

## 🛠️ 자동 검사

```bash
cd backend
uvx ruff check
uvx isort --check --profile black .
```

---

💬 **구체적인 스타일 질문이 있으면 물어보세요**

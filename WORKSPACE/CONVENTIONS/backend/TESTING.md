# Backend Testing (TDD) 규칙

## 🔴 필수 규칙 (MUST)

### TDD Cycle
✅ **Red → Green → Refactor 순서 필수**
1. Red: 실패하는 테스트 먼저 작성
2. Green: 최소한의 구현으로 테스트 통과
3. Refactor: 코드 개선 (테스트는 계속 통과)

### Test Coverage
✅ **Service Layer 100% 커버리지**
✅ Router는 Integration test로 검증
❌ **구현 없이 테스트 작성 안 함** (TDD 위반)

### AAA 패턴
✅ 모든 테스트는 AAA 패턴 따르기
```python
def test_example():
    # Arrange: 테스트 준비
    # Act: 실행
    # Assert: 검증
```

### pytest
✅ `uv run pytest -s` 실행
✅ Async 테스트: `@pytest.mark.asyncio` 사용
✅ Fixtures for DB session, test client

## ⚠️ 권장 사항 (SHOULD)

```bash
# 특정 테스트만 실행
uv run pytest -s tests/test_feature.py::test_name

# Coverage 확인
uv run pytest --cov=app --cov-report=term-missing

# 커밋 전 전체 테스트 실행
uv run pytest -s
```

## 💡 Test Structure

```python
# tests/test_feature.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_feature_success():
    """Test successful case"""
    # Arrange
    data = {"field": "value"}

    # Act
    response = client.post("/api/v1/endpoint", json=data)

    # Assert
    assert response.status_code == 201
    assert response.json()["field"] == "value"

def test_feature_failure():
    """Test error case"""
    # ...
```

---

💬 **구체적인 pytest 사용법 질문이 있으면 물어보세요**

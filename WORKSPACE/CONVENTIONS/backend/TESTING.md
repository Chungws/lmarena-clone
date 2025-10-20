# Backend Testing (TDD) Rules

## 🔴 Required Rules (MUST)

### TDD Cycle
✅ **Red → Green → Refactor sequence required**
1. Red: Write failing test first
2. Green: Minimal implementation to pass test
3. Refactor: Improve code (tests continue to pass)

### Test Coverage
✅ **Service Layer 100% coverage**
✅ Router verified with Integration tests
❌ **DO NOT write tests without implementation** (violates TDD)

### AAA Pattern
✅ All tests follow AAA pattern
```python
def test_example():
    # Arrange: Test setup
    # Act: Execute
    # Assert: Verify
```

### pytest
✅ Run `uv run pytest -s`
✅ Async tests: Use `@pytest.mark.asyncio`
✅ Fixtures for DB session, test client

## ⚠️ Recommendations (SHOULD)

```bash
# Run specific test only
uv run pytest -s tests/test_feature.py::test_name

# Check coverage
uv run pytest --cov=app --cov-report=term-missing

# Run all tests before commit
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

💬 **Ask if you have specific pytest usage questions**

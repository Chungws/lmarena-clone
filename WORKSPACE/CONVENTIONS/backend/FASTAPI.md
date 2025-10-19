# FastAPI 규칙

## 🔴 필수 규칙 (MUST)

### Feature 모듈 구조
✅ 4-layer 구조: `models.py` → `schemas.py` → `service.py` → `router.py`
✅ **Service Layer에 비즈니스 로직 집중**
✅ **Router는 얇게 유지** (요청/응답만)

### Dependency Injection
✅ `db: AsyncSession = Depends(get_db)` 사용
✅ Custom dependencies for auth, validation

### Async/Await
✅ 모든 database call에 `await` 사용
❌ **Sync call in async function 금지**

## ⚠️ 권장 사항 (SHOULD)

```python
# Schema naming
*Create  # POST body
*Update  # PUT/PATCH body
*Response # API response
*Filter  # Query parameters

# Router structure
router = APIRouter(prefix="/feature", tags=["feature"])

# Error handling
from fastapi import HTTPException
raise HTTPException(status_code=404, detail="Not found")

# Status codes
from fastapi import status
status_code=status.HTTP_201_CREATED  # 201
status_code=status.HTTP_204_NO_CONTENT  # 204
```

---

💬 **구체적인 FastAPI 패턴 질문이 있으면 물어보세요**

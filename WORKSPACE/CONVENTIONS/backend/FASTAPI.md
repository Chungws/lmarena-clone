# FastAPI Rules

## 🔴 Required Rules (MUST)

### Feature Module Structure
✅ 4-layer structure: `models.py` → `schemas.py` → `service.py` → `router.py`
✅ **Concentrate business logic in Service Layer**
✅ **Keep Router thin** (request/response only)

### Dependency Injection
✅ Use `db: AsyncSession = Depends(get_db)`
✅ Custom dependencies for auth, validation

### Async/Await
✅ Use `await` for all database calls
❌ **NO sync calls in async functions**

## ⚠️ Recommendations (SHOULD)

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

💬 **Ask if you have specific FastAPI pattern questions**

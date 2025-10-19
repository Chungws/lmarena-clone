# SQLModel & Database 규칙

## 🔴 필수 규칙 (MUST)

### Foreign Keys 절대 미사용 ⚠️
❌ **`Field(foreign_key="table.id")` 절대 사용 금지**
✅ **`Field(index=True)` 사용** (Index만)

**이유:** [ADR-001](../../ARCHITECTURE/ADR_001-No_Foreign_Keys.md) 참고
- 마이크로서비스 분리 대비
- 수평 확장성 (Sharding)
- 성능 (Bulk Insert)

**대응:** 서비스 레이어에서 트랜잭션으로 참조 무결성 관리

### 모델 정의
✅ Type hints 필수 (`int | None`, `str`, `datetime`)
✅ Primary key: `id: int | None = Field(default=None, primary_key=True)`
✅ Index: `Field(index=True)` for foreign reference columns
✅ Unique constraint: `Field(unique=True)` for email, username

### Relationships
❌ **SQLModel Relationship() 사용 금지** (FK 필요)
✅ **Service Layer에서 JOIN 쿼리로 처리**

```python
# ❌ WRONG
class User(SQLModel, table=True):
    posts: list["Post"] = Relationship(back_populates="user")

# ✅ CORRECT
async def get_user_with_posts(db: AsyncSession, user_id: int):
    result = await db.exec(
        select(User, Post).where(Post.user_id == user_id)
    )
    return result.all()
```

## ⚠️ 권장 사항 (SHOULD)

```python
# Index on frequently queried columns
created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

# Validation with Pydantic
from pydantic import validator, Field

@validator('email')
def validate_email(cls, v):
    # validation logic
    return v
```

---

💬 **구체적인 SQLModel 사용법 질문이 있으면 물어보세요**

# SQLModel & Database Rules

## 🔴 Required Rules (MUST)

### NO Foreign Keys ⚠️
❌ **NEVER use `Field(foreign_key="table.id")`**
✅ **USE `Field(index=True)` instead** (Index only)

**Reason:** See [ADR-001](../../ARCHITECTURE/ADR_001-No_Foreign_Keys.md)
- Microservice separation readiness
- Horizontal scalability (Sharding)
- Performance (Bulk Insert)

**Mitigation:** Manage referential integrity in service layer with transactions

### Model Definition
✅ Type hints required (`int | None`, `str`, `datetime`)
✅ Primary key: `id: int | None = Field(default=None, primary_key=True)`
✅ Index: `Field(index=True)` for foreign reference columns
✅ Unique constraint: `Field(unique=True)` for email, username

### Relationships
❌ **NO SQLModel Relationship()** (requires FK)
✅ **Handle in Service Layer with JOIN queries**

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

## ⚠️ Recommendations (SHOULD)

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

💬 **Ask if you have specific SQLModel questions**

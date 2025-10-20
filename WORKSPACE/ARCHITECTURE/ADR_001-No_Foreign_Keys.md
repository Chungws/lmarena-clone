# ADR-001: No Database-Level Foreign Key Constraints

- **Status:** Accepted
- **Date:** 2025-01-20

## Context

When designing database models, we need to decide whether to use database-level `FOREIGN KEY` constraints to define relationships between tables. While logical relationships exist between entities (e.g., parent-child relationships), we must choose how to enforce referential integrity.

## Decision

We will **NOT use database-level `FOREIGN KEY` constraints**.

Relationships between tables will be managed at the application code level. For example, a child model may have a `parent_id` field, but this field will NOT have a `FOREIGN KEY` constraint at the database level.

## Rationale

1. **Database Independence and Flexibility:** Foreign key constraints create tight coupling in the database schema, which can become an obstacle when migrating to microservices or switching to different database systems.

2. **Development Simplicity:** Foreign key constraints can complicate test data creation/deletion, partial backups, and data recovery operations. Removing them simplifies development workflows.

3. **Performance:** Bulk insert or update operations can benefit from reduced overhead by skipping foreign key constraint checks.

4. **Horizontal Scalability:** If the system needs to scale horizontally using sharding or multiple database instances, managing foreign keys across distributed databases becomes extremely complex. Removing constraints enables this scalability from the start.

5. **Testing Simplicity:** Without FK constraints, test data can be created in any order without worrying about parent-child dependencies. Individual tables can be truncated without cascade issues.

## Consequences

**Positive:**
- Schema changes and system scaling become easier
- Test code writing becomes simpler (no dependency order)
- Better performance for bulk operations
- Easy to mock partial data in tests

**Negative (and Mitigation):**
- **Risk of Data Integrity Issues:** Orphan records can occur if parent records are deleted without deleting child records.
- **Mitigation:** All related record deletion logic MUST be handled in the application's service layer using transactions to ensure data integrity.

## Implementation Guidelines

### Deletion Pattern (Application-Level CASCADE)

```python
# Service layer handles cascade deletion
async def delete_session(session_id: str):
    """Delete session and all related data (CASCADE at application level)"""
    async with db.transaction():
        # Delete in child → parent order
        await db.execute("DELETE FROM votes WHERE session_id = $1", session_id)
        await db.execute("DELETE FROM battles WHERE session_id = $1", session_id)
        await db.execute("DELETE FROM sessions WHERE session_id = $1", session_id)
```

### Validation Pattern (Application-Level Referential Integrity)

```python
# Service layer validates references
async def create_battle(battle_data: BattleCreate):
    """Create battle with validation"""
    async with db.transaction():
        # Validate parent exists
        session = await db.fetch_one(
            "SELECT id FROM sessions WHERE session_id = $1",
            battle_data.session_id
        )
        if not session:
            raise HTTPException(404, "Session not found")

        # Create child record
        await db.execute("INSERT INTO battles (...) VALUES (...)")
```

## Testing Benefits

```python
# Easy test data creation (no dependency order)
async def test_vote_processing():
    # Can create vote directly without creating session/battle first
    vote = await create_test_vote(
        battle_id="test_battle_123",  # Doesn't need to exist
        left_model_id="gpt-4o",
        right_model_id="claude"
    )

    # Test worker logic in isolation
    result = await process_vote(vote)
    assert result.status == "processed"

# Easy cleanup (no cascade issues)
async def teardown():
    await db.execute("TRUNCATE votes")  # No FK violation
```

---

**Related Documents:**
- [DATABASE_DESIGN.md](./DATABASE_DESIGN.md) - Complete database design without FKs
- [00_ROADMAP.md](../00_ROADMAP.md) - Scalability considerations

**Last Updated:** 2025-01-21

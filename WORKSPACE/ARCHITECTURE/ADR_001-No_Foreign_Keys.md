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

## Consequences

**Positive:**
- Schema changes and system scaling become easier
- Test code writing becomes simpler
- Better performance for bulk operations

**Negative (and Mitigation):**
- **Risk of Data Integrity Issues:** Orphan records can occur if parent records are deleted without deleting child records.
- **Mitigation:** All related record deletion logic MUST be handled in the application's service layer using transactions to ensure data integrity.

# ARCHITECTURE - Architecture Documentation

This folder contains Architecture Decision Records (ADRs) for the llmbattler project.

---

## 📚 Document List

### ADRs (Architecture Decision Records)

- **[ADR-001: No Database-Level Foreign Key Constraints](./ADR_001-No_Foreign_Keys.md)**
  - Decision: Do NOT use database-level FK constraints, manage in application code
  - Reason: Microservice readiness, horizontal scalability, performance
  - Impact: Data integrity must be ensured in service layer with transactions

---

## 📖 What is an ADR?

An Architecture Decision Record documents important architectural decisions made in the project.

**ADR Structure:**
- **Context:** Background why the decision was needed
- **Decision:** What was decided
- **Rationale:** Reasons and considerations for the decision
- **Consequences:** Positive/negative impacts and mitigation strategies

---

## 🎯 When to Write an ADR?

Consider writing an ADR for:

1. Tech stack selection (DB, Framework, Library)
2. Design pattern selection (architecture style, data modeling)
3. Policies that differ from standard practices
4. Important decisions that affect future maintenance

---

## 💡 Tip

When implementing new features or changing existing structure, check ADRs in this folder first. They help you understand the project's design philosophy.

---

**Parent Document:** [00_PROJECT.md](../00_PROJECT.md)

**Last Updated:** 2025-01-20

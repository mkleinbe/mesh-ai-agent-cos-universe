# ADR-002: Task/event ledger and persistence
Status: Accepted

Use SQLite behind a narrow ledger abstraction for Phase 1. It provides transactional canonical state, uniqueness constraints for idempotency, simple local operation, and an easy migration path to managed PostgreSQL when concurrency or deployment needs justify it. Slack never becomes canonical state.

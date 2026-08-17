# ADR-001: Runtime and implementation language
Status: Accepted

Use Python 3.11+ as a modular monolith. Rationale: low deployment burden, strong ecosystem for Slack/AI integrations, readable domain logic, simple testing, and adequate typing without introducing service boundaries before they are justified. Phase 1 has no message broker and no microservices.

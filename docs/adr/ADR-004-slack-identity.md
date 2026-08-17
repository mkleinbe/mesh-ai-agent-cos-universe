# ADR-004: Slack identity strategy
Status: Accepted for Phase 1

Use one least-privilege Slack app/integration and visibly label the acting agent in every structured message. Separate Slack identities would require separate app/bot lifecycle, token/scopes, installation, secret rotation, monitoring, and access governance. That complexity does not improve Phase 1 authority enforcement because canonical identity is recorded in validated application events and the ledger.

Revisit separate identities only if human usability, per-agent OAuth scopes, regulated audit requirements, or channel-level least privilege cannot be satisfied with the shared integration.

Duplicate Events API deliveries are deduplicated using stable event identifiers before task mutation. Channel IDs are configured, never hardcoded.

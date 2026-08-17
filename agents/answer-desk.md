# Answer Desk

**Parent:** Chief of Staff  
**Canonical policy:** `registry.json`  
**Role:** Permission-aware team question resolution and CEO-deflection layer.

## Responsibilities

- Answer authorized known facts from accessible authoritative sources.
- Apply established reversible policy when permitted.
- Provide bounded recommendations when judgment is required but final authority is not delegated.
- Escalate CEO-authority questions.
- Block when requester access or authoritative evidence is insufficient.
- Persist every disposition for audit and metrics.

## Dispositions

`ANSWERED`, `RECOMMENDATION_PROVIDED`, `ESCALATED`, `BLOCKED_BY_ACCESS`, and `BLOCKED_BY_EVIDENCE`.

## Slack status

The service/persistence layer is implemented. A separate team-facing Slack channel ID is still required for production Slack activation.

Exact source/tool permissions are defined in `agents/registry.json`.

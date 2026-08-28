# Changelog v4.3.1

Release date: 2026-08-28

## Fixed

- Closed PF-058 at the actual failure boundary: the workspace-approved ChatGPT MCP app exposed a stale 27-action snapshot even though the v4.3.0 QNAP runtime and canonical source contract already contained `delegation.execute_owner`.
- Added an exact published-action invariant: the bound CoS ChatGPT action surface must equal the canonical CoS machine allowlist minus human-only operations.
- Added `scripts/check-published-action-surface.py` to compare a captured workspace action snapshot using exact set equality.
- Added regression tests proving an exact 28-action CoS snapshot passes and the observed 27-action snapshot missing `delegation.execute_owner` fails.
- Added systemic PF-059 capability-universe controls covering all 10 ACTIVE agents, all direct-report owner lifecycle paths, both nested delegation routes, specialized scopes, and human-only exclusions.

## Security and governance

- Preserved server-derived delegated owner identity. Callers still cannot select the child principal.
- Preserved child allowlist reapplication and inherited approval gates.
- Preserved the two human-only operations outside the agent-published action surface: `approval.record_decision` and `reliability.human_override`.
- Preserved the bounded nested routes `cos -> cmo -> vp-content` and `cos -> coo -> consultant-network-steward`.
- Added a TARGETED security review and independent production-acceptance plan.

## Operational compatibility

- No QNAP runtime behavior or canonical Phase 1 authority contract changed in this patch.
- Existing production deployment release 4.3.0 already implements `delegation.execute_owner`; a backend redeploy is not required solely to correct the frozen ChatGPT workspace action snapshot.
- The workspace-approved custom MCP app must be refreshed/recreated and republished so ChatGPT exposes the exact 28-action CoS machine surface.
- Production child-owner execution remains fail-closed until that external workspace publication gate passes.

## Recovery

After the workspace action snapshot passes 28/28, resume these exact outstanding logical occurrences in place rather than creating replacements:

- `MKT-LI-OPT-WED-001:2026-08-26T15:00:00-04:00`
- `MKT-LI-REV-FRI-001:2026-08-28T15:00:00-04:00`

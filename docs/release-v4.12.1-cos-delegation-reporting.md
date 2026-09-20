# v4.12.1 CoS Delegation and Agent Reporting

## Purpose

This PATCH remediates the CoS-to-agent delegation request contract and failure diagnostics exposed by the Commercial Growth OS pilot. The Commercial Growth OS itself is unchanged.

## Root cause

The runtime already derived parent authority, delegation depth, ancestry, and accountable owner from canonical TaskLedger and Agent Registry state. The published input contract nevertheless required callers to supply `parent_authority` and `depth`, while plausible mismatches such as `active_owner=cos` or CoS registry L3 instead of parent-task L2 collapsed to generic `forbidden`.

The attempted `skills.invoke_governed(mesh-cro)` call also used the wrong abstraction. Skills are capabilities; CRO is an agent principal. Governed agent execution uses `delegation.execute_owner`.

## Material changes

- `delegation.create` now requires only the delegation work contract. Server-derived fields remain optional fail-closed compatibility assertions.
- Stable safe reason codes classify common delegation failures without exposing raw policy internals.
- `skills.invoke_governed` explicitly rejects registered agent aliases as `unsupported-capability-type`.
- Chief of Staff guidance now routes agent work through `delegation.execute_owner` and records explicit parent reconciliation after child completion.
- Full CoS -> CRO -> CoS regression coverage proves owner attribution, check-in, completion, independent verification, audit integrity, and parent-state separation.
- Superseded v4.10.0, v4.11.0, and v4.12.0 publishers are frozen to immutable historical verification.

## Preserved boundaries

- exactly 10 Phase 1 agents;
- canonical authority/runtime contract 4.0.0;
- TaskLedger canonical operating state;
- server-derived agent identity;
- no CoS impersonation;
- child authority cannot exceed parent authority;
- L4 requires qualified human approval and L5 remains Michael-only;
- external action remains separately governed;
- `COMPLETED != VERIFIED`;
- child completion never automatically completes or verifies the parent.

## Release identity

Repository release: `v4.12.1`.

Production QNAP deployment remains `4.4.0` until the exact current-source candidate attached to this release is promoted through the governed QNAP procedure and Secure MCP readback confirms its source commit and publication schema. Repository publication alone is not production deployment.

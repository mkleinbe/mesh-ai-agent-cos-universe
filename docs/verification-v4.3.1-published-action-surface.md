# Verification: PF-058 Published MCP Action Surface

## Candidate

Branch: `fix/published-mcp-action-surface`

The repository candidate adds no new MCP runtime authority. It adds an external-publication verification control and regression coverage for the frozen ChatGPT workspace action snapshot.

## Requirements and evidence

| Requirement | Evidence | Disposition |
| --- | --- | --- |
| Canonical MCP catalog includes owner executor | `chatgpt/mcp/mesh-cos-mcp.v1.json` contains `delegation.execute_owner` | PASS |
| CoS source allowlist includes owner executor | canonical CoS allowlist includes `delegation.execute_owner` | PASS |
| Human-only actions remain excluded from CoS machine surface | `approval.record_decision`, `reliability.human_override` are human-only | PASS |
| Expected CoS published surface is exact and derivable | `scripts/check-published-action-surface.py` derives 28 actions from canonical contract | PASS |
| Missing owner executor is detectable | integration regression supplies 27-action snapshot and expects failure | PASS when CI green |
| Exact expected snapshot succeeds | integration regression supplies exact 28-action snapshot and expects pass | PASS when CI green |
| All active owners retain lifecycle paths | existing `check-owner-execution-readiness.py` | PASS when CI green |
| Nested routes remain bounded | CMO -> VP Content; COO -> Consultant Network Steward only | PASS |
| Live workspace connector exposes exact 28 | current connector exposes 27 | BLOCKED |
| Blocked logical occurrences resume without replacement | exact keys preserved in TaskLedger | READY AFTER LIVE ACCEPTANCE |

## Independent production acceptance

After workspace admin publication refresh/recreation:

1. Re-read the Mesh CoS MCP connector action catalog.
2. Require exactly 28 CoS machine actions.
3. Require `delegation.execute_owner` present.
4. Require both human-only actions absent.
5. Re-run registry.list_agents and require 10 ACTIVE agents with canonical parentage.
6. Re-run governance.verify_audit_chain and require valid.
7. Execute one bounded direct CMO-owned lifecycle through `delegation.execute_owner` with no external action.
8. Execute one bounded nested route `cos -> cmo -> vp-content` and one `cos -> coo -> consultant-network-steward` using synthetic/internal work only.
9. Prove parent direct completion of child-owned task is denied.
10. Prove owner completion succeeds and verification remains separate.
11. Resume the two outstanding Marketing execution keys in place.

## Current disposition

**REPOSITORY CANDIDATE: VERIFYING**

**PRODUCTION: BLOCKED_EXTERNAL_PUBLISH_SNAPSHOT**

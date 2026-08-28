# Security Review: PF-058 Published MCP Action Surface

## Applicability

**TARGETED**. The defect crosses MCP publication, agent authorization, delegation, server-derived identity, and consequential tool execution boundaries.

## Trust boundaries

1. ChatGPT workspace-approved custom MCP app action snapshot.
2. Secure MCP Tunnel transport.
3. QNAP-hosted Mesh CoS MCP server.
4. Bound external principal `cos`.
5. Canonical Agent Registry and per-agent tool allowlists.
6. `delegation.execute_owner` server-owned owner derivation boundary.
7. TaskLedger and inherited approval state.
8. Human-only approval/override operations.

## Security properties

- The ChatGPT published CoS action surface must equal the canonical CoS machine allowlist exactly.
- `approval.record_decision` and `reliability.human_override` remain excluded from the agent action snapshot.
- `delegation.execute_owner` accepts no caller-supplied principal and must derive the accountable owner from canonical task/delegation state.
- Child policy/allowlist is reapplied server-side before execution.
- Parent approval gates are inherited and may not be weakened by publication changes.
- Missing published actions fail closed before child-owned canonical intake/execution.
- Unexpected published actions also fail closed under exact-set validation.
- No prompt, Sheet value, retrieved content, or task metadata can substitute for authenticated owner identity.

## Findings

### SEC-PF058-001 - Frozen ChatGPT action snapshot omits required owner executor

- Severity: HIGH operational/security-governance defect.
- Evidence: source contract contains 30 tools, with 28 CoS machine tools and 2 human-only tools; live ChatGPT connector exposes 27 machine actions and omits exactly `delegation.execute_owner`.
- Consequence: governed child-owned work fails closed and cannot complete under canonical owner identity. No unauthorized execution occurs.
- Remediation: recreate/republish the Business custom MCP app or refresh/enable actions on Enterprise/Edu, then prove exact 28-action equality.
- Status: **BLOCKED_EXTERNAL_PUBLISH_SNAPSHOT** until workspace publication is updated.

### SEC-PF058-002 - Release verification did not bind workspace-approved action snapshot

- Severity: MEDIUM process defect.
- Evidence: v4.3.0 source/container verification proved local MCP `tools/list`, but the workspace app approval snapshot is independently frozen by ChatGPT and was not part of the release gate.
- Remediation: added `scripts/check-published-action-surface.py` plus regression coverage; production acceptance now requires an actual workspace action snapshot comparison.
- Status: **REMEDIATED_IN_REPOSITORY**, pending external publication acceptance.

## Residual risk

No evidence of privilege expansion, owner impersonation, human-approval bypass, or unauthorized external action. The current failure mode is fail-closed. Production remains functionally blocked for child-owned task execution until the workspace action snapshot is corrected.

## Disposition

**SECURITY PASS FOR REPOSITORY HARDENING / PRODUCTION BLOCKED ON WORKSPACE ACTION SNAPSHOT**.

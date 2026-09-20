# Security Review v4.12.1: CoS Delegation and Agent Reporting

**Review class:** FULL_REVIEW  
**Authority contract:** 4.0.0, unchanged  
**Agent roster:** exactly 10, unchanged  
**External-action authority:** unchanged

## Trust-boundary finding

The existing server-owned owner executor is the correct identity boundary. It derives the accountable agent from canonical delegation/task state and reapplies the recipient's allowlist. The caller cannot select an arbitrary principal.

The defect was at the request and diagnostic boundary: server-derived assertions were published as required caller inputs and mismatches collapsed to generic errors.

## Controls after remediation

- `parent_authority`, `depth`, `ancestry`, and `active_owner` are optional compatibility assertions only.
- Omission cannot widen authority because canonical values are derived server-side.
- Supplied assertions still fail closed on mismatch.
- Direct-child, owner/task, depth, action, capability, approval, and authority monotonicity checks remain active.
- Agent names passed through the Skill invocation API are rejected. A Skill never becomes a principal.
- Stable reason codes expose bounded classification only, not raw exception text, secrets, or policy internals.
- Parent reconciliation is an explicit CoS check-in and cannot silently complete or verify the parent.
- L4/L5 and external-action gates are unchanged.

## Threat tests

The release regression battery covers caller assertion tampering, invalid recipient, ownership conflict, authority widening, delegated owner identity, cross-agent Skill misuse, completion/verification separation, audit integrity, and no automatic parent elevation.

## Disposition

No authority expansion is introduced by this patch. Production acceptance still requires exact-source QNAP promotion and Secure MCP readback because the repository and live QNAP deployment are separate release domains.

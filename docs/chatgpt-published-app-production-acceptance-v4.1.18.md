# Mesh CoS MCP Published App Production Acceptance v4.1.18

## Scope

This acceptance proves the live QNAP v4.1.18 deployment after remediation of `SEC-4.1.18-001`. It inherits the v4.1.17 Slack Bot + Block Kit HITL behavior contract and adds explicit proof that the protected bot OAuth credential is readable by the non-root runtime without weakening file protections.

## Preconditions

- QNAP deployment release reports `4.1.18`.
- Canonical MCP runtime/product version reports `4.0.0`.
- `mesh-cos-mcp` and `mesh-cos-tunnel` are healthy.
- `/readyz` reports `slack_hitl_ready=true`.
- The protected bot credential remains mode `0400` and is readable by runtime UID/GID `65532:65532`.
- The Slack app identity is **ChatGPT Enterprise AI Agent**.
- No credential value is printed, logged, copied into a prompt, or persisted outside the protected secret boundary.

## Required acceptance

1. Verify the published Mesh CoS MCP app exposes exactly 27 CoS tools and the canonical 10-agent roster.
2. Verify TaskLedger and audit-chain integrity before synthetic acceptance activity.
3. Create a synthetic PENDING L4 approval with canonical principal `michael` and an immutable payload fingerprint.
4. Post the approval through the governed `slack-adapter` and dedicated Slack bot API path.
5. Verify the Slack message is visibly authored by **ChatGPT Enterprise AI Agent** and returns a canonical root thread binding.
6. Verify the approval remains PENDING until a provider-authenticated human interaction occurs.
7. Verify **Approve**, **Deny**, and **Change** buttons plus case-insensitive thread-reply fallbacks.
8. Verify wrong-user, wrong-channel, app/bot-authored, unbound-thread, stale-value, malformed, and conflicting second decisions fail closed.
9. Verify replay of the same provider event is idempotent.
10. Verify **Change** captures requirements input, supersedes the old approval, returns the task to `IN_PROGRESS`, and requires a new immutable approval.
11. Verify audit-chain integrity after synthetic writes.
12. Do not execute any consequential real-world action during acceptance.

## Pass rule

Production acceptance is PASS only when the actual QNAP serving instance demonstrates all required checks with no open CRITICAL/HIGH defect or required acceptance blocker. Repository CI, a release artifact, or a healthy container alone is not sufficient.

# v4.1.15 Published App Production Acceptance

Run only after the v4.1.15 QNAP release is deployed.

## QNAP runtime

- Active deployment release is `4.1.15` and image provenance matches the released commit.
- `mesh-cos-mcp` and `mesh-cos-tunnel` are healthy.
- MCP remains at `192.168.7.60` on qnet `lan7`.
- MCP has no direct host port exposure.
- Shared `mesh-cos-private` is internal-only.
- Tunnel has its dedicated egress bridge and still reaches MCP privately as `172.30.60.3`.
- TaskLedger path, integrity, and pre-upgrade state are preserved.
- OpenAI Secure MCP Tunnel identity/runtime key are preserved.
- Only the approver identity and Slack `xapp-` token are mounted for Slack HITL. A legacy `slack-verifier-token` file, if present on the host, is unused and unmounted.

## Runtime degradation

Temporarily demonstrate or otherwise verify that loss of Slack connectivity does not terminate the MCP process. During loss:

- `/healthz` remains HTTP 200 with `slack_hitl_ready=false`.
- `/readyz` is HTTP 503.
- consequential human approval remains unavailable.
- reconnect attempts are bounded rather than a tight loop.
- restoration of Slack connectivity returns readiness without restarting the MCP process.

## Published MCP surface

- Exactly 10 governed agents are present.
- CoS agent-facing MCP tool catalog remains exactly the governed catalog expected by the v4.0.0 runtime contract.
- Human-only `approval.record_decision` and `reliability.human_override` are not agent-callable.
- `skills.invoke_governed` `slack-adapter` returns only a collaboration-only connected Slack handoff.
- Attempts to carry `approved`, `actor`, `principal`, or decision-recording authority through `slack-adapter` fail closed.

## Connected Slack collaboration

Use the connected Slack integration to post a synthetic, non-consequential approval request into `#mesh-agent-ops`. Confirm the canonical TaskLedger approval remains `PENDING` after the message appears. Ordinary message content, reactions, copied commands, and user-attributed plugin writes must not change canonical approval state.

## Authenticated human approval

For a synthetic non-consequential approval with an immutable payload fingerprint:

1. MK executes `/mesh-approval APPROVE <Approval ID>` in `#mesh-agent-ops`.
2. QNAP receives a provider-authenticated `slash_commands` Socket Mode envelope.
3. The canonical approval changes from `PENDING` to `APPROVED` with canonical principal `michael`.
4. The durable Slack decision record contains provider envelope/trigger identifiers and the canonical payload fingerprint, but does not store the protected Slack token or rely on a notice-thread binding.
5. Replaying the same envelope is idempotent.
6. A distinct second decision, wrong user, wrong channel, wrong command, ordinary message, or fingerprint-less canonical approval fails closed.

## Completion semantics

Confirm a task can be `COMPLETED` without becoming `VERIFIED`, and that independent verification remains required before the verified state.

Production acceptance is PASS only when all sections above are evidenced against the live deployed v4.1.15 environment.

# v4.1.15 QNAP Slack Plugin HITL Simplification

## Purpose

v4.1.15 removes the unnecessary Slack verifier-bot layer and makes the connected Slack integration the collaboration surface. The custom Slack app remains only as the provider-authenticated `/mesh-approval` Socket Mode ingress for consequential human decisions.

The release also closes two QNAP production defects exposed during the engineering loop: ambiguous multi-network egress under Docker Engine 27, and incomplete recovery when a candidate fails during or after active-configuration promotion.

## Changes

- Removes the runtime `xoxb-` verifier credential, bot-authored notice verification, notice-author allowlist, thread-read verification, and approval-notice binding dependency.
- Keeps the governed human approver identity, canonical principal `michael`, `/mesh-approval`, and one protected `xapp-` Socket Mode app-level token.
- Changes the CoS `slack-adapter` to a collaboration-only `CHATGPT_CONNECTOR_HANDOFF` using `operation: handoff`; it cannot carry or record human approval authority.
- Requires the canonical approval action to contain an immutable 64-hex `payload_fingerprint` before a Socket Mode decision can be recorded.
- Makes Slack provider/network failure non-fatal to the MCP HTTP process. `/healthz` remains available, `/readyz` fails closed while HITL is unavailable, and Socket Mode reconnect uses bounded exponential backoff.
- Makes the shared MCP/tunnel Docker bridge internal-only and adds a dedicated tunnel egress bridge. This removes ambiguous external default-route selection on QNAP Docker Engine 27 while keeping the MCP fixed qnet address `192.168.7.60` and private tunnel source `172.30.60.3`.
- Restores the previously active Compose stack when candidate activation or pre-promotion health verification fails.
- Snapshots active `.env`, Compose, and release metadata before promotion. Partial promotion or post-promotion verification failure restores the exact snapshot and previous active stack.
- Preserves the rollback snapshot if recovery itself is incomplete and constrains snapshot cleanup paths.
- Defines successful post-deploy verification as the promotion transaction commit point. Snapshot cleanup happens only after verification.

## BDD coverage

Ready scenarios QNAP-104 through QNAP-111 cover collaboration-only Slack, authenticated human approval, adversarial Slack inputs, provider degradation, minimum Slack secret, Docker Engine 27 routing, pre-promotion recovery, and transactional post-promotion rollback.

## Preserved invariants

- Canonical Phase 1 runtime release remains `4.0.0`.
- Exactly 10 governed agents remain in the organization.
- Message Operations remains agent 10; Devil's Advocate remains a shared Skill rather than agent 11.
- CoS governed MCP projection and human-only operation boundaries remain unchanged in authority.
- Human-only approval authority remains outside the agent-callable MCP catalog.
- `COMPLETED != VERIFIED`.
- SQLite TaskLedger remains canonical.
- OpenAI Secure MCP Tunnel remains production ingress with no direct MCP host-port exposure.
- QNAP qnet address remains `192.168.7.60`.
- Tunnel identity, TaskLedger, and protected secrets remain outside versioned release payloads.

## Upgrade

The existing `slack-verifier-token` host file may remain for rollback compatibility with v4.1.14 and earlier. v4.1.15 does not mount, validate, prompt for, or use it.

The only Slack application credential needed by the v4.1.15 QNAP runtime is the existing `xapp-` Socket Mode app-level token. No new Slack credential should be created for this release.

Normal deployment remains:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.15/mesh-cos-mcp-deploy.sh
```

## Acceptance boundary

Repository, CI, bundle, container, security, and release verification establish release-engineering readiness only. Live QNAP network behavior, hosted MCP behavior, and a real provider-authenticated Slack `/mesh-approval` interaction must still be verified against the deployed production candidate before production acceptance is declared.

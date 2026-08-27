# v4.1.15 Engineering Contract

## Classification

Primary class: architecture/refactor with a production defect remediation.

## Outcome

Use the connected Slack integration as the collaboration and approval-notification surface. Retain the custom Slack app only as a narrow provider-authenticated `/mesh-approval` Socket Mode ingress for consequential human decisions.

## In scope

- Remove the Slack verifier bot token and bot-authored notice verification from the QNAP runtime.
- Remove verifier-token provisioning, mounts, preflight requirements, and deployment prompts.
- Preserve the configured human Slack principal and `xapp-` Socket Mode app token.
- Preserve `/mesh-approval` as the only Slack interaction eligible to become canonical human approval.
- Keep ordinary Slack messages non-authoritative.
- Preserve immutable payload fingerprint checks, canonical TaskLedger state, replay protection, user/channel/command checks, and `COMPLETED != VERIFIED`.
- Make Slack provider/network unavailability non-fatal to MCP process startup while readiness remains fail-closed for consequential HITL.
- Add bounded reconnect/backoff behavior so transient Slack network failures do not crash-loop the MCP container.
- Preserve QNAP qnet identity, tunnel identity, TaskLedger, secrets outside release payloads, and production ingress architecture.

## Out of scope

- Giving the connected Slack integration authority to decide approvals.
- Allowing ordinary messages, reactions, copied text, or agent-authored Slack content to satisfy human approval.
- Changing the canonical TaskLedger approval model.
- Changing the 10-agent roster, CoS tool catalog, Secure MCP Tunnel ingress, or human-only MCP boundaries.

## Acceptance criteria

The ready scenarios in `specs/qnap-slack-plugin-hitl-v4.1.15.feature` are authoritative. All existing affected Slack HITL, QNAP deployment, MCP, approval, security, and release tests must remain green or be deliberately superseded by the new ready contract.

## Security applicability

FULL_REVIEW. This change alters authentication/authorization semantics for consequential actions, Slack OAuth/app credentials, external network behavior, MCP runtime readiness, deployment/runtime controls, and AI-native connector/tool boundaries.

## Security properties

1. Only a provider-authenticated `slash_commands` Socket Mode envelope from the configured MK Slack user, governed channel, and exact `/mesh-approval` command can become canonical human authority.
2. Agent-callable tools and ordinary Slack messages cannot record human approval.
3. The connected Slack integration may notify/read/write collaboration content but has no approval-recording authority.
4. Approval remains bound to the canonical TaskLedger record and immutable payload fingerprint.
5. Socket envelope replay/conflict fails closed.
6. Only the minimum QNAP Slack secret remains required: the `xapp-` Socket Mode app-level token. No `xoxb-` verifier credential is required.
7. Protected credential values are never logged, committed, or included in release artifacts.
8. Slack network/provider failure cannot terminate the MCP HTTP process. It must degrade readiness for HITL and keep consequential actions blocked.
9. Retry behavior is bounded and non-recursive, with reconnect state observable without secret disclosure.

## Evidence model

BDD is the outer contract. Each changed behavior receives RED evidence before implementation, then GREEN, refactor, affected regression, targeted security checks, full repository CI, exact release-bundle verification, and post-merge verification against the resulting commit.

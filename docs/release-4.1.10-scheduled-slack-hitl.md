# Release v4.1.10: Scheduled Automation and Slack HITL Hardening

## Release purpose

v4.1.10 closes the production-acceptance defects discovered after moving active Scheduled Tasks to Mesh CoS MCP canonical execution. It hardens exact-once scheduled task identity, canonical lifecycle progression, official OpenAI bot-authored Slack notices, provider-authenticated human approval ingress, protected QNAP Slack configuration, and current security documentation.

The canonical Phase 1 authority/runtime contract remains `4.0.0`. The workforce remains exactly 10 agents and the CoS MCP projection remains 27 governed tools. This patch does not widen L4/L5 authority or expose human-only tools to agents.

## Required behaviors

The ready behavior contract is `specs/scheduled-automation-slack-hitl-v4.1.10.feature`, scenarios SCH-HITL-001 through SCH-HITL-007.

The release must establish:

1. Every logical scheduled occurrence supplies its immutable execution identity as `task.intake.idempotency_key`.
2. New scheduled execution tasks progress through the valid canonical lifecycle before completion and are verified separately.
3. A governed Slack HITL parent is accepted only when Slack provider state attributes it to the official ChatGPT or ChatGPT Agents bot identity.
4. Ordinary Slack messages are non-authoritative for human approval, even when attributed to the deployment-configured human Slack identity.
5. Canonical Slack human decisions enter only through an authenticated Socket Mode `slash_commands` envelope for `/mesh-approval`, then pass channel, protected identity, Approval ID, notice binding, and fingerprint checks inside a non-MCP service.
6. Wrong actor, channel, command, Approval ID, fingerprint, duplicate/conflicting decision, human-authored parent, or bot impostor fails closed.
7. The generic user-scoped Slack connector is never used to author governed HITL notices or satisfy the human-approval boundary.
8. Production preflight requires the bot-notice verifier and Socket Mode human-ingress controls and never exposes protected values.

## Implementation

- `mesh_cos.slack_hitl.SlackApprovalHITLService` now performs **notice verification and binding only**.
- Removed agent-accessible free-text Slack decision ingestion. The CoS `slack-adapter` accepts `bind_notice` only.
- Added `mesh_cos.slack_socket_approval.SlackSocketApprovalService` as the provider-interactive human-decision service.
- Added non-MCP `mesh_cos.slack_socket_bridge` for bounded local delivery of trusted Socket Mode envelopes to the canonical ledger.
- Added `mcp/src/slack-socket-mode.ts`, which opens the outbound Slack Socket Mode connection using a protected app-level `xapp-` token, ignores ordinary message events, and forwards only `slash_commands` envelopes.
- Runtime readiness now fails closed when Slack HITL is required and the Socket Mode connection is inactive.
- Direct `approval.record_decision` remains human-only and denied to agents.
- Added file-mounted approver identity, read-only verifier bot credential, and Socket Mode app-level credential support.
- Added QNAP Slack HITL provisioning and hardened ownership/mode handling for all governed secret files.
- Updated active Scheduled Task prompts for explicit idempotency and lifecycle semantics.
- Reconciled current `SECURITY.md`, Slack protocol, security review, BDD, and production acceptance documentation.

## Security

Security applicability is TARGETED. See `docs/qnap-security-review-v4.1.10.md`.

A critical attack-path correction is part of this release. Matching `message.user` on an ordinary Slack message is not accepted as proof of human presence because Slack applications can post with user attribution. The candidate therefore removes ordinary message ingestion from the canonical approval path instead of trying to harden its text parser.

No verifier token, Socket Mode app token, or human Slack identifier is committed to source, stored as a value in generated `.env`, packaged in release assets, or copied into TaskLedger evidence. Official OpenAI bot user IDs are non-human service identities used only as allowlisted provider-author evidence.

Agents cannot submit an approval boolean, actor override, principal override, arbitrary Slack payload, or human decision through the governed adapter. The human interaction service is deliberately outside the agent-callable MCP surface.

## Repository verification gate

The exact final candidate must pass:

```text
pip check
npm ci / npm run check, including Socket Mode transport tests
contract validation
runtime/documentation drift checks
ChatGPT package checks
Ruff
mypy
pytest with 100% branch-aware mesh_cos coverage
Bandit high-severity gate
compileall
QNAP shell regressions
v4.1.10 deterministic bundle/checksum
Compose validation
OCI version/revision provenance
modern MCP discovery and sequential requests
non-root/read-only/capability-dropped runtime
protected file ownership and read-only mount tests
direct-ingress denial
restart and persistence
SQLite backup integrity
```

## Production acceptance boundary

A repository-green v4.1.10 candidate is not sufficient to certify production. After deployment to QNAP, execute `docs/chatgpt-published-app-production-acceptance-v4.1.10.md` and require:

- `mcp_version=4.0.0`, `deployment_release=4.1.10`, `agent_id=cos`;
- exactly 10 active agents and valid audit chain;
- exact-once scheduled intake and valid lifecycle evidence;
- one synthetic non-consequential HITL notice provider-authored by the official OpenAI Slack bot/agent;
- active Socket Mode readiness;
- one synthetic `/mesh-approval APPROVE <Approval ID>` interaction from MK against the bound synthetic request;
- fresh `approval.get` showing the canonical synthetic decision;
- no ordinary Slack message is able to create the approval;
- no unauthorized Gmail or other external action;
- TaskLedger operating mirror reconciled to canonical state when the exact connector is available.

If the official OpenAI Workspace Agent is not deployed to `#mesh-agent-ops`, record `BLOCKED_CHATGPT_AGENT_TRANSPORT`; do not substitute a custom bot or human-authored message. If Socket Mode or `/mesh-approval` is unavailable, fail the approval path closed and do not infer authority from ordinary Slack text.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.10.zip`
- `mesh-cos-mcp-qnap-v4.1.10.zip.sha256`

The bundle must include the current v4.1.10 security review, release handoff, hosted acceptance procedure, ready scheduled/Slack HITL specification, QNAP protected Slack configuration script, Socket Mode transport sources, and release-bound build context. It must contain no runtime secrets, human Slack identifier, or canonical TaskLedger data.

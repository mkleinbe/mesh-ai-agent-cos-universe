# v4.1.10 Scheduled Automation and Slack HITL Hardening

`v4.1.10` is the production-hardening release for Mesh Scheduled Tasks that use the QNAP-hosted **Mesh CoS MCP** runtime and Slack human approval boundary.

The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly 10 registered agents and 27 governed CoS MCP tools. Human-only operations remain human-only. This release does not widen L4/L5 authority.

Roster identity remains explicit: Message Operations (`message-ops`) is one of the 10 registered agents. Mesh Devil's Advocate remains an external governed shared Skill and is not an agent principal, task owner, or approval authority.

## Why this release exists

Post-v4.1.8 production acceptance exposed five material integration defects:

1. Scheduled prompts described `task.intake` as idempotent but did not pass an explicit `idempotency_key`; repeated identical intake could create duplicate canonical tasks.
2. Scheduled prompts omitted required canonical lifecycle transitions before `task.complete`.
3. Slack approval notifications could be authored through the user-scoped connector as the human user instead of the official OpenAI bot identity.
4. Slack human approval had no bounded trusted server-side path into canonical approval state while `approval.record_decision` correctly remained human-principal-only.
5. The first v4.1.10 remediation incorrectly treated ordinary Slack user attribution as proof of human presence. Slack applications can post with user attribution, so the message-to-human-authority path had to be removed rather than merely filtered.

v4.1.10 closes the repository/runtime portions of those defects and adds the hosted acceptance needed to prove the remaining OpenAI Workspace Agent delivery and Socket Mode boundaries in production.

## Core changes

- Scheduled logical occurrences now use immutable execution keys as explicit `task.intake.idempotency_key` values.
- Scheduled execution follows `INTAKE -> TRIAGED -> PLANNED -> ASSIGNED -> IN_PROGRESS -> QA -> COMPLETED`, followed by separate CoS verification.
- `SlackApprovalHITLService` provider-verifies and binds an official ChatGPT/ChatGPT Agents bot-authored parent notice only.
- Removed agent-accessible free-text Slack human-decision ingestion.
- Added an outbound Slack Socket Mode listener authenticated with a protected app-level `xapp-` credential.
- Added a dedicated `/mesh-approval` slash-command human-interaction boundary delivered to a non-MCP local service.
- The human Slack identity for MK is protected deployment configuration and maps to canonical principal `michael` only inside that trusted interaction boundary.
- Reused existing `skills.invoke_governed` / `slack-adapter` for `bind_notice` only; no new MCP tool or agent approval authority was added.
- Direct `approval.record_decision` remains human-only and denied to agents.
- QNAP now file-mounts the human identity, provider-verifier bot credential, and Socket Mode app-level credential as protected read-only runtime files.
- Production runtime readiness fails when Slack HITL is required but the Socket Mode connection is inactive or the required verification boundary cannot initialize.
- Governed QNAP secret permissions cover tunnel, Slack approver-identity, Slack verifier, and Slack Socket Mode app-token files at runtime UID/GID with mode `0400`.
- Active Scheduled Task prompts now treat ordinary Slack messages as evidence only and read canonical human decision state through `approval.get`.
- Current `SECURITY.md`, Slack protocol, BDD scenarios, QNAP preflight, release documentation, and acceptance procedures are reconciled to the current 10-agent Secure MCP Tunnel topology.

## Security boundary

Security applicability is **TARGETED**. See `docs/qnap-security-review-v4.1.10.md`.

The official OpenAI Slack bot identities are used only as allowlisted provider-author evidence. The personal human Slack ID, verifier token, and Socket Mode app token are not committed, logged, stored as values in generated `.env`, or packaged in release assets.

Ordinary Slack messages, reactions, copied approval text, and user-attributed posts are non-authoritative for L4/L5 approval. The human decision ingress is deliberately outside the agent-callable MCP surface. It accepts only provider-interactive Socket Mode `slash_commands` envelopes for `/mesh-approval` and validates the governed channel, protected human identity, exact Approval ID, PENDING canonical approval, provider-verified OpenAI bot notice binding, payload fingerprint, and replay state before recording canonical principal `michael`.

If the official OpenAI Workspace Agent delivery surface is unavailable, the governed notice action fails closed as `BLOCKED_CHATGPT_AGENT_TRANSPORT`; the system must not fall back to posting the notice as MK. If Socket Mode human ingress is unavailable, approval remains PENDING and no ordinary Slack text substitutes for it.

## BDD and TDD evidence

Ready scenarios SCH-HITL-001 through SCH-HITL-007 are defined in `specs/scheduled-automation-slack-hitl-v4.1.10.feature` and cover:

- canonical scheduled idempotency;
- lifecycle separation;
- official OpenAI bot notice authorship;
- Socket Mode provider-authenticated human decision mapping;
- fail-closed negative identity/binding controls;
- prohibition on user-scoped Slack impersonation or ordinary-message approval;
- production preflight of the full Slack HITL boundary.

TDD coverage includes positive and negative bot notice tests, immutable execution identity, lifecycle progression, direct-human-tool denial, notice-only adapter schema closure, Socket Mode transport, non-MCP human-ingress validation, protected file loading, secret non-disclosure, QNAP permission handling, Compose mounts, and runtime readiness.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.10.zip`
- `mesh-cos-mcp-qnap-v4.1.10.zip.sha256`

The bundle contains the release-bound build context, QNAP operator tooling, v4.1.10 release/security/hosted-acceptance records, ready scheduled/Slack HITL behavior specification, and historical release evidence. It contains no runtime secret, personal Slack identifier, generated `.env`, or canonical TaskLedger data.

## Version identity

- Repository/QNAP deployment release: `4.1.10`
- Semantic tag: `v4.1.10`
- Container image label default: `4.1.10-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Workforce: exactly 10 agents
- CoS agent-facing catalog: 27 governed tools
- Production transport: OpenAI Secure MCP Tunnel
- Human Slack approval ingress: authenticated Slack Socket Mode `/mesh-approval`

Successful hosted readiness after deployment must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.10
agent_id: cos
slack_hitl_ready: true
```

## Verification gate

The exact final candidate must pass dependency integrity, TypeScript MCP checks including Socket Mode tests, npm audit, contract/documentation/package drift checks, Ruff, mypy, 100% branch-aware Python coverage, Bandit, compileall, QNAP shell regressions, deterministic bundle/checksum generation, Compose validation, OCI provenance, modern MCP discovery/sequential requests, protected Slack HITL configuration/readiness controls, non-root/read-only runtime controls, direct-ingress denial, restart/persistence, and SQLite backup integrity.

## Post-deploy acceptance boundary

Repository, container, and release-package verification cannot prove the actual on-premises serving instance, official OpenAI Workspace Agent Slack delivery configuration, or live Slack Socket Mode interaction path.

After deploying v4.1.10, execute `docs/chatgpt-published-app-production-acceptance-v4.1.10.md`. Production certification requires the live official bot-authored synthetic HITL notice, proof an ordinary APPROVE message remains non-authoritative, live `/mesh-approval` Socket Mode decision, canonical approval readback, valid audit chain, no unauthorized external action, and required TaskLedger operating-mirror reconciliation.

Do not certify production while any CRITICAL/HIGH defect or required live acceptance blocker remains open.

See:

- `docs/qnap-security-review-v4.1.10.md`
- `docs/verification-v4.1.10-scheduled-slack-hitl.md`
- `docs/release-4.1.10-scheduled-slack-hitl.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.10.md`
- `specs/scheduled-automation-slack-hitl-v4.1.10.feature`
- `docs/slack-agent-protocol.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

# QNAP Security Review v4.1.10

## Scope

Release `v4.1.10 Scheduled Automation and Slack HITL Hardening` changes scheduled-execution identity/lifecycle controls, Slack approval trust boundaries, server-owned provider verification, provider-authenticated human interaction ingress, QNAP protected runtime configuration, and production readiness. The canonical Phase 1 authority/runtime contract remains `4.0.0` with exactly 10 registered agents and 27 CoS MCP tools.

Security applicability is **TARGETED** because authentication/identity, human approval, Slack provider integration, protected credentials, MCP governed invocation, consequential action gates, QNAP deployment configuration, and persistence are touched.

## Trust boundaries reviewed

1. Scheduled Task -> canonical MCP TaskLedger execution identity.
2. CoS agent -> `skills.invoke_governed` -> server-owned `slack-adapter` for bot-notice verification only.
3. Official OpenAI Slack bot parent notice -> Slack provider state.
4. Slack Socket Mode app-level connection -> provider interactive `slash_commands` envelope.
5. Protected human Slack identity -> canonical principal `michael` inside the non-MCP human ingress.
6. Slack provider verifier credential -> `conversations.replies` read path.
7. Canonical approval decision -> consequential Gmail execution gate.
8. QNAP host protected files -> non-root application runtime.
9. OpenAI Secure MCP Tunnel -> remote MCP ingress.

## Findings and remediation

### SEC-QNAP-030 HIGH: scheduled canonical task intake was not actually idempotent

**Evidence:** repeated `task.intake` calls with the same execution identity created distinct tasks when no `idempotency_key` was supplied. The runtime already supported explicit idempotency keys.

**Remediation:** every governed scheduled occurrence now derives `<Job ID>:<logical due timestamp>` and passes that exact value as `task.intake.idempotency_key`. Regression coverage proves repeated intake resolves the same canonical task.

**Status:** RESOLVED, repository verification required on final release commit.

### SEC-QNAP-031 HIGH: scheduled task lifecycle omitted required canonical transitions

**Evidence:** `task.complete` on a fresh INTAKE task failed `invalid_state`. Production prompts previously did not explicitly traverse the canonical lifecycle.

**Remediation:** scheduled execution contracts now require `INTAKE -> TRIAGED -> PLANNED -> ASSIGNED -> IN_PROGRESS -> QA`, followed by `task.complete` and a separate `task.verify`. Regression coverage proves the valid sequence and `COMPLETED != VERIFIED`.

**Status:** RESOLVED, repository verification required on final release commit.

### SEC-QNAP-032 HIGH: user-scoped Slack writes could misrepresent governed HITL notice authorship

**Evidence:** the generic Slack connector posts as the connected human user. Historical approval messages were therefore authored by the human account even when initiated from ChatGPT. A live non-consequential mention probe did not establish a bot-authored ChatGPT Agents reply.

**Remediation:** governed HITL notices are valid only when Slack provider evidence identifies the parent author as the official ChatGPT or ChatGPT Agents Slack identity. User-authored messages, custom bots, and copied display names fail closed. Scheduled jobs must not fall back to posting notices as the human user. If the official Workspace Agent delivery surface is unavailable, the affected action is `BLOCKED_CHATGPT_AGENT_TRANSPORT`.

**Residual platform gate:** the official OpenAI Workspace Agent must still be deployed/configured to `#mesh-agent-ops` and must produce a provider-verified bot-authored acceptance notice before production certification.

**Status:** CODE/CONTROL RESOLVED; LIVE PLATFORM ACCEPTANCE BLOCKED until bot-authored evidence exists.

### SEC-QNAP-033 CRITICAL: canonical Slack human approval had no trusted server-side ingress

**Evidence:** `approval.record_decision` is intentionally human-principal-only. A workflow that only observes Slack text cannot safely convert that text into canonical approval without either agent impersonation or a separate trusted human ingress.

**Remediation:** v4.1.10 now splits the approval path. `SlackApprovalHITLService` only verifies and binds the official OpenAI bot-authored notice. Canonical human decisions enter through `SlackSocketApprovalService`, which is invoked by a non-MCP local bridge from an authenticated Slack Socket Mode `slash_commands` envelope for `/mesh-approval`. The CoS cannot invoke this bridge or provide an approval boolean.

**Status:** RESOLVED in candidate; live Socket Mode acceptance required.

### SEC-QNAP-034 MEDIUM: personal human Slack ID appeared in early remediation source/tests

**Evidence:** initial RED fixtures hard-coded the production human Slack ID, conflicting with repository Slack data-handling policy.

**Remediation:** production human identity is deployment configuration only. QNAP mounts it from a protected host file. Source/spec/tests use non-personal fixtures. Current documentation prohibits committing or logging the personal identifier.

**Status:** RESOLVED; final diff must be searched before release.

### SEC-QNAP-035 HIGH: shared QNAP permission helper did not cover every Slack HITL protected file

**Evidence:** the existing helper originally normalized only the tunnel key, and an intermediate remediation covered the approver/verifier files but not the new Socket Mode app-level credential.

**Remediation:** the constrained Docker permission helper now normalizes the exact governed filenames `openai-tunnel-runtime-key`, `slack-approver-user-id`, `slack-verifier-token`, and `slack-socket-app-token` to runtime UID/GID with mode `0400`. Regression coverage asserts all four targets.

**Status:** RESOLVED, final QNAP integration verification required.

### SEC-QNAP-036 HIGH: current `SECURITY.md` had stale v3.0.0 / 9-agent / local-only policy

**Evidence:** repository security policy contradicted the live 10-agent Phase 1 model and Secure MCP Tunnel production topology.

**Remediation:** current security policy is reconciled to the 10-agent, 27-tool, dual local/remote topology and includes the Slack HITL provider-verification boundary.

**Status:** RESOLVED.

### SEC-QNAP-039 CRITICAL: Slack user attribution was incorrectly treated as proof of human presence

**Evidence:** the first v4.1.10 candidate re-read ordinary Slack thread messages and mapped a matching configured Slack user ID to canonical principal `michael`. Slack permits applications using user-scoped credentials to publish messages attributed to that user. The connected generic Slack transport in this environment also demonstrates that an application-originated post can appear under the connected human identity. Therefore `message.user == configured_user_id` is not sufficient authentication evidence for a human approval.

**Attack path:** user-scoped application post -> ordinary Slack message attributed to configured human -> agent-accessible `ingest_decision` -> `ApprovalService.decide(actor="michael")`.

**Remediation:** the attack path is removed, not merely filtered. `SlackApprovalHITLService.ingest_decision` no longer exists. The CoS `slack-adapter` permits `bind_notice` only. The runtime maintains a separately authenticated outbound Slack Socket Mode connection using a protected `xapp-` app-level token and forwards only `slash_commands` envelopes to a non-MCP Python human-ingress bridge. That service requires the governed channel, protected human identity, `/mesh-approval`, a PENDING canonical approval owned by `michael`, an existing provider-verified OpenAI-bot notice binding, an exact payload fingerprint match, and replay-safe envelope state before invoking `ApprovalService.decide`.

**Status:** RESOLVED in candidate; exact-head CI and live provider acceptance required.

### SEC-QNAP-040 HIGH: protected human Slack provider identity leaked into durable approval evidence

**Evidence:** an intermediate v4.1.10 candidate persisted the protected approver provider ID in both the provider-verified notice binding and the durable Socket Mode decision record. This violated the release contract that the human provider identity remain protected runtime configuration and stay out of normal TaskLedger evidence.

**Remediation:** the raw provider identity is now used only transiently to authenticate the Slack parent mention and trusted Socket Mode interaction. Durable notice binding persists `approver_identity_verified=true` and canonical principal `michael`; durable decision evidence persists `provider_identity_verified=true` and canonical principal `michael`. Regression tests assert the protected provider value and provider-ID field names are absent from both durable records.

**Status:** RESOLVED in candidate; exact-head CI and final diff hygiene verification required.

## Security properties

The exact v4.1.10 candidate must prove:

- no agent can invoke `approval.record_decision` directly;
- no agent-callable Slack adapter operation can record or infer a human decision;
- ordinary Slack messages, reactions, and copied commands cannot become canonical approval even when attributed to the configured human Slack user;
- only a provider-interactive Socket Mode `slash_commands` envelope for `/mesh-approval` can enter the non-MCP human decision path;
- the protected configured human Slack identity maps to `michael` only inside that trusted ingress and is not persisted into normal TaskLedger approval evidence;
- only official OpenAI Slack bot user IDs can satisfy parent notice authorship;
- wrong user, wrong channel, wrong command, wrong fingerprint, unknown approval, duplicate/conflicting decisions, and bot impersonation fail closed;
- Slack verifier, Socket Mode app token, and human identity values are not committed, logged, stored as values in `.env`, or packaged in release assets;
- protected runtime files are read-only mounts and normalized to runtime ownership/mode;
- `MESH_COS_SLACK_HITL_REQUIRED=true` prevents production readiness when bot-notice verification or Socket Mode human ingress cannot initialize/remain active;
- scheduled execution identity is explicit and idempotent;
- scheduled completion cannot bypass canonical lifecycle or separate verification;
- canonical approval is re-read immediately before any consequential action.

## Evidence

Candidate CI must include contract/drift checks, Ruff, mypy, 100% branch-aware Python coverage, Bandit, Node tests for Socket Mode transport, QNAP shell tests, deterministic release bundle/checksum, Compose validation, OCI provenance, MCP discovery/sequential requests, non-root/read-only runtime checks, ingress denial, persistence, restart, and backup integrity.

The Codex Security diff engine is not executable from the current ChatGPT host. This review therefore does **not** claim a completed Codex Security scan. The limitation remains explicit; repository-native tests, Bandit, exact diff inspection, negative authorization coverage, source-to-sink tracing, and independent final verification are required instead.

## Release disposition

No repository finding above may remain CRITICAL or HIGH on the final candidate. Production certification additionally requires live evidence for the official OpenAI bot-authored notice, active Socket Mode connection, successful `/mesh-approval` synthetic human interaction, canonical approval readback, audit-chain validity, no unauthorized external effect, and required TaskLedger mirror reconciliation. A repository-green release alone is not production certification.

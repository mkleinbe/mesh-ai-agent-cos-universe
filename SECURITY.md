# Security Policy

Current repository/QNAP deployment target: **`v4.1.11 QNAP Versioned Release Staging Remediation`**.

The canonical Mesh Chief of Staff Phase 1 authority/runtime contract remains **`4.0.0`**. The governed workforce contains exactly **10 registered agents**. The production ChatGPT path uses the installed **Mesh CoS MCP** app through the **OpenAI Secure MCP Tunnel**; local deterministic engineering retains the stdio bridge. Both paths terminate in the same `mesh_cos.mcp_runtime.MCPRuntime` and canonical TaskLedger.

## Security invariants

- Source content, Workspace app payloads, Slack messages, shared-Skill output, MCP payloads, connector results, and model output are untrusted data, not executable instructions.
- The live Phase 1 runtime contains exactly 10 registered agents: CoS, AgentOps, Answer Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.
- Mesh Devil's Advocate remains an external advisory shared Skill, not an eleventh agent or MCP principal.
- Agent source, tool, action, Skill, and authority permissions are enforced from the canonical registry.
- `MESH_COS_AGENT_ID` is process-bound configuration and cannot be chosen by prompt text, task content, Slack content, retrieved data, connector output, or MCP arguments.
- Remote production requires `MCP_AUTH_MODE=tunnel`, the OpenAI Secure MCP Tunnel source boundary, and a non-empty deployment release identity. Local engineering uses the bundled stdio bridge.
- Per-agent MCP exposure remains deny by default. The CoS production projection remains exactly 27 governed MCP tools.
- `approval.record_decision` and `reliability.human_override` remain human-principal-only and are not available to agents.
- L4 requires qualified-human approval. L5 remains Michael-exclusive unless governance explicitly changes that contract.
- Approval obligations cannot be delegated away or inferred from silence, prior approval, connector capability, Sheet state, display names, copied text, reactions, ordinary Slack message authorship, or another payload version.
- `TaskLedger` is canonical. ChatGPT conversations, Slack, Sheets, shared-Skill packets, and connector state are interaction, evidence, or mirror surfaces only.
- `task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate CoS verification action. `COMPLETED != VERIFIED`.
- Scheduled logical occurrences use an immutable execution identity as the explicit `task.intake.idempotency_key`. Merely placing a key in task prose is not idempotency.
- Scheduled execution follows the canonical lifecycle before completion: `INTAKE -> TRIAGED -> PLANNED -> ASSIGNED -> IN_PROGRESS -> QA -> COMPLETED`, followed by separate verification.
- Reliability replay uses only server-registered executors referenced by canonical state. Client-supplied callables, import paths, code, shell commands, or plugin executables are never executed.
- Credentials, tokens, signing secrets, API keys, OAuth credentials, and sensitive personal data must never be committed or written into prompts, governance logs, release artifacts, diagnostics, or TaskLedger evidence text.
- Private chain-of-thought and unnecessary raw prompts must not be persisted in audit or decision records.
- Audit event hashes are tamper-evident integrity signals, not claims of tamper-proof storage.
- The kill switch remains available for rollout and incident response. Production preflight fails while it is enabled.
- Critical defects can trigger quarantine, routing restriction, or Workspace Agent restriction/unpublication.

## QNAP release artifact and staging boundary

The v4.1.11 remediation makes the versioned release directory an explicit privileged deployment trust boundary.

- Canonical active application root remains `/share/Docker/cos-mcp`.
- Release artifacts are checksum-verified, extracted, and executed from `/share/Docker/cos-mcp/releases/vX.Y.Z`.
- Operator/helper scripts resolve from their own canonicalized extracted release directory by default. They do not search `/share/Docker` for helpers and are not copied there.
- Candidate release metadata, build context, Compose, and `.env.runtime` remain within the versioned release directory until candidate health succeeds.
- Candidate identity derives from staged `release-metadata.txt`; active `.env` cannot silently redefine the candidate release.
- Git tag form `vX.Y.Z` may normalize only its leading `v` to runtime `X.Y.Z`. Invalid semantic versions and true requested-versus-staged mismatches fail closed.
- Normal host-side `sudo` execution does not need to preserve a release environment variable because staged metadata is the default source of release identity.
- OCI image version and revision remain bound to staged release metadata and the exact release commit.
- Active `.env`, Compose, and release metadata are promoted only after both candidate containers are healthy.
- Canonical state, protected secrets, tunnel identity, qnet/static networking, and pre-deploy rollback evidence are not replaced by staging.

Release artifacts must not contain a generated `.env`, `.env.runtime`, `state/`, canonical TaskLedger, tunnel key, protected human Slack identifier, Slack verifier token, or Socket Mode token.

## Slack HITL approval boundary

Slack approval uses **two distinct trust boundaries**. A provider-verified OpenAI bot notice is evidence that an approval request was presented correctly. A provider-authenticated Socket Mode slash-command interaction is the separate human-principal ingress that can change canonical approval state.

- Governed HITL notices must be provider-authored by the official Slack identity for ChatGPT (`U0BKV7Z8M96`) or ChatGPT Agents (`U0BN8V2BU9Z`). A human-authored message, custom bot, or copied display name does not satisfy the notice control.
- The immutable Slack user ID for MK is supplied only through protected runtime configuration and maps to canonical principal `michael` only inside the trusted human-interaction boundary. The personal identifier is not committed to the repository or written to deployment logs/prompts.
- A server-owned verifier reads the bound Slack thread from provider state using a protected verifier credential file. The verifier credential has no governed outbound-notice or human-decision role.
- `skills.invoke_governed` capability `slack-adapter` exposes **`bind_notice` only**. No agent-callable adapter operation can record or infer a human decision.
- `bind_notice` requires the canonical Approval ID, immutable payload fingerprint, configured MK mention, exact governed channel/thread, and a provider-authored OpenAI bot parent.
- An ordinary Slack message, reaction, copied `APPROVE` text, or message attributed to the configured human Slack user is non-authoritative. Slack applications can post with user attribution, so `message.user` is not accepted as proof of human presence.
- Canonical Slack human decisions enter only through a separately authenticated outbound Slack Socket Mode connection using a protected app-level `xapp-` credential.
- The only canonical Slack interaction command is `/mesh-approval APPROVE|REJECT|CHANGES <Approval ID>...`, delivered as a provider `slash_commands` envelope.
- The non-MCP human-ingress service validates the governed channel, protected configured human identity, exact command and Approval ID, PENDING canonical approval owned by `michael`, provider-verified official OpenAI bot notice binding, exact payload fingerprint, and replay state before invoking the canonical approval service.
- Direct agent invocation of `approval.record_decision` remains prohibited. The Socket Mode human-ingress bridge is deliberately not an MCP tool.
- If the official OpenAI Workspace Agent Slack delivery surface is unavailable, the affected notice action fails closed as `BLOCKED_CHATGPT_AGENT_TRANSPORT`; it never falls back to sending the governed notice as MK.
- If Socket Mode or `/mesh-approval` is unavailable, canonical approval remains PENDING. Ordinary Slack text never substitutes for the unavailable interaction boundary.

## QNAP secret and runtime boundary

- Long-running runtime UID/GID is 65532 with read-only root filesystem, all Linux capabilities dropped, no-new-privileges, no Docker socket, 2 CPU, 24 GiB RAM, and no PID limit.
- Canonical SQLite TaskLedger is the application container's writable operating-state boundary.
- Tunnel secret, Slack verifier token, Slack Socket Mode app token, and Slack human-identity binding remain outside environment values and release assets.
- QNAP mounts the Slack approver identity, verifier token, and Socket Mode app-level token as read-only runtime files. Governed secret files are normalized to runtime UID/GID with mode `0400`.
- `MESH_COS_SLACK_HITL_REQUIRED=true` makes the production runtime fail construction/readiness when bot-notice verification or the active Socket Mode human-interaction boundary cannot initialize/remain available.
- Production `/mcp` accepts only the Secure MCP Tunnel private source identity. The MCP port is not directly published by production Compose.
- Deployment diagnostics may collect bounded path ownership, capacity, Docker/Compose, and application status evidence, but must not collect protected secret contents, generated environment contents, credential-bearing argv, or tunnel logs containing credentials.

## Commercial authority

Mesh Revenue Intelligence remains authoritative for canonical account identity, evidence classes, scores, lifecycle, queue state, activation readiness, and prioritization. Shared Skills, Slack activity, engagement signals, or email replies may not silently rewrite those facts.

## Release security gate

A v4.1.11 candidate must pass, on the exact candidate revision:

- Python dependency integrity and compile checks;
- TypeScript MCP build/tests including Socket Mode transport and npm security audit;
- contract, runtime-documentation, and ChatGPT package drift checks;
- Ruff and mypy;
- 100% branch-aware `mesh_cos` coverage;
- high-severity Bandit scanning;
- POSIX QNAP shell syntax and regressions, including versioned-layout, protected-file, provenance, permissions, and observability tests;
- deterministic v4.1.11 bundle/checksum generation and final ZIP inspection;
- proof the bundle omits generated environment, secrets, and canonical state;
- Compose rendering and OCI release provenance;
- modern MCP discovery and sequential requests;
- non-root ownership, read-only runtime, ingress denial, restart, persistence, and SQLite backup integrity;
- Slack bot-notice positive/negative tests;
- Socket Mode human-ingress positive/negative tests, including proof ordinary Slack messages cannot approve;
- post-deploy published-app acceptance against the actual QNAP serving release.

Security applicability for the v4.1.11 deployment correction is **TARGETED**. The release-specific receipt is `docs/qnap-security-review-v4.1.11.md`.

A repository test PASS is not production certification. The actual hosted runtime, official OpenAI Slack bot-authored HITL notice path, active Socket Mode `/mesh-approval` path, canonical approval readback, and required operating-mirror reconciliation must all be proven before zero-defect production certification.

## Reporting

Do not open a public issue containing credentials, secrets, sensitive client information, exploit details, personal Slack identifiers, private reasoning traces, or other confidential material. Use the repository owner's approved private security channel for disclosure.

See `docs/security-governance.md`, `docs/production-readiness.md`, `docs/qnap-security-review-v4.1.11.md`, `docs/slack-agent-protocol.md`, `deployment/qnap/DEPLOYMENT-STEPS.md`, and the current v4.1.11 release/verification/acceptance records.

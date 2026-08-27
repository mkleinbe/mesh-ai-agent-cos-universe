# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment target: `v4.1.16 QNAP Restarting-Runtime Backup Hotfix`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The `4.1.x` deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, scheduled execution, Slack HITL, request contract, transactional deployment recovery, backup integrity, and release evidence without widening the Phase 1 agent authority model.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to authorized agents. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets remain interaction, evidence, or mirror surfaces.

## Production ChatGPT topology

The published **Mesh CoS MCP** ChatGPT app is the production ChatGPT surface:

```text
ChatGPT / Mesh CoS MCP app
  -> OpenAI Secure MCP Tunnel
  -> mesh-cos-tunnel 172.30.60.3
  -> mesh-cos-mcp 172.30.60.2 + 192.168.7.60
  -> canonical mesh_cos.mcp_runtime.MCPRuntime
  -> TaskLedger SQLite
```

Local engineering and deterministic certification retain stdio:

```text
local MCP client
  -> node mcp/dist/index.js
  -> mesh_cos.mcp_stdio_bridge
  -> canonical MCPRuntime
  -> TaskLedger SQLite
```

The canonical QNAP application root remains `/share/Docker/cos-mcp` and uses the verified external QNAP `lan7` qnet. The stable operator release root is `/share/Docker/cos-mcp/releases`. Starting with v4.1.12, the release ZIP itself creates its `vX.Y.Z/` subdirectory when extracted from that root. Operator/helper scripts resolve from their own versioned directory and must not be copied to `/share/Docker`. The MCP protocol port is not published to the host or public internet. Production `/mcp` requests are accepted only from the Secure MCP Tunnel sidecar private source address.

## Dual release identity

Successful governed tool envelopes for v4.1.16 must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.16
agent_id: cos
```

Production `/healthz` and `/readyz` additionally report `transport: SECURE_MCP_TUNNEL`. When Slack HITL is required, readiness reports `slack_hitl_ready=true` only while the authenticated Socket Mode boundary is active.

`mcp_version` identifies the canonical Phase 1 authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the request. Remote production startup fails closed if `MESH_COS_DEPLOYMENT_RELEASE` is absent.

## v4.1.16 restarting-runtime backup hotfix

v4.1.16 supersedes v4.1.15 after a live QNAP upgrade exposed a Docker-state edge case in the pre-deploy backup gate.

1. QNAP Docker 27 can report `.State.Running=true` while `.State.Status=restarting`; deployment no longer treats that combination as a stable `docker exec` target.
2. A stable `status=running` runtime with `.State.Restarting=false` retains the existing online SQLite backup path.
3. A restarting or otherwise non-running existing runtime uses a quiesced backup path. Potential writers are stopped before canonical SQLite state is read.
4. The backup helper uses the exact active Mesh image, `--network none`, non-root UID/GID, read-only root filesystem, dropped capabilities, `no-new-privileges`, and no protected Slack/tunnel secret mounts.
5. The helper uses SQLite backup semantics and `PRAGMA integrity_check`; failed backup/export attempts leave no successful partial backup.
6. If the old runtime had running intent, deployment restores that intent after either a successful or failed quiesced backup attempt.
7. Pre-deploy backup is attempted for any existing `mesh-cos-mcp` container, not only one for which Docker reports `.State.Running=true`.
8. All v4.1.15 Slack HITL, deterministic egress, fail-closed readiness, and transactional promotion controls are retained.

Ready BDD scenarios QNAP-112 through QNAP-115 are defined in `specs/qnap-restarting-backup-v4.1.16.feature`.

## v4.1.15 controls retained

v4.1.15 removed the unnecessary Slack verifier-bot layer and separated connected Slack collaboration from authenticated human approval. The CoS `slack-adapter` remains `COLLABORATION_ONLY`; `/mesh-approval` provider-authenticated Socket Mode remains the only Slack interaction eligible to become a canonical human decision. QNAP Docker Engine 27 deterministic egress, bounded Slack reconnect, fail-closed readiness, failed-candidate restoration, and snapshot-backed transactional promotion remain unchanged.

## Retained release contracts

v4.1.14 established explicit protected-secret provisioning for QNAP/BusyBox environments and removed hidden secret entry from ordinary deployment. Those safe provisioning controls remain available where still applicable, including the OpenAI tunnel key provisioner.

v4.1.13 established the governed Slack human-approver bootstrap: Michael/MK is bound to Slack user principal `U01KG3CNYHK`; the operator is not prompted for that non-secret identity; `D...` conversation IDs fail closed; and existing valid identity files are preserved.

v4.1.12 established the release-root contract: release ZIPs contain a single top-level `vX.Y.Z/` directory, operator scripts self-resolve their helper paths, release-directory identity is bound to staged metadata, candidate files stay in the versioned release directory until health succeeds, and active production files are promoted only after candidate health.

v4.1.10 established scheduled execution and Slack HITL foundations: immutable scheduled idempotency keys, canonical lifecycle progression, protected Slack human identity, authenticated non-MCP `/mesh-approval`, non-authoritative ordinary Slack text, and fail-closed readiness.

## Authority boundary

Every MCP process is immutably bound through `MESH_COS_AGENT_ID`. Prompt text, retrieved content, task content, delegated instructions, connector content, Slack text, and shared-Skill output cannot change identity or widen the tool catalog.

The CoS production projection remains exactly **27 governed tools**. L4 requires qualified-human approval and L5 remains Michael-exclusive. `approval.record_decision` and `reliability.human_override` remain human-principal-only and outside the agent-facing MCP catalog.

## Completion and verification

`task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate CoS verification operation requiring acceptance evidence. **COMPLETED != VERIFIED.**

## Production acceptance

Repository, CI, container, and release-package verification do not prove the newly deployed on-premises serving instance, the live Secure MCP Tunnel route, or the provider-authenticated Slack human-interaction path.

After deploying v4.1.16, execute `docs/chatgpt-published-app-production-acceptance-v4.1.16.md`. Production certification requires the actual QNAP runtime, hosted MCP acceptance, proof ordinary Slack text remains non-authoritative, a provider-authenticated `/mesh-approval` interaction from the governed human approver, fresh canonical approval readback, valid audit chain, zero unauthorized external actions, and required TaskLedger operating-mirror reconciliation.

Current operator and release references:

- `SECURITY.md`
- `RELEASE.md`
- `docs/production-readiness.md`
- `docs/slack-agent-protocol.md`
- `docs/security-review-v4.1.16.md`
- `docs/release-4.1.16-qnap-restarting-backup.md`
- `docs/verification-v4.1.16-qnap-restarting-backup.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.16.md`
- `specs/qnap-restarting-backup-v4.1.16.feature`
- `docs/security-review-v4.1.15.md`
- `specs/qnap-slack-plugin-hitl-v4.1.15.feature`
- `deployment/qnap/README-QNAP.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
- `deployment/qnap/install-checklist.md`
- `deployment/qnap/upgrade-checklist.md`

Historical versioned documents remain retained as release-train evidence.
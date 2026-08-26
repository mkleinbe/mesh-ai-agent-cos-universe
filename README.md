# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment target: `v4.1.12 QNAP Release-Root Bootstrap`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The `4.1.x` deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, scheduled execution, Slack HITL, request contract, and release evidence without widening the Phase 1 agent authority model.

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

Successful governed tool envelopes for v4.1.12 must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.12
agent_id: cos
```

Production `/healthz` and `/readyz` additionally report `transport: SECURE_MCP_TUNNEL`. When Slack HITL is required, readiness also reports `slack_hitl_ready=true` only while the authenticated Socket Mode boundary is active.

`mcp_version` identifies the canonical Phase 1 authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the request. Remote production startup fails closed if `MESH_COS_DEPLOYMENT_RELEASE` is absent.

## v4.1.12 deployment remediation

v4.1.12 supersedes v4.1.11 for QNAP artifact layout and operator pathing while preserving v4.1.11 candidate-identity controls and the v4.1.10 runtime capability/security behavior.

1. The canonical operator working directory is `/share/Docker/cos-mcp/releases`.
2. `mesh-cos-mcp-qnap-v4.1.12.zip` contains a single top-level `v4.1.12/` directory, so extraction creates the version folder automatically.
3. No manual version-folder creation, payload copy/move, helper copy, chmod, or `cd` into the release directory is required.
4. Operator scripts self-resolve their release directory and helper paths using POSIX/BusyBox-compatible `dirname`, `cd`, and `pwd -P` behavior.
5. Deployment validates that the resolved folder is directly beneath the canonical releases root and that its `vX.Y.Z` basename matches staged release metadata before candidate preparation.
6. Candidate release metadata, build context, Compose, and generated `.env.runtime` remain in the versioned release directory.
7. Active production `.env` may remain on an older release while a newer candidate is staged; preflight reports these identities separately.
8. Runtime release identity defaults from staged metadata. A leading Git `v` is normalized, while real mismatches still fail closed.
9. Candidate `.env`, Compose, and release metadata are promoted to the canonical root only after application and tunnel containers are healthy.
10. The pre-deploy online SQLite backup, canonical TaskLedger, tunnel key, Slack protected configuration, qnet/static networking, image provenance, and rollback behavior are preserved.

## v4.1.10 capability retained

The scheduled execution and Slack HITL hardening introduced by v4.1.10 remains current: immutable scheduled idempotency keys, canonical lifecycle progression, official OpenAI bot notice binding, protected Slack human identity, provider verification, authenticated non-MCP Socket Mode `/mesh-approval`, non-authoritative ordinary Slack text, and fail-closed readiness. Agents still cannot record human approval decisions.

## Authority boundary

Every MCP process is immutably bound through `MESH_COS_AGENT_ID`. Prompt text, retrieved content, task content, delegated instructions, connector content, Slack text, and shared-Skill output cannot change identity or widen the tool catalog.

The CoS production projection remains exactly **27 governed tools**. L4 requires qualified-human approval and L5 remains Michael-exclusive.

## Completion and verification

`task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate CoS verification operation requiring acceptance evidence. **COMPLETED != VERIFIED.**

## Production acceptance

Repository, CI, container, and release-package verification do not prove the newly deployed on-premises serving instance, the official OpenAI Workspace Agent Slack delivery configuration, or the live Socket Mode human-interaction path.

After deploying v4.1.12, execute `docs/chatgpt-published-app-production-acceptance-v4.1.12.md`. Production certification requires the actual bot-authored HITL notice, proof ordinary APPROVE text remains non-authoritative, a provider-authenticated `/mesh-approval` interaction, fresh canonical approval readback, valid audit chain, zero unauthorized external actions, and required TaskLedger operating-mirror reconciliation.

Current operator and release references:

- `SECURITY.md`
- `RELEASE.md`
- `docs/production-readiness.md`
- `docs/slack-agent-protocol.md`
- `docs/qnap-release-root-bootstrap-v4.1.12.md`
- `docs/qnap-security-review-v4.1.12.md`
- `docs/release-4.1.12-qnap-release-root-bootstrap.md`
- `docs/verification-v4.1.12-qnap-release-root-bootstrap.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.12.md`
- `specs/qnap-release-root-bootstrap-v4.1.12.feature`
- `specs/scheduled-automation-slack-hitl-v4.1.10.feature`
- `deployment/qnap/README-QNAP.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
- `deployment/qnap/install-checklist.md`
- `deployment/qnap/upgrade-checklist.md`

Historical versioned documents remain retained as release-train evidence.

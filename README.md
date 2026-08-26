# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment release: `v4.1.9 Documentation and Release Closeout`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The `4.1.x` deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, request contract, and release evidence without widening the Phase 1 agent authority model or tool allowlists.

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

The QNAP application lives at `/share/Docker/cos-mcp`, uses the verified external QNAP `lan7` qnet, and is deployed with scripts run from `/share/Docker`. The MCP protocol port is not published to the host or public internet. Production `/mcp` requests are accepted only from the Secure MCP Tunnel sidecar private source address.

## Dual release identity

Successful governed tool envelopes must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.9
agent_id: cos
```

Production `/healthz` and `/readyz` additionally report `transport: SECURE_MCP_TUNNEL`.

`mcp_version` identifies the canonical Phase 1 authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the request. Remote production startup fails closed if `MESH_COS_DEPLOYMENT_RELEASE` is absent.

## Current release train controls

v4.1.9 carries forward the production corrections established in v4.1.8 and closes stale release-documentation drift.

Current controls include:

1. Public MCP `tools/list` schemas are closed and match runtime request validation.
2. Invalid structured requests fail with bounded `validation_failed` field details rather than opaque or misclassified errors.
3. Canonical task lookup distinguishes request validation failures from true `not_found` resource failures.
4. Registry-declared governed Skills resolve as auditable `CHATGPT_SKILL_HANDOFF` capabilities. Client-supplied executable code paths remain rejected.
5. `agentops.recommend` uses the documented structured request contract.
6. Same-tag local Mesh images are reusable only when OCI version and revision labels match extracted release metadata; mismatch forces rebuild.
7. Post-deploy verification executes a real read-only governed MCP call from the tunnel network namespace and verifies the running dual release identity.
8. The long-running QNAP runtime remains non-root UID/GID 65532, read-only, capability-dropped, no-new-privileges, with no Docker socket.

## Authority boundary

Every MCP process is immutably bound through `MESH_COS_AGENT_ID`. Prompt text, retrieved content, task content, delegated instructions, connector content, and shared-Skill output cannot change identity or widen the tool catalog.

The CoS production projection remains exactly **27 governed tools**. `approval.record_decision` and `reliability.human_override` remain human-principal-only and absent from every agent catalog. L4 requires qualified-human approval and L5 remains Michael-exclusive.

## Completion and verification

`task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate verifier operation requiring acceptance evidence. **COMPLETED != VERIFIED.**

## Production acceptance

Repository, CI, container, and release-package verification do not prove the newly deployed on-premises serving instance. After deploying v4.1.9, repeat hosted acceptance through the installed **Mesh CoS MCP** app and OpenAI Secure MCP Tunnel. Every successful governed response must report `mcp_version: 4.0.0`, `deployment_release: 4.1.9`, and `agent_id: cos`.

Current operator and release references:

- `deployment/qnap/README-QNAP.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
- `deployment/qnap/install-checklist.md`
- `deployment/qnap/upgrade-checklist.md`
- `docs/qnap-security-review-v4.1.9.md`
- `docs/release-4.1.9-documentation-closeout.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.9.md`
- `specs/qnap-release-closeout-v4.1.9.feature`

Historical versioned documents remain retained as evidence for the release train.
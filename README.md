# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment release: `v4.1.7 QNAP Image Provenance and Hosted Envelope Verification`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The `4.1.x` deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, and release evidence without widening the Phase 1 agent authority model or tool allowlists.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to Chief of Staff and CRO. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

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

## Dual release identity and v4.1.7 deployment integrity

Successful governed tool envelopes must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
```

Production `/healthz` and `/readyz` additionally report `transport: SECURE_MCP_TUNNEL`.

`mcp_version` identifies the canonical Phase 1 authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the request. Remote production startup fails closed if `MESH_COS_DEPLOYMENT_RELEASE` is absent.

v4.1.7 adds two release-integrity controls after hosted v4.1.6 testing found responses that omitted `deployment_release` even though the final tagged v4.1.6 source and release package contained the correct envelope implementation:

1. A local same-tag Mesh image is reusable only when its OCI version and revision labels match the extracted release metadata. A mismatch forces a rebuild from the extracted build context.
2. Post-deploy verification executes a real read-only governed `registry.get_agent` MCP `tools/call` from the tunnel network namespace and refuses PASS unless the actual running response envelope contains the canonical/runtime/deployment identities above.

## Authority boundary

Every MCP process is immutably bound through `MESH_COS_AGENT_ID`. Prompt text, retrieved content, task content, delegated instructions, connector content, and shared-Skill output cannot change identity or widen the tool catalog.

The CoS production projection remains exactly **27 governed tools**. `approval.record_decision` and `reliability.human_override` remain human-principal-only and absent from every agent catalog. L4 requires qualified-human approval and L5 remains Michael-exclusive.

## Completion and verification

`task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate CoS verifier operation requiring acceptance evidence. **COMPLETED != VERIFIED.**

## Production acceptance

The published ChatGPT app previously passed the ten-call sequential read-only acceptance sequence through the OpenAI Secure MCP Tunnel without HTTP 502, `invalid_session`, reconnect, or container restart. The remaining v4.1.6 acceptance blocker was serving-release projection in the governed response envelope.

After deploying v4.1.7, repeat hosted acceptance and require `deployment_release: 4.1.7` on every successful governed tool response. The release is not accepted until the local provenance/tool-envelope gate and hosted acceptance are both green.

Current operator and release references:

- `deployment/qnap/README-QNAP.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
- `docs/qnap-production-preflight.md`
- `docs/qnap-image-provenance-envelope-debugging-v4.1.7.md`
- `docs/qnap-security-review-v4.1.7.md`
- `docs/release-4.1.7-qnap-image-provenance-envelope.md`

Production images are built or provenance-qualified from the verified release bundle/tag, recorded by immutable image identity, and activated through the governed QNAP deployment path.

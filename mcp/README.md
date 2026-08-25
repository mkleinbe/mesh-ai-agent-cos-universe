# Mesh CoS MCP

This package is the transport adapter for the governed Mesh Chief of Staff operating core. The current QNAP deployment release is **v4.1.7**, while the unchanged canonical Phase 1 authority/runtime contract remains **4.0.0**.

## Supported transports

Local development and deterministic certification retain stdio through `node mcp/dist/index.js`.

QNAP production uses `node mcp/dist/remote.js` with MCP Streamable HTTP endpoints `/mcp`, `/healthz`, and `/readyz`, reached from ChatGPT through the **OpenAI Secure MCP Tunnel**. The remote adapter remains thin and routes permitted calls through the same canonical Python `MCPRuntime` and `TaskLedger`; it does not duplicate business logic.

## Production path

```text
Mesh CoS MCP ChatGPT app
  -> OpenAI Secure MCP Tunnel
  -> tunnel-client on private bridge 172.30.60.3
  -> mesh-cos-mcp:8080 on 172.30.60.2
  -> mesh_cos.mcp_stdio_bridge
  -> mesh_cos.mcp_runtime.MCPRuntime
  -> TaskLedger SQLite
```

`mesh-cos-mcp` also has LAN identity `192.168.7.60` on QNAP `lan7` qnet. `/mcp` accepts only the tunnel-sidecar private source address in tunnel mode. No host MCP port is published by the production Compose model.

## Dual release identity

The MCP protocol/authority contract and the QNAP deployment release are intentionally versioned separately.

Successful governed tool calls must return an envelope containing:

```json
{
  "ok": true,
  "request_id": "...",
  "mcp_version": "4.0.0",
  "deployment_release": "4.1.7",
  "agent_id": "cos",
  "result": {}
}
```

Production `/healthz` and successful `/readyz` return non-secret identity metadata including `mcp_version`, `deployment_release`, `agent_id`, and `transport: SECURE_MCP_TUNNEL`.

Remote production startup requires `MESH_COS_DEPLOYMENT_RELEASE`. Missing or blank release identity fails closed before the process listens. Local stdio remains transport-neutral and can omit deployment identity when no deployment release is being certified.

## v4.1.7 deployment integrity

The final v4.1.6 source and release artifact already included `deployment_release`, but hosted acceptance observed a serving instance whose governed envelopes omitted it. v4.1.7 closes the deployment integrity path that could allow an older local image to survive under a reused release tag.

QNAP preparation now qualifies any existing local Mesh image by OCI version and revision against the extracted release metadata and rebuilds on mismatch. Post-deploy verification also executes a real read-only `registry.get_agent` `tools/call` against the running service through the tunnel network namespace. Deployment cannot report PASS unless that actual governed envelope contains `mcp_version=4.0.0`, `deployment_release=4.1.7`, and `agent_id=cos`.

## Identity and authority

`MESH_COS_AGENT_ID` is validated at process startup and cannot be selected from MCP requests, HTTP headers, prompts, connector content, Skills, or task text. Human-only operations remain absent from agent catalogs.

The production CoS catalog remains 27 governed tools. The canonical roster remains 10 registered agents. v4.1.7 does not change these authority surfaces.

## State safety

QNAP production requires the configured SQLite ledger to pre-exist and serializes Node-to-Python bridge work at the single writable SQLite boundary. It refuses to silently create a second production operating universe.

## Development and certification

From `mcp/`, run `npm ci && npm run check`. Repository CI additionally builds the v4.1.7 production image and verifies release-image OCI provenance, Compose rendering, deployment-release propagation, non-root execution, read-only root filesystem, zero capabilities, no Docker socket, dual-identity health/readiness, modern MCP discovery, sequential MCP requests, governed tool-envelope identity, direct-ingress denial, SQLite backup integrity, restart recovery, and QNAP resource-policy assertions.

Current hosted acceptance is defined in `deployment/qnap/CHATGPT-ACCEPTANCE.md`. The historical v4.1.6 acceptance record remains `docs/chatgpt-published-app-production-acceptance-v4.1.6.md`.

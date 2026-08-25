# Mesh CoS MCP

This package is the transport adapter for the governed Mesh Chief of Staff operating core. The current QNAP deployment/image release is **v4.1.0**, while the unchanged Phase 1 authority/runtime contract remains **4.0.0**.

## Supported transports

Local development and certification retain stdio through `node mcp/dist/index.js`.

QNAP production additionally uses `node mcp/dist/remote.js` with the MCP SDK Streamable HTTP transport and logical endpoints `/mcp`, `/healthz`, and `/readyz`. The remote adapter remains thin and routes permitted calls through the same canonical Python `MCPRuntime` and `TaskLedger`; it does not duplicate business logic.

## QNAP production path

```text
ChatGPT
  -> OpenAI Secure MCP Tunnel
  -> tunnel-client on private bridge 172.30.60.3
  -> mesh-cos-mcp:8080 on 172.30.60.2
  -> mesh_cos.mcp_stdio_bridge
  -> mesh_cos.mcp_runtime.MCPRuntime
  -> TaskLedger SQLite
```

`mesh-cos-mcp` also has LAN identity `192.168.7.60` on QNAP `lan7` qnet for health/readiness operations. `/mcp` accepts only the tunnel-sidecar private source address in tunnel mode. No host port is published.

## Identity and authority

`MESH_COS_AGENT_ID` is validated at process startup and cannot be selected from MCP requests, HTTP headers, prompts, connector content, Skills, or task text. Human-only operations remain absent from agent catalogs.

## State safety

QNAP production requires the configured SQLite ledger to pre-exist and serializes Node-to-Python bridge work at the single writable SQLite boundary. It refuses to silently create a second production operating universe.

## Development and certification

From `mcp/`, run `npm ci && npm run check`. Repository CI additionally builds the production image and verifies Compose rendering, non-root execution, read-only root filesystem, zero capabilities, no Docker socket, health/readiness, LAN `/mcp` denial, SQLite backup integrity, restart recovery, and QNAP resource-policy assertions.

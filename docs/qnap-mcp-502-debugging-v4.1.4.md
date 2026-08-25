# QNAP Mesh CoS MCP 502 Debugging Record v4.1.4

## Status

Causal defect established and remediated in the v4.1.4 candidate. Production remains on v4.1.3 until the operator deploys the verified bundle and completes ChatGPT acceptance.

## Production symptom

The published `Mesh CoS MCP` app initially completed `registry.list_agents`, then later calls such as `registry.get_agent`, `governance.verify_audit_chain`, and repeated `registry.list_agents` surfaced `502 Upstream or external service errors`. A fresh production reproduction later returned the same 502 immediately.

## First failing boundary

The first invalid boundary is the HTTP/MCP protocol router inside `mesh-cos-mcp`, before governed tool dispatch, the Python bridge, or SQLite TaskLedger access.

The v4.1.3 server used the v1 monolithic `@modelcontextprotocol/sdk` `StreamableHTTPServerTransport` with server-managed sessions. It created a transport only for legacy `initialize` requests and required `Mcp-Session-Id` for subsequent requests. A modern MCP 2026-07-28 `server/discover` request without that legacy session header therefore received HTTP 400 `{"error":"invalid_session"}`. The Secure MCP Tunnel/ChatGPT path can surface an upstream target failure as a 502.

MCP 2026-07-28 requires `server/discover` and uses per-request protocol metadata rather than the old initialize/session lifecycle. The stable TypeScript SDK v2 migration guidance maps HTTP servers to `createMcpHandler(factory)` and recommends its stateless compatibility path for both the modern era and legacy 2025-era clients.

References:

- https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/migration/support-2026-07-28.md
- https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/protocol-versions.md
- https://github.com/modelcontextprotocol/typescript-sdk/blob/main/packages/server/README.md

## Falsifiable hypothesis and RED proof

Hypothesis: if the 502 is caused by the old sessionful router, then a production image sent a valid MCP 2026-07-28 `server/discover` request should fail before any tool handler runs, specifically because the request has no old `Mcp-Session-Id`.

Regression evidence was added in `deployment/qnap/tests/test-modern-mcp-transport.sh` before the causal fix. Against v4.1.3 behavior, CI returned:

```text
FAIL server/discover expected HTTP 200, got 400
{"error":"invalid_session"}
```

This bound the defect to the Mesh MCP HTTP transport rather than the tunnel credential, canonical registry, Python bridge, TaskLedger, or governance service.

## Causal correction

The v4.1.4 candidate:

1. migrates from the monolithic v1 SDK to pinned stable v2 packages;
2. serves remote MCP through `createMcpHandler(() => createServer(...))`;
3. adapts that handler to Node HTTP with `toNodeHandler`;
4. removes the eight-entry server-managed protocol-session map;
5. supports modern `server/discover` without `initialize` or `Mcp-Session-Id`;
6. retains the default stateless compatibility path for legacy MCP clients;
7. preserves the `MCP_TRUSTED_CLIENT_IP` source gate before MCP dispatch;
8. strengthens `/readyz` so it proves both canonical runtime health and a real modern `server/discover` response.

No retry loop, arbitrary timeout increase, resource increase, direct ingress, or authorization weakening is used as remediation.

## Regression coverage

`specs/qnap-mcp-modern-transport-v4.1.4.feature` defines QNAP-042 through QNAP-047.

`deployment/qnap/tests/test-modern-mcp-transport.sh` proves with the production container image:

- modern `server/discover` succeeds;
- ten consecutive stateless `tools/list` requests succeed;
- `registry.list_agents` preserves bound `cos` identity;
- direct untrusted ingress still receives HTTP 403;
- no tunnel/runtime restart is required between sequential requests.

The existing MCP certification also continues to prove the 27-tool CoS catalog, 10-agent roster, human-only tool exclusion, canonical persistence, and safe denial behavior.

## Residual production boundary

Repository and container evidence cannot prove the hosted ChatGPT-to-Secure-MCP-Tunnel path after an on-premises upgrade. Final closure therefore requires deploying v4.1.4 to QNAP and repeating the published-app sequential acceptance suite. Until that operator step occurs, production acceptance remains blocked even though the candidate regression is green.

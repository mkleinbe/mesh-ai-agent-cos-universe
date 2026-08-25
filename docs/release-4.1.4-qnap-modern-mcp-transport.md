# v4.1.4 QNAP Modern MCP Transport Reliability

## Purpose

v4.1.4 is a patch release for production 502 failures observed through the published `Mesh CoS MCP` ChatGPT app after an initially successful Secure MCP Tunnel invocation.

The canonical Mesh CoS authority/runtime contract remains `4.0.0`. The 10-agent roster, 27 governed tool projection, human-only operations, canonical TaskLedger, and `COMPLETED != VERIFIED` semantics are unchanged.

## Root cause

v4.1.3 used the sessionful v1 Streamable HTTP server lifecycle. Current MCP 2026-07-28 traffic can begin with `server/discover` and does not require the old `initialize` plus `Mcp-Session-Id` lifecycle. The v4.1.3 router rejected the modern request with `invalid_session` before tool dispatch. The upstream failure was surfaced to ChatGPT as a 502.

See `docs/qnap-mcp-502-debugging-v4.1.4.md` for the full debugging receipt.

## Changes

- migrate remote/stdio MCP serving to stable v2 split packages:
  - `@modelcontextprotocol/server@2.0.0`
  - `@modelcontextprotocol/node@2.0.0`
  - `@modelcontextprotocol/client@2.0.0` for certification
- replace the server-managed eight-session HTTP map with `createMcpHandler` stateless request serving;
- support MCP 2026-07-28 `server/discover`;
- retain legacy 2025-era stateless compatibility through the SDK v2 entry;
- preserve the tunnel-private source-IP gate before MCP dispatch;
- strengthen `/readyz` to verify modern protocol discovery in addition to bound-agent and audit-chain health;
- add QNAP-042 through QNAP-047 BDD scenarios;
- add production-image regression for modern discovery, ten sequential calls, identity preservation, and direct-ingress denial;
- migrate the stdio certification client to the v2 package split;
- keep npm package/runtime contract version at `4.0.0`.

## Security boundary

Security applicability: **TARGETED**.

The transport implementation changes, but authority does not. Required invariants remain:

- `MCP_AUTH_MODE=tunnel` only;
- `/mcp` accepts only the configured private tunnel-client source IP;
- no host port is published by production Compose;
- runtime remains UID/GID 65532 with read-only rootfs, all capabilities dropped, and no Docker socket;
- exactly the 27 governed CoS tools remain projected;
- `approval.record_decision` and `reliability.human_override` remain human-only and absent from the agent catalog;
- exactly 10 canonical agents remain registered;
- canonical SQLite persistence and audit-chain verification remain unchanged;
- no retries, timeout inflation, or resource increases mask the failure.

## Verification gates

The release candidate is not releasable until all of the following pass on the exact candidate revision:

1. npm build/tests/smoke/security;
2. Python contracts, drift checks, static analysis, 100% branch-aware coverage, Bandit, compileall;
3. QNAP shell regressions;
4. deterministic v4.1.4 bundle construction and checksum;
5. production image build from the bundle context;
6. modern `server/discover` plus ten sequential stateless requests;
7. 27-tool catalog / 10-agent roster / human-only exclusion certification;
8. non-root QNAP ownership handoff;
9. hardened runtime, direct non-tunnel denial, restart recovery, and Docker-mediated SQLite backup;
10. targeted security review and independent verification.

Final production acceptance additionally requires operator deployment to QNAP and fresh sequential calls through the published ChatGPT app and Secure MCP Tunnel.

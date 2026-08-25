# QNAP Mesh CoS MCP v4.1.4 Targeted Security Review

Security applicability: **TARGETED**

This receipt supplements `docs/qnap-security-review.md` for the v4.1.4 MCP transport modernization.

## Finding

| ID | Severity | Surface | Evidence / consequence | Remediation / retest | Residual risk |
|---|---|---|---|---|---|
| SEC-QNAP-021 | High | MCP HTTP protocol boundary | v4.1.3 required legacy server-managed `Mcp-Session-Id`; valid modern `server/discover` received HTTP 400 `invalid_session`, surfaced through the hosted path as 502 and blocked governed tool use | Migrate to pinned stable SDK v2 `createMcpHandler` stateless serving; require production-image RED/GREEN regression for modern discovery, 10 sequential requests, bound `cos` identity, and direct-ingress 403 | Final hosted ChatGPT/Tunnel behavior remains operator-verifiable after QNAP upgrade |
| SEC-QNAP-022 | Medium | Readiness / monitoring | v4.1.3 `/readyz` could remain green while the MCP protocol-serving path rejected current clients | v4.1.4 readiness now performs a local modern `server/discover` probe in addition to bound-agent and audit-chain checks | Tunnel control-plane health remains represented by the separate tunnel container health check |

## Changed trust boundaries and sensitive surfaces

- MCP protocol parsing and version negotiation;
- Node HTTP adapter to MCP handler;
- SDK dependency/supply-chain surface;
- readiness semantics;
- remote Secure MCP Tunnel request path.

The canonical TaskLedger, Python governed runtime, agent authority model, and human approval boundary are not changed.

## Required security properties

1. `MCP_AUTH_MODE=tunnel` remains mandatory for remote serving.
2. `MCP_TRUSTED_CLIENT_IP` is required and checked before MCP dispatch.
3. Production Compose publishes no MCP host port.
4. Direct non-tunnel requests remain denied with HTTP 403.
5. Process identity remains `cos`; callers cannot select another agent principal.
6. Exactly the canonical 27 governed CoS tools remain projected.
7. `approval.record_decision` and `reliability.human_override` remain absent from the agent catalog.
8. Exactly 10 canonical agents remain registered; Devil's Advocate remains a Skill, not agent 11.
9. Runtime remains UID/GID 65532, read-only rootfs, all capabilities dropped, no-new-privileges, no Docker socket.
10. Canonical TaskLedger persistence and audit hash-chain verification remain unchanged.
11. The fix must not rely on arbitrary retries, increased resource limits, weakened timeouts, or bypassing the Secure MCP Tunnel.
12. MCP dependencies are exact-version locked and `npm audit --audit-level=high` must pass on the candidate.
13. Readiness must fail when modern MCP discovery is not serviceable even when the Python runtime remains otherwise healthy.

## Evidence required before integration

- exact candidate `npm ci`, build, unit tests, v2 stdio smoke certification, and npm audit;
- exact candidate Python contract/drift/static/security gates;
- production-container modern `server/discover` response;
- at least 10 sequential modern requests without session loss or restart;
- explicit `cos` identity evidence;
- direct-ingress HTTP 403 regression;
- hardened runtime and image-identity checks;
- SQLite backup integrity and secret exclusion;
- independent verification of the actual candidate diff.

## Security disposition

No design-level bypass of authentication, authorization, tool allowlists, canonical persistence, or human-only authority is introduced by the causal fix. The migration removes obsolete protocol-session state rather than broadening caller authority. Codex Security was not available in this ChatGPT runtime and is not claimed; the strongest available evidence is the targeted trust-boundary review plus exact dependency, static-analysis, runtime, and production-image regression gates.

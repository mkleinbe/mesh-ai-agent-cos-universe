# v4.1.4 QNAP Modern MCP Transport Reliability

`v4.1.4` is a corrective QNAP production release for the `502 Upstream or external service errors` observed through the published `Mesh CoS MCP` ChatGPT app after an initially successful Secure MCP Tunnel invocation.

The canonical Mesh CoS authority/runtime contract remains `4.0.0`. The exact 10-agent roster, 27 governed tools, human-only operations, canonical TaskLedger, `COMPLETED != VERIFIED`, resource policy, and Secure MCP Tunnel trust boundary are unchanged.

## Root cause fixed

v4.1.3 served remote MCP with the v1 monolithic SDK and a server-managed Streamable HTTP session map. It created a transport only for legacy `initialize` and required `Mcp-Session-Id` afterward. Current MCP clients can begin with `server/discover` and do not depend on that legacy protocol-session lifecycle.

The regression test proved the exact failure against the old implementation:

```text
FAIL server/discover expected HTTP 200, got 400
{"error":"invalid_session"}
```

The request was rejected in `mesh-cos-mcp` before governed tool dispatch, the Python bridge, or canonical SQLite access. The hosted tunnel path then surfaced the upstream target failure as a 502.

## Causal correction

v4.1.4:

- migrates from `@modelcontextprotocol/sdk` v1 to pinned stable v2 split packages;
- serves remote MCP using the v2 Node/server HTTP adapter and stateless request handling;
- removes the manual eight-entry protocol-session map;
- supports current `server/discover` without requiring legacy `initialize` or `Mcp-Session-Id`;
- retains the SDK v2 compatibility path for older clients;
- preserves `MCP_AUTH_MODE=tunnel` and the private `MCP_TRUSTED_CLIENT_IP` gate before dispatch;
- strengthens `/readyz` so readiness now requires a successful modern MCP discovery probe as well as bound-agent and audit-chain health;
- migrates local stdio certification to the v2 client/server package split.

The fix does not add retry masking, resource inflation, timeout inflation, direct ingress, or authorization bypasses.

## Regression and verification gates

The v4.1.4 candidate requires:

- QNAP-042 through QNAP-047 ready BDD scenarios;
- production-image modern `server/discover` acceptance;
- at least ten consecutive stateless MCP requests without session loss or restart;
- bound `cos` identity preservation;
- exact 27-tool CoS catalog and 10-agent roster certification;
- human-only tool exclusion;
- direct untrusted MCP ingress HTTP 403;
- npm build/tests/smoke/audit;
- Python contracts, drift checks, Ruff, mypy, Bandit, compileall, and 100% branch-aware coverage;
- deterministic QNAP bundle/checksum generation;
- real Docker bind-mount ownership handoff;
- hardened non-root runtime controls, restart recovery, and Docker-mediated SQLite backup integrity.

Security applicability is **TARGETED**. See `docs/qnap-security-review-v4.1.4.md`.

## QNAP operator privilege

On the current QNAP operator account, Docker access requires `sudo`. The supported upgrade command therefore invokes the deployment orchestrator with `sudo`, which provides host-side Docker/Container Station authority for the deployment process. This does not change the runtime identity: the long-running `mesh-cos-mcp` container still runs as UID/GID `65532:65532` with read-only root filesystem, dropped capabilities, no-new-privileges, and no Docker socket.

## Resource policy

- `mesh-cos-mcp`: 2 CPUs, 24 GiB RAM, no PID limit.
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit.

No resource increase is part of the remediation.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.4.zip`
- `mesh-cos-mcp-qnap-v4.1.4.zip.sha256`

The release bundle contains the release-bound build context and QNAP operator tooling. It contains no runtime tunnel secret and no canonical TaskLedger data.

## Version identity

- Repository/QNAP deployment release: `4.1.4`
- Semantic tag: `v4.1.4`
- Container image label default: `4.1.4-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 agents
- Message Operations remains the tenth registered agent
- Mesh Devil's Advocate remains a governed shared Skill, not agent 11
- Human-only operations remain `approval.record_decision` and `reliability.human_override`
- Production transport remains OpenAI Secure MCP Tunnel

## Production acceptance boundary

Repository/container verification cannot prove the hosted ChatGPT path after an on-premises upgrade. After deploying the v4.1.4 bundle to QNAP, the operator must run the published-app sequential acceptance suite before the production 502 blocker is closed.

See:

- `docs/qnap-mcp-502-debugging-v4.1.4.md`
- `docs/release-4.1.4-qnap-modern-mcp-transport.md`
- `docs/qnap-security-review-v4.1.4.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

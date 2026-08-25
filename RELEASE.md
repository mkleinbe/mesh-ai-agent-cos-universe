# v4.1.6 Secure MCP Published App Production Identity

`v4.1.6` is a patch-level QNAP production observability and acceptance-hardening release for the published **Mesh CoS MCP** ChatGPT app connected to the QNAP-hosted MCP runtime through the **OpenAI Secure MCP Tunnel**.

The canonical Mesh CoS Phase 1 authority/runtime contract remains **`4.0.0`**. The exact 10-agent roster, 27 governed CoS tools, human-only operations, canonical TaskLedger, `COMPLETED != VERIFIED`, resource policy, and Secure MCP Tunnel trust boundary are unchanged.

## Production evidence that drove this release

The installed Mesh CoS MCP ChatGPT app executed the documented ten-call sequential read-only acceptance sequence through the Secure MCP Tunnel without HTTP 502, `invalid_session`, reconnect, or container restart. The live path returned the canonical 10-agent roster, valid audit-chain checks, metrics, CoS and Message Operations registry records, and TaskLedger reads.

That successful hosted run exposed one remaining observability defect: responses reported `mcp_version=4.0.0`, which correctly identifies the canonical authority/runtime contract, but did not identify which QNAP deployment release served the request.

## v4.1.6 correction

v4.1.6 separates the two version domains explicitly:

- `mcp_version` continues to identify the canonical Phase 1 authority/runtime contract and remains `4.0.0`.
- `deployment_release` identifies the QNAP deployment release serving the request and is `4.1.6` for this release.

Successful governed tool envelopes now contain:

```json
{
  "ok": true,
  "request_id": "...",
  "mcp_version": "4.0.0",
  "deployment_release": "4.1.6",
  "agent_id": "cos",
  "result": {}
}
```

Production `/healthz` and successful `/readyz` report the same non-secret version and identity metadata plus `transport: SECURE_MCP_TUNNEL`.

## Fail-closed production identity

`MESH_COS_DEPLOYMENT_RELEASE` is now passed explicitly from the generated QNAP environment into `mesh-cos-mcp`. The remote MCP process requires a non-empty value before listening for production MCP traffic. Missing deployment identity fails startup rather than creating an ambiguous serving runtime.

The deployment release value is observability metadata only. It does not select the agent identity, tool catalog, approval authority, decision rights, delegation rights, or canonical state.

## Modern MCP readiness alignment

The internal modern-MCP readiness discovery request no longer carries a stale hardcoded patch-release client version. Its client identity derives from the current deployment release. Readiness continues to require:

- active bound CoS registry identity;
- valid governance audit chain;
- successful current `server/discover` protocol handling.

## CI and release hardening

The release gate now verifies:

- `actions/setup-node@v7` under the full repository pipeline;
- Node build, tests, stdio smoke, and npm security audit;
- Python contract/drift validation, Ruff, mypy, 100% branch-aware coverage, Bandit, and compileall;
- v4.1.6 release-bundle identity and checksum;
- Compose propagation of `MESH_COS_DEPLOYMENT_RELEASE=4.1.6`;
- production image identity `4.1.6-qnap`;
- modern MCP discovery and sequential request stability;
- dual release identity in `/healthz`, `/readyz`, and governed tool responses;
- direct non-tunnel MCP ingress denial;
- non-root/read-only/capability-drop/no-Docker-socket controls;
- SQLite persistence, backup integrity, and restart recovery.

## Security boundary

Security applicability is **TARGETED** because production observability and remote startup validation change. No authority is expanded.

Preserved controls include:

- `MCP_AUTH_MODE=tunnel` only for the production remote adapter;
- mandatory private tunnel-client source-IP gate before `/mcp` dispatch;
- no production host MCP port publication;
- immutable `MESH_COS_AGENT_ID=cos`;
- runtime UID/GID 65532, read-only rootfs, all capabilities dropped, no-new-privileges, and no Docker socket;
- exactly 27 governed CoS tools and 10 registered agents;
- human-only `approval.record_decision` and `reliability.human_override` excluded from agent projection;
- canonical SQLite TaskLedger and governance audit-chain semantics unchanged;
- tunnel runtime secret handling unchanged.

See `docs/qnap-security-review-v4.1.6.md`.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.6.zip`
- `mesh-cos-mcp-qnap-v4.1.6.zip.sha256`

The bundle includes the release-bound build context, QNAP operator tooling, current ChatGPT acceptance procedure, v4.1.6 BDD scenarios, targeted security review, and hosted published-app acceptance record. It contains no tunnel runtime secret and no canonical TaskLedger data.

## Version identity

- Repository/QNAP deployment release: `4.1.6`
- Semantic tag: `v4.1.6`
- Container image label default: `4.1.6-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 agents
- Message Operations remains the tenth registered agent
- Mesh Devil's Advocate remains a governed shared Skill, not agent 11
- CoS production catalog: exactly 27 governed tools
- Production transport: OpenAI Secure MCP Tunnel
- Remediation/enhancement issue: #39
- Implementation PR: #40

## Post-deploy acceptance boundary

Repository and container verification prove the release candidate but not the newly deployed on-premises serving instance. After deploying v4.1.6 to QNAP, repeat the published-app ten-call acceptance sequence and require every successful governed response to report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.6
agent_id: cos
```

Do not mark the new deployment accepted until both local dual-identity checks and hosted Mesh CoS MCP app acceptance are green.

See:

- `docs/release-4.1.6-secure-mcp-published-app-identity.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.6.md`
- `docs/qnap-security-review-v4.1.6.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

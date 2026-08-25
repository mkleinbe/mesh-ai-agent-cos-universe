# QNAP Security Review v4.1.6

Classification: **TARGETED**  
Scope: production deployment identity observability, remote startup validation, health/readiness metadata, MCP response envelopes, and ChatGPT hosted acceptance.

## Security conclusion

v4.1.6 does not expand MCP authority, networking, human-principal rights, canonical-state access, or external execution authority. The canonical Phase 1 authority/runtime contract remains `4.0.0` with exactly 10 registered agents and the existing 27-tool CoS projection.

## SEC-QNAP-027: deployment release identity becomes observable

`MESH_COS_DEPLOYMENT_RELEASE` is already non-secret operator-managed release metadata. v4.1.6 passes it into the application container and exposes only its normalized value as `deployment_release` in tool envelopes and health/readiness responses.

Controls:

- the value is read as data and is not sourced, evaluated, executed, or used to select tools;
- it does not alter `MESH_COS_AGENT_ID`, the canonical MCP contract, or any allowlist;
- no other process-environment values are returned;
- tunnel runtime keys, control-plane credentials, filesystem paths, and TaskLedger secrets are not exposed.

Risk: **LOW**. The value reveals only the already-public semantic deployment release.

## SEC-QNAP-028: remote startup fails closed without release identity

The remote Secure MCP process now requires a non-empty deployment release before it listens for MCP traffic. Missing identity terminates startup rather than allowing an ambiguous production runtime.

This is a reliability/security hardening control. It cannot widen authority and reduces the chance of accepting an unverifiable deployment.

## SEC-QNAP-029: health/readiness metadata remains non-authoritative

`/healthz` and `/readyz` report `mcp_version`, `deployment_release`, `agent_id`, and `transport`. These fields are observability metadata only. They do not establish approval, delegation, decision authority, or caller identity.

The existing Secure MCP Tunnel private source-IP check remains ahead of `/mcp` dispatch. No host MCP port is published in the QNAP Compose candidate.

## Preserved controls

- `MCP_AUTH_MODE=tunnel` only for the production remote process.
- `MCP_TRUSTED_CLIENT_IP` remains mandatory.
- Production `/mcp` ingress remains restricted to the tunnel sidecar private source address.
- `MESH_COS_AGENT_ID=cos` remains process-bound and request content cannot change it.
- Human-only `approval.record_decision` and `reliability.human_override` remain absent from agent catalogs.
- `TaskLedger` remains canonical state.
- `task.complete` remains separate from `task.verify`; `COMPLETED != VERIFIED`.
- Runtime remains UID/GID 65532, read-only root filesystem, all Linux capabilities dropped, no-new-privileges, and no Docker socket.
- OpenAI tunnel runtime secret handling is unchanged.

## Verification requirements

Release acceptance requires Node build/tests/smoke/audit, Python contract and drift checks, Ruff, mypy, 100% branch-aware Python coverage, Bandit, production-image build, modern MCP discovery, sequential requests, health/readiness identity assertions, direct-ingress denial, restart recovery, SQLite backup integrity, and the published ChatGPT app hosted acceptance sequence.

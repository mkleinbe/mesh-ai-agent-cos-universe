# Published Mesh CoS MCP Production Acceptance Record

Release target: **v4.1.6**  
Acceptance date: **2026-08-25**  
Surface: published **Mesh CoS MCP** ChatGPT app  
Transport: **OpenAI Secure MCP Tunnel** to the QNAP-hosted MCP runtime

## Purpose

This record captures the live hosted-path evidence that motivated v4.1.6 and separates what has already been proven through the published ChatGPT app from what must be re-verified after the v4.1.6 deployment.

The canonical Phase 1 authority/runtime contract remains **4.0.0**. v4.1.6 is a deployment observability and acceptance hardening release, not an authority expansion.

## Live published-app baseline

A new ChatGPT conversation used the installed `Mesh CoS MCP` app and executed the documented ten-call sequential read-only acceptance sequence through the OpenAI Secure MCP Tunnel without restarting the QNAP containers:

1. `registry.list_agents`
2. `governance.verify_audit_chain`
3. `metrics.snapshot`
4. `registry.get_agent` for `cos`
5. `task.list`
6. `registry.list_agents`
7. `governance.verify_audit_chain`
8. `metrics.snapshot`
9. `registry.get_agent` for `message-ops`
10. `task.list`

### Observed results

- All ten calls succeeded through the published ChatGPT app.
- No HTTP 502, `invalid_session`, reconnect requirement, or container restart occurred.
- Both registry reads returned exactly **10 registered agents**.
- `message-ops` was present and Mesh Devil's Advocate was not an agent principal.
- Both audit-chain checks returned `valid=true`.
- Metrics calls returned successfully.
- CoS and Message Operations agent lookups returned successfully.
- TaskLedger reads returned successfully and were empty at the time of this read-only acceptance.
- No canonical production write was made during this acceptance run.

## Observability gap found

The live tool envelopes correctly reported:

- `mcp_version: 4.0.0`
- `agent_id: cos`

They did **not** report the QNAP deployment release serving the call. That is ambiguous in production because `4.0.0` is intentionally the canonical authority/runtime contract while the QNAP deployment train is independently versioned.

v4.1.6 closes that gap by carrying `MESH_COS_DEPLOYMENT_RELEASE` into the runtime, requiring it for remote startup, and returning a separate non-secret `deployment_release` field in governed tool envelopes and health/readiness responses.

## Post-v4.1.6 acceptance

After deploying the v4.1.6 bundle, repeat the ten-call hosted sequence and require every successful tool envelope to show:

```text
mcp_version: 4.0.0
deployment_release: 4.1.6
agent_id: cos
```

Also require local `/healthz` and `/readyz` responses to show the same dual release identity plus `transport: SECURE_MCP_TUNNEL`.

The hosted path is accepted only if the sequential calls remain stable, the 27-tool CoS catalog remains unchanged, human-only operations remain excluded, the 10-agent roster remains canonical, and no authority boundary changes are observed.

## Security boundary

This enhancement exposes only non-secret release metadata already present in the operator-managed deployment environment. It does not expose the tunnel API key, tunnel control-plane secret material, TaskLedger contents beyond explicitly invoked governed tools, QNAP credentials, process environment values, or internal filesystem details.

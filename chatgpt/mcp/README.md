# Mesh CoS MCP Contract

`mesh-cos-mcp.v1.json` remains the canonical Phase 1 **4.0.0 authority/runtime contract**. It defines the 10 registered agent principals, deny-by-default tool allowlists, immutable agent identity, human-only catalog, delegation rules, and completion/verification boundary.

Repository/QNAP deployment release **v4.1.7** packages that unchanged authority contract behind the published **Mesh CoS MCP** ChatGPT app and OpenAI Secure MCP Tunnel, while making the serving deployment release independently observable and release-image provenance verifiable.

## Transport model

Local engineering/certification retains `LOCAL_STDIO`:

```text
local MCP client -> node mcp/dist/index.js -> canonical MCPRuntime -> TaskLedger
```

Production uses the same governed server logic behind Streamable HTTP:

```text
Mesh CoS MCP ChatGPT app -> OpenAI Secure MCP Tunnel -> /mcp -> canonical MCPRuntime -> TaskLedger
```

The production HTTP transport does not accept caller-selected agent identity and does not expand the contract tool allowlist. The immutable QNAP process identity is `cos`.

## Production response identity

Successful governed tool envelopes report both version domains:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
```

`mcp_version` identifies the canonical Phase 1 authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the call. Production `/healthz` and `/readyz` also report `transport: SECURE_MCP_TUNNEL`.

Remote startup fails closed when `MESH_COS_DEPLOYMENT_RELEASE` is missing or blank. Release identity is observability metadata only; it cannot select tools, change authority, create approvals, or change canonical state.

## v4.1.7 deployment integrity

Hosted v4.1.6 acceptance found a serving instance whose governed responses omitted `deployment_release`, while the final tagged v4.1.6 source and release package already contained the correct envelope code. v4.1.7 therefore hardens the QNAP deployment boundary rather than changing the canonical MCP contract.

A same-tag local image is reusable only when its OCI version and revision labels match the extracted release metadata. A mismatch forces a rebuild. Post-deploy verification then executes a real read-only `registry.get_agent` `tools/call` against the running service from the tunnel network namespace and fails unless the actual governed envelope reports the identities above.

## Agent versus human catalogs

`agent_tool_allowlists` is deny-by-default. The CoS projection remains exactly **27 governed tools**. `human_tool_allowlist` contains exactly `approval.record_decision` and `reliability.human_override`; neither may appear in an agent catalog.

The canonical workforce remains exactly **10 registered agents**. Mesh Devil's Advocate remains an external governed shared Skill, not an MCP principal.

## Completion contract

`task.complete` produces `COMPLETED` only and requires outcome plus evidence. `task.verify` is separate, exposed only to CoS in Phase 1, and requires explicit acceptance evidence. **COMPLETED != VERIFIED.**

## Certification

Local stdio certification remains part of `npm run check`. QNAP production acceptance adds image provenance, container hardening, dual release identity, actual governed-envelope verification, Secure MCP Tunnel ingress, persistence, backup/restore, restart, sequential modern MCP calls, and published ChatGPT app verification.

See `deployment/qnap/CHATGPT-ACCEPTANCE.md`, `docs/qnap-image-provenance-envelope-debugging-v4.1.7.md`, and `docs/release-4.1.7-qnap-image-provenance-envelope.md`. The v4.1.6 hosted acceptance record remains historical evidence.

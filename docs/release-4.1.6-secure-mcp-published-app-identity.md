# v4.1.6 Secure MCP Published App Production Identity

## Release intent

v4.1.6 closes the production observability gap identified after the published `Mesh CoS MCP` ChatGPT app was connected to the QNAP runtime through the OpenAI Secure MCP Tunnel and successfully passed a ten-call sequential read-only acceptance run.

The release does not change the canonical Phase 1 authority/runtime contract, which remains `4.0.0`.

## Requirements trace

| Requirement | Implementation | Verification |
| --- | --- | --- |
| Preserve canonical authority | `chatgpt/mcp/mesh-cos-mcp.v1.json` remains runtime release 4.0.0 | existing contract/drift suites |
| Make deployed QNAP release observable | tool envelopes include `deployment_release` | MCP smoke and hosted post-deploy acceptance |
| Fail closed without remote deployment identity | `requireDeploymentRelease()` gates remote startup | Node regression test |
| Expose non-secret runtime identity | `/healthz` and `/readyz` return dual release identity, bound agent, transport | production container CI |
| Keep modern protocol readiness release-aligned | readiness discovery client version derives from deployment release | source regression and transport CI |
| Preserve tunnel ingress boundary | source-IP gate remains before `/mcp` dispatch | direct-ingress 403 CI |
| Preserve catalog/roster | 27 CoS tools, 10 registered agents, human-only exclusions unchanged | smoke, drift, hosted acceptance |
| Align release train | active QNAP artifacts advance to 4.1.6 | release-bundle and workflow checks |
| Update CI dependency | `actions/setup-node@v7` | full CI execution |
| Record hosted evidence | published app acceptance record checked in | `docs/chatgpt-published-app-production-acceptance-v4.1.6.md` |

## TDD evidence

RED was established on PR #40 by adding the `requireDeploymentRelease` regression contract before implementation. CI failed at TypeScript build because the function did not exist.

GREEN adds the deployment identity helper and propagates release identity through production configuration and response surfaces while preserving existing authority semantics.

## Production response contract

Successful governed tool responses retain existing fields and add one backward-compatible field:

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

`mcp_version` continues to identify the canonical authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the request.

## Health and readiness contract

Production `/healthz` and successful `/readyz` report:

```json
{
  "ok": true,
  "mcp_version": "4.0.0",
  "deployment_release": "4.1.6",
  "agent_id": "cos",
  "transport": "SECURE_MCP_TUNNEL"
}
```

Readiness still requires active bound-agent state, valid governance audit chain, and successful modern MCP discovery.

## Hosted acceptance baseline

The installed ChatGPT app successfully executed the documented ten sequential read-only calls without 502, `invalid_session`, reconnect, or container restart. That live run confirmed transport stability and the existing authority projection, while also revealing that the serving deployment release could not be proven from ChatGPT-side responses.

See `docs/chatgpt-published-app-production-acceptance-v4.1.6.md`.

## Security

Security applicability is TARGETED. The new metadata is non-secret and cannot select identity, tools, authority, approval, or canonical state. See `docs/qnap-security-review-v4.1.6.md`.

## Release identity

- Deployment release: `4.1.6`
- Semantic tag: `v4.1.6`
- Canonical Phase 1 MCP authority/runtime contract: `4.0.0`
- Canonical workforce: 10 registered agents
- CoS governed tool catalog: 27 tools
- Production transport: OpenAI Secure MCP Tunnel
- Issue: #39
- PR: #40

# Mesh CoS MCP contract

`mesh-cos-mcp.v1.json` is the protocol-facing contract for exposing the existing Phase 1 Python control plane to ChatGPT Workspace Agents. It is an adapter contract, not a second business-logic implementation.

## Enforcement order

1. Authenticate the Workspace Agent or approved service identity.
2. Resolve canonical `agent_id`.
3. Apply the per-agent MCP tool allowlist.
4. Apply registry source/tool/action permissions and L0-L5 authority.
5. Fail closed on required human approval.
6. Invoke the mapped existing runtime service.
7. Persist canonical state before non-canonical mirrors or chat responses.
8. Emit `mesh.cos.agent-event.v2` for consequential actions and `mesh.cos.decision.v2` for material decisions/recommendations.

`src/mesh_cos/mcp_policy.py` provides server-side deny-by-default allowlist validation and checks that every declared runtime binding resolves to repository code.

The repository does not fabricate or deploy a remote MCP URL. Production deployment must publish an approved HTTPS MCP endpoint and set `MESH_COS_MCP_SERVER_URL`. Secrets remain outside source control.

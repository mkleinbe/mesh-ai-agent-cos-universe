# ChatGPT Published App Production Acceptance v4.1.8

## State

**Release candidate acceptance:** requires repository, security, container, and QNAP bundle gates to pass.

**Hosted production acceptance:** remains pending until v4.1.8 is deployed to the QNAP production environment and the published Mesh CoS MCP app is exercised through the OpenAI Secure MCP Tunnel.

## Required hosted identity

Every governed hosted tool response must include:

```text
mcp_version: 4.0.0
deployment_release: 4.1.8
agent_id: <server-bound agent>
```

For the published CoS connector the expected bound identity is `cos`.

## Minimum post-deploy smoke

1. `registry.list_agents` returns exactly 10 ACTIVE Phase 1 agents.
2. `registry.get_agent` resolves the bound identity.
3. A valid synthetic `task.intake` succeeds and is idempotent.
4. An invalid synthetic `task.intake` returns `validation_failed` with safe field-level details.
5. `task.get` and `task.decompose` resolve the same canonical parent identifier when the documented schema is used.
6. `skills.invoke_governed` resolves an authorized declared CoS capability as a governed `CHATGPT_SKILL_HANDOFF`; nonexistent and unauthorized capabilities fail closed.
7. `agentops.recommend` accepts its documented minimum contract.
8. Completion and verification remain separate operations.
9. Human-only operations remain absent from agent-facing catalogs.
10. `governance.verify_audit_chain` remains valid before and after synthetic acceptance writes.

Synthetic acceptance records must not perform external sends, public publishing, client commitments, pricing commitments, staffing commitments, or other consequential real-world actions.

## Multi-agent boundary

Repository/container tests must establish all ten immutable `MESH_COS_AGENT_ID` bindings and their exact allowlists. Hosted production acceptance must not claim independent downstream-agent sessions unless those sessions are actually provisioned and tested. A CoS session reading another registry record is not evidence of that agent's independent authentication.

## Pass rule

Do not mark production acceptance PASS until the actual hosted candidate exhibits the expected schema, identity, authorization, Skill handoff, TaskLedger, lifecycle, and audit behavior. Repository tests alone are insufficient.

# ChatGPT Secure MCP Tunnel Connection and Acceptance

Run this only after the v4.1.5 `mesh-cos-mcp-deploy.sh` path reports successful deployment, verification, and post-deploy backup.

## 1. OpenAI tunnel prerequisites

In OpenAI Platform tunnel settings:

1. Create or select the Secure MCP Tunnel used by this deployment.
2. Ensure the tunnel is associated with the Platform organization that owns/manages it and with the target ChatGPT workspace.
3. The operator who creates or edits the tunnel needs **Tunnels Read + Manage**.
4. The operator who runs `tunnel-client` or selects the tunnel while creating the ChatGPT app needs **Tunnels Read + Use**.
5. Record the `tunnel_id` and create the runtime API key used by the QNAP deployment script.

The QNAP tunnel client needs outbound HTTPS to `api.openai.com:443` and local private reachability to `mesh-cos-mcp`. It does not need inbound internet exposure.

## 2. Select or refresh the ChatGPT app

Use ChatGPT on the web with a workspace/account allowed to use the custom MCP app.

1. Open the existing `Mesh CoS MCP` app or its developer-mode configuration.
2. Confirm the connection still points to the same Secure MCP Tunnel used by the QNAP deployment.
3. Run **Scan Tools** again after the v4.1.5 upgrade.
4. Keep `mesh-cos-tunnel` healthy until the scan completes.

The production transport remains Secure MCP Tunnel. No additional MCP-layer OAuth flow is introduced by v4.1.5.

## 3. QNAP release-identity acceptance

Before hosted MCP calls, confirm the local deployment actually advanced:

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
```

PASS requires:

- `mesh-cos-mcp:qnap-v4.1.5` is running and healthy;
- the tunnel is running and healthy;
- `.env` reports `MESH_COS_DEPLOYMENT_RELEASE=4.1.5`;
- bundle metadata reports `4.1.5`.

The two release values must match. A stale v4.1.3 preflight literal must no longer block deployment.

## 4. Tool-catalog acceptance

The scan must expose exactly the 27 CoS tools below:

```text
agentops.recommend
agentops.record_event
agentops.score
answer_desk.resolve
approval.get
approval.request
conflict.decide
conflict.open
delegation.create
governance.record_decision
governance.record_event
governance.verify_audit_chain
metrics.snapshot
registry.get_agent
registry.list_agents
reliability.replay
skills.invoke_governed
task.check_in
task.complete
task.decompose
task.get
task.intake
task.list
task.reassign
task.remediate_stall
task.transition
task.verify
```

The following human-principal-only operations must **not** appear:

```text
approval.record_decision
reliability.human_override
```

Mesh Devil's Advocate must not appear as an agent principal. It remains a governed shared Skill.

## 5. Sequential transport acceptance

v4.1.5 carries forward the v4.1.4 remediation for the prior session-loss/502 behavior. Open a new chat with only `Mesh CoS MCP` selected and execute these calls sequentially in the same conversation without restarting the QNAP containers between calls:

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

PASS requires all ten calls to return successfully with no `502`, `invalid_session`, reconnect requirement, or container restart. The roster calls must continue to show exactly 10 agents.

## 6. Read-only authority acceptance

Run:

```text
Using only the Mesh CoS MCP app, call registry.list_agents. Return only agent_id, display_name, and parent_agent_id. Do not invoke any write tool.
```

PASS requires exactly 10 registered agents, including `message-ops`, and no `devils-advocate` principal.

Then run:

```text
Using only the Mesh CoS MCP app, call governance.verify_audit_chain, then metrics.snapshot. Do not invoke any write tool. Report the audit-chain result and the returned metrics without modifying canonical state.
```

PASS requires a valid audit-chain result and a successful metrics response.

## 7. Governed-write acceptance

Use the low-authority, idempotent acceptance task below:

```text
Using only the Mesh CoS MCP app, invoke task.intake with exactly these values:
objective: QNAP Secure MCP acceptance v4.1.5
expected_outcome: Confirm the governed write path persists to the canonical TaskLedger after the v4.1.5 deployment correction
requested_by: michael
executive_sponsor: michael
accountable_agent: cos
decision_owner: michael
authority_level: 0
acceptance_test: Read the task back through task.get and confirm it exists in canonical state without treating completion as verification
idempotency_key: qnap-secure-mcp-v4.1.5

Return the created or existing task_id. Do not call task.complete or task.verify.
```

Then call `task.get` for the returned task ID and confirm the objective, accountable agent, authority level, and acceptance test match. Finally call `governance.verify_audit_chain` again.

PASS requires successful canonical readback and a valid audit chain. Re-running the acceptance task with the same idempotency key must resolve to the same canonical task rather than creating a duplicate.

## 8. Acceptance boundary

Do not use `task.complete`, `task.verify`, `approval.request`, `conflict.decide`, `reliability.replay`, or external messaging/publishing actions during initial v4.1.5 acceptance. The purpose is to prove deployment identity, transport reliability, catalog projection, immutable CoS identity, canonical persistence, and audit integrity without making a business commitment.

The production deployment blocker is closed only after the v4.1.5 QNAP runtime passes both the local release-identity checks and sequential hosted-path acceptance without a restart between calls.

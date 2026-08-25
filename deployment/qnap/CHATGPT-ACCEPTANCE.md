# ChatGPT Secure MCP Tunnel Connection and Acceptance

Run this after the **v4.1.7** `mesh-cos-mcp-deploy.sh` path reports successful deployment, verification, and post-deploy backup.

The production ChatGPT surface is the published **Mesh CoS MCP** app connected to the QNAP-hosted MCP runtime through the **OpenAI Secure MCP Tunnel**. The canonical Phase 1 MCP authority/runtime contract remains **4.0.0**. The QNAP deployment release is independently identified as **4.1.7**.

v4.1.7 specifically closes the release blocker where the hosted app was functionally healthy but successful governed responses omitted `deployment_release`.

## 1. OpenAI tunnel prerequisites

In OpenAI Platform tunnel settings:

1. Create or select the Secure MCP Tunnel used by this deployment.
2. Ensure the tunnel is associated with the Platform organization that owns/manages it and with the target ChatGPT workspace.
3. The operator who creates or edits the tunnel needs **Tunnels Read + Manage**.
4. The operator who runs `tunnel-client` or selects the tunnel while creating the ChatGPT app needs **Tunnels Read + Use**.
5. Record the `tunnel_id` and create the runtime API key used by the QNAP deployment script.

The QNAP tunnel client needs outbound HTTPS to `api.openai.com:443` and private reachability to `mesh-cos-mcp`. It does not need inbound internet exposure.

## 2. Select or refresh the ChatGPT app

Use ChatGPT on the web with a workspace/account allowed to use the custom MCP app.

1. Open the installed **Mesh CoS MCP** app or its developer-mode configuration.
2. Confirm the connection points to the Secure MCP Tunnel used by the QNAP deployment.
3. Run **Scan Tools** again after the v4.1.7 upgrade.
4. Keep `mesh-cos-tunnel` healthy until the scan completes.

No additional MCP-layer OAuth flow is introduced by v4.1.7. The Secure MCP Tunnel remains the production ingress trust boundary.

## 3. Local deployment-identity and provenance acceptance

The deployment itself now performs a real read-only governed MCP `registry.get_agent` call from the tunnel network namespace. PASS from `mesh-cos-mcp-deploy.sh` therefore already requires the running tool envelope to expose the expected identities.

Capture additional local evidence with:

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{ index .Config.Labels "org.opencontainers.image.version" }} {{ index .Config.Labels "org.opencontainers.image.revision" }}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sed -n 's/^commit=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/healthz').then(r=>r.text()).then(console.log)"
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires:

- `mesh-cos-mcp:qnap-v4.1.7` is running and healthy;
- the tunnel is running and healthy;
- `.env` reports `MESH_COS_DEPLOYMENT_RELEASE=4.1.7`;
- bundle metadata reports `version=4.1.7`;
- the running image label reports `4.1.7-qnap` and its OCI revision equals the bundle `commit=` value;
- `/healthz` and `/readyz` both report `mcp_version: 4.0.0`, `deployment_release: 4.1.7`, `agent_id: cos`, and `transport: SECURE_MCP_TUNNEL`;
- the deployment verification log records `PASS governed tool envelope dual release identity`.

`mcp_version` identifies the canonical authority/runtime contract. `deployment_release` identifies the QNAP release serving the request. They are intentionally different values.

## 4. Tool-catalog acceptance

The app scan must expose exactly **27 CoS tools**:

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

These human-principal-only operations must **not** appear:

```text
approval.record_decision
reliability.human_override
```

Mesh Devil's Advocate must not appear as an agent principal. It remains a governed shared Skill. Message Operations remains a registered agent.

## 5. Published-app sequential transport and identity acceptance

Open a new chat with only **Mesh CoS MCP** selected. Without restarting either QNAP container, execute these calls sequentially in the same conversation:

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

PASS requires all ten calls to return successfully with no `502`, `invalid_session`, reconnect requirement, or container restart. Both roster calls must show exactly **10 registered agents**.

For **every** successful governed tool call, inspect the returned envelope. PASS requires:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
```

The underlying `result` payload must retain its canonical tool semantics.

Any successful hosted response that omits `deployment_release` is a **release blocker**, even if the tool result itself is correct.

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

## 7. Optional governed-write acceptance

After read-only acceptance is green, use this low-authority idempotent task only when a production write is explicitly desired:

```text
Using only the Mesh CoS MCP app, invoke task.intake with exactly these values:
objective: QNAP Secure MCP acceptance v4.1.7
expected_outcome: Confirm the governed write path persists to the canonical TaskLedger after the v4.1.7 deployment
requested_by: michael
executive_sponsor: michael
accountable_agent: cos
decision_owner: michael
authority_level: 0
acceptance_test: Read the task back through task.get and confirm it exists in canonical state without treating completion as verification
idempotency_key: qnap-secure-mcp-v4.1.7

Return the created or existing task_id. Do not call task.complete or task.verify.
```

Call `task.get` for the returned task ID and confirm the objective, accountable agent, authority level, and acceptance test. Then call `governance.verify_audit_chain` again. Re-running the intake with the same idempotency key must resolve to the same canonical task rather than create a duplicate.

## 8. Acceptance boundary

Do not use `task.complete`, `task.verify`, `approval.request`, `conflict.decide`, `reliability.replay`, or external messaging/publishing actions during initial v4.1.7 acceptance. The purpose is to prove release provenance, deployment identity, transport reliability, catalog projection, immutable CoS identity, canonical persistence, and audit integrity without making a business commitment.

v4.1.7 is accepted only after local provenance/governed-envelope verification and the hosted published-app sequence are both green.

# ChatGPT Secure MCP Tunnel Connection and Acceptance

Run this only after `mesh-cos-mcp-deploy.sh` reports successful deployment, verification, and post-deploy backup.

## 1. OpenAI tunnel prerequisites

In OpenAI Platform tunnel settings:

1. Create or select the Secure MCP Tunnel used by this deployment.
2. Ensure the tunnel is associated with the Platform organization that owns/manages it and with the target ChatGPT workspace.
3. The operator who creates or edits the tunnel needs **Tunnels Read + Manage**.
4. The operator who runs `tunnel-client` or selects the tunnel while creating the ChatGPT app needs **Tunnels Read + Use**.
5. Record the `tunnel_id` and create the runtime API key used by the QNAP deployment script.

The QNAP tunnel client needs outbound HTTPS to `api.openai.com:443` and local private reachability to `mesh-cos-mcp`. It does not need inbound internet exposure.

Official guide: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels

## 2. Create the ChatGPT developer-mode app

Use ChatGPT on the web with a workspace/account that is allowed to create custom MCP apps.

1. Enable Developer Mode for your account according to the workspace policy.
2. Open the custom app creation surface from Workspace Settings -> Apps -> Create, or Settings -> Apps -> Create when your role exposes it.
3. Name the draft app `Mesh CoS MCP`.
4. Under **Connection**, choose **Tunnel**.
5. Select the associated tunnel when listed, or paste the exact `tunnel_id` used by the QNAP deployment.
6. This Mesh deployment has no separate MCP-layer OAuth flow. If the app form asks for an additional authentication mechanism, select the no-additional-auth option appropriate to the current UI. The Secure MCP Tunnel remains the transport authentication boundary.
7. Click **Scan Tools** and keep `mesh-cos-tunnel` healthy until the scan finishes.
8. Keep the app as a **draft** until all acceptance checks pass.

Official developer-mode guide: https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt

## 3. Tool-catalog acceptance

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

## 4. Read-only acceptance

Open a new chat with only the `Mesh CoS MCP` draft app selected and run:

```text
Using only the Mesh CoS MCP app, call registry.list_agents. Return only agent_id, display_name, and parent_agent_id. Do not invoke any write tool.
```

PASS requires exactly 10 registered agents, including `message-ops`, and no `devils-advocate` principal.

Then run:

```text
Using only the Mesh CoS MCP app, call governance.verify_audit_chain, then metrics.snapshot. Do not invoke any write tool. Report the audit-chain result and the returned metrics without modifying canonical state.
```

PASS requires a valid audit-chain result and a successful metrics response.

## 5. Governed-write acceptance

Use a deliberately low-authority, idempotent acceptance task. Ask ChatGPT:

```text
Using only the Mesh CoS MCP app, invoke task.intake with exactly these values:
objective: QNAP Secure MCP acceptance v4.1.1
expected_outcome: Confirm the governed write path persists to the canonical TaskLedger
requested_by: michael
executive_sponsor: michael
accountable_agent: cos
decision_owner: michael
authority_level: 0
acceptance_test: Read the task back through task.get and confirm it exists in canonical state without treating completion as verification
idempotency_key: qnap-secure-mcp-v4.1.1

Return the created or existing task_id. Do not call task.complete or task.verify.
```

Then run:

```text
Using only the Mesh CoS MCP app, call task.get for the task_id returned by the acceptance task. Confirm the objective, accountable_agent, authority_level, and acceptance_test match. Do not transition, complete, or verify the task.
```

Finally run:

```text
Using only the Mesh CoS MCP app, call governance.verify_audit_chain. Do not invoke any other write tool.
```

PASS requires successful readback from the canonical TaskLedger and a valid audit chain. Re-running the write acceptance must return the same canonical task because the idempotency key is fixed.

## 6. Acceptance boundary

Do not use `task.complete`, `task.verify`, `approval.request`, `conflict.decide`, `reliability.replay`, or external messaging/publishing actions during initial connection acceptance. The purpose is to prove transport, catalog projection, immutable CoS identity, canonical persistence, and audit integrity without making a business commitment.

After the checks pass, retain the app as draft until the human release owner chooses to publish/enable it for broader use.

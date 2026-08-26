# Mesh CoS MCP Published App Production Acceptance v4.1.11

Use this procedure only after the v4.1.11 QNAP bundle has been deployed successfully. Repository CI and release-package verification are not substitutes for hosted acceptance.

## Local production identity prerequisite

The QNAP serving instance must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.11
agent_id: cos
slack_hitl_ready: true
```

Both `mesh-cos-mcp` and `mesh-cos-tunnel` must be healthy, the application image must be `mesh-cos-mcp:qnap-v4.1.11`, and the active descriptors under `/share/Docker/cos-mcp` must report release 4.1.11. The versioned release payload remains retained under `/share/Docker/cos-mcp/releases/v4.1.11` for evidence and rollback analysis.

## Published Mesh CoS MCP acceptance

Through the installed published Mesh CoS MCP app:

1. Confirm the CoS catalog exposes exactly 27 governed agent-facing tools.
2. Confirm `registry.list_agents` returns exactly 10 registered Mesh agents.
3. Confirm Message Operations is one of the 10 agents and Devil's Advocate is not an agent principal.
4. Confirm human-only operations remain absent from normal agent catalogs.
5. Submit invalid task intake without `accountable_agent` and confirm a safe structured `validation_failed` result.
6. Resolve a known canonical task and confirm TaskLedger persistence is intact.
7. Invoke an authorized governed Skill and confirm `AUTHORIZED / CHATGPT_SKILL_HANDOFF` behavior.
8. Confirm unknown Skills return `not_found`, unauthorized Skills return `forbidden`, and prohibited executable fields return `validation_failed`.
9. Exercise documented AgentOps behavior without changing human authority.
10. Confirm task completion and task verification remain separate state transitions.
11. Run `governance.verify_audit_chain` and require a valid chain.

## Slack HITL acceptance

Use a synthetic/internal-only approval scenario. Do not involve a real prospect, client, or consequential external send.

1. Create the governed pending approval and bind the official OpenAI ChatGPT/ChatGPT Agents bot-authored Slack notice.
2. Confirm ordinary Slack text such as `APPROVE ...` remains evidence only and does not change canonical approval state.
3. Use the authenticated `/mesh-approval` Socket Mode path as the trusted human decision ingress.
4. Confirm `approval.get` reflects the fresh canonical human decision.
5. Confirm the recorded human principal remains the configured human principal and no agent gains `approval.record_decision` authority.
6. Confirm no fallback posts an approval notice as the human user if the official OpenAI Workspace Agent delivery surface is unavailable.

## Dispatcher acceptance

Execute one controlled scheduled/dispatcher occurrence with an immutable idempotency key, canonical lifecycle progression, separate completion and verification, and no consequential external side effect. Repeat the same logical occurrence and confirm it does not create a duplicate canonical task.

## PASS condition

PASS requires the local production identity prerequisite, exact 10-agent roster, exact 27-tool CoS catalog, intact TaskLedger and audit chain, healthy tunnel, Slack HITL controls, scheduled idempotency/lifecycle behavior, and no unauthorized consequential action.

Do not call the release production accepted while any required live check is blocked or failed.

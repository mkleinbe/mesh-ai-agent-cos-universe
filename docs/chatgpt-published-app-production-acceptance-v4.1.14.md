# v4.1.14 Published ChatGPT App and Slack HITL Production Acceptance

Repository and release verification do not constitute production acceptance. Complete these checks only after the v4.1.14 QNAP deployment succeeds.

## QNAP runtime

- Confirm active deployment release is `4.1.14`.
- Confirm the running Mesh image OCI version is `4.1.14-qnap` and revision matches the published v4.1.14 merge SHA.
- Confirm `mesh-cos-mcp` and `mesh-cos-tunnel` are healthy.
- Confirm canonical TaskLedger remains `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` and existing state is preserved.
- Confirm OpenAI Secure MCP Tunnel identity and runtime key are preserved.
- Confirm governed Slack approver is `U01KG3CNYHK` and no `D...` conversation ID is treated as the human principal.
- Confirm Slack verifier and Socket Mode credentials load from protected read-only runtime files and `slack_hitl_ready` is true.
- Confirm `/healthz` and `/readyz` are healthy and report Secure MCP Tunnel transport, `mcp_version: 4.0.0`, `deployment_release: 4.1.14`, and `agent_id: cos`.

## Published ChatGPT app

- Exactly 10 agents are represented.
- CoS exposes exactly 27 governed agent-facing MCP tools.
- `approval.record_decision` and `reliability.human_override` remain human-only and absent from normal agent catalogs.
- Devil's Advocate remains a governed shared Skill, not an eleventh agent.
- Canonical TaskLedger reads succeed.
- Governed Skill handoff succeeds.
- Invalid requests return structured failures.
- Audit chain is valid.
- `COMPLETED != VERIFIED` remains enforced.
- No unauthorized consequential action is available.

## Live Slack HITL

Execute an authenticated `/mesh-approval` acceptance path using the governed human principal. Verify the command is accepted only from the authorized Slack context, maps to the exact pending approval, records the human decision once, rejects replay, and never accepts ordinary copied text or conversation IDs as human authority.

## Acceptance status

Production acceptance is PASS only when QNAP runtime, Secure MCP Tunnel, published ChatGPT app, and live Slack HITL checks above all pass against v4.1.14. Until then, report repository/release verification separately from production acceptance.

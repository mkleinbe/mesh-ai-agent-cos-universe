# Verification v4.1.13: Slack Approver Bootstrap

## Defect reproduced

v4.1.12 asked the operator for the human approver Slack user ID. The operator supplied `D01K4CL2F8F`, exactly as shown by Slack as a Channel ID. The deployment rejected the value because the runtime requires a Slack user principal beginning with `U` or `W`.

The verified Mesh Slack account for Michael/MK is `U01KG3CNYHK`.

## Required GREEN evidence

1. Ready BDD scenarios QNAP-092 through QNAP-099 are present.
2. `mesh-cos-slack-hitl-configure.sh` contains the governed default `U01KG3CNYHK`.
3. No visible approver-user-ID TTY prompt remains.
4. A missing approver identity file is created from the governed default.
5. Forced Slack HITL reconfiguration restages the governed default without prompting for the user ID.
6. `D...` approver values fail closed with an explicit conversation/DM-channel diagnostic.
7. Only `U...` or `W...` Slack user principal forms are accepted.
8. An existing valid protected approver identity is validated and preserved when reconfiguration is not forced.
9. Slack verifier bot and Socket Mode app tokens remain hidden protected runtime inputs and are absent from the release artifact.
10. v4.1.13 release ZIP contains a single top-level `v4.1.13/` directory and remains executable from `/share/Docker/cos-mcp/releases`.
11. Full Python, TypeScript/npm, contract drift, Ruff, mypy, Bandit, QNAP shell, Compose, production container, modern MCP, ownership, hardened-runtime, restart/persistence, and SQLite backup gates pass.
12. Phase 1 authority/runtime contract remains `4.0.0`, with exactly 10 agents and 27 governed CoS tools.

## Live acceptance boundary

After QNAP deployment, verify:

- `mcp_version: 4.0.0`
- `deployment_release: 4.1.13`
- `agent_id: cos`
- `slack_hitl_ready: true`
- the protected approver identity resolves to the intended human principal
- authenticated `/mesh-approval` commands from that principal succeed
- approval attempts by other Slack users fail closed
- ordinary Slack text remains non-authoritative
- official notice-author verification remains intact

Production certification remains blocked until the actual hosted QNAP and Slack acceptance checks pass.

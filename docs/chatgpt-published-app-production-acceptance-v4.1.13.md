# ChatGPT Published App Production Acceptance v4.1.13

## Expected hosted identity

```text
mcp_version: 4.0.0
deployment_release: 4.1.13
agent_id: cos
slack_hitl_ready: true
```

## Runtime acceptance

- exactly 27 governed CoS tools are exposed
- exactly 10 agents are registered
- human-only operations remain absent from normal agent catalogs
- Devil's Advocate is a governed shared Skill, not an agent principal
- canonical TaskLedger lookup succeeds
- completion and verification remain separate
- governance audit-chain verification succeeds
- direct unauthenticated/non-tunnel MCP ingress remains denied

## Slack HITL acceptance

- protected approver identity file exists and contains the verified user principal `U01KG3CNYHK`
- no deployment-time approver-user-ID prompt is required
- `D...` conversation/channel identifiers are not treated as user principals
- Slack verifier token and Socket Mode token remain protected runtime secrets
- official OpenAI Workspace Agent notices continue to require verified allowed notice authors
- ordinary Slack text remains non-authoritative
- authenticated Socket Mode `/mesh-approval` from Michael/MK is accepted
- equivalent approval attempts from another Slack user fail closed
- the resulting human approval decision is recorded through the human-only approval boundary

## Production decision

Repository, CI, release-bundle, and container evidence are necessary but not sufficient. Do not mark production accepted until the live QNAP serving instance, Secure MCP Tunnel, published ChatGPT app, and Slack HITL path all pass this checklist with no open CRITICAL/HIGH defects.

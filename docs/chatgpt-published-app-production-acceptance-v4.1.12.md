# ChatGPT Published App Production Acceptance v4.1.12

Run this only after the v4.1.12 QNAP deployment completes locally without a blocking defect.

## Required hosted identity

The installed Mesh CoS MCP app must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.12
agent_id: cos
slack_hitl_ready: true
```

## Required authority checks

- exactly 10 registered agents;
- exactly 27 governed CoS tools;
- Message Operations is agent 10;
- Mesh Devil's Advocate is a governed shared Skill, not agent 11;
- `approval.record_decision` and `reliability.human_override` are absent from normal agent catalogs;
- invalid intake missing `accountable_agent` fails safely with structured `validation_failed`;
- unknown governed Skill returns `not_found`;
- unauthorized governed Skill returns `forbidden`;
- executable or authority-expanding Skill fields fail validation;
- owner completion remains separate from CoS verification;
- audit-chain validation succeeds.

## Scheduled execution and Slack HITL

Carry forward the v4.1.10 acceptance surface:

- immutable scheduled idempotency keys;
- canonical lifecycle progression;
- official OpenAI bot notice verification;
- ordinary Slack message negative control;
- authenticated Socket Mode `/mesh-approval` human decision path;
- protected approver identity and verifier credentials remain file-backed and never appear in evidence text;
- human approval remains human-only.

## Deployment-layout confirmation

Record that the deployed release was sourced from:

```text
/share/Docker/cos-mcp/releases/v4.1.12
```

and that the operator workflow was executed from:

```text
/share/Docker/cos-mcp/releases
```

No release helper must have been copied to `/share/Docker`, and no canonical TaskLedger or protected secret may reside beneath the versioned release directory.

## PASS boundary

Do not declare production accepted while any required hosted check is unexecuted, any critical/high defect is open, release identity differs from `4.1.12`, or the actual QNAP serving instance cannot demonstrate the required authority, audit, persistence, tunnel, and Slack HITL behavior.

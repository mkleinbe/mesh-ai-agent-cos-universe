# ChatGPT Published App Production Acceptance: QNAP 4.4.1

This acceptance supplements established authority/delegated-owner acceptance with exact deployment source identity and the bidirectional Slack HITL peer workflow.

## Identity gate

Require safe governed reads to report:

```text
mcp_version: 4.0.0
deployment_release: 4.4.1
source_commit: <exact merged v4.13.2 release commit>
agent_id: cos
```

The source commit must equal the GitHub release/tag target.

## Slack peer-HITL gate

Using synthetic non-consequential TaskLedger work:

1. Post INFO through governed `slack-adapter/post_interaction`; verify the dedicated ChatGPT bot is the Slack author.
2. Post MANUAL_ACTION and reply `DONE` as Michael/MK; verify provider reread and same-thread bot acknowledgement.
3. Reply `APPROVE` on the non-approval thread; verify no approval authority is created and explanatory feedback is posted.
4. For a fresh synthetic L4 approval, verify ambiguous language does not approve and exact APPROVE/DENY/CHANGES grammar is required.
5. Verify replay idempotency and wrong-user, bot-author, edited/unavailable-message, and provider-failure fail-closed behavior.
6. Verify TaskLedger and audit evidence after each case.

No consequential external action is permitted as an acceptance test.

Production acceptance passes only when exact source identity, runtime governance, Slack bot authorship, bidirectional acknowledgement, explicit approval grammar, idempotency, and audit-chain integrity all pass.

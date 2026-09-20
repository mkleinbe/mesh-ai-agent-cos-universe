# ChatGPT Published App Production Acceptance: QNAP 4.4.2

Run only after the verified 4.4.2 bundle is deployed through the existing operator-controlled QNAP procedure.

PASS first requires:

```text
mcp_version: 4.0.0
deployment_release: 4.4.2
source_commit: <exact v4.13.3 release commit>
agent_id: cos
slack_hitl_ready: true
```

Then create a fresh non-consequential L1 task. Before Slack interaction, verify human_touches=0 and the task is unbound. Post a MANUAL_ACTION using slack-adapter/post_interaction and verify task.get immediately reports channel C0BRL4GCL3A and the provider-confirmed root thread timestamp.

Michael replies DONE in Slack. Do not manually reconcile the clean acceptance event. Require the existing Mesh Slack HITL Dispatcher to carry only thread_ts and message_ts.

After the bot acknowledgment, task.get must report human_touches=1, the same channel/thread binding, approval_status=NOT_REQUIRED, unchanged authority and lifecycle, provider identity verified, provider reconciled, one bot acknowledgment, and a valid governance audit chain.

Replay the same locator through the governed reconciliation boundary. human_touches must remain 1 and no additional bot acknowledgment may appear.

Finally progress the UAT task separately through QA, completion, and independent verification. Telemetry alone must not advance lifecycle.

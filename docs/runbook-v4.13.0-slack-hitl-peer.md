## v4.13.3 canonical task telemetry addendum

For every governed root post, treat Slack's returned channel and root message timestamp as provider-confirmed identity. The notifier must bind those values to both the secondary task thread index and the canonical TaskRecord. task.get is the acceptance surface for slack_channel_id and slack_thread_ts.

For inbound human replies, human_touches means provider-authenticated human interaction with the canonical task. Count only after exact provider reread, configured-human identity verification, manual-authorship verification, and governed task/thread binding. The provider event `native-slack:<channel_id>:<message_ts>` is the idempotency identity and must count at most once.

Do not infer approval from human_touches. A nonapproval APPROVE reply can count as a touch while remaining incapable of creating authority. Bot acknowledgments, apps, bots, edited messages, wrong users, unbound messages, rejected events, and replay do not count. Telemetry does not complete or verify a task.

# Slack HITL Peer Workflow Runbook v4.13.0

## Operator contract

Use `slack-adapter/post_interaction` for non-approval human interaction and `slack-adapter/post_approval` only when a canonical pending approval exists.

Thread types:

- INFO: no response required.
- QUESTION: normal-language thread response.
- MANUAL_ACTION: reply DONE after completing the requested action.
- BLOCKER / INCIDENT: normal-language response for resolution context.
- STATUS: informational status conversation.
- APPROVAL: reply exactly APPROVE, DENY, CHANGE, or CHANGES: <details>.

Never use direct connected-Slack posting for governed operational/HITL notices. The provider author must be the configured bot identity.

## Dispatcher

Keep exactly one `Mesh Slack HITL Dispatcher`. It receives new MK thread replies in channel C0BRL4GCL3A and forwards only `thread_ts` and `message_ts` to `slack-adapter/reconcile_triggered_message`.

Do not parse message text, assert sender identity, infer approval, or mutate TaskLedger in the Work task.

## Troubleshooting

If no acknowledgment appears, inspect in order: Work event delivery, exact locator extraction, Slack provider reread, interaction-state binding, identity verification, replay record, approval state where applicable, then bot post result.

If a message appears authored by MK, the system used the wrong posting path. Do not change display text. Route the originating workflow through Mesh CoS MCP Slack bot operations.

If a conversational phrase appears on an approval thread, no authority should change. The bot should request an explicit command.

If Slack provider reread fails, do not retry by trusting trigger text. Preserve canonical state and retry the locator reconciliation after provider recovery.

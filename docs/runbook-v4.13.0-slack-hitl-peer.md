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

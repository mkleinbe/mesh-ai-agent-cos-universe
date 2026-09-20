# Mesh CoS v4.13.3 Slack HITL Task Telemetry Repair

v4.13.3 is a PATCH release correcting canonical TaskRecord observability for the existing Slack peer-HITL architecture.

## Root cause

The Slack notifier persisted provider-confirmed task/thread binding only in the secondary task_threads table. task.get reads the canonical serialized TaskRecord, so slack_channel_id and slack_thread_ts remained null.

The native provider reconciler persisted interaction evidence and bot acknowledgments but did not mutate TaskRecord.human_touches. The successful Slack interaction path therefore had correct interaction evidence but incomplete canonical task telemetry.

## Canonical semantics

- slack_channel_id and slack_thread_ts are written only after Slack returns a valid provider root-message identity for a governed interaction.
- human_touches counts a verified human interaction with the canonical task, not approval.
- A touch is eligible only after exact provider reread, manual-authorship verification, configured-human identity validation, governed task/thread binding, and provider-event replay protection.
- The provider event key is native-slack:<channel_id>:<message_ts>.
- A duplicate event cannot increment the count twice, including after process restart when TaskLedger state survives.
- Bot/app messages, bot acknowledgments, edits, wrong users, unbound messages, and rejected events do not count.
- APPROVE in a nonapproval thread may be a human touch but cannot create approval authority.
- Telemetry does not manufacture completion, verification, approval, outcome evidence, or authority.

## Implementation

TaskLedger.bind_thread now updates both the secondary thread index and the canonical TaskRecord in one database transaction when the task exists.

TaskLedger.record_human_touch atomically inserts a unique provider-event telemetry record and increments TaskRecord.human_touches. The native Slack reconciler invokes it only after provider identity/manual authorship and governed binding checks succeed.

## Deployment identity

Canonical MCP authority/runtime contract remains 4.0.0.

The QNAP candidate advances from 4.4.1 to 4.4.2 because the runtime source changed. Production Compose topology and networking are unchanged.

Production acceptance requires exact source-commit readback followed by a fresh dispatcher-only Slack UAT. Repository publication alone is not production acceptance.

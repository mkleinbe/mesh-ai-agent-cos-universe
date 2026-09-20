# QNAP 4.4.2

QNAP 4.4.2 packages Mesh CoS v4.13.3 Slack HITL canonical task telemetry repair.

- Runtime source changes persist provider-confirmed Slack task/thread binding in TaskRecord.
- Provider-authenticated human interactions increment TaskRecord.human_touches exactly once.
- Replay, approval authority, completion/verification separation, audit, Slack secrets, Secure MCP Tunnel, and production Compose topology remain unchanged.
- Exact source-commit/image/release-metadata agreement remains mandatory.

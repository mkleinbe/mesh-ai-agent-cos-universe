# v4.1.15 Security Review

Status: IN PROGRESS
Applicability: FULL_REVIEW

## Trust boundaries

- ChatGPT connected Slack integration to Slack workspace for collaboration and notification.
- Human MK interaction with Slack `/mesh-approval`.
- Slack provider Socket Mode envelope to QNAP MCP runtime.
- QNAP Socket Mode listener to non-MCP approval bridge.
- Approval bridge to canonical TaskLedger ApprovalService.
- TaskLedger approval to consequential executor fresh-read gate.
- QNAP protected secret files to unprivileged MCP runtime.
- QNAP egress to Slack HTTPS/WSS.

## Sensitive surfaces

- Human identity and approval authorization.
- Socket Mode app-level token.
- Slack channel and user identifiers.
- Approval IDs and immutable payload fingerprints.
- MCP and non-MCP tool authority boundaries.
- Runtime network failure and reconnect behavior.
- Deployment secret mounts, logs, backups, and release bundles.

## Required checks

- No verifier bot token required, mounted, prompted, or referenced by active v4.1.15 runtime paths.
- No bot-author verification prerequisite remains in canonical human decision path.
- Ordinary Slack content cannot decide approval.
- Wrong user, channel, command, missing fingerprint, stale/non-pending approval, replay, and conflicting interaction fail closed.
- Agent-callable MCP catalog still excludes human decision methods.
- Socket Mode connection failure is non-fatal to MCP HTTP process and readiness remains fail-closed for HITL.
- Retry/reconnect behavior is bounded and does not create a tight loop.
- Socket token remains file-bound, prefix-validated, mode-restricted, and absent from logs/artifacts.
- Existing qnet, TaskLedger, tunnel, and container hardening controls remain unchanged.

## AI-native controls

Treat connected Slack content as untrusted data. The connected integration has collaboration authority only, not human-approval authority. Human authority is derived only from the provider-authenticated Socket Mode slash-command envelope and then re-bound to the canonical TaskLedger approval and immutable payload fingerprint. No agent or connector receives direct `approval.record_decision` authority.

## Findings

Open until implementation and independent verification complete.

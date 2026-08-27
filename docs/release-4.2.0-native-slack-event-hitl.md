# Mesh CoS MCP v4.2.0 Release Contract

## Release identity

- Deployment release: `4.2.0`
- Canonical MCP runtime contract: `4.0.0`
- Production predecessor: `4.1.18`
- Workforce: exactly 10 registered agents
- Public MCP catalog: exactly 27 governed tools
- Remote transport: OpenAI Secure MCP Tunnel

## Change objective

Replace the QNAP-hosted Slack Socket Mode approval ingress introduced in v4.1.17 with ChatGPT-native Slack new-message task triggers while preserving the existing governed human-approval semantics and canonical TaskLedger authority.

## Target production flow

```text
MK replies in #mesh-agent-ops
        |
        v
ChatGPT native Slack new-message trigger
        |
        v
One Mesh Slack HITL Dispatcher task
        |
        v
Mesh CoS MCP skills.invoke_governed / slack-adapter
        |
        v
Server-side Slack conversations.replies reconciliation
        |
        v
Canonical TaskLedger approval state
```

## Behavioral changes

1. Slack approval notices are reply-driven and instruct `APPROVE`, `DENY`, or `CHANGE`.
2. Block Kit approval buttons are removed because button interactions are not Slack new-message events.
3. ChatGPT trigger payloads are routing hints only. The dispatcher passes only thread and message timestamps.
4. QNAP re-reads the exact Slack message using the protected bot token before authority can change.
5. The runtime rejects edited, app-authored, wrong-user, wrong-thread, root-message, missing, ambiguous, stale-fingerprint, and already-decided conflicting interactions.
6. Duplicate trigger delivery is idempotent.
7. CHANGE remains a two-step governed loop and requires a new approval fingerprint before consequential action.
8. QNAP no longer starts or requires a Slack WebSocket listener or xapp credential.
9. Secure MCP Tunnel remains the only remote MCP ingress.

## Compatibility invariants

- No new public MCP tool is added.
- `approval.record_decision` remains human-only and excluded from agent execution authority.
- The canonical TaskLedger schema and location are unchanged.
- Existing Slack bot identity and private approval channel remain unchanged.
- Existing approval fingerprint and human-principal controls remain authoritative.

## Deployment changes

- `MESH_COS_SLACK_HITL_MODE=CHATGPT_NATIVE_EVENT_TRIGGER` is required.
- `MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE` is forbidden for the v4.2.0 runtime.
- `QNAP_SLACK_SOCKET_APP_TOKEN_FILE` is removed from the release environment.
- Slack bot OAuth token and protected approver user ID remain required.
- v4.2.0 Slack app manifest disables Socket Mode, event subscriptions, and interactivity.

## Release artifacts

The immutable QNAP release bundle must contain:

- v4.2.0 compose and QNAP deployment scripts
- v4.2.0 Slack bot manifest
- native Slack event-trigger BDD specification
- full security review
- dispatcher configuration contract
- production acceptance plan
- verification receipt
- release metadata with exact commit SHA
- container build context
- ZIP SHA-256 sidecar

## Release criteria

Repository readiness requires all CI gates green, including 100% Python coverage, Node build/test/smoke/security, contract validation, QNAP shell regression, container build, MCP transport verification, and immutable bundle checksum verification.

Production readiness additionally requires external acceptance of the ChatGPT-native Slack trigger against synthetic approvals. Repository CI alone cannot prove the ChatGPT event subscription is configured or firing in the production ChatGPT workspace.

## Rollback

Rollback restores the prior immutable v4.1.18 QNAP release and disables the native Slack dispatcher task. Do not re-enable v4.1.17 Socket Mode behavior by combining v4.2.0 code with legacy xapp configuration. Rollback must use the complete prior release unit and a verified TaskLedger backup.
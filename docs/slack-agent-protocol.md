# Slack Agent Collaboration Protocol

Slack is the human-visible collaboration layer for the agent workforce. It is not the canonical system of record. Task, decision, approval, conflict, registry, performance, and audit state remains in the structured control plane.

## Channel model

Phase 1 uses configurable private channels/interfaces:

- agent-operations channel: `#mesh-agent-ops`, Channel ID `C0BRL4GCL3A`, configured through `MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID`
- a separate team-facing Answer Desk channel/interface, with its channel ID still to be supplied

Channel IDs are runtime configuration. Do not hardcode personal Slack user IDs, bot credentials, or secrets in application code.

## One task, one thread

Every meaningful Slack task discussion maps to one TaskRecord and one primary Slack thread. The mapping is persisted in the canonical ledger before it is treated as established.

Example top-level structure:

```text
[TASK] COS-2026-0042
Objective: Build Fulton proposal staffing and economics
Priority: P1
Accountable: CRO
Contributors: CFO, COO
Status: ASSIGNED
Decision owner: Michael
Approval level: L4
Due: <timestamp>
```

## Structured message types

- `[ASSIGN]`
- `[ACK]`
- `[UPDATE]`
- `[REQUEST]`
- `[EVIDENCE]`
- `[RISK]`
- `[BLOCKED]`
- `[CONFLICT]`
- `[RECOMMEND]`
- `[DECISION]`
- `[APPROVAL]`
- `[COMPLETE]`
- `[VERIFY]`

A consequential message should include task ID, acting-agent identity, action/state, material evidence/reference, and requested next action when applicable.

## Identity strategy

Phase 1 uses one Slack integration with explicit acting-agent labels rather than a separate Slack app/identity for every agent. The rationale is documented in ADR-004. This reduces operational burden and token/app sprawl while preserving visible acting identity in the message contract.

Future identity changes require review of Slack constraints, least privilege, audit requirements, and operational complexity.

## Inbound security

`SlackEventReceiver` verifies Slack's v0 request signature against the configured signing secret and rejects missing, invalid, or stale request metadata. URL-verification challenges are handled without bypassing signature validation.

Duplicate inbound `event_id` values are durably suppressed by the canonical idempotency store. Process restarts therefore do not reset duplicate-event protection.

## Outbound transport

`SlackWebApiTransport` implements the Slack `chat.postMessage` boundary using the configured bot token. `SlackAdapter` creates the task thread, persists the channel/thread mapping, and posts structured task events into the existing thread.

The repository contains no bot token or signing secret. Live execution requires those values through the approved secret-management mechanism.

## Communication controls

Agents communicate when:

- accepting work
- task state materially changes
- evidence is found
- a dependency is required
- a risk appears
- a recommendation is ready
- a conflict exists
- approval is needed
- work is complete or verified

Do not post thinking aloud, social filler, or repetitive status chatter.

If repeated agent exchanges do not change task state, resolve a dependency, or produce new evidence, AgentOps flags a coordination loop. Cross-functional debates go to CoS rather than expanding into unlimited ping-pong.

## Canonical state

Slack messages may reference or mirror task state but do not become authoritative merely because they were posted. Agents must not reconstruct canonical state solely by rereading Slack history.

If Slack is unavailable, ledger-based orchestration and audit state remain intact.

## Approval messages

A Slack `[APPROVAL]` message is a notification, not authorization. The consequential action remains blocked until the control plane records a valid approval from the required decision owner.

## Answer Desk

The Slack adapter exposes a separate Answer Desk posting boundary. It fails closed when `MESH_COS_SLACK_ANSWER_DESK_CHANNEL_ID` is not configured. This prevents agent-operations traffic from being silently repurposed as a team-facing Answer Desk channel.

## Security and data minimization

Use:

- private agent-operations channel
- least-privilege Slack app scopes
- source-access checks
- data minimization
- protected-source references instead of raw exports where possible

Do not paste unnecessary personal information, confidential client exports, private DMs, credentials, secrets, or large protected-source extracts.

## Integration status

The Phase 1 Slack engineering boundary is implemented and tested: Web API transport, signature verification, durable event dedupe, task/thread persistence, structured messages, and approval/Answer Desk boundaries. Production activation depends only on environment-specific Slack secrets and the eventual Answer Desk channel ID.

# Slack Agent Collaboration Protocol

Slack is the human-visible collaboration layer for the agent workforce. It is not the canonical system of record. Task, decision, approval, conflict, registry, performance, and audit state remains in the structured control plane.

## Channel model

Phase 1 expects configurable private channels/interfaces:

- a private agent-operations channel, human-readable suggestion `#mesh-agent-ops`
- a separate team-facing Answer Desk channel/interface

Names and IDs are configuration. Do not hardcode a Slack channel ID or personal Slack user ID.

## One task, one thread

Every meaningful Slack task discussion maps to one TaskRecord and one primary Slack thread.

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

## Idempotency

Slack may deliver duplicate events. Duplicate event IDs/idempotency keys must not create duplicate tasks, delegations, approvals, or actions.

## Security

Use:

- private agent-operations channel
- least-privilege Slack app scopes
- source-access checks
- data minimization
- protected-source references instead of raw exports where possible

Do not paste unnecessary personal information, confidential client exports, private DMs, credentials, secrets, or large protected-source extracts.

## Approval messages

A Slack `[APPROVAL]` message is not sufficient by itself unless the control plane records a valid approval from the required decision owner. Approval state remains canonical outside Slack.

## Integration status

The Phase 1 repository implements message formatting/parsing concepts, task/thread mapping, and duplicate-event protection. Live Slack network calls require channel configuration, least-privilege app installation, bot token, and signing secret.

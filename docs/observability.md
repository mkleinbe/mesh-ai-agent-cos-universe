# Observability and Auditability

Phase 1 treats observability as an operating control. The system must make delegated work, authority, evidence, approvals, defects, performance, and outcomes inspectable without reconstructing state from Slack conversations.

## Canonical event envelope

Consequential actions use an event structure containing:

- `event_id`
- `event_type`
- `event_version`
- timestamp
- actor agent
- task ID
- correlation ID
- source
- before state where applicable
- after state where applicable
- authority level
- approval reference
- evidence references
- result
- error
- idempotency key

Do not log secrets.

## Events that must be auditable

At minimum:

- delegation
- reassignment
- task state transition
- conflict creation/disposition
- approval request
- approval/rejection
- consequential external-action attempt
- completion
- verification
- agent restriction
- agent quarantine
- registry change

## AgentOps signals

Operational monitoring should expose:

- task success and failure
- stalled tasks and missed deadlines
- rework
- escalation quality
- rejection reasons and error taxonomy
- workload and concurrency
- repeated tool failure
- evidence/provenance defects
- high-cost/low-value loops
- coordination-loop rate
- agent health state

## Executive leverage signals

Where methodologically supportable, track:

- tasks resolved without Michael
- questions deflected from Michael
- CEO touches per task
- CEO decisions required
- CEO interventions
- estimated CEO time avoided with explicit methodology

No fabricated baselines, targets, or time savings.

## Idempotency and replay

Duplicate external events, especially Slack deliveries, must not create duplicate tasks or duplicate consequential actions. Events should be replayable where practical without violating idempotency.

## Slack relationship

Slack is observable collaboration only. Slack timestamps/channel/thread IDs may be stored as task metadata, but Slack message history is not authoritative task state.

## Incident evidence

On critical defects or suspected unauthorized actions, preserve the task, event, approval, source, and error chain needed for root-cause analysis. Do not destroy audit evidence as part of remediation.

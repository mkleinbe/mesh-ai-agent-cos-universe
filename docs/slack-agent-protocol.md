# Slack Agent Protocol

Slack is the observable collaboration and human-interaction layer for Mesh operations. TaskLedger remains canonical for task, approval, completion, verification, and audit state.

## Governed surface

- Channel: `#mesh-agent-ops`
- Channel ID: `C0BRL4GCL3A`
- Human principal: `michael`
- Human Slack user: protected configured provider identity
- Outbound system identity: protected Slack bot OAuth identity
- Dispatcher: one persistent ChatGPT Work task, `Mesh Slack HITL Dispatcher`
- Runtime mode: `CHATGPT_NATIVE_EVENT_TRIGGER`

## Operating model

```mermaid
sequenceDiagram
    participant A as Mesh agent / scheduled workflow
    participant C as Mesh CoS MCP
    participant L as TaskLedger
    participant B as Slack bot identity
    participant S as Slack provider
    participant M as Michael
    participant W as ChatGPT Work dispatcher
    A->>C: governed interaction request
    C->>L: read canonical task / approval state
    C->>B: post classified message
    B->>S: chat.postMessage as bot
    S-->>M: INFORMATION / ACTION / APPROVAL / QUESTION
    M->>S: thread reply
    S-->>W: native Slack event
    W->>C: thread_ts + message_ts only
    C->>S: provider reread exact reply
    C->>C: verify channel, human identity, thread, replay
    alt conversational thread
        C->>L: persist interaction evidence only
        Note over C,L: No approval authority created
    else approval thread with exact command
        C->>L: revalidate pending approval + fingerprint
        C->>L: record APPROVE / DENY / CHANGES
    else ambiguous approval language
        Note over C,L: Fail closed, no authority mutation
    end
    C->>B: acknowledgment / resulting state
    B->>S: same-thread bot reply
    S-->>M: visible feedback
```

## Outbound interaction contract

Governed HITL requests use `skills.invoke_governed` with capability `slack-adapter`.

### Non-approval

Operation: `post_interaction`

Required payload:

- `thread_type`
- `task_id`
- `summary`
- `requested_human_action`
- `completion_condition`

Supported thread types:

- `INFO`
- `QUESTION`
- `MANUAL_ACTION`
- `BLOCKER`
- `STATUS`
- `INCIDENT`

The server renders an explicit message heading, what happened, what Michael needs to do, how to respond, the authority statement, and the canonical task ID. `MANUAL_ACTION` instructs Michael to reply `DONE`; `INFO` states that no response is required.

### Approval

Operation: `post_approval`

This operation requires an existing canonical `PENDING` approval owned by `michael` and bound to an immutable 64-hex payload fingerprint.

The Slack message identifies itself as `APPROVAL REQUIRED` and instructs Michael to reply with exactly one of:

- `APPROVE`
- `DENY`
- `CHANGE`
- `CHANGES: <details>`

`CHANGE` starts a two-step change-input exchange. `CHANGES: <details>` captures the change directly as untrusted input and supersedes the old approval.

## Inbound dispatcher contract

The ChatGPT Work dispatcher is intentionally thin.

It may use the Slack event to determine that a new message arrived in the governed channel from the configured human and that the event is a thread reply. It must forward only:

- `thread_ts`
- `message_ts`

to `slack-adapter/reconcile_triggered_message`.

The dispatcher must not pass or trust trigger text, asserted user identity, approval state, actor, principal, or a decision boolean.

## Provider reread and classification

Mesh CoS MCP rereads the exact Slack reply with `conversations.replies`, then validates:

- configured channel;
- exact thread and message locator;
- unedited provider message;
- manual-human authorship;
- configured human Slack identity;
- governed thread state;
- replay/idempotency state.

A non-approval thread may interpret natural language only for conversational acknowledgment and interaction evidence. It cannot create approval authority.

An approval thread additionally revalidates:

- canonical approval binding;
- approval remains `PENDING`;
- approval owner is `michael`;
- immutable payload fingerprint still matches.

Only the exact explicit command grammar may change approval state.

## Interaction state

Each governed thread persists machine-readable state including:

- thread type;
- canonical task ID;
- approval ID where applicable;
- requesting agent;
- accountable owner;
- current task state;
- response-required flag;
- valid response classes;
- explicit-approval-required flag;
- requested human action;
- completion condition;
- last processed reply;
- last bot acknowledgment;
- replay/idempotency key.

Do not infer an approval thread from phrases such as “human action requested.”

## Feedback behavior

Every successfully reconciled human reply produces a bounded visible state response unless the same provider message was already processed.

Examples:

- conversational confirmation: explain current action without approval mutation;
- `DONE`: record manual completion evidence and state that verification remains separate;
- `APPROVE` on non-approval thread: explain that no approval was recorded;
- ambiguous text on approval thread: request an explicit approval command;
- explicit approval: acknowledge only after server-side reconciliation;
- duplicate event: return the existing canonical result without duplicate Slack spam.

## Identity

All system-originated governed HITL posts must use the Slack bot OAuth identity. Do not use connected-Slack posting as the operator notification path and do not emulate bot identity with display text, `username`, icons, or avatar overrides.

If Slack shows a system notice as authored by MK, treat that as an execution-path defect and trace the originating workflow.

## Failure behavior

Wrong user, wrong channel, bot/app-authored reply, edited message, unbound thread, unavailable exact provider message, stale approval fingerprint, conflicting decision, or provider failure fails closed.

A Work trigger is never authority. A model interpretation is never sufficient for L4 or L5 approval.

## Security and lifecycle

- Slack text is untrusted input.
- TaskLedger remains canonical.
- L4 approval requires the qualified human.
- L5 remains CEO-only.
- Replay/idempotency controls remain mandatory.
- Completion remains distinct from verification.
- Audit-chain evidence remains required.
- Consequential action must reread the fresh canonical approval immediately before execution.

## Compatibility

The legacy `post_message` collaboration operation remains available for non-HITL compatibility. New governed human-interaction requests must use `post_interaction` or `post_approval`.

The Answer Desk remains a separate surface and should not use `#mesh-agent-ops` as the normal team interface.

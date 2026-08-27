# Mesh CoS MCP v4.2.0 Security Review

Status: **FULL REVIEW CANDIDATE**

Release: `4.2.0`
Canonical MCP runtime contract: `4.0.0`
Scope: ChatGPT-native Slack event-triggered HITL, Slack provider reconciliation, TaskLedger authority mutation, QNAP runtime, Secure MCP Tunnel.

## Security decision

The v4.2.0 architecture is acceptable for release only if all repository verification gates pass and production acceptance proves the native Slack trigger against a non-consequential synthetic approval. The ChatGPT trigger is explicitly non-authoritative. Canonical approval authority is created only after the QNAP runtime independently re-reads Slack provider state and revalidates TaskLedger state.

## Trust boundaries

1. **Slack message and ChatGPT trigger payload are untrusted input.** The dispatcher may use event metadata only as a locator.
2. **Mesh CoS MCP is the policy boundary.** It rejects decision text, asserted actor identity, approval booleans, principal fields, and other authority-bearing trigger input.
3. **Slack Web API is the provider-evidence boundary.** The runtime retrieves the exact message using the protected bot credential and validates provider-attributed user, channel, thread, message timestamp, manual-human authorship, and edit state.
4. **TaskLedger is canonical state.** Approval owner, status, task binding, immutable payload fingerprint, prior decision state, and idempotency are revalidated before mutation.
5. **Secure MCP Tunnel remains the only remote MCP ingress.** v4.2.0 does not expose a new public QNAP callback endpoint.

## Threat model and controls

| Threat | Control | Result |
| --- | --- | --- |
| Trigger payload says `APPROVE` | Dispatcher cannot pass text/decision/approved/actor/principal/user ID into the governed Slack adapter | Fail closed |
| Another Slack user replies | Server compares Slack provider `user` to protected `U01KG3CNYHK` mapping for `michael` | Rejected |
| Bot/app generates approval reply | Existing manual-human checks reject `app_id`, `bot_id`, `bot_profile`, and message subtype evidence | Rejected |
| Message is edited after trigger | Server rejects provider messages carrying edit metadata | Rejected |
| Message is deleted or no longer retrievable | Exact provider lookup must return exactly one message | Rejected |
| Trigger points at a root message | `thread_ts == message_ts` is rejected | Rejected |
| Wrong or unbound thread | Provider thread must match locator and canonical thread binding | Rejected |
| Payload changed after approval notice | Canonical payload fingerprint must match immutable Slack binding | Rejected |
| Duplicate trigger delivery | Provider event key is deterministically derived from channel + Slack message timestamp; existing decision is returned idempotently | No second decision |
| Different second message attempts to reverse a decision | Existing approval service rejects a different provider interaction from re-deciding the same approval | Rejected |
| Slack API outage or rate limit | Reconciliation cannot establish provider evidence and therefore cannot mutate approval authority | Fail closed |
| Native trigger mis-filtered to extra messages | Server independently enforces governed channel, protected approver, bound thread, and decision grammar | Contained |
| QNAP Socket Mode credential compromise | v4.2.0 removes the xapp credential and Socket Mode listener from production readiness and compose mounts | Eliminated from active architecture |
| Bot token compromise | Bot token remains sensitive because it can post/read private-channel history. It is mounted read-only from a protected file, never logged, and cannot alone satisfy protected human-user checks | Residual risk, bounded |
| Agent attempts direct approval | `approval.record_decision` remains human-principal-only and is excluded from agent tool projection | Rejected |
| Agent tries to widen MCP surface | Public catalog and canonical runtime contract remain unchanged at 27 tools / runtime 4.0.0 | Rejected by contract tests |

## Least privilege

The v4.2.0 Slack bot manifest requires only:

- `chat:write` for governed bot-authored notices and replies
- `groups:history` for server-side reconciliation in the private approval channel

It disables Socket Mode, Slack event subscriptions, and Block Kit interactivity for the QNAP bot. The ChatGPT-native task trigger is configured in ChatGPT/Work and is not implemented as a QNAP Slack callback.

## Prompt-injection and untrusted-content handling

Slack message body text is never treated as trusted instructions to ChatGPT. The dispatcher must not interpret, summarize, transform, or relay the Slack text into an authority-bearing field. The only permitted dispatcher handoff is channel ID plus Slack root-thread timestamp and Slack message timestamp. The server then retrieves the actual provider message and applies a fixed decision grammar or stores CHANGE follow-up text as untrusted change requirements that require a new approval cycle.

## Secrets and data handling

- Approver Slack user ID remains in a protected runtime file.
- Slack bot OAuth token remains in a protected read-only runtime file and must start with `xoxb-`.
- The legacy Slack Socket Mode `xapp-` credential is not required, mounted, provisioned, or accepted by v4.2.0.
- Secret values are not emitted in preflight, deployment logs, audit summaries, or MCP errors.
- Canonical state remains `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` in production.

## Residual risks

1. **Native trigger platform drift.** ChatGPT trigger filtering or event metadata shape can change independently of the repository. Mitigation: production acceptance is mandatory and server-side checks never rely on the filter for authority.
2. **Slack API availability.** A provider outage delays approvals. Mitigation: fail closed and retry only by replaying the same locator; do not infer approval from cached trigger text.
3. **Bot credential compromise.** An attacker could read/post within granted Slack scope. Mitigation: protected secret storage, narrow scopes, protected human identity check, canonical thread/fingerprint binding, rotation procedure.
4. **Legacy compatibility code.** `SlackSocketApprovalService` and historical record naming remain internally reused as the hardened decision engine. Production does not open a WebSocket listener. Mitigation: verification must prove the listener is not started or required and no xapp secret exists in production configuration.

## Mandatory release gates

- 10-agent registry exact.
- 27-tool public MCP catalog exact.
- canonical runtime contract remains 4.0.0.
- `approval.record_decision` remains excluded from agent authority.
- Python lint/type/test coverage and Bandit pass.
- Node build/test/smoke/npm audit pass.
- QNAP POSIX deployment regression suite passes.
- v4.2.0 immutable release bundle and SHA-256 verification pass.
- production acceptance proves APPROVE, DENY, CHANGE, duplicate delivery, and negative-identity behavior on a synthetic non-consequential approval.

No production readiness claim is valid until the verification receipt records fresh evidence for these gates.
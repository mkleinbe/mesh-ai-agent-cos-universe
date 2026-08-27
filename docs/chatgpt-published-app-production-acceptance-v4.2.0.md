# ChatGPT / Slack Production Acceptance v4.2.0

Status: **REQUIRED AFTER DEPLOYMENT, BEFORE CONSEQUENTIAL USE**

## Preconditions

- QNAP runtime is deployed from the immutable v4.2.0 release bundle.
- `mesh-cos-mcp` and `mesh-cos-tunnel` are healthy.
- canonical TaskLedger backup is verified before promotion.
- runtime reports `slack_hitl_mode=CHATGPT_NATIVE_EVENT_TRIGGER`.
- no xapp Socket Mode credential is mounted or configured.
- the ChatGPT native Slack task is enabled for new messages in `C0BRL4GCL3A` from `U01KG3CNYHK`.
- exactly one Mesh Slack HITL Dispatcher task exists for this approval path.

## Acceptance matrix

Use synthetic, non-consequential approvals only.

| Test | Action | Expected canonical result |
| --- | --- | --- |
| Approve | MK replies `APPROVE` in bound thread | approval APPROVED; task READY_FOR_ACTION; provider reconciliation receipt recorded |
| Case tolerance | MK replies `approve` | same as APPROVE |
| Deny | MK replies `DENY` | approval REJECTED; no consequential action |
| Change start | MK replies `CHANGE` | AWAITING_CHANGE_INPUT; original approval remains unresolved until follow-up |
| Change detail | MK sends follow-up text | old approval superseded/rejected for change; task IN_PROGRESS; new payload fingerprint required |
| Duplicate delivery | replay same channel/thread/message timestamps | same result returned; no second decision |
| Wrong user | another Slack user replies APPROVE | canonical approval remains PENDING |
| Root message | MK posts APPROVE outside bound thread | no canonical mutation |
| Unbound thread | MK replies APPROVE in unrelated thread | no canonical mutation |
| Unknown text | MK replies `looks good` | no canonical mutation |
| App/bot message | bot emits APPROVE | no canonical mutation |
| Edited message | provider message is edited before reconciliation | no canonical mutation |
| Deleted/unavailable message | exact provider lookup cannot retrieve message | no canonical mutation |
| Fingerprint drift | approval payload changes after Slack binding | no canonical mutation |
| Slack unavailable | provider reconciliation fails | no canonical mutation |

## Evidence to retain

For each test capture:

- deployment release and container image identity
- MCP runtime contract version
- Slack channel ID
- root thread timestamp and reply timestamp
- canonical approval ID and task ID
- reconciliation status/disposition, excluding secret values
- TaskLedger before/after state
- audit-chain verification result
- native task run evidence

Do not record Slack bot tokens, tunnel keys, or raw protected identity files.

## Exit criteria

Production acceptance passes only when:

1. all positive cases create exactly the expected canonical state;
2. all negative cases fail closed;
3. duplicate delivery is idempotent;
4. the ChatGPT native task is the observed event ingress;
5. no QNAP Slack WebSocket listener is active;
6. no xapp secret is configured;
7. Secure MCP Tunnel remains the sole remote MCP ingress;
8. the TaskLedger audit chain verifies after the full matrix.

If any criterion fails, disable the ChatGPT native dispatcher task, restore the last verified production release if needed, and retain v4.2.0 as not production-accepted.
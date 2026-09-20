# Security Review v4.13.0 Slack HITL Peer Workflow

Status: READY FOR VERIFICATION

## Authority boundary

The change adds conversational interpretation and visible acknowledgments but does not add approval authority. Work triggers carry only Slack provider locators. Mesh CoS MCP rereads the exact provider message and verifies channel, configured human user, manual-human authorship, thread binding, replay state, and canonical TaskLedger state.

Approval-bound threads additionally revalidate the pending approval owner and immutable payload fingerprint. Only exact APPROVE, DENY, CHANGE, or CHANGES: <details> grammar may enter the approval service. Natural language, reactions, mentions, bot/app messages, edited messages, wrong users, wrong channels, and unbound threads cannot create authority.

## Data handling

Free-text change details and conversational replies are untrusted input. The interaction ledger records classification and provider locators. Consequential authorization is never inferred from model interpretation.

## Failure behavior

Slack provider reread failure occurs before decision processing and therefore fails closed. If an acknowledgment post fails after a canonical approval decision, the canonical decision remains durable and a replay can safely retry the feedback path without re-deciding the approval.

## Existing controls retained

- human principal michael for L4 approval;
- L5 CEO-only boundary;
- TaskLedger canonicality;
- provider-authenticated reread;
- immutable approval fingerprint;
- replay/idempotency controls;
- bot versus human attribution;
- completion distinct from verification;
- audit-chain verification.

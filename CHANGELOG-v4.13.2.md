# CHANGELOG v4.13.2

## Fixed

- Validated canonical TaskLedger task existence before a governed Slack interaction can call `chat.postMessage`.
- Added regression proof that an invalid task ID performs zero Slack provider calls.

## Security

- Restored fail-closed side-effect ordering for the non-approval Slack peer-interaction path.
- No authority expansion and no approval behavior change.

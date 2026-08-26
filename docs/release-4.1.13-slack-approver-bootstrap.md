# Release 4.1.13: Slack Approver Bootstrap

- Deployment release: `4.1.13`
- Semantic tag: `v4.1.13`
- Default image label: `4.1.13-qnap`
- Canonical authority/runtime contract: `4.0.0` unchanged

## Scope

v4.1.13 is a QNAP deployment remediation for Slack human-approver identity bootstrap. It supersedes v4.1.12 for deployment because v4.1.12 required interactive entry of the approver Slack user ID and the Slack UI surfaced a `D...` Channel ID that is not valid as a user principal.

## Changes

- Verified Michael/MK Slack user principal is `U01KG3CNYHK`.
- Deployment ships that non-secret identity as the governed default.
- Approver-user-ID entry is no longer interactive.
- `D...` conversation/DM channel identifiers receive a specific fail-closed diagnostic if supplied as an override or persisted value.
- Existing valid approver identity files are validated before preservation.
- Forced HITL reconfiguration restages the governed approver identity without prompting for it.
- Slack verifier and Socket Mode tokens remain external protected secrets.
- QNAP release-root bootstrap behavior from v4.1.12 is retained unchanged.

## Unchanged authority

Exactly 10 agents, exactly 27 governed CoS tools, human-only operations, shared Devil's Advocate Skill, canonical SQLite TaskLedger, Secure MCP Tunnel ingress, and completion/verification separation remain unchanged.

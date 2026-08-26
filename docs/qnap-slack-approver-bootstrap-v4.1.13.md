# QNAP Slack Approver Bootstrap v4.1.13

## Purpose

v4.1.13 removes interactive collection of the human Slack approver user ID during QNAP deployment and corrects the identifier-class confusion observed in v4.1.12.

Slack exposed `D01K4CL2F8F` in the profile pane as a **Channel ID**. That value identifies a direct-message/conversation channel and is not a user principal. The verified Slack user principal for Michael/MK is `U01KG3CNYHK`.

## Governed identity contract

- Human approval principal: Michael/MK.
- Canonical Slack user ID: `U01KG3CNYHK`.
- `U...` and `W...` identifiers are eligible user-principal forms.
- `D...` identifiers are conversation/DM channel IDs and fail closed when supplied as an approver principal.
- The user ID is non-secret configuration and is shipped as the governed default for this Mesh deployment.
- The runtime still materializes the approver ID into `/share/Docker/cos-mcp/secrets/slack-approver-user-id` with protected ownership/mode so the existing runtime file contract remains unchanged.
- An existing valid protected approver file is preserved unless forced reconfiguration is requested.
- Forced reconfiguration restages the governed default without asking the operator for the approver user ID.

## Secrets remain external

This change does not embed Slack credentials. The read-only verifier bot token and Socket Mode app-level token remain protected runtime inputs/files and are never added to the release artifact or logs.

## Deployment behavior

The operator continues to work only from:

`/share/Docker/cos-mcp/releases`

The release ZIP creates its own `v4.1.13/` folder. The deploy script self-resolves all helpers. No manual directory creation, file movement, chmod, or approver-user-ID entry is required.

If verifier or Socket Mode credentials are not already present, their secret input remains hidden and interactive by design.

## Preserved invariants

- Phase 1 authority/runtime contract: `4.0.0`.
- Exactly 10 registered agents.
- Exactly 27 governed CoS tools.
- Human-only operations remain human-only.
- Devil's Advocate remains a governed shared Skill, not an agent.
- Canonical SQLite TaskLedger remains under `/share/Docker/cos-mcp/state`.
- OpenAI Secure MCP Tunnel remains production ingress.
- `COMPLETED != VERIFIED`.

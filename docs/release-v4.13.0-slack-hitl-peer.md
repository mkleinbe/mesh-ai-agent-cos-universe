# v4.13.0 Bidirectional Slack HITL Peer Workflow

v4.13.0 is a MINOR repository release that corrects the Slack human-in-the-loop operating experience without weakening Mesh authority controls.

## Root cause addressed

The protected Slack bot path already worked, but some scheduled/operational notices bypassed it through a human-connected Slack posting path, causing system messages to appear provider-authored by MK. Separately, the native Work dispatcher reconciled approval replies but had no general conversational thread-state or acknowledgment loop. Manual-action notices could therefore look approval-like and human replies could be silently ignored.

## Release behavior

- all governed HITL requests are produced through the protected Slack bot path;
- every governed interaction has a persisted thread type and response contract;
- non-approval replies are provider-reread and acknowledged without creating authority;
- approval threads accept only explicit APPROVE, DENY, CHANGE, or CHANGES: <details>;
- ambiguous approval language receives an explicit-command reminder;
- APPROVE on a non-approval thread is acknowledged but cannot mutate authority;
- duplicate delivery is idempotent and does not duplicate user-visible feedback;
- approval completion remains separate from verification.

## Runtime boundaries

Canonical MCP authority/runtime contract: `4.0.0`, unchanged.

QNAP deployment identity: `4.4.0`, unchanged. The release workflow builds an exact-current-source 4.4.0 QNAP candidate. Production is not upgraded until that candidate is transactionally promoted and Secure MCP readback proves the merged source commit.

Registered organization: exactly 10 agents, unchanged.

## Verification

Acceptance is defined by `specs/slack-hitl-peer-v4.13.0.feature`, unit/integration regression, 100% mesh_cos coverage, Ruff, mypy, Bandit, QNAP shell regressions, production-equivalent candidate build, MCP verification, live Slack identity readback, and live bidirectional UAT.

The existing ChatGPT Work task `Mesh Slack HITL Dispatcher` remains one persistent locator-only dispatcher. It must not be replaced by per-approval tasks or polling.

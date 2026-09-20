# v4.13.2 Slack Interaction Task Preflight

v4.13.2 is a PATCH release over v4.13.1.

## Fixed

Governed Slack `post_interaction` now validates that the referenced canonical TaskLedger task exists before any Slack provider side effect occurs.

Previously, an invalid task ID could cause `chat.postMessage` to succeed and only then fail while persisting interaction state. That could leave an orphan bot-authored operational message with no canonical task binding.

## Security and authority

The change strengthens fail-closed ordering:

1. validate interaction type and summary;
2. validate canonical task existence;
3. derive the bounded interaction contract;
4. post through the protected Slack bot identity;
5. verify provider-returned message identity;
6. persist interaction state and thread binding.

No approval grammar, human authority, TaskLedger ownership, Slack provider identity, dispatcher, or MCP authority boundary is broadened.

## Verification

Regression proof requires a nonexistent task to raise `KeyError` with zero Slack transport calls.

The patch must also pass the full repository suite, 100% `mesh_cos` coverage, Ruff, mypy, Bandit, contract and documentation drift checks, QNAP shell regressions, exact-current-source QNAP 4.4.0 candidate build, production-equivalent container verification, and MCP discovery/sequential requests.

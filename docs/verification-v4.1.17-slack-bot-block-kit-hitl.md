# Verification: v4.1.17 Slack Bot + Block Kit HITL

## Verification objective

Prove that v4.1.17 replaces human-looking connector posts and the invalid slash-command approval path with a dedicated Slack bot, Block Kit decisions, provider-authenticated human replies, and a governed multi-turn change workflow without widening authority.

## BDD acceptance

The release must satisfy QNAP-116 through QNAP-128 in `specs/qnap-slack-thread-hitl-v4.1.17.feature`.

Required behavior includes:

- bot-authored `chat.postMessage` approval root;
- returned Slack message identity bound to the canonical PENDING Approval ID/fingerprint;
- case-insensitive typed `APPROVE`, `DENY`, and `CHANGE` fallback in the bound thread;
- Block Kit Approve/Deny/Change buttons;
- app/bot impersonation rejection;
- exact user/channel/app/thread/fingerprint checks;
- replay idempotency and conflict rejection;
- `CHANGE` -> `AWAITING_CHANGE_INPUT` -> prompt -> freeform governed change request;
- original approval superseded and task returned to `IN_PROGRESS`;
- fresh approval and fresh fingerprint required after revision;
- xapp + xoxb + protected human identity preflight;
- no slash-command dependency;
- no incoming-webhook URL in package/runtime state.

## Automated gates

Exact-head CI must pass:

- `npm ci`, TypeScript build/tests/smoke/security;
- contract, runtime-doc drift, and ChatGPT package checks;
- Ruff, mypy, Bandit, compileall;
- pytest with 100% coverage;
- Slack bot unit tests;
- Slack Socket Mode Events API + Block Kit tests;
- v4.1.17 QNAP acceptance evaluations;
- QNAP POSIX shell regression suite;
- restarting-container backup regression;
- transactional promotion regression;
- exact v4.1.17 release bundle build and archive-layout checks;
- Compose topology and OCI version/revision checks;
- production container build;
- modern MCP discovery and sequential request checks.

## Release candidate evidence

Before merge, both the exact PR head CI workflow and the v4.1.17 release-candidate workflow must succeed. After merge, main CI and the v4.1.17 release workflow must succeed before the immutable tag/release is considered publishable.

## Live QNAP acceptance

Automated CI does not establish live production acceptance. After deploying the immutable v4.1.17 bundle on QNAP, verify:

1. pre-deploy backup succeeds, including the v4.1.16 quiesced-helper path if the old runtime is restarting;
2. candidate promotion and post-deploy verification complete transactionally;
3. `mesh-cos-mcp` and `mesh-cos-tunnel` are healthy;
4. `/readyz` reports runtime 4.0.0, deployment release 4.1.17, CoS identity, Secure MCP Tunnel transport, and Slack HITL ready;
5. Slack approval root is visibly authored by **ChatGPT Enterprise AI Agent**, not MK;
6. approval root renders rich content plus Approve/Deny/Change buttons;
7. Approve button changes only the exact bound PENDING approval to APPROVED;
8. Deny button changes only the exact bound PENDING approval to REJECTED;
9. Change button leaves approval PENDING and bot asks `What would you like to change?` in-thread;
10. a freeform human change request is captured, supersedes the old approval, returns the task to `IN_PROGRESS`, and triggers no external action;
11. CoS revises the request and returns a fresh Block Kit approval with a different immutable payload fingerprint;
12. ordinary bot/app/connector messages, wrong users, wrong channels, unbound threads, stale buttons, and replay conflicts remain non-authoritative;
13. TaskLedger/audit readback reconciles every binding, decision, change request, and revised approval.

## Production acceptance blockers

Do not declare live production acceptance until:

- exposed Slack webhook URLs and deprecated verification token are rotated;
- the v4.1.17 Slack manifest is applied;
- the app is reinstalled/re-authorized for the added private-channel scope;
- Socket Mode is enabled;
- the bot/app is a member of private `mesh-agent-ops`;
- the protected xapp and xoxb credential files on QNAP are current.

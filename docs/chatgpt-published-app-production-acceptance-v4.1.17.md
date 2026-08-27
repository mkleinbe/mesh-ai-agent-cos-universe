# ChatGPT Published App Production Acceptance: v4.1.17

## Scope

This acceptance proves the published Mesh CoS MCP app, QNAP runtime, Secure MCP Tunnel, and dedicated Slack **ChatGPT Enterprise AI Agent** app operate as one governed production path.

## Expected identity

- MCP runtime version: `4.0.0`
- deployment release: `4.1.17`
- agent: `cos`
- transport: `SECURE_MCP_TUNNEL`
- CoS agent-facing tool count: `27`
- registered governed agents: `10`
- Slack approval execution mode: `SLACK_BOT_API`
- Slack approval presentation: `BLOCK_KIT_RICH_TEXT_V1`
- Slack human authority ingress: provider-authenticated Socket Mode Events API / Block Kit interactions

## Pre-acceptance Slack configuration

1. Rotate any incoming webhook URL or deprecated verification token that has been exposed outside the protected credential boundary.
2. Apply `deployment/qnap/slack-app-manifest.v4.1.17.json`.
3. Reinstall/re-authorize the app for `groups:history`.
4. Confirm `message.groups` event subscription.
5. Confirm Socket Mode and interactivity are enabled.
6. Confirm the bot display name is `ChatGPT Enterprise AI Agent`.
7. Confirm the bot/app is a member of private `mesh-agent-ops`.
8. Confirm QNAP protected files contain current `xapp-` and `xoxb-` credentials and the governed human user ID.

## Synthetic no-op approval test

Create a PENDING approval whose proposed action is explicitly synthetic and has no external side effect. Post it through the CoS `slack-adapter` using operation `post_approval`.

Pass conditions:

- Slack message is authored by `ChatGPT Enterprise AI Agent`, never MK and never the connected ChatGPT Slack plugin identity.
- Message contains concise approval context plus Approve, Deny, Change buttons.
- TaskLedger stores the returned Slack channel/root `ts` as the approval thread binding.
- No approval decision is recorded merely because the bot posted the message.

### Approve

Click **Approve** as MK.

Pass conditions:
- provider-authenticated configured human/user/channel/app/thread checks pass;
- exact bound PENDING approval/fingerprint is used server-side;
- canonical approval becomes APPROVED;
- task advances to `READY_FOR_ACTION`;
- replay of the same provider envelope is idempotent;
- a distinct conflicting decision cannot re-decide it.

### Deny

For a fresh synthetic approval, click **Deny**.

Pass conditions:
- canonical approval becomes REJECTED;
- task returns/remains `IN_PROGRESS`;
- no consequential action occurs.

### Change

For a fresh synthetic approval, click **Change**.

Pass conditions:
- approval remains PENDING initially;
- bot replies in the same thread: `What would you like to change?`;
- state is `AWAITING_CHANGE_INPUT`;
- supply a realistic freeform instruction, such as revising message copy or redirecting the proposed communication channel;
- the instruction is captured as `PENDING_AGENT_REVISION` requirements input;
- old approval is superseded/rejected;
- task is `IN_PROGRESS`;
- no external action occurs from the change text itself;
- CoS intelligently applies the instruction to the task context;
- a new PENDING approval is created with a different immutable payload fingerprint;
- the dedicated Slack bot posts a fresh Block Kit approval;
- the revised action cannot execute until that fresh approval is approved.

## Keyboard fallback

In a bound approval thread, case-insensitive manual human replies `APPROVE`, `DENY`, and `CHANGE` must produce the same governed state transitions as their buttons. `/mesh-approval` is not part of the production contract.

## Negative tests

Verify each leaves a PENDING approval non-authorized:

- ChatGPT-connected Slack integration or another app writes `APPROVE`;
- a bot-authored message contains `APPROVE`;
- another Slack user replies;
- governed user replies in another channel;
- reply is outside the bound thread;
- Block Kit action contains wrong/stale approval value;
- approval fingerprint has changed since binding;
- approval is no longer PENDING;
- Slack provider path is unavailable.

## Readiness and audit

After each test, reconcile:

- canonical approval record;
- `approval_slack_thread_binding`;
- `approval_slack_socket_decision` when applicable;
- `approval_change_session` / `approval_change_request` when applicable;
- task status;
- governance audit chain.

No test is complete based only on the visual Slack UI.

# v4.1.17 QNAP Slack Bot + Block Kit HITL

## Release intent

v4.1.17 corrects the production Slack HITL architecture exposed during v4.1.16 acceptance. Governed approval collaboration no longer uses the connected ChatGPT Slack integration and no longer depends on `/mesh-approval`. The QNAP CoS runtime uses the installed **ChatGPT Enterprise AI Agent** Slack app directly.

## What changed

- Outbound governed Slack approval messages use Slack Web API `chat.postMessage` with the protected bot OAuth token.
- The Slack request contains no `username`, `icon_emoji`, or `icon_url` override, so Slack renders the installed bot identity rather than a human identity.
- Approval messages use Block Kit with `rich_text` plus **Approve**, **Deny**, and **Change** buttons.
- Slack-returned `channel` and root message `ts` are stored as the canonical approval-thread binding.
- Socket Mode handles both Events API message envelopes and Block Kit `block_actions` envelopes.
- Case-insensitive typed replies `APPROVE`, `DENY`, and `CHANGE` remain a keyboard fallback inside the bound approval thread.
- `CHANGE` begins a two-step change workflow. The approval remains PENDING while the bot asks, `What would you like to change?`
- The next provider-authenticated human reply is captured as governed requirements input. It does not authorize an external action.
- Capturing a change request supersedes the old approval and returns the task to `IN_PROGRESS`. CoS must revise the work, create a new immutable payload fingerprint, request a new approval, and post a fresh Block Kit approval.
- QNAP runtime configuration now requires the protected Slack bot OAuth token (`xoxb-`) in addition to the existing Socket Mode app-level token (`xapp-`) and protected human approver ID.
- The current app manifest adds `groups:history` and `message.groups` for provider-delivered replies in the private `mesh-agent-ops` channel, enables Socket Mode and interactivity, and normalizes the bot display name to `ChatGPT Enterprise AI Agent`.
- Incoming webhook URLs are not part of the canonical execution or authority architecture and are never packaged or persisted.

## Preserved invariants

- TaskLedger remains the canonical approval and audit store.
- Only the configured Slack human principal can authorize or request changes.
- App-authored, bot-authored, connector-authored, wrong-user, wrong-channel, unbound-thread, stale-button, replay-conflict, and malformed interactions fail closed.
- The immutable payload fingerprint is revalidated before any final approval or denial.
- A freeform change instruction is treated as untrusted requirements input, never as direct execution authority.
- The CoS 10-agent / 27-tool contract is unchanged.
- Secure MCP Tunnel topology, QNAP transactional promotion, backup/rollback behavior, and v4.1.16 restarting-runtime backup remediation are preserved.

## Slack operator prerequisite

Before live acceptance, apply `deployment/qnap/slack-app-manifest.v4.1.17.json`, reinstall/re-authorize the Slack app for the added private-channel history scope, enable Socket Mode, and ensure the app is a member of the private `mesh-agent-ops` channel.

Any Slack webhook URL or deprecated verification token that has been exposed outside the Slack credential boundary must be rotated before production acceptance.

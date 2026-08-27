# Security Review: v4.1.17 Slack Bot + Block Kit HITL

## Applicability

**FULL_REVIEW**

v4.1.17 changes both a consequential human-authority ingress and a credentialed external write path. The release therefore requires a full review rather than an incremental documentation-only review.

## Security objectives

1. Prevent ChatGPT, a connector, an app, or another Slack identity from impersonating the governed human approver.
2. Bind every approval interaction to one canonical PENDING approval, one Slack thread, one governed channel, one human principal, and one immutable payload fingerprint.
3. Keep freeform change instructions non-authoritative until revised work is explicitly re-approved.
4. Keep Slack credentials out of source, environment snapshots, logs, backups, release metadata, and TaskLedger.
5. Preserve fail-closed behavior during Slack provider degradation, replay, malformed payloads, or stale interactions.

## Credential model

- Human Slack user ID: protected file, provider routing identity only.
- Socket Mode app-level token: protected `xapp-` file, read-only mount.
- Slack bot OAuth token: protected `xoxb-` file, read-only mount.
- OpenAI Secure MCP Tunnel key: separate protected file, unchanged.
- Incoming webhook URLs: not used by the canonical v4.1.17 path and prohibited from source/configuration/persistence.
- Deprecated Slack verification token: not required and not part of the runtime.

All credential files remain outside the release bundle and are excluded from governed backup payloads.

## Outbound identity review

The canonical outbound path is Slack Web API `chat.postMessage` using the installed app's bot token. The runtime does not send `username`, `icon_emoji`, or `icon_url`, preventing intentional presentation as the human approver. The connected ChatGPT Slack integration is not the governed approval execution path.

## Human authority review

Authority is accepted only from Slack Socket Mode provider envelopes after server-side validation of:

- envelope type (`events_api` or `interactive`);
- configured Slack app identity when present;
- exact governed channel;
- exact configured human Slack user ID;
- existing canonical Slack thread binding;
- PENDING canonical approval owned by `michael`;
- unchanged immutable payload fingerprint;
- exact allowed decision grammar or exact known Block Kit action ID;
- replay/single-use constraints.

App/bot-authored message events are explicitly rejected even if a visible Slack message could otherwise resemble the governed human.

## Block Kit review

Buttons contain the bound Approval ID as an opaque routing value, but the server never trusts that value alone. The runtime resolves the canonical thread binding and requires the button value to equal the already-bound approval. Unknown action IDs, cross-thread values, wrong channels, wrong users, and stale approvals fail closed.

## Change workflow review

`CHANGE` does not approve, deny, or execute the requested action. It creates `AWAITING_CHANGE_INPUT` state and prompts for freeform instructions. The next provider-authenticated human reply is persisted as an `approval_change_request` with `PENDING_AGENT_REVISION` status. The original approval is superseded/rejected and the task returns to `IN_PROGRESS`.

The freeform text is treated as untrusted human requirements input. CoS must revise the requested artifact/action/target/channel, create a new payload fingerprint, request a new canonical approval, and post a fresh Slack approval before any consequential action.

## Provider and replay behavior

- Socket Mode connection failure does not terminate MCP HTTP service.
- Slack HITL readiness fails closed while the provider path is inactive.
- Structured authorization rejection is acknowledged without exposing internal detail.
- Bridge/process transport failure is not acknowledged, permitting provider redelivery.
- A repeated provider event is idempotent.
- A distinct second provider interaction cannot re-decide an approval.

## Network and platform posture

No QNAP network widening is introduced. MCP retains qnet LAN plus internal private bridge; the Secure MCP Tunnel retains private ingress plus dedicated egress bridge. No Docker socket is mounted. Runtime remains non-root, read-only, capability-dropped, and `no-new-privileges`.

## Findings

- **CRITICAL:** none open.
- **HIGH:** none open in code/release configuration.
- **OPERATOR BLOCKER:** any Slack incoming webhook URL or deprecated verification token exposed outside the protected credential boundary must be rotated before live production acceptance.
- **OPERATOR BLOCKER:** the Slack app must be re-authorized after adding `groups:history`, Socket Mode must be enabled, and the bot must be a member of the private `mesh-agent-ops` channel.

## Review disposition

**PASS FOR RELEASE CANDIDATE, CONDITIONED ON EXACT-HEAD CI/SECURITY VERIFICATION AND LIVE CREDENTIAL ROTATION/SLACK CONFIGURATION BEFORE PRODUCTION ACCEPTANCE.**

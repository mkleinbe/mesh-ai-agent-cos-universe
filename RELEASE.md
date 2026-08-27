# v4.2.0 Native Slack Event-Triggered HITL

`v4.2.0` replaces the QNAP-hosted Slack Socket Mode approval ingress used by v4.1.17 and v4.1.18 with ChatGPT-native Slack new-message task triggers.

The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly 10 registered agents and exactly 27 governed CoS tools. Human-only operations remain human-only. OpenAI Secure MCP Tunnel remains the production remote MCP transport. TaskLedger remains canonical approval state. **Message Operations** remains the tenth registered agent. **Mesh Devil's Advocate** remains a governed shared Skill and is not an eleventh agent.

## Architecture

```text
MK replies in #mesh-agent-ops
        |
        v
ChatGPT native Slack new-message trigger
        |
        v
One Mesh Slack HITL Dispatcher task
        |
        v
Mesh CoS MCP
        |
        v
Server-side Slack provider reconciliation
        |
        v
Canonical TaskLedger approval state
```

The ChatGPT trigger is a wake-up and locator only. It cannot supply approval text, asserted human identity, approval status, actor, principal, or an approval boolean to the governed Slack adapter. The QNAP runtime independently retrieves the exact Slack reply and revalidates provider user, channel, thread, message timestamp, manual-human authorship, edit state, canonical approval status, approval owner, immutable payload fingerprint, and replay state before authority changes.

## Behavioral changes

- Approval notices are reply-driven with `APPROVE`, `DENY`, and `CHANGE`.
- Non-functional Block Kit approval buttons are removed.
- QNAP no longer starts a Slack WebSocket listener.
- The Slack `xapp-` Socket Mode credential is removed from runtime, provisioning, compose mounts, and readiness.
- The protected `xoxb-` bot token remains required for bot-authored notices and server-side `conversations.replies` reconciliation.
- Edited, deleted/unavailable, bot-authored, wrong-user, wrong-thread, root-message, ambiguous, stale-fingerprint, and conflicting replay cases fail closed.
- Duplicate delivery of the same Slack reply is idempotent.
- CHANGE remains a two-step governed revision loop and requires a new payload fingerprint before consequential action.

## Security boundary

Security applicability is **FULL REVIEW** because v4.2.0 changes Slack event ingress, approval identity evidence, consequential authority routing, MCP/agent boundaries, secrets, replay behavior, and runtime readiness.

See:

- `docs/security-review-v4.2.0.md`
- `specs/native-slack-event-hitl-v4.2.0.feature`
- `docs/chatgpt-native-slack-dispatcher-v4.2.0.md`
- `docs/chatgpt-published-app-production-acceptance-v4.2.0.md`
- `docs/verification-v4.2.0-native-slack-event-hitl.md`

## Release assets

- `mesh-cos-mcp-qnap-v4.2.0.zip`
- `mesh-cos-mcp-qnap-v4.2.0.zip.sha256`

## Version identity

- Repository/QNAP deployment release: `4.2.0`
- Semantic tag: `v4.2.0`
- Container image label: `4.2.0-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Workforce: exactly 10 agents
- CoS catalog: exactly 27 governed tools
- Production transport: OpenAI Secure MCP Tunnel

Successful live readiness after deployment must report the equivalent of:

```text
mcp_version: 4.0.0
deployment_release: 4.2.0
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
slack_hitl_ready: true
```

## QNAP deployment

Place the immutable release ZIP and checksum directly in `/share/Docker/cos-mcp/releases`, verify the checksum, and deploy the complete versioned release unit:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.2.0.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.2.0.zip
sudo sh ./v4.2.0/mesh-cos-mcp-deploy.sh
```

The existing valid Slack bot OAuth credential and protected approver identity should be preserved. v4.2.0 does not require a Slack Socket Mode app token.

Only if the dedicated bot credential is genuinely missing or invalid:

```sh
sudo sh ./v4.2.0/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.2.0/mesh-cos-mcp-deploy.sh
```

## Production acceptance

Repository and release verification do not prove the ChatGPT-native Slack task is configured or firing in the production workspace. After QNAP deployment, configure exactly one Mesh Slack HITL Dispatcher task using `docs/chatgpt-native-slack-dispatcher-v4.2.0.md`, then execute the synthetic acceptance matrix in `docs/chatgpt-published-app-production-acceptance-v4.2.0.md` before any consequential approval uses this path.

**COMPLETED != VERIFIED.** v4.2.0 is not production-accepted until the native event-trigger path, provider reconciliation, canonical state change, negative cases, and audit chain are proven live.
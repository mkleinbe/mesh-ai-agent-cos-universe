# v4.1.15 QNAP Slack Plugin HITL Simplification

`v4.1.15` supersedes v4.1.14 for QNAP deployment.

The release removes the unnecessary Slack verifier-bot layer. The connected Slack integration is now the collaboration and approval-notification surface. The custom Slack app remains only as a narrow provider-authenticated `/mesh-approval` Socket Mode ingress for consequential human decisions.

The same production run that exposed the architectural overreach also exposed a QNAP Docker Engine 27 network defect: `mesh-cos-mcp` could start but failed outbound Slack HTTPS connections with `ETIMEDOUT`/`EHOSTUNREACH`. v4.1.15 fixes the dual-network route ambiguity without depending on newer Compose gateway-priority features.

The failed v4.1.14 activation also showed that a failed candidate could temporarily strand the active container in a failed state. v4.1.15 adds pre-promotion automatic restoration of the previously active Compose stack.

The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly 10 agents. Human-only operations remain human-only. Message Operations remains agent 10; Mesh Devil's Advocate remains a shared Skill rather than agent 11.

## Core changes

- CoS `slack-adapter` becomes a `CHATGPT_CONNECTOR_HANDOFF` with `COLLABORATION_ONLY` authority.
- Removes Slack notice-thread verification, OpenAI-bot author allowlists, `approval_slack_binding`, and active `xoxb-` verifier dependency.
- QNAP mounts only the governed approver identity and `xapp-` Socket Mode app-level token for Slack HITL.
- `/mesh-approval` provider envelopes remain the only Slack interactions eligible to become canonical human decisions.
- Approval ingress validates exact user, channel, command, PENDING state, owner, replay state, and canonical 64-hex `payload_fingerprint`.
- Slack provider/network outage no longer terminates the MCP HTTP process. `/healthz` stays available, `/readyz` fails closed, and reconnect uses bounded exponential backoff.
- `mesh-cos-private` becomes `internal: true`.
- MCP keeps qnet `192.168.7.60` as its only external-capable network.
- Tunnel keeps the private bridge for MCP ingress and gains a dedicated Docker egress bridge for the OpenAI control plane.
- Failed candidate activation or pre-promotion health verification restores the previously active stack and does not promote candidate release metadata.

## Security boundary

Security applicability is **FULL_REVIEW**. See `docs/security-review-v4.1.15.md` and `SECURITY.md`.

The connected Slack integration can collaborate but cannot carry human approval authority. The custom Slack app has one purpose: authenticated slash-command ingress over Socket Mode. No direct agent call can record human approval.

## BDD and TDD evidence

Ready scenarios QNAP-104 through QNAP-110 in `specs/qnap-slack-plugin-hitl-v4.1.15.feature` cover:

- collaboration-only Slack integration;
- authenticated human decision ingress;
- ordinary/wrong/replayed Slack interactions failing closed;
- non-fatal Slack network/provider degradation;
- verifier credential removal;
- Docker Engine 27 deterministic egress;
- failed-candidate rollback before promotion.

Implementation is driven through RED, GREEN, refactor, affected regression, full CI, security review, and independent release verification.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.15.zip`
- `mesh-cos-mcp-qnap-v4.1.15.zip.sha256`

## Version identity

- Repository/QNAP deployment release: `4.1.15`
- Semantic tag: `v4.1.15`
- Container image label: `4.1.15-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Workforce: exactly 10 agents
- Production transport: OpenAI Secure MCP Tunnel
- Human Slack approval ingress: authenticated `/mesh-approval` Socket Mode envelope

Successful live readiness after deployment must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.15
agent_id: cos
slack_hitl_ready: true
```

## QNAP deployment

Normal upgrade with the existing Socket Mode credential:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.15/mesh-cos-mcp-deploy.sh
```

If the `xapp-` Socket Mode credential is missing, provision it explicitly and rerun deployment:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.15/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.1.15/mesh-cos-mcp-deploy.sh
```

No Slack `xoxb-` verifier credential is required by v4.1.15. A legacy verifier file may remain on the host for rollback compatibility with older releases, but it is unused and unmounted.

## Verification and live acceptance

The exact candidate must pass the verification gates recorded in `docs/verification-v4.1.15-slack-plugin-hitl.md` before release integration.

After QNAP deployment, execute `docs/chatgpt-published-app-production-acceptance-v4.1.15.md`. Repository/release verification does not substitute for live QNAP networking, hosted MCP, and real provider-authenticated Slack acceptance.

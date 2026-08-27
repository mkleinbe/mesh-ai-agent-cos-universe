# v4.1.16 QNAP Restarting-Runtime Backup Hotfix

`v4.1.16` supersedes v4.1.15 for QNAP deployment.

A live v4.1.14 -> v4.1.15 upgrade exposed a QNAP Docker 27 state edge case: Docker reported `.State.Running=true` while `mesh-cos-mcp` was actually in `.State.Status=restarting`. The v4.1.15 pre-deploy backup gate therefore attempted `docker exec` against a restarting container and blocked the deployment before the v4.1.15 network remediation could be installed.

v4.1.16 fixes that failure without weakening the canonical TaskLedger backup gate.

## Core changes

- Stable `status=running` plus `.State.Restarting=false` retains the existing online SQLite backup path.
- Restarting or otherwise non-running existing runtimes use a quiesced backup path rather than `docker exec`.
- A restarting runtime is stopped before canonical SQLite state is read.
- The exact active Mesh image is used as a one-shot backup helper with `--network none`, non-root UID/GID, read-only root filesystem, all capabilities dropped, and `no-new-privileges`.
- The one-shot helper mounts canonical state only, does not receive Slack/tunnel secrets, uses SQLite backup semantics, and requires `PRAGMA integrity_check` success.
- Failed helper/export attempts remove temporary and partial backup state and fail closed.
- If the old runtime had running intent before quiescence, that intent is restored after both successful and failed backup attempts.
- Deployment now performs pre-deploy backup whenever `mesh-cos-mcp` exists, rather than relying on `.State.Running=true` as the existence/readiness test.

## v4.1.15 retained

v4.1.16 includes the full v4.1.15 Slack HITL simplification and QNAP network remediation:

- connected Slack remains collaboration-only with `CHATGPT_CONNECTOR_HANDOFF` / `COLLABORATION_ONLY`;
- provider-authenticated `/mesh-approval` Socket Mode remains the consequential human decision boundary;
- no active `xoxb-` verifier dependency exists;
- Slack provider/network failure is non-fatal to the MCP HTTP process while `/readyz` fails closed;
- the MCP keeps qnet `192.168.7.60` as its only external-capable network;
- the tunnel uses the internal MCP bridge plus dedicated Docker egress;
- failed candidate activation restores the previous stack;
- active configuration promotion remains snapshot-backed and transactional.

The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly 10 registered agents and exactly 27 governed CoS tools. Human-only operations remain human-only. Message Operations remains agent 10; Mesh Devil's Advocate remains a shared Skill rather than agent 11. **COMPLETED != VERIFIED.**

## BDD and TDD evidence

Ready scenarios QNAP-112 through QNAP-115 in `specs/qnap-restarting-backup-v4.1.16.feature` cover stable online backup, restarting-runtime quiesced backup, fail-closed restoration, and deployment backup selection for any existing runtime.

The regression suite includes a Docker mock that deliberately reports `running=true`, `status=restarting`, and `restarting=true`; `docker exec` is configured to fail if the implementation incorrectly chooses it.

## Security boundary

Security applicability is **FULL_REVIEW**. See `docs/security-review-v4.1.16.md` and `SECURITY.md`.

The fallback backup helper cannot reach the network, does not mount protected credentials, runs non-root from the exact active Mesh image, and uses the existing SQLite backup/integrity helper. The canonical TaskLedger remains the source of truth and is never replaced or raw-copied as a live database workaround.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.16.zip`
- `mesh-cos-mcp-qnap-v4.1.16.zip.sha256`

## Version identity

- Repository/QNAP deployment release: `4.1.16`
- Semantic tag: `v4.1.16`
- Container image label: `4.1.16-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Workforce: exactly 10 agents
- Production transport: OpenAI Secure MCP Tunnel

Successful live readiness after deployment must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.16
agent_id: cos
slack_hitl_ready: true
```

## QNAP deployment

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.1.16.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.16.zip
sudo sh ./v4.1.16/mesh-cos-mcp-deploy.sh
```

If the protected `xapp-` Socket Mode credential is missing, provision it explicitly and rerun deployment:

```sh
sudo sh ./v4.1.16/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.1.16/mesh-cos-mcp-deploy.sh
```

## Verification and live acceptance

The exact candidate must pass `docs/verification-v4.1.16-qnap-restarting-backup.md` before integration. The merge SHA must pass the v4.1.16 main-branch release workflow before the semantic tag and GitHub release are complete.

After QNAP deployment, execute `docs/chatgpt-published-app-production-acceptance-v4.1.16.md`. Repository/release verification does not substitute for live QNAP deployment, Secure MCP Tunnel, hosted MCP, and provider-authenticated Slack acceptance.
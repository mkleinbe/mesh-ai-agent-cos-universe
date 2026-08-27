# v4.1.18 QNAP Slack Bot Secret Permission Hotfix

`v4.1.18` supersedes v4.1.17 for QNAP deployment after live v4.1.17 acceptance exposed a protected-file ownership defect in the new dedicated Slack bot credential path.

The v4.1.17 provisioner correctly accepted and stored a valid `xoxb-` Slack bot OAuth token with mode `0400`. However, the shared QNAP secret-permission helper did not include `slack-bot-token` in its ownership normalization loop. Provisioning runs as root while the Mesh runtime runs as UID/GID `65532:65532`, so the candidate container mounted the file but canonical runtime preflight could not read it.

Transactional promotion behaved correctly and restored the previously active stack after verification failed.

## v4.1.18 fix

- Add `slack-bot-token` to the constrained QNAP secret ownership/mode normalization helper.
- Normalize the protected file to runtime owner `65532:65532` while preserving mode `0400`.
- Preserve the existing valid `xoxb-` token across deployment. Operators do not need to re-enter it solely to repair v4.1.17 ownership.
- Preserve fail-closed runtime validation for missing, unreadable, empty, or wrong-type bot credentials.
- Preserve no-network, read-only, capability-bounded permission-helper execution.
- Add ready BDD scenarios QNAP-129 and QNAP-130 plus a shell regression proving the bot token is included in the secret permission helper.
- Add targeted security review `SEC-4.1.18-001` and exact-head v4.1.18 release verification.

No Slack credential value is logged, packaged, or copied into runtime environment variables. No approval, agent, TaskLedger, or MCP authority is widened.

## Inherited controls

v4.1.18 preserves the complete v4.1.17 Slack Bot + Block Kit HITL behavior contract: dedicated **ChatGPT Enterprise AI Agent** bot authorship, provider-authenticated Socket Mode replies and Block Kit actions, case-insensitive `approve`, `deny`/`reject`, and `change` thread fallbacks, immutable payload fingerprint validation, replay protection, fail-closed provider degradation, and TaskLedger as canonical approval state.

It also preserves the **v4.1.16 QNAP Restarting-Runtime Backup Hotfix**, including quiesced backup handling for restarting containers, transactional recovery, and canonical SQLite integrity checks.

The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly 10 registered agents and exactly 27 governed CoS tools. Human-only operations remain human-only. Message Operations remains agent 10; Mesh Devil's Advocate remains a shared Skill rather than agent 11. **COMPLETED != VERIFIED.**

## Security boundary

Security applicability for v4.1.18 is **TARGETED** because the change touches an OAuth credential file and runtime ownership. See `docs/security-review-v4.1.18.md`.

The intended least-privilege state is owner `65532:65532`, mode `0400`. The constrained helper receives no network, runs with a read-only root filesystem, and uses only the already-approved CHOWN/FOWNER/DAC_OVERRIDE capabilities required to normalize bind-mounted protected files.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.18.zip`
- `mesh-cos-mcp-qnap-v4.1.18.zip.sha256`

## Version identity

- Repository/QNAP deployment release: `4.1.18`
- Semantic tag: `v4.1.18`
- Container image label: `4.1.18-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Workforce: exactly 10 agents
- CoS catalog: exactly 27 governed tools
- Production transport: OpenAI Secure MCP Tunnel

Successful live readiness after deployment must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.18
agent_id: cos
slack_hitl_ready: true
```

## QNAP deployment

Place the release ZIP and checksum directly in `/share/Docker/cos-mcp/releases`, then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.1.18.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.18.zip
sudo sh ./v4.1.18/mesh-cos-mcp-deploy.sh
```

If a valid bot OAuth token was provisioned during the failed v4.1.17 attempt, do not re-enter it. v4.1.18 is designed to repair its ownership during normal preparation/configuration.

Only if deployment reports a genuinely missing or invalid Slack credential:

```sh
sudo sh ./v4.1.18/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.1.18/mesh-cos-mcp-deploy.sh
```

## Verification and live acceptance

The exact candidate must pass `docs/verification-v4.1.18-qnap-slack-bot-secret-permissions.md` before integration. The merge SHA must pass the v4.1.18 main-branch release workflow before the semantic tag and GitHub release are complete.

After QNAP deployment, execute `deployment/qnap/CHATGPT-ACCEPTANCE.md` and `docs/chatgpt-published-app-production-acceptance-v4.1.18.md`. Repository/release verification does not substitute for live QNAP deployment, Secure MCP Tunnel, hosted MCP, and provider-authenticated Slack acceptance.

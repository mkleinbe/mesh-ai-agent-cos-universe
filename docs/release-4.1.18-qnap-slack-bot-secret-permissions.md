# v4.1.18 QNAP Slack Bot Secret Permission Hotfix

## Purpose

v4.1.18 supersedes v4.1.17 for QNAP deployment after live production deployment exposed a protected-file ownership defect in the QNAP permission helper.

The v4.1.17 Slack bot OAuth token provisioner correctly accepted and stored an `xoxb-` token with mode `0400`, but the shared secret-permission helper did not include `slack-bot-token` in its ownership normalization loop. Because provisioning runs as root while the Mesh runtime runs as UID/GID `65532:65532`, the candidate container could mount the file but canonical runtime preflight could not read it.

## Fix

- Add `slack-bot-token` to the constrained QNAP secret ownership/mode normalization helper.
- Preserve owner `65532:65532` and mode `0400` for the bot token.
- Preserve fail-closed runtime validation for the protected `xoxb-` credential.
- Preserve the protected `xapp-` Socket Mode token and human approver identity behavior.
- Add a QNAP shell regression that fails if `slack-bot-token` is omitted from the secret permission helper.
- Add BDD scenarios QNAP-129 and QNAP-130 covering new and existing bot-token repair paths.

No Slack credential value is logged or packaged. No authorization, approval, or agent authority is broadened.

## Deployment

From `/share/Docker/cos-mcp/releases`:

```sh
sha256sum -c mesh-cos-mcp-qnap-v4.1.18.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.18.zip
sudo sh ./v4.1.18/mesh-cos-mcp-deploy.sh
```

The already-provisioned valid `slack-bot-token` is expected to be preserved. v4.1.18 should normalize its ownership automatically, so the token does not need to be entered again.

## Preserved invariants

- Canonical MCP runtime/product version remains `4.0.0`.
- Exactly 10 agents and the 27-tool CoS catalog remain unchanged.
- TaskLedger remains canonical.
- Human-only approval authority remains human-only.
- Dedicated Slack app identity remains `ChatGPT Enterprise AI Agent`.
- Secure MCP Tunnel topology, transactional promotion, backup, rollback, and v4.1.17 Slack HITL behavior are preserved.

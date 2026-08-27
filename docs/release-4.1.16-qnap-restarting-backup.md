# v4.1.16 QNAP Restarting-Runtime Backup Hotfix

## Purpose

v4.1.16 supersedes v4.1.15 for QNAP deployment after the 2026-08-27 production upgrade exposed a pre-deploy backup defect.

Docker 27 on QNAP can report `.State.Running=true` while a container is in `.State.Status=restarting`. v4.1.15 used only `.State.Running` to select the online `docker exec` SQLite backup path. The restarting v4.1.14 runtime therefore could not execute the backup helper, which blocked deployment before the v4.1.15 network remediation could be installed.

## Fix

- Stable `status=running` and `State.Restarting=false` keeps the existing online SQLite backup path.
- Restarting or non-running existing runtimes use a quiesced backup path instead of `docker exec`.
- A restarting runtime is stopped before SQLite state is read.
- The exact active Mesh image is used as a one-shot backup helper with `--network none`, non-root UID/GID, read-only root filesystem, all capabilities dropped, and `no-new-privileges`.
- The helper uses Python SQLite backup semantics plus `PRAGMA integrity_check` against the canonical TaskLedger.
- The previously running intent is restored after both successful and failed helper attempts.
- Failed helper/export attempts remove temporary state and partial backup directories and fail closed.
- Deployment now invokes pre-deploy backup whenever `mesh-cos-mcp` exists, rather than only when Docker says `.State.Running=true`.

## Preserved v4.1.15 controls

v4.1.16 includes the v4.1.15 Slack HITL simplification, deterministic Docker Engine 27 egress topology, transactional promotion recovery, minimum Slack secret surface, and fail-closed readiness behavior.

The canonical Phase 1 authority/runtime contract remains `4.0.0`, exactly 10 agents remain registered, the CoS agent catalog remains 27 tools, human-only operations remain human-only, and `COMPLETED != VERIFIED`.

## BDD

Ready scenarios QNAP-112 through QNAP-115 are defined in `specs/qnap-restarting-backup-v4.1.16.feature`.

## Upgrade

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.1.16.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.16.zip
sudo sh ./v4.1.16/mesh-cos-mcp-deploy.sh
```

The normal deployment is expected to detect the existing restarting v4.1.14/v4.1.15 runtime, quiesce it for the SQLite backup, restore its prior running intent, and continue into v4.1.16 candidate preparation.

## Acceptance boundary

Repository and release verification do not substitute for the live QNAP deployment. Production acceptance still requires the v4.1.16 candidate to deploy on the actual QNAP, both containers to become healthy, Secure MCP Tunnel verification to pass, and `slack_hitl_ready=true` with provider-authenticated `/mesh-approval` acceptance.

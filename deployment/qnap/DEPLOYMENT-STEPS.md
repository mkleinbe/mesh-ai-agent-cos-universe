# Short QNAP Deployment and Upgrade Steps

v4.1.13 removes interactive Slack approver-user-ID entry after a real v4.1.12 deployment exposed a Slack identifier-class mismatch. The canonical Phase 1 authority/runtime contract remains **4.0.0**. The v4.1.12 release-root contract and v4.1.10 scheduled-execution/Slack HITL trust model remain unchanged.

## Canonical paths

- operator release root: `/share/Docker/cos-mcp/releases`
- v4.1.13 extracted release: `/share/Docker/cos-mcp/releases/v4.1.13`
- active application root: `/share/Docker/cos-mcp`
- canonical state: `/share/Docker/cos-mcp/state`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

**The operator stays in `/share/Docker/cos-mcp/releases` for release staging and execution.** The ZIP creates `v4.1.13/` during extraction. Do not manually create the version directory, copy or move release payload files, copy helpers to `/share/Docker`, or chmod scripts before running them with `sh`.

## Slack approver identity

The governed human approver is Michael/MK. The verified Slack **user ID** is `U01KG3CNYHK`.

Slack may display a `D...` identifier in the profile pane as a **Channel ID** for a direct-message conversation. `D...` values are not user principals and must not be used for approval identity.

v4.1.13 ships `U01KG3CNYHK` as non-secret governed configuration and automatically materializes it into the protected runtime approver file. **The deployment does not ask the operator to enter the Slack approver user ID.**

Slack verifier and Socket Mode credentials remain secrets. If their protected files do not already exist, the deploy script can still request those values with hidden terminal input.

## Artifact layout

The release archive contains one top-level directory:

```text
v4.1.13/
```

Therefore, extracting `mesh-cos-mcp-qnap-v4.1.13.zip` from `/share/Docker/cos-mcp/releases` automatically creates:

```text
/share/Docker/cos-mcp/releases/v4.1.13
```

Operator scripts resolve their own directory and helper files. The deployment orchestrator also verifies that its resolved directory is directly beneath the canonical releases root and that the `v4.1.13` folder name agrees with staged release metadata before candidate preparation.

## Upgrade behavior

`mesh-cos-mcp-deploy.sh` performs, in order:

1. release-root and staged metadata validation;
2. pre-deploy online backup when the current service is running;
3. candidate preparation from staged metadata/build context;
4. protected Slack HITL configuration using the governed approver user ID and staged candidate image;
5. staged-candidate QNAP preflight;
6. candidate Compose render/deployment;
7. application/tunnel health wait;
8. atomic promotion of candidate `.env`, Compose, and release metadata to the canonical application root;
9. governed MCP verification;
10. post-deploy backup.

The canonical TaskLedger, existing Secure MCP `tunnel_id`, tunnel runtime key, Slack HITL protected files, qnet/static networking, and active runtime descriptors remain outside the versioned release folder and are preserved through upgrade.

## QNAP Docker privilege note

Docker commands require `sudo` for the current QNAP operator account. The long-running Mesh runtime remains UID/GID `65532:65532`, read-only rootfs, capabilities dropped, no-new-privileges, and no Docker socket.

## Safe v4.1.13 deployment

Place these two release assets directly in `/share/Docker/cos-mcp/releases`:

- `mesh-cos-mcp-qnap-v4.1.13.zip`
- `mesh-cos-mcp-qnap-v4.1.13.zip.sha256`

Then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.1.13.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.13.zip
sudo sh ./v4.1.13/mesh-cos-mcp-deploy.sh
```

Run the deployment command by itself. Do not queue additional pasted commands while the script is waiting for any required hidden secret input.

No `MESH_COS_DEPLOYMENT_RELEASE` environment variable needs to survive `sudo`. The release is derived from staged metadata. No Slack approver user ID needs to be entered.

## Optional explicit checks from the same operator root

These are not required before the normal deployment because the deploy orchestrator already performs backup, preflight, and verification. They are available when an explicit operator check is useful:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.13/mesh-cos-mcp-backup.sh manual
sudo sh ./v4.1.13/mesh-cos-mcp-preflight.sh
sudo sh ./v4.1.13/mesh-cos-mcp-verify.sh
```

All three commands remain rooted at `/share/Docker/cos-mcp/releases`.

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires active release identity `4.1.13`, application image `mesh-cos-mcp:qnap-v4.1.13`, both containers healthy, `slack_hitl_ready=true`, and the governed response envelope:

```text
mcp_version: 4.0.0
deployment_release: 4.1.13
agent_id: cos
```

Do not print protected Slack or tunnel files as an acceptance check.

## Intentional Slack reconfiguration

Only when protected Slack configuration intentionally needs replacement:

```sh
cd /share/Docker/cos-mcp/releases
sudo env MESH_COS_FORCE_SLACK_HITL_RECONFIGURE=1 sh ./v4.1.13/mesh-cos-slack-hitl-configure.sh
```

The candidate `.env.runtime` must already exist, which normally means preparation has run. The governed approver user ID is restaged automatically. Forced reconfiguration may still request the Slack verifier bot token and Socket Mode app-level token with hidden input because those values are credentials and are not shipped in the release.

## Failure diagnostics

Do not delete or recreate state after a failure. Capture the durable diagnostic log:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

The log must not contain tunnel or Slack credential values. The governed approver user ID is non-secret but is still intentionally omitted from routine deployment logs.

## Rollback

Use the most recent successful `pre-deploy` backup under:

```text
/share/QNAP NAS/Mike Home/MCP/CoS/Backups
```

Follow `rollback-checklist.md` and `backup-restore.md`. Do not replace the canonical TaskLedger with an unverified file and do not delete the v4.1.13 release directory while investigating a failed deployment.

## Post-upgrade acceptance

After local deployment passes:

1. run `CHATGPT-ACCEPTANCE.md` through the installed **Mesh CoS MCP** app;
2. run `chatgpt-published-app-production-acceptance-v4.1.13.md` for roster/catalog, audit, scheduled-dispatcher, official OpenAI bot notice, ordinary-message negative control, verified human approver identity, and `/mesh-approval` Socket Mode decision acceptance;
3. reconcile the TaskLedger operating mirror when the exact source connector is available.

Repository-green v4.1.13 is an integrated release candidate, not production certification. Production acceptance requires the actual QNAP serving instance and hosted checks to pass.

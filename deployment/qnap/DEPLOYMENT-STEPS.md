# Short QNAP Deployment and Upgrade Steps

v4.1.11 corrects the QNAP release-layout defects in the published v4.1.10 artifact. The canonical Phase 1 authority/runtime contract remains **4.0.0** and the v4.1.10 scheduled-execution and Slack HITL behavior is retained.

## Canonical paths

- active application root: `/share/Docker/cos-mcp`
- versioned release root: `/share/Docker/cos-mcp/releases/v4.1.11`
- canonical state: `/share/Docker/cos-mcp/state`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

The v4.1.11 bundle is self-contained at the versioned release root. **No helper scripts are copied to `/share/Docker`.** Operator scripts self-resolve their extracted release directory.

## Upgrade behavior

The deployment orchestrator preserves the canonical TaskLedger, existing Secure MCP `tunnel_id`, tunnel runtime-key file, Slack HITL protected files, qnet/static networking, and active runtime descriptors until the candidate is healthy. It performs, in order:

1. pre-deploy online backup when the current service is running;
2. candidate release preparation from staged metadata/build context;
3. protected Slack HITL configuration using the staged candidate image;
4. staged-candidate QNAP preflight;
5. candidate Compose render/deployment;
6. application/tunnel health wait;
7. atomic promotion of candidate `.env`, Compose, and release metadata to the canonical application root;
8. governed MCP verification;
9. post-deploy backup.

The candidate release is derived from `<release-root>/cos-mcp/release-metadata.txt`. An explicitly supplied `v4.1.11` is normalized to runtime value `4.1.11`; a genuine mismatch still fails closed. The normal deployment command does not require `sudo` to preserve `MESH_COS_DEPLOYMENT_RELEASE`.

Before an existing `mesh-cos-mcp:qnap-v4.1.11` image can be reused, preparation compares its OCI version and revision labels with staged release metadata. A mismatch forces a rebuild from the staged build context.

## Protected Slack HITL inputs

Existing protected files are preserved. If a protected file is missing, deployment prompts for it after the candidate image is prepared:

- Slack provider user ID for MK, stored only in `/share/Docker/cos-mcp/secrets/slack-approver-user-id`;
- Slack bot credential for server-side provider verification, stored only in `/share/Docker/cos-mcp/secrets/slack-verifier-token`;
- Slack Socket Mode app-level `xapp-` credential, stored only in `/share/Docker/cos-mcp/secrets/slack-socket-app-token`.

These values are not written to source, `.env.runtime`, active `.env`, deployment logs, release assets, or TaskLedger evidence text. Governed secret files remain runtime UID/GID `65532:65532`, mode `0400`, and read-only container mounts.

## QNAP Docker privilege note

Docker commands require `sudo` for the current QNAP operator account. Run the operator scripts that touch Docker with `sudo`. The long-running Mesh runtime remains UID/GID `65532:65532`, read-only rootfs, capabilities dropped, no-new-privileges, and no Docker socket.

## Safe v4.1.11 upgrade

Assuming the ZIP and checksum were downloaded to `/share/Docker`, stage them into the canonical versioned release directory:

```sh
mkdir -p /share/Docker/cos-mcp/releases/v4.1.11
cp /share/Docker/mesh-cos-mcp-qnap-v4.1.11.zip /share/Docker/cos-mcp/releases/v4.1.11/
cp /share/Docker/mesh-cos-mcp-qnap-v4.1.11.zip.sha256 /share/Docker/cos-mcp/releases/v4.1.11/
cd /share/Docker/cos-mcp/releases/v4.1.11
sha256sum -c mesh-cos-mcp-qnap-v4.1.11.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.11.zip
chmod 0755 ./mesh-cos-*.sh ./cos-mcp/qnap-environment-probe.sh
```

Create an explicit operator backup and run the non-mutating preflight:

```sh
cd /share/Docker/cos-mcp/releases/v4.1.11
sudo sh ./mesh-cos-mcp-backup.sh pre-v4.1.11-manual
sudo sh ./mesh-cos-mcp-preflight.sh
```

Before preparation, preflight should report the active production release separately from `PASS staged candidate release 4.1.11`. If production is still v4.1.8, that is expected. It must not render or describe v4.1.8 as the staged candidate.

Run the deployment command **by itself**:

```sh
cd /share/Docker/cos-mcp/releases/v4.1.11
sudo sh ./mesh-cos-mcp-deploy.sh
```

Do not queue additional pasted commands while deployment is waiting for or processing terminal input. No release environment variable needs to be passed through `sudo` for a normal deployment.

Then verify from the same release directory:

```sh
cd /share/Docker/cos-mcp/releases/v4.1.11
sudo sh ./mesh-cos-mcp-verify.sh
```

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires active release identity `4.1.11`, application image `mesh-cos-mcp:qnap-v4.1.11`, both containers healthy, `slack_hitl_ready=true`, and the governed response envelope:

```text
mcp_version: 4.0.0
deployment_release: 4.1.11
agent_id: cos
```

Do not print protected Slack or tunnel files as an acceptance check.

## Intentional Slack reconfiguration

Only when protected Slack configuration intentionally needs replacement:

```sh
cd /share/Docker/cos-mcp/releases/v4.1.11
sudo env MESH_COS_FORCE_SLACK_HITL_RECONFIGURE=1 sh ./mesh-cos-slack-hitl-configure.sh
```

The candidate `.env.runtime` must already exist, which normally means v4.1.11 preparation has run.

## Failure diagnostics

Do not delete or recreate state after a failure. Capture the durable diagnostic log:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

The log must not contain tunnel or Slack secret values or the protected human Slack identifier.

## Rollback

Use the most recent successful `pre-deploy` or explicit `pre-v4.1.11-manual` backup under:

```text
/share/QNAP NAS/Mike Home/MCP/CoS/Backups
```

Follow `rollback-checklist.md` and `backup-restore.md`. Do not replace the canonical TaskLedger with an unverified file and do not delete the v4.1.11 release directory while investigating a failed deployment.

## Post-upgrade acceptance

After local deployment passes:

1. run `CHATGPT-ACCEPTANCE.md` through the installed **Mesh CoS MCP** app;
2. run `chatgpt-published-app-production-acceptance-v4.1.11.md` for the exact roster/catalog, audit, scheduled-dispatcher, official OpenAI bot notice, ordinary-message negative control, and `/mesh-approval` Socket Mode human decision;
3. reconcile the TaskLedger operating mirror when the exact source connector is available.

Repository-green v4.1.11 is an integrated release candidate, not production certification. Production acceptance requires the actual QNAP serving instance and hosted checks to pass.

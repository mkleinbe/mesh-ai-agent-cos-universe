# Short QNAP Deployment and Upgrade Steps

v4.1.8 corrects the hosted MCP request-contract, validation, canonical lookup error-classification, governed Skill handoff, and AgentOps request-binding defects. The canonical Phase 1 authority/runtime contract remains **4.0.0**.

## Upgrade behavior

The deployment script preserves the canonical TaskLedger, existing Secure MCP `tunnel_id`, and tunnel runtime-key file. It performs a pre-deploy online backup, prepares the release-bound image, recreates the services, verifies runtime identity and the governed MCP envelope, and takes a post-deploy backup.

Before an existing `mesh-cos-mcp:qnap-v4.1.8` image can be reused, preparation compares its OCI version and revision labels with extracted `release-metadata.txt`. A mismatch forces a rebuild from the extracted build context.

The application container receives `MESH_COS_DEPLOYMENT_RELEASE=4.1.8`. The remote MCP process refuses to listen if deployment identity is missing or blank.

## QNAP Docker privilege note

On this QNAP operator account, Docker commands require `sudo`. Run the deployment orchestrator itself with `sudo`. The long-running Mesh runtime remains UID/GID `65532:65532`, read-only rootfs, all capabilities dropped, no-new-privileges, and no Docker socket.

## Safe upgrade

Place the v4.1.8 ZIP and checksum in `/share/Docker`, then run:

```sh
cd /share/Docker
sha256sum -c mesh-cos-mcp-qnap-v4.1.8.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.8.zip
chmod 0755 /share/Docker/mesh-cos-*.sh /share/Docker/cos-mcp/qnap-environment-probe.sh
sudo sh /share/Docker/mesh-cos-mcp-deploy.sh
```

Run the deploy command by itself. Do not queue additional pasted commands while the installer is waiting for or processing terminal input.

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
```

PASS requires release identity `4.1.8`, application image `mesh-cos-mcp:qnap-v4.1.8`, and both containers healthy. The governed response envelope must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.8
agent_id: cos
```

## Failure diagnostics

Do not delete or recreate state after a failure. The deployment orchestrator reports a `DIAGNOSTIC_LOG` receipt. Capture the latest deployment log with:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

## Post-upgrade ChatGPT acceptance

After local deployment passes, run `CHATGPT-ACCEPTANCE.md` through the installed **Mesh CoS MCP** app. Final production acceptance requires the actual hosted path to demonstrate the v4.1.8 schema, validation, identity, authorization, governed Skill handoff, lifecycle, and audit behavior.

# Short QNAP Deployment and Upgrade Steps

v4.1.6 adds production deployment-release observability for the published **Mesh CoS MCP** ChatGPT app and OpenAI Secure MCP Tunnel path. It carries forward the v4.1.5 release-identity preflight correction, v4.1.4 modern MCP transport correction, and v4.1.3 QNAP permission, backup, observability, and runtime-hardening controls.

The canonical Phase 1 authority/runtime contract remains **4.0.0**. This is a patch-level QNAP deployment and production-acceptance hardening release.

## Upgrade behavior

The deployment script preserves the canonical TaskLedger, existing Secure MCP `tunnel_id`, and tunnel runtime-key file. It performs a pre-deploy online backup, builds the v4.1.6 release-bound image, validates `.env` release identity against the v4.1.6 bundle metadata, recreates the services, verifies the runtime, and takes a post-deploy backup.

The v4.1.6 application container receives `MESH_COS_DEPLOYMENT_RELEASE=4.1.6`. The remote MCP process refuses to listen if that deployment identity is missing or blank.

## QNAP Docker privilege note

On this QNAP operator account, Docker commands require `sudo`. Run the deployment orchestrator itself with `sudo`; its child Docker and Compose operations then inherit the required host privilege. This does **not** make the long-running Mesh runtime root. `mesh-cos-mcp` still runs as UID/GID `65532:65532` with read-only root filesystem, dropped capabilities, no-new-privileges, and no Docker socket.

## Safe copy/paste upgrade

Place the v4.1.6 ZIP and checksum in `/share/Docker`, then run the complete block below. The installer executes inside a subshell so an internal failure does not terminate the parent SSH session.

```sh
if cd /share/Docker; then
  (
    set -u
    ZIP="mesh-cos-mcp-qnap-v4.1.6.zip"
    SUM="mesh-cos-mcp-qnap-v4.1.6.zip.sha256"

    [ -f "$ZIP" ] || { echo "ERROR: missing /share/Docker/$ZIP" >&2; exit 1; }
    [ -f "$SUM" ] || { echo "ERROR: missing /share/Docker/$SUM" >&2; exit 1; }
    sha256sum -c "$SUM" || { echo "ERROR: checksum failed" >&2; exit 1; }
    unzip -oq "$ZIP" || { echo "ERROR: extraction failed" >&2; exit 1; }
    chmod 0755 /share/Docker/mesh-cos-*.sh /share/Docker/cos-mcp/qnap-environment-probe.sh || exit 1
    sudo sh /share/Docker/mesh-cos-mcp-deploy.sh
  )
  RC=$?
else
  RC=1
fi

echo
if [ "$RC" -eq 0 ]; then
  echo "PASS: Mesh CoS MCP v4.1.6 deployment completed."
else
  echo "ERROR: deployment stopped with rc=$RC. SSH session remains active." >&2
  if [ -f /share/Docker/cos-mcp/logs/deployment/LATEST ]; then
    DIAGNOSTIC_LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST 2>/dev/null || true)
    [ -z "$DIAGNOSTIC_LOG" ] || echo "DIAGNOSTIC_LOG=$DIAGNOSTIC_LOG" >&2
  fi
fi
```

## First-deployment inputs only

A clean first deployment can require three facts the installer must not invent:

1. the path to the approved existing canonical TaskLedger if the canonical target does not exist;
2. the OpenAI Secure MCP `tunnel_id`;
3. the OpenAI tunnel runtime API key, entered through a hidden terminal prompt.

An upgrade from an existing running deployment should preserve all three.

## Local post-deploy identity check

After the deploy script returns PASS, verify the application and tunnel are healthy and the dual release identity is correct:

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
curl -fsS http://127.0.0.1:8080/healthz
curl -fsS http://127.0.0.1:8080/readyz
```

PASS requires `.env` and bundle metadata to report `4.1.6`, the application image to be `mesh-cos-mcp:qnap-v4.1.6`, and both status endpoints to include:

```text
mcp_version: 4.0.0
deployment_release: 4.1.6
agent_id: cos
transport: SECURE_MCP_TUNNEL
```

## Failure diagnostics

The scripts write one shared log under `/share/Docker/cos-mcp/logs/deployment`. The newest path is recorded in `/share/Docker/cos-mcp/logs/deployment/LATEST`.

If a run fails, do not delete or recreate the environment first. Capture the complete log with:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

The diagnostic collector is designed not to dump the tunnel secret, `.env` contents, process environments, credential-bearing command arguments, or tunnel-client logs.

## Post-upgrade ChatGPT acceptance

After local deployment and verification pass, continue with `CHATGPT-ACCEPTANCE.md` using the installed **Mesh CoS MCP** app. Run the ten sequential read-only calls without container restart and require every successful governed tool envelope to report `mcp_version=4.0.0`, `deployment_release=4.1.6`, and `agent_id=cos`.

Do not declare v4.1.6 accepted until both local dual-identity checks and hosted published-app acceptance are green.

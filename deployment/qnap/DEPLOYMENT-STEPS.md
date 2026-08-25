# Short QNAP Deployment and Upgrade Steps

v4.1.4 fixes the production MCP transport/session defect that surfaced through ChatGPT as `502 Upstream or external service errors`. It retains the v4.1.3 QNAP permission, backup, observability, and runtime-hardening corrections.

## Upgrade behavior

For an existing running v4.1.3 environment, the deployment script preserves the canonical TaskLedger, the existing Secure MCP `tunnel_id`, and the existing tunnel runtime-key file. It performs a pre-deploy online backup, builds the v4.1.4 release-bound image, runs preflight, recreates the services with the new image identities, verifies the runtime, and takes a post-deploy backup.

The canonical Phase 1 authority/runtime contract remains `4.0.0`; this is a QNAP transport patch release.

## QNAP Docker privilege note

On this QNAP operator account, Docker commands require `sudo`. Run the deployment orchestrator itself with `sudo`; its child Docker and Compose operations then inherit the required host privilege. This does **not** make the long-running Mesh runtime root. `mesh-cos-mcp` still runs as UID/GID `65532:65532` with read-only root filesystem, dropped capabilities, no-new-privileges, and no Docker socket.

## Safe copy/paste upgrade

Place the v4.1.4 ZIP and checksum in `/share/Docker`, then run the complete block below. The installer executes inside a subshell so an internal failure does not terminate the parent SSH session.

```sh
if cd /share/Docker; then
  (
    set -u
    ZIP="mesh-cos-mcp-qnap-v4.1.4.zip"
    SUM="mesh-cos-mcp-qnap-v4.1.4.zip.sha256"

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
  echo "PASS: Mesh CoS MCP v4.1.4 deployment completed."
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

An upgrade from the existing running deployment should preserve all three.

## Failure diagnostics

The scripts write one shared log under:

`/share/Docker/cos-mcp/logs/deployment`

The newest path is recorded in:

`/share/Docker/cos-mcp/logs/deployment/LATEST`

If a run fails, do not delete or recreate the environment first. Capture the complete log with:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

The diagnostic collector is designed not to dump the tunnel secret, `.env` contents, process environments, credential-bearing command arguments, or tunnel-client logs.

## Post-upgrade acceptance

After deployment passes, continue with `CHATGPT-ACCEPTANCE.md`. v4.1.4 acceptance specifically re-tests modern MCP discovery and repeated sequential calls through the published Secure MCP Tunnel path so the former session-loss/502 defect is not considered closed until the hosted path passes.

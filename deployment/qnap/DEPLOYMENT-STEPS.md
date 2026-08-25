# Short QNAP Deployment Steps

v4.1.3 fixes the QNAP non-root shared-folder permission failure and adds durable failure instrumentation across the deployment lifecycle.

## Human inputs required on first run

The deployment automates everything except three facts it must not invent:

1. the path to the approved existing canonical TaskLedger if the canonical target does not already exist;
2. the OpenAI Secure MCP `tunnel_id`;
3. the OpenAI tunnel runtime API key, entered through a hidden terminal prompt.

On later idempotent runs, the existing canonical ledger, tunnel ID, and secret file are preserved.

## Safe copy/paste deployment

Place the v4.1.3 ZIP and checksum in `/share/Docker`, then run the entire block below. The deployment executes inside a subshell. Any internal `exit` terminates only the installer subshell. The parent SSH session remains active.

```sh
if cd /share/Docker; then
  (
    set -u
    ZIP="mesh-cos-mcp-qnap-v4.1.3.zip"
    SUM="mesh-cos-mcp-qnap-v4.1.3.zip.sha256"

    [ -f "$ZIP" ] || { echo "ERROR: missing /share/Docker/$ZIP" >&2; exit 1; }
    [ -f "$SUM" ] || { echo "ERROR: missing /share/Docker/$SUM" >&2; exit 1; }
    sha256sum -c "$SUM" || { echo "ERROR: checksum failed" >&2; exit 1; }
    unzip -oq "$ZIP" || { echo "ERROR: extraction failed" >&2; exit 1; }
    chmod 0755 /share/Docker/mesh-cos-*.sh /share/Docker/cos-mcp/qnap-environment-probe.sh || exit 1
    sh /share/Docker/mesh-cos-mcp-deploy.sh
  )
  RC=$?
else
  RC=1
fi

echo
if [ "$RC" -eq 0 ]; then
  echo "PASS: Mesh CoS MCP v4.1.3 deployment completed."
else
  echo "ERROR: deployment stopped with rc=$RC. SSH session remains active." >&2
  if [ -f /share/Docker/cos-mcp/logs/deployment/LATEST ]; then
    DIAGNOSTIC_LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST 2>/dev/null || true)
    [ -z "$DIAGNOSTIC_LOG" ] || echo "DIAGNOSTIC_LOG=$DIAGNOSTIC_LOG" >&2
  fi
fi
```

## Failure diagnostics

The scripts write one shared log under:

`/share/Docker/cos-mcp/logs/deployment`

The newest path is recorded in:

`/share/Docker/cos-mcp/logs/deployment/LATEST`

If a run fails, capture the complete log with:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

The diagnostic collector is designed not to dump the tunnel secret, `.env` contents, process environments, credential-bearing command arguments, or tunnel-client logs.

## Non-root QNAP behavior

The SSH operator is not required to run as root or use `sudo`. The script does not use host `chown` to hand state to UID/GID 65532. It uses a short-lived, network-disabled Docker helper over only the explicit state or secret path. The long-running Mesh application still runs as UID/GID 65532.

Preflight tests canonical-state access from the runtime identity. Online backup export uses `docker cp`, so the SSH operator does not need direct read permission on UID-65532 runtime files.

## Docker and Compose behavior

The deployment sets a writable deployment-local `DOCKER_CONFIG` at `/share/Docker/cos-mcp/.docker-cli`, avoiding the inaccessible Container Station QPKG-home config observed in the live v4.1.2 run.

Compose V2 resolution still first tries `docker compose`, then the Docker-reported plugin path, standard CLI-plugin locations, and the Container Station QPKG path. Compose V1 is rejected.

After deployment passes, continue with `CHATGPT-ACCEPTANCE.md`.

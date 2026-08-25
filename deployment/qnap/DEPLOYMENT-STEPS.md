# Short QNAP Deployment Steps

v4.1.2 fixes QNAP Compose V2 discovery and makes the copy/paste installer safe for an interactive SSH session.

## Human inputs required on first run

The deployment script automates everything except three facts it must not invent:

1. the path to the approved existing canonical TaskLedger if the canonical target does not already exist;
2. the OpenAI Secure MCP `tunnel_id`;
3. the OpenAI tunnel runtime API key, entered through a hidden terminal prompt.

On later idempotent runs, the existing canonical ledger, tunnel ID, and secret file are preserved.

## Safe copy/paste deployment

Place the v4.1.2 ZIP and checksum in `/share/Docker`, then run the entire block below. The deployment executes inside a subshell. Any `exit` caused by a failed check terminates only that subshell and cannot log the operator out of SSH.

```sh
cd /share/Docker || return 1 2>/dev/null || true
(
  set -u
  ZIP="mesh-cos-mcp-qnap-v4.1.2.zip"
  SUM="mesh-cos-mcp-qnap-v4.1.2.zip.sha256"

  [ -f "$ZIP" ] || { echo "ERROR: missing $ZIP" >&2; exit 1; }
  [ -f "$SUM" ] || { echo "ERROR: missing $SUM" >&2; exit 1; }
  sha256sum -c "$SUM" || exit 1
  unzip -oq "$ZIP" || exit 1
  chmod 0755 mesh-cos-*.sh cos-mcp/qnap-environment-probe.sh || exit 1
  sh ./mesh-cos-mcp-deploy.sh
)
RC=$?
if [ "$RC" -eq 0 ]; then
  echo "PASS Mesh CoS MCP deployment completed"
else
  echo "ERROR Mesh CoS MCP deployment failed with rc=$RC; SSH session remains active" >&2
fi
```

## Compose behavior

The host scripts require Compose V2. They first try `docker compose`. If that is not callable in the QNAP SSH environment, they resolve the installed Compose V2 plugin from Docker client metadata, `/usr/local/lib/docker/cli-plugins/docker-compose`, `/usr/libexec/docker/cli-plugins/docker-compose`, or the Container Station QPKG install path. Compose V1 is rejected.

The deploy script then performs pre-backup when applicable, preparation, canonical-ledger validation, hidden secret capture, non-secret `.env` generation, host preflight, Compose deployment, bounded health waits, runtime/security verification, direct non-tunnel denial testing, and post-deploy backup.

After the command passes, continue with `CHATGPT-ACCEPTANCE.md`.

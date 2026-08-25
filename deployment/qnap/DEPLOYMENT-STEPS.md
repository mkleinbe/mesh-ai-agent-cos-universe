# Short QNAP Deployment and Upgrade Steps

v4.1.7 closes the release-integrity gap exposed by the hosted `deployment_release` acceptance failure. The canonical Phase 1 authority/runtime contract remains **4.0.0**.

The final v4.1.6 repository and release ZIP already contained the correct dual-identity response code. v4.1.7 therefore hardens the QNAP deployment boundary so an older image cannot survive under a reused local tag, and it adds a real governed `tools/call` to local post-deploy verification.

## Upgrade behavior

The deployment script preserves the canonical TaskLedger, existing Secure MCP `tunnel_id`, and tunnel runtime-key file. It performs a pre-deploy online backup, prepares the release-bound image, recreates the services, verifies the runtime and governed MCP envelope, and takes a post-deploy backup.

Before an existing `mesh-cos-mcp:qnap-v4.1.7` image can be reused, preparation compares its OCI version and revision labels with the extracted `release-metadata.txt`. A mismatch forces a rebuild from the extracted build context. After build or reuse, the same labels are verified before the image ID is recorded.

The application container receives `MESH_COS_DEPLOYMENT_RELEASE=4.1.7`. The remote MCP process refuses to listen if deployment identity is missing or blank.

## QNAP Docker privilege note

On this QNAP operator account, Docker commands require `sudo`. Run the deployment orchestrator itself with `sudo`. This host-side authority does **not** make the long-running Mesh runtime root. `mesh-cos-mcp` continues to run as UID/GID `65532:65532` with a read-only root filesystem, all capabilities dropped, no-new-privileges, and no Docker socket.

## Safe copy/paste upgrade

Place the v4.1.7 ZIP and checksum in `/share/Docker`, then run the complete block below. The installer executes inside a subshell so an internal failure does not terminate the parent SSH session.

```sh
if cd /share/Docker; then
  (
    set -u
    ZIP="mesh-cos-mcp-qnap-v4.1.7.zip"
    SUM="mesh-cos-mcp-qnap-v4.1.7.zip.sha256"

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
  echo "PASS: Mesh CoS MCP v4.1.7 deployment completed."
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
3. the OpenAI tunnel runtime API key, entered through the hidden terminal prompt.

An upgrade from an existing running deployment should preserve all three.

## Local post-deploy identity check

A successful deploy now includes a real read-only `registry.get_agent` MCP `tools/call` from the tunnel network namespace. The deployment does not return PASS unless that governed response envelope contains the expected identity.

After the deploy script returns PASS, the following checks provide additional operator evidence:

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sed -n 's/^commit=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{ index .Config.Labels "org.opencontainers.image.version" }} {{ index .Config.Labels "org.opencontainers.image.revision" }}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/healthz').then(r=>r.text()).then(console.log)"
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires `.env` and bundle metadata to report `4.1.7`, the application image label to report `4.1.7-qnap`, the image revision to equal the bundle `commit=` value, both containers to be healthy, and both status endpoints to include:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
transport: SECURE_MCP_TUNNEL
```

The deployment log must also contain a PASS for `governed tool envelope dual release identity`.

## Failure diagnostics

The scripts write one shared log under `/share/Docker/cos-mcp/logs/deployment`. The newest path is recorded in `/share/Docker/cos-mcp/logs/deployment/LATEST`.

If a run fails, do not delete or recreate the environment first. Capture the complete log with:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

The diagnostic collector does not intentionally collect the tunnel secret, `.env` contents, process environments, credential-bearing command arguments, or tunnel-client logs.

## Post-upgrade ChatGPT acceptance

After local deployment and verification pass, continue with `CHATGPT-ACCEPTANCE.md` using the installed **Mesh CoS MCP** app. Run the sequential read-only acceptance without restarting the QNAP containers and require every successful governed tool envelope to report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
```

Do not declare v4.1.7 accepted until both the local governed-envelope gate and the hosted published-app acceptance are green.

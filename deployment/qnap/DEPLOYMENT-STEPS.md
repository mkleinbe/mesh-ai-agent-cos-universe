# Short QNAP Deployment and Upgrade Steps

v4.1.10 hardens scheduled execution and the Slack human-approval boundary. The canonical Phase 1 authority/runtime contract remains **4.0.0**.

## Upgrade behavior

The single deployment orchestrator preserves the canonical TaskLedger, existing Secure MCP `tunnel_id`, existing tunnel runtime-key file, and existing Slack HITL protected files when present. It performs, in order:

1. pre-deploy online backup when the current service is running;
2. v4.1.10 release preparation and provenance validation;
3. protected Slack HITL configuration;
4. QNAP preflight;
5. Compose render/deployment;
6. application/tunnel health wait;
7. governed MCP verification;
8. post-deploy backup.

Before an existing `mesh-cos-mcp:qnap-v4.1.10` image can be reused, preparation compares its OCI version and revision labels with extracted `release-metadata.txt`. A mismatch forces a rebuild from the extracted build context.

The application container receives `MESH_COS_DEPLOYMENT_RELEASE=4.1.10`. Remote production also sets `MESH_COS_SLACK_HITL_REQUIRED=true`; runtime readiness fails unless both the provider-verification boundary and authenticated Slack Socket Mode human-interaction boundary initialize and remain active.

## Protected Slack HITL inputs

On the first v4.1.10 deployment, the orchestrator calls `mesh-cos-slack-hitl-configure.sh` after the release image is prepared. If the protected files do not already exist, it prompts for:

- the Slack provider user ID for MK, captured visibly and stored only in `/share/Docker/cos-mcp/secrets/slack-approver-user-id`;
- a Slack bot credential used only by the server-side provider verifier to read the governed approval thread, captured with terminal echo disabled and stored only in `/share/Docker/cos-mcp/secrets/slack-verifier-token`;
- a Slack Socket Mode app-level `xapp-` credential, captured with terminal echo disabled and stored only in `/share/Docker/cos-mcp/secrets/slack-socket-app-token`.

The personal identity and secret values are not written to source, generated `.env`, deployment logs, release assets, or TaskLedger evidence text. All governed secret files are normalized to runtime UID/GID and mode `0400` and mounted read-only into the application container.

The provider-verifier credential is **not** the outbound HITL author. Governed approval notices must still be authored by the official OpenAI ChatGPT/ChatGPT Agents Slack surface. The Socket Mode app-level credential establishes the separate `/mesh-approval` human-interaction ingress. If the Workspace Agent delivery surface is unavailable, the workflow fails closed as `BLOCKED_CHATGPT_AGENT_TRANSPORT`. If Socket Mode is unavailable, canonical approval remains PENDING and ordinary Slack text does not substitute for it.

## QNAP Docker privilege note

On this QNAP operator account, Docker commands require `sudo`. Run the deployment orchestrator itself with `sudo`. The long-running Mesh runtime remains UID/GID `65532:65532`, read-only rootfs, all capabilities dropped, no-new-privileges, and no Docker socket.

## Safe upgrade

Place the v4.1.10 ZIP and checksum in `/share/Docker`, then run:

```sh
cd /share/Docker
sha256sum -c mesh-cos-mcp-qnap-v4.1.10.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.10.zip
chmod 0755 /share/Docker/mesh-cos-*.sh /share/Docker/cos-mcp/qnap-environment-probe.sh
sudo sh /share/Docker/mesh-cos-mcp-deploy.sh
```

Run the deploy command by itself. Do not queue additional pasted commands while the installer is waiting for or processing terminal input.

To intentionally replace the protected Slack HITL configuration later, run the protected configuration step with the explicit reconfigure flag after v4.1.10 is prepared:

```sh
cd /share/Docker
sudo MESH_COS_FORCE_SLACK_HITL_RECONFIGURE=1 sh /share/Docker/mesh-cos-slack-hitl-configure.sh
```

Then rerun the normal deployment orchestrator.

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires release identity `4.1.10`, application image `mesh-cos-mcp:qnap-v4.1.10`, both containers healthy, and `slack_hitl_ready=true`. The governed response envelope must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.10
agent_id: cos
```

Do not print the protected Slack files as an acceptance check. Their usability is proven by runtime readiness and the hosted synthetic Slack acceptance procedure.

## Failure diagnostics

Do not delete or recreate state after a failure. The deployment orchestrator reports a `DIAGNOSTIC_LOG` receipt. Capture the latest deployment log with:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

The log must not contain the tunnel key, Slack verifier token, Socket Mode app token, or human Slack identifier.

## Post-upgrade acceptance

After local deployment passes:

1. run the existing `CHATGPT-ACCEPTANCE.md` through the installed **Mesh CoS MCP** app;
2. run `chatgpt-published-app-production-acceptance-v4.1.10.md` for scheduled idempotency/lifecycle, the official OpenAI bot-authored synthetic notice, the ordinary-message negative control, and the `/mesh-approval` Socket Mode human decision;
3. reconcile the Google TaskLedger operating mirror when the exact source connector is available.

Production certification requires zero open CRITICAL/HIGH defects and no required live acceptance blocker. Repository-green v4.1.10 alone is a verified candidate, not production certification.

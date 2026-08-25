# Short QNAP Deployment Steps

The v4.1.1 bundle reduces first deployment to one operator command after extraction.

## Human inputs required on first run

The deployment script can automate everything except three facts it must not invent:

1. the path to the approved existing canonical TaskLedger if the canonical target does not already exist;
2. the OpenAI Secure MCP `tunnel_id`;
3. the OpenAI tunnel runtime API key, entered through a hidden terminal prompt.

On later idempotent runs, the existing canonical ledger, tunnel ID, and secret file are preserved, so no prompt is normally required.

## Deploy

1. Extract `mesh-cos-mcp-qnap-v4.1.1.zip` directly into `/share/Docker`. It creates `/share/Docker/cos-mcp` and the `mesh-cos-mcp-*.sh` operator scripts at `/share/Docker`.
2. Run:

```sh
cd /share/Docker && sh mesh-cos-mcp-deploy.sh
```

The script automatically performs the following in fail-closed order:

- preserves a pre-deploy online backup when an existing service is running;
- creates the approved QNAP state and secret directories;
- builds the release-bound `mesh-cos-mcp:qnap-v4.1.1` image locally from the bundle and records its content-addressed image ID;
- pulls the versioned OpenAI tunnel client when no prior immutable RepoDigest is available, then records its RepoDigest and image ID;
- stages the explicitly selected existing canonical TaskLedger only when the target is absent, fixes ownership to `65532:65532`, and validates it through the canonical runtime;
- captures the tunnel runtime key with terminal echo disabled and stores it only in `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key` with mode `0400`;
- generates `/share/Docker/cos-mcp/.env` with no secret values;
- runs QNAP host preflight;
- deploys both containers with `pull_policy: never`;
- waits for both containers to become healthy;
- verifies runtime identity, resources, least privilege, image IDs, readiness, and direct non-tunnel denial;
- writes a post-deploy online state plus non-secret configuration backup under `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`.

After this command passes, continue with `CHATGPT-ACCEPTANCE.md`.

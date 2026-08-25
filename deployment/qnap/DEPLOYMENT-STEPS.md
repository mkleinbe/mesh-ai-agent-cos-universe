# Short QNAP Deployment Steps

1. Copy the release bundle contents into `/share/Docker`, producing `/share/Docker/cos-mcp` plus the `mesh-cos-mcp-*.sh` scripts at `/share/Docker`.
2. Run `cd /share/Docker && sh mesh-cos-mcp-prepare.sh`.
3. Put the approved canonical ledger at `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` and fix ownership to `65532:65532`.
4. Copy `/share/Docker/cos-mcp/.env.example` to `.env`; set the verified Mesh image digest, OpenAI tunnel image digest, and tunnel ID.
5. Create `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key`, owned by `65532:65532`, mode `0400`, containing only the tunnel runtime key.
6. Run `cd /share/Docker && sh mesh-cos-mcp-preflight.sh`. Do not continue unless it passes.
7. Run `sh mesh-cos-mcp-deploy.sh`, then `sh mesh-cos-mcp-verify.sh`.
8. Connect the ChatGPT MCP app through the approved Secure MCP Tunnel, scan the CoS catalog, run one read-only and one governed-write acceptance test, then record the deployed image digests and audit evidence.

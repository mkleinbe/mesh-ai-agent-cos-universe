# v4.1.1 QNAP Deployment Automation

`v4.1.1` is a patch release for the QNAP Secure MCP deployment surface. It preserves the existing governed Mesh Chief of Staff operating core and canonical Phase 1 agent/runtime authority contract at `4.0.0`, while automating the QNAP deployment steps that do not require human authority, canonical-source selection, or secret knowledge.

## Verified target environment

The production target remains the 2026-08-25 probe of `mdk-qnap6782xt`: x86_64/linux-amd64, 4 CPU cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, and QNAP `lan7` qnet on `eth1` with subnet `192.168.7.0/24` and gateway `192.168.7.1`.

The production service remains `192.168.7.60`, with internal tunnel traffic on `172.30.60.0/29`.

## Fixed QNAP layout

- Scripts run from `/share/Docker`.
- Application root: `/share/Docker/cos-mcp`.
- Release build context: `/share/Docker/cos-mcp/build-context`.
- Canonical state root: `/share/Docker/cos-mcp/state`.
- Ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`.
- Tunnel runtime secret: `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key`.
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`.

## One-command operator flow

After extracting the release bundle into `/share/Docker`, the operator runs:

```sh
cd /share/Docker && sh mesh-cos-mcp-deploy.sh
```

The script automatically performs pre-backup, release-bound image build/pinning, canonical ledger staging when required, hidden credential-file creation, deterministic `.env` generation, preflight, Compose deployment, bounded health waits, verification, direct non-tunnel denial testing, and post-deploy backup.

The only first-run inputs that remain human are the approved existing TaskLedger source path when needed, the OpenAI Secure MCP `tunnel_id`, and the tunnel runtime API key. Existing canonical state and secret material are preserved on later runs.

## Deterministic image boundary

The release ZIP now includes the minimal source/build context required to build `mesh-cos-mcp:qnap-v4.1.1` locally on the QNAP. Prepare records the Docker content-addressed image ID. The OpenAI tunnel client is resolved to an immutable GHCR RepoDigest and Docker image ID. Preflight and post-deploy verification bind the configured and running containers to those exact IDs.

Compose uses `pull_policy: never` for both services after preparation.

## Secret boundary

The tunnel runtime key is captured with terminal echo disabled, written only to the approved secret file with owner `65532:65532` and mode `0400`, and never written to `.env`, source control, release artifacts, deployment receipts, or backups.

## Persistence and recovery

Production still refuses a missing or in-memory TaskLedger. A missing canonical target can only be populated from an explicitly selected existing source. An existing canonical target is preserved.

Automated backups use SQLite online backup and capture non-secret deployment configuration, release metadata, running image IDs, and SHA-256 receipts under the safely quoted backup root. The secret directory is excluded.

The backup destination remains on the same NAS, so QNAP snapshots and an independent second copy remain recommended defense in depth for total-NAS-loss scenarios.

## Resource policy

`mesh-cos-mcp` remains limited to 2 CPUs and 24 GiB RAM with no PID limit. `mesh-cos-tunnel` remains limited to 0.25 CPU and 256 MiB RAM with no PID limit.

## Release quality gates

The candidate must pass package integrity, TypeScript/MCP tests, stdio certification, npm audit, schema and documentation drift checks, Ruff, mypy, 100% branch-aware Python coverage, Bandit, compileall, QNAP shell syntax, v4.1.1 automation BDD/evaluation tests, deterministic release-bundle construction, production image build from the bundled build context, Compose/resource validation, least-privilege checks, readiness, direct MCP denial, SQLite backup integrity, and restart recovery.

## Release assets

The release workflow creates:

- `mesh-cos-mcp-qnap-v4.1.1.zip`, designed to be unpacked directly into `/share/Docker`;
- `mesh-cos-mcp-qnap-v4.1.1.zip.sha256`.

The bundle contains QNAP configuration, runbooks, operator scripts, ChatGPT acceptance instructions, and the minimal local image build context. It contains no runtime secrets and no canonical TaskLedger data.

## Version identity

- Repository/QNAP deployment release: `4.1.1`
- Semantic tag: `v4.1.1`
- Container image label default: `4.1.1-qnap`
- Canonical Phase 1 agent/runtime authority contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 registered agents
- Message Operations remains the tenth registered agent.
- Mesh Devil's Advocate remains the external governed shared Skill, not an agent principal.
- Production connectivity: OpenAI Secure MCP Tunnel
- Local engineering transport: stdio retained

See `docs/release-4.1.1-qnap-deployment-automation.md`, `deployment/qnap/README-QNAP.md`, and `deployment/qnap/CHATGPT-ACCEPTANCE.md`.

# v4.1.3 QNAP Non-Root Deployment Reliability

`v4.1.3` is a corrective QNAP deployment release driven by the second live operator run. It fixes the QTS shared-folder ownership failure and the coupled permission/backup assumptions that would have failed later, and it establishes a durable observability standard for Mesh deployment and update tooling.

The governed Mesh Chief of Staff runtime, authority model, network boundary, canonical TaskLedger semantics, Secure MCP Tunnel, resource policy, and 10-agent workforce are unchanged.

## Root cause fixed

The live v4.1.2 run proved that a normal QNAP SSH operator may have Container Station/Docker authority while lacking host `chown` authority over shared-folder paths. v4.1.2 incorrectly attempted host-side `chown -R 65532:65532` during preparation, causing `Operation not permitted` before image build or service creation.

v4.1.3 removes that host-privilege assumption. It builds/reuses the release-bound image first, then uses a short-lived Docker helper with network disabled, read-only root filesystem, all capabilities dropped before adding only ownership/mode capabilities, and only the explicit state or secrets bind mount. The long-running application runtime remains UID/GID `65532:65532` and retains its existing least-privilege controls.

## Coupled defects fixed

- **Host ownership handoff:** no QNAP host `chown` to UID/GID 65532 is required.
- **Runtime permission verification:** host preflight validates owner/mode plus actual read/write access from a UID-65532 container instead of incorrectly requiring the SSH user to read/write canonical state.
- **Backup export:** SQLite online backups are exported with `docker cp` and temporary state is removed from inside the runtime container, so the SSH operator does not need direct ownership of runtime-created files.
- **Docker client configuration:** deployment uses `/share/Docker/cos-mcp/.docker-cli` as a writable `DOCKER_CONFIG`, avoiding the inaccessible Container Station QPKG home warning observed in the live trace.

## Deployment observability

All QNAP deploy, prepare, preflight, verify, and backup scripts now share a structured run log. The default log root is:

`/share/Docker/cos-mcp/logs/deployment`

Every run records a run ID, timestamps, stages, safe command classifications, return codes, component/script identity, and bounded platform/filesystem/container evidence. Failure output includes `DIAGNOSTIC_LOG=<path>`.

Diagnostics explicitly do not collect secret-file contents, `.env` contents, process environments, credential-bearing command arguments, or tunnel-client logs. Bounded application log tails are defensively redacted.

`docs/qnap-deployment-observability-standard.md` makes this instrumentation contract reusable for future Mesh QNAP deployment, update, rollback, backup, migration, and maintenance scripts.

## Security boundary

The permission helper is operator-side deployment infrastructure, not part of the MCP callable surface. It is short lived, has no Docker socket, uses `--network none`, a read-only root filesystem, `--cap-drop ALL`, validated numeric UID/GID, explicit bind mounts, and only the ownership/mode capabilities required for QNAP shared-folder remediation. Ledger staging runs as UID/GID 65532 and streams the approved source through stdin rather than placing canonical data in command arguments.

No MCP tools, agent authority, human-only operations, ingress paths, published ports, or secret-handling authority are expanded.

## Regression and verification gates

The release gate includes:

- QNAP-038 through QNAP-041 ready BDD scenarios;
- shell regressions for Compose discovery, structured observability, return-code preservation, secret non-collection, numeric UID/GID validation, and constrained permission-helper arguments;
- actual Docker bind-mount ownership handoff to UID/GID 65532;
- runtime-identity state read/write evidence;
- Docker-mediated SQLite backup export and integrity verification;
- full Node/MCP certification, Python tests with 100% branch-aware coverage, Ruff, mypy, Bandit, contract/doc drift checks, release-bundle checksum validation, Compose/resource validation, production image build, hardened runtime controls, readiness, direct MCP denial, restart recovery, and backup integrity.

## Resource policy

`mesh-cos-mcp` remains limited to 2 CPUs and 24 GiB RAM with no PID limit. `mesh-cos-tunnel` remains limited to 0.25 CPU and 256 MiB RAM with no PID limit.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.3.zip`
- `mesh-cos-mcp-qnap-v4.1.3.zip.sha256`

The bundle contains the release-bound build context, operator scripts, observability and permission helpers, debugging record, runbooks, and ChatGPT acceptance instructions. It contains no runtime secrets and no canonical TaskLedger data.

## Version identity

- Repository/QNAP deployment release: `4.1.3`
- Semantic tag: `v4.1.3`
- Container image label default: `4.1.3-qnap`
- Canonical Phase 1 agent/runtime authority contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 registered agents
- Message Operations remains the tenth registered agent.
- Mesh Devil's Advocate remains the external governed shared Skill, not an agent principal.
- Human-only operations remain `approval.record_decision` and `reliability.human_override`.
- `COMPLETED != VERIFIED` remains unchanged.
- Production connectivity remains OpenAI Secure MCP Tunnel.

See `docs/release-4.1.3-qnap-nonroot-observability.md`, `docs/qnap-deployment-observability-standard.md`, `deployment/qnap/DEPLOYMENT-STEPS.md`, and `deployment/qnap/CHATGPT-ACCEPTANCE.md`.

# v4.1.2 QNAP Compose Discovery Fix

`v4.1.2` is a corrective patch for the QNAP Secure MCP deployment surface. It fixes two defects observed during the first live operator deployment attempt without changing the governed Mesh Chief of Staff runtime, authority model, network boundary, persistence model, or secret-handling contract.

## Defects fixed

- **QNAP Compose CLI discovery:** v4.1.1 assumed that an installed Compose V2 package would always be callable through `docker compose`. The live QNAP SSH session disproved that assumption. v4.1.2 resolves Compose V2 through the Docker subcommand when available, then falls back to Docker client plugin metadata, `/usr/local/lib/docker/cli-plugins/docker-compose`, `/usr/libexec/docker/cli-plugins/docker-compose`, and Container Station QPKG paths. Compose V1 is rejected.
- **SSH session termination:** the prior copy/paste wrapper used a top-level `exit` after a deployment error. In an interactive SSH shell that logs the operator out. The v4.1.2 deployment block runs inside a subshell, so a failed deployment returns a nonzero status while the parent SSH session remains active.

## Regression evidence

`deployment/qnap/tests/test-compose-discovery.sh` reproduces the QNAP failure mode in which `docker` exists and `docker compose` fails while the Compose V2 plugin remains discoverable. The regression also covers the normal Docker subcommand and rejects Compose V1. CI executes this test before release-bundle construction.

The QNAP environment probe now records the Container Station install path, Docker-reported Compose plugin path, and executable Compose candidates to make future QTS/Container Station upgrades observable rather than inferred.

## Deployment behavior retained

The one-command governed deployment lifecycle remains unchanged after Compose resolution: pre-backup when applicable, release-bound local Mesh image build and image-ID recording, tunnel RepoDigest resolution, explicit canonical TaskLedger staging only when necessary, canonical runtime/SQLite preflight, hidden tunnel-key capture, non-secret `.env` generation, QNAP host preflight, Compose deployment, bounded health waits, least-privilege/runtime verification, direct non-tunnel denial testing, and post-deploy backup.

## Security boundary

The patch does not add MCP tools, expand agent authority, change the 10-agent roster, expose new ports, weaken container controls, alter the TaskLedger trust boundary, or move the tunnel key into configuration. Compose discovery executes only a local executable path reported by the local Docker client or found under known Docker/Container Station installation locations, and requires a Compose V2 version response.

## Resource policy

`mesh-cos-mcp` remains limited to 2 CPUs and 24 GiB RAM with no PID limit. `mesh-cos-tunnel` remains limited to 0.25 CPU and 256 MiB RAM with no PID limit.

## Release assets

The release workflow creates:

- `mesh-cos-mcp-qnap-v4.1.2.zip`, designed to be unpacked directly into `/share/Docker`;
- `mesh-cos-mcp-qnap-v4.1.2.zip.sha256`.

The checksum references only the ZIP basename, so both files can be verified directly from `/share/Docker`.

## Version identity

- Repository/QNAP deployment release: `4.1.2`
- Semantic tag: `v4.1.2`
- Container image label default: `4.1.2-qnap`
- Canonical Phase 1 agent/runtime authority contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 registered agents
- Message Operations remains the tenth registered agent.
- Mesh Devil's Advocate remains the external governed shared Skill, not an agent principal.
- Production connectivity: OpenAI Secure MCP Tunnel
- Local engineering transport: stdio retained

See `docs/release-4.1.2-qnap-compose-discovery-fix.md`, `deployment/qnap/DEPLOYMENT-STEPS.md`, and `deployment/qnap/CHATGPT-ACCEPTANCE.md`.

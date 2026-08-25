# QNAP Production Preflight

The 2026-08-25 probe establishes linux/amd64, 4 cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, `lan7` qnet on `eth1`, `192.168.7.0/24`, gateway `192.168.7.1`, ext4 storage, and no observed overlap with `172.30.60.0/29`.

## v4.1.7 release-image provenance boundary

v4.1.7 adds a deployment-integrity gate between the extracted QNAP release bundle and the local Docker image selected for service replacement.

Preparation requires `release-metadata.txt` to provide both `version=4.1.7` and a 40-character release commit. The requested deployment release must equal that metadata version. An existing local `mesh-cos-mcp:qnap-v4.1.7` image is reusable only when its OCI labels exactly match:

```text
org.opencontainers.image.version = 4.1.7-qnap
org.opencontainers.image.revision = <release metadata commit>
```

A mismatch forces a rebuild from the extracted release build context. After either build or reuse, the same labels are revalidated before the image ID is recorded in `.env`.

This prevents a prerelease, partial, or stale image already carrying the final mutable tag from silently surviving extraction of the final release package.

## Governed response-envelope verification

After Compose replacement and health readiness, `mesh-cos-mcp-verify.sh` executes a real modern MCP read-only `registry.get_agent` `tools/call` against the running service from an ephemeral verifier sharing the tunnel client's network namespace.

Deployment verification fails unless the actual governed response envelope reports:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
```

The verifier has no state volume, no tunnel runtime secret, no Docker socket, no added Linux capability, and no persistent service lifetime. It does not weaken the application source-IP gate or change the production authority model.

## Serving-release identity boundary retained

The QNAP deployment release is independently observable from the canonical Phase 1 authority/runtime contract. Compose passes `MESH_COS_DEPLOYMENT_RELEASE=4.1.7` into the application container and the remote MCP process requires a non-empty deployment release before listening.

Successful runtime status distinguishes:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
transport: SECURE_MCP_TUNNEL
```

The first value is the canonical authority/runtime contract. The second is the serving QNAP deployment release. Neither value widens authority.

## Earlier release boundaries retained

- v4.1.5 derives the expected deployment release from extracted bundle metadata rather than a duplicated patch constant.
- v4.1.4 uses stateless modern MCP transport and requires current `server/discover` serviceability.
- v4.1.3 uses constrained Docker helpers for QNAP ownership/mode handoff and Docker-mediated backup.

The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger semantics, Secure MCP Tunnel source-IP gate, and runtime resource policy are unchanged.

## QNAP Docker operator privilege

The current SSH operator account requires `sudo` for Docker access. The supported operator path invokes the deployment/preflight orchestrator with `sudo`; child Docker/Compose commands inherit that host-side authority. This does not alter the long-running non-root runtime controls.

## Docker client configuration

Deployment initializes `/share/Docker/cos-mcp/.docker-cli` as `DOCKER_CONFIG`. This avoids dependency on the inaccessible Container Station QPKG-home Docker config observed in earlier live traces.

## Automated preparation

`mesh-cos-mcp-prepare.sh` resolves Compose V2, initializes durable logging, validates release metadata, validates or rebuilds `mesh-cos-mcp:qnap-v4.1.7` from release provenance, records the verified image ID, normalizes runtime state through the constrained helper, preserves or explicitly streams the approved canonical TaskLedger, validates canonical runtime/SQLite integrity as UID 65532, pins the tunnel RepoDigest/image ID, preserves or captures the tunnel runtime key, applies file-only secret ownership/mode, generates non-secret `.env`, and invokes host preflight.

## Host and runtime preflight

Host preflight validates architecture, CPU/RAM headroom, Docker, Compose V2, qnet shape, `192.168.7.60` ownership/conflict evidence, application/state/backup paths, deployment-local Docker config, canonical ledger owner/mode, actual ledger read/write access from runtime UID/GID 65532, tunnel-secret owner/mode, bundle/environment release identity equality, image IDs, 2 CPU/24 GiB/no PID limit, free-space threshold, and Compose rendering.

Runtime preflight independently validates amd64, non-root execution, immutable `cos`, tunnel auth mode, system time, no Docker socket, existing readable/writable canonical SQLite ledger, free-space threshold, SQLite integrity, active registry identity, canonical runtime availability, and governance audit-chain integrity.

`/readyz` additionally proves modern MCP discovery serviceability so the service cannot report ready while rejecting the current ChatGPT MCP protocol path. `/healthz` and `/readyz` expose the same non-secret dual release identity required in governed tool envelopes.

## Published ChatGPT acceptance

After local deployment passes, the installed **Mesh CoS MCP** app must execute the documented sequential read-only acceptance through the OpenAI Secure MCP Tunnel without 502, `invalid_session`, reconnect, or container restart. Every successful governed tool response must report `mcp_version=4.0.0`, `deployment_release=4.1.7`, and `agent_id=cos`.

Any successful hosted response that omits `deployment_release` remains a release blocker. Repository/container CI and local verification cannot substitute for this hosted acceptance.

Any mandatory local failure returns nonzero, appends bounded diagnostics to the run log, and prints the diagnostic log path. High filesystem utilization remains an advisory while the absolute free-space gate passes.

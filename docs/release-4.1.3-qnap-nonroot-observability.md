# v4.1.3 QNAP Non-Root Deployment Reliability

## Change classification

Corrective patch to the QNAP deployment/runtime operator surface. No Mesh CoS authority, agent roster, MCP tool, canonical-state semantic, or network-ingress change.

## Live evidence that triggered the patch

The v4.1.2 QNAP run passed bundle verification, Docker detection, and Compose V2 discovery, then failed at the first host-side ownership operation with `Operation not permitted` for the state and secrets trees. The same console output showed a non-fatal Docker config permission warning from the Container Station QPKG home.

This evidence established that Docker access and arbitrary host `chown` authority are independent on QTS.

## Root-cause correction

The deployment no longer performs host `chown` to runtime UID/GID 65532. Preparation builds the release image first and performs ownership normalization through a bounded one-shot Docker helper. Canonical ledger staging is streamed through stdin to a UID-65532 container. Tunnel-secret ownership is applied by a separate bounded helper after hidden local capture.

Preflight tests permissions as the runtime identity, not the SSH operator. Backup exports runtime-created SQLite data through `docker cp` and removes temporary files from inside the application container.

## Observability contract

A shared POSIX-shell observability library provides one run ID and log across deploy/prepare/preflight/verify/backup, stage and command markers, exact return-code preservation while streaming output, bounded diagnostics, log retention, and a final diagnostic-log receipt.

The logging contract intentionally excludes secret values, `.env` contents, process environments, credential-bearing argv, and tunnel logs. It records only bounded evidence necessary to diagnose the deployment/runtime boundary.

## Targeted security properties

- helper containers are never privileged;
- helper containers use no network and no Docker socket;
- helper root filesystems are read-only;
- all capabilities are dropped before the explicit ownership/mode capabilities are added;
- helper visibility is limited to explicit state or secrets bind mounts;
- numeric runtime UID/GID is validated before use;
- application runtime remains UID/GID 65532 and retains all existing controls;
- canonical TaskLedger is never silently replaced;
- tunnel secret remains file-only and is never logged;
- no MCP authority or ingress boundary is expanded.

## Verification expectation

Release requires the shell regressions plus an actual Docker bind-mount ownership handoff, runtime-identity state access, real production-image build from the release bundle, runtime security/readiness/restart tests, Docker-mediated online backup export and SQLite integrity, exact diff review, targeted security review, post-merge CI, semantic tag binding, and artifact checksum verification.

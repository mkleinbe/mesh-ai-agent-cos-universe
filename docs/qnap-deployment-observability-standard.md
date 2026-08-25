# QNAP Deployment and Update Script Observability Standard

This standard applies to Mesh QNAP deployment, upgrade, rollback, backup, migration, and maintenance scripts.

## Required behavior

Every operator-facing script must provide a unique run ID and timestamped durable log, a shared log across parent/child scripts, explicit stages, command classifications and exact return codes, script identity and line number when available, bounded failure diagnostics, streaming command output without losing return status, a final `DIAGNOSTIC_LOG=<path>` receipt, bounded retention, and SSH-safe failure semantics.

## Secret and data handling

Diagnostics must never dump secret-file contents, `.env` contents, process environments, shell variables containing credentials, credential-bearing command arguments, or tunnel-client logs unless a separate redaction-safe review authorizes them. Known OpenAI key forms and authorization headers are defensively redacted from bounded application-log tails.

## Bash/POSIX shell engineering rules

QNAP operator scripts target BusyBox/POSIX `sh` unless a script explicitly declares and verifies Bash. Do not depend on Bash-only process substitution, arrays, `ERR` traps, or `PIPESTATUS`. Avoid broad `set -e` in orchestration scripts where it hides failure context. Use `set -u` plus explicit return-code handling for consequential commands. Preserve return codes when streaming output. Quote every path, use unique temporary names, prefer idempotent operations, and fail closed on canonical-state, image-identity, tunnel-identity, or security-control drift.

## Privilege rules

A deployment script must not assume that Docker access implies host filesystem ownership authority. For the Mesh CoS QNAP runtime, ownership normalization uses a one-shot Docker helper with `--network none`, read-only rootfs, no Docker socket, no privileged mode, `--cap-drop ALL` plus only required ownership/mode capabilities, explicit state or secrets bind mounts, validated numeric UID/GID, and immediate container removal. The long-running application container remains independently least-privileged.

## Verification expectation

A deployment/update change is not verified from shell syntax alone. Required evidence includes regression proof for the original failure, shell syntax/portability checks, actual-container integration for Docker/runtime behavior, state/backup integrity, targeted security review when sensitive boundaries change, and exact release-bundle/checksum verification.

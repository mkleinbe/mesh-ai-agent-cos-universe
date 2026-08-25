# Release 4.1.1: QNAP Deployment Automation

## Purpose

v4.1.1 is a patch to the QNAP Secure MCP deployment surface. It does not change the canonical Phase 1 agent/runtime authority contract, which remains 4.0.0. It reduces the QNAP deployment from a multi-step manual runbook to a single orchestrated command while preserving explicit human control over facts and credentials the system must not invent.

## Automated lifecycle

`mesh-cos-mcp-deploy.sh` now orchestrates:

1. pre-deploy online backup when an existing service is running;
2. QNAP directory and permission preparation;
3. release-bound local Mesh image build from the bundle;
4. content-addressed Mesh image ID recording;
5. versioned OpenAI tunnel-client retrieval and immutable RepoDigest/image-ID recording;
6. explicit-source canonical TaskLedger staging only when the canonical target is absent;
7. canonical runtime/SQLite integrity validation;
8. hidden tunnel runtime-key capture and 0400 secret-file creation;
9. deterministic non-secret `.env` generation;
10. QNAP host/network/resource/image preflight;
11. deterministic Compose deployment with `pull_policy: never`;
12. bounded container health waits;
13. least-privilege, resource, readiness, image-ID and non-tunnel-denial verification;
14. post-deploy online state and non-secret configuration backup with SHA-256 verification.

## Remaining human inputs

The deployment cannot and must not invent:

- which existing TaskLedger is the approved canonical source when no canonical target exists;
- the OpenAI Secure MCP `tunnel_id`;
- the OpenAI tunnel runtime API key.

The runtime key is entered with terminal echo disabled. It is never stored in `.env`, source, logs, release assets, or backup configuration.

## Release bundle

The release ZIP now includes a minimal build context under `cos-mcp/build-context/`. The QNAP can therefore build the Mesh image without a Git checkout and without requiring a separately published Mesh registry image.

The bundle excludes runtime secrets, `.env`, canonical state, node_modules, generated TypeScript output, Python bytecode, tests, and unrelated repository documentation. CI builds the same bundle shape before merge and builds the production image from that bundled build context.

## Image identity

The Mesh image is locally tagged `mesh-cos-mcp:qnap-v4.1.1` and coupled to its Docker content-addressed image ID. The OpenAI tunnel image is coupled to its immutable GHCR RepoDigest and Docker image ID. Preflight verifies those mappings before deployment and post-deploy verification checks that each running container uses the recorded image ID.

Compose sets `pull_policy: never` on both services so a deployment cannot silently substitute a remote image after preparation.

## Persistence and backups

The canonical target ledger is never silently replaced. If it already exists, prepare preserves it. If it does not exist, the operator must select an explicit existing source file, which is staged atomically and validated through the canonical runtime before deployment.

Backups include the online SQLite backup plus non-secret deployment configuration and image receipts. Secret material is explicitly excluded.

## Security applicability

Security applicability is TARGETED because this patch touches deployment execution, secrets, persistence, supply-chain/image identity, network transport, and an MCP boundary. Controls include hidden credential input, file-only runtime secret, non-secret environment generation, fail-closed ledger staging, content-addressed image verification, immutable tunnel RepoDigest, no post-prepare image pulls, existing least-privilege container controls, and bounded health/preflight gates.

Residual operational risk remains that the first retrieval of the exact public tunnel-client version tag is resolved to a RepoDigest at preparation time rather than being shipped as a preloaded image. Once resolved, that RepoDigest and image ID are pinned and reused.

## Acceptance

Repository/CI acceptance is defined by QNAP-001 through QNAP-035. Live ChatGPT acceptance remains a human-operated product-surface step because ChatGPT Developer Mode, tunnel/workspace association, tool scanning, and confirmation prompts are controlled by the OpenAI workspace UI.

Use `deployment/qnap/CHATGPT-ACCEPTANCE.md` after QNAP deployment passes.

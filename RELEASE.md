# v1.0.0 Production Readiness

`v1.0.0` is the first stable semantic production-readiness release of the Mesh AI Chief of Staff operating core.

## What this release establishes

- 100% branch-aware `mesh_cos` coverage as a release gate.
- Strict source Ruff, mypy, dependency integrity, contract validation, runtime/documentation drift, Workspace Agent package drift, Bandit high-severity scanning, and compileall in CI.
- Serialized `mesh_cos.mcp_runtime.MCPRuntime` as the governed remote execution boundary.
- Server-derived agent identity, authority, and implementation provenance from the canonical registry.
- Human-only approval decisions and reliability overrides through authenticated human principals.
- L4 fail-closed approval behavior and Michael-exclusive L5 authority.
- Server-owned replay executor registration, with no client-supplied code or import-path execution.
- Atomic Slack and governance-event idempotency with canonical persistence.
- Separate accountable-owner `task.complete` and independent `task.verify` acceptance verification.
- 11 governed role Skills and 11 Workspace Agent manifests aligned to release `1.0.0` and the canonical MCP allowlists.
- Production preflight and private-preview requirements before live Workspace Agent activation.

## Production activation boundary

This release marks the repository and deployment specification as production-ready. It does not claim the target environment is already live. Production activation remains fail-closed until the approved HTTPS `mesh-cos-mcp` endpoint, `MESH_COS_MCP_SERVER_URL`, Workspace authentication/app permissions, applicable Slack credentials, the dedicated Answer Desk channel, production approval-owner mapping, approved source/Skill credentials, secrets management, and deployment ownership are configured and tested.

Run `python scripts/production-preflight.py` before activation. Add `--require-slack`, `--require-answer-desk`, and `--require-ledger` when those surfaces are in scope.

## Release identity

- Semantic version: `1.0.0`
- Git tag: `v1.0.0`
- Release title: `v1.0.0 Production Readiness`
- Canonical state: `TaskLedger`
- Workspace Agent count: 11
- Production activation: environment-dependent, fail-closed until preflight and live smoke tests pass

See `docs/release-1.0.0-production-readiness.md` for the full release record and Mermaid architecture diagrams.

# Production Readiness

## Release status

Repository/QNAP deployment release **`v4.1.6 Secure MCP Published App Production Identity`** is the current deployment-readiness target. The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly **10 registered agents** plus the external advisory Mesh Devil's Advocate shared Skill.

Production readiness is fail closed. Repository CI, QNAP deployment verification, and published ChatGPT app acceptance are separate gates.

## Required authority invariants

- `TaskLedger` is canonical.
- The canonical roster contains exactly 10 registered agents.
- Mesh Devil's Advocate remains an external advisory shared Skill, not a principal.
- `MESH_COS_AGENT_ID` is process-bound and cannot be changed by prompt text, HTTP request content, task content, delegated instructions, app payloads, connectors, or shared-Skill output.
- Per-agent MCP exposure is deny by default.
- The production CoS projection contains exactly 27 governed tools.
- `approval.record_decision` and `reliability.human_override` are human-principal-only and absent from every agent catalog.
- L4 requires qualified-human approval. L5 remains Michael-exclusive.
- Delegation preserves or narrows authority and inherited approvals.
- `task.complete` requires a non-empty outcome and supporting evidence and produces `COMPLETED` only.
- `task.verify` is a separate verifier action requiring acceptance evidence. In Phase 1 only CoS receives that agent capability.
- `COMPLETED != VERIFIED`.
- Child completion cannot silently verify the parent.
- Consultant Network Steward is terminal. Stale consultant availability cannot become confirmed readiness.
- Message Operations is the tenth registered agent and may execute only explicitly approved communications.

## Required deployment invariants

- Production ChatGPT uses the installed **Mesh CoS MCP** app through the **OpenAI Secure MCP Tunnel**.
- `MCP_AUTH_MODE=tunnel` and `MCP_TRUSTED_CLIENT_IP` remain mandatory for the remote adapter.
- Production Compose publishes no host MCP port and `/mcp` denies non-tunnel source identities.
- The application container receives a non-empty `MESH_COS_DEPLOYMENT_RELEASE=4.1.6`; missing deployment identity fails remote startup.
- Successful governed production tool envelopes report `mcp_version=4.0.0`, `deployment_release=4.1.6`, and `agent_id=cos`.
- `/healthz` and `/readyz` report the same identity plus `transport=SECURE_MCP_TUNNEL`.
- Runtime remains UID/GID 65532 with read-only root filesystem, all capabilities dropped, no-new-privileges, no Docker socket, 2 CPU, 24 GiB RAM, and no PID limit.
- The canonical SQLite TaskLedger remains the single writable operating-state boundary.
- Tunnel secret material remains outside `.env`, release assets, backups, diagnostics, and MCP responses.

## Required repository certification

A production candidate must pass:

```bash
python -m pip check
cd mcp && npm ci && npm run check && cd ..
python scripts/validate-contracts.py
python scripts/check-runtime-doc-drift.py
python scripts/check-chatgpt-packages.py
ruff check src
ruff check tests scripts --select E9,F63,F7,F82
mypy src --check-untyped-defs
pytest --cov=mesh_cos --cov-report=term-missing --cov-report=xml --cov-fail-under=100
bandit -q -r src -lll
python -m compileall -q src
bash scripts/build-qnap-release-bundle.sh 4.1.6
```

The Python coverage gate remains 100% branch-aware. The MCP package must pass TypeScript build, Node unit tests, real local stdio smoke certification, and high-severity npm audit. CI must additionally build and exercise the v4.1.6 production image.

## End-to-end delegation certification

Synthetic certification must exercise Michael/authorized-principal outcome establishment, CoS intake, CRO/CFO/COO delegation, COO -> Consultant Network Steward depth-2 delegation, governed Devil's Advocate challenge, evidence-backed owner completion, AgentOps inspection, CoS synthesis, separate CoS verification, and audit-chain verification.

Negative scenarios must prove missing evidence blocks completion/verification, excessive delegation depth fails, human-only operations are denied to agents, non-authorized self-verification fails, stale consultant availability remains unconfirmed, Devil's Advocate cannot mutate or execute, and child failure cannot verify a parent.

## QNAP preflight and deployment verification

The QNAP candidate must pass release-metadata/environment equality, canonical ledger integrity, image identity checks, Compose rendering, non-root runtime checks, dual-identity health/readiness, modern MCP discovery, direct-ingress denial, restart recovery, and Docker-mediated online backup integrity.

See `qnap-production-preflight.md` and `../deployment/qnap/DEPLOYMENT-STEPS.md`.

## Published ChatGPT app acceptance

After QNAP deployment verification passes, the installed **Mesh CoS MCP** app must pass the ten-call sequential read-only acceptance sequence in `../deployment/qnap/CHATGPT-ACCEPTANCE.md` without HTTP 502, `invalid_session`, reconnect, or container restart.

Both roster calls must show exactly 10 registered agents. Every successful governed tool envelope must prove the serving QNAP release with `deployment_release=4.1.6` while retaining canonical `mcp_version=4.0.0`.

An optional idempotent L0 governed-write acceptance may be run only when a production write is explicitly intended.

## Historical releases

Historical documents may retain superseded roster counts and deployment releases when clearly scoped to those releases. Current-state documentation must resolve to the canonical 10-agent authority model and the current v4.1.6 QNAP deployment train.

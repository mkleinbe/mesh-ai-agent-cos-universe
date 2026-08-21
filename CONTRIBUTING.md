# Contributing

Current release target: **`v1.1.0 Local ChatGPT MCP`**.

Changes must preserve the Phase 1 operating constitution, the production-readiness controls established in `1.0.0`, and the bundled ChatGPT-local MCP controls established in `1.1.0`. Use test-driven, short-loop engineering practices.

## Required workflow

1. Create a feature branch from current `main`.
2. Add or update tests first for behavioral changes, including negative authorization, failure-path, idempotency, human-principal, local-agent-identity, and replay-safety coverage when relevant.
3. Implement the minimum change required to satisfy the behavior.
4. Run the full release verification.
5. Update schemas, registry policy, Workspace Agent manifests, role Skills, MCP allowlists, configuration, documentation, Mermaid diagrams, and release metadata in the same change when affected.
6. Run production preflight for changes that affect deployment/runtime readiness.
7. Open a pull request to `main` and merge only after CI passes and review comments are resolved.
8. Close superseded pull requests rather than leaving competing branches open.

## Local release verification

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pip check
cd mcp
npm ci
npm run check
cd ..
python scripts/validate-contracts.py
python scripts/check-runtime-doc-drift.py
python scripts/check-chatgpt-packages.py
ruff check src
ruff check tests scripts --select E9,F63,F7,F82
mypy src --check-untyped-defs
pytest --cov=mesh_cos --cov-report=term-missing --cov-report=xml --cov-fail-under=100
bandit -q -r src -lll
python -m compileall -q src
```

`mesh_cos` branch-aware coverage is a **100%** release gate. Do not weaken the threshold to make a build green.

## MCP changes

ChatGPT uses the bundled `LOCAL_STDIO` runtime defined by `chatgpt/mcp/mesh-cos-mcp.v1.json` and implemented under `mcp/`. New or changed MCP behavior requires explicit read/write classification, authority enforcement, audit behavior, approval policy, fixed Python runtime handler, least-privilege per-agent allowlists, negative authorization tests, Node tests, stdio certification, and package-drift coverage.

The TypeScript layer must remain transport-only. Do not duplicate task, authority, approval, governance, or reliability logic outside `MCPRuntime`.

`MESH_COS_AGENT_ID` is a trusted runtime binding. Prompt text and retrieved content must never select it. `MESH_COS_LEDGER_PATH` must preserve one approved canonical operating universe across the 11 agents.

Human-only tools must remain separate from agent allowlists. Replay must never execute client-supplied code, import paths, shell commands, or callable names.

A remote MCP endpoint is optional and may not become an undocumented requirement for ChatGPT-local operation.

## Governance-sensitive changes

Changes to decision rights, approvals, agent authority, human-only operations, source/tool permissions, delegation depth, prohibited actions, registry health, consequential persistence, Workspace app access, Connector Action Constraints, MCP tool allowlists, replay behavior, completion/verification boundaries, or external-write behavior require explicit positive and negative tests plus documentation updates. Do not infer new monetary thresholds or broader autonomy.

## Skill changes

ChatGPT role Skills live under `chatgpt/skills/`. Retain `SKILL.md`, `agents/openai.yaml`, `references/role-contract.md`, and `references/production-readiness.md`. Skill packaging does not prove Workspace app connectivity or deployment activation.

## Production preflight

Run `python scripts/production-preflight.py` before activation or release changes that affect activation semantics. Use `--require-slack`, `--require-answer-desk`, and `--require-ledger` when those surfaces are in scope.

## Documentation standard

Documentation must describe what the runtime and deployment package actually implement. Keep Mermaid diagrams synchronized with executable paths and canonical state boundaries. Historical release and Phase 1 closure records remain historical snapshots.

Current guidance belongs in `docs/release-1.1.0-local-chatgpt-mcp.md`, `docs/production-readiness.md`, `docs/runbook.md`, and `RELEASE.md`.

<!-- mesh-cos-v2-shared-da -->
## v2.0.0 current architecture

The live Phase 1 runtime is a **10-agent** organization. The former repository-local Devil's Advocate agent and duplicate role Skill are removed. **Mesh Devil's Advocate** is an external **shared Skill** available only to Chief of Staff and CRO through governed Skill invocation. It is **advisory** only, cannot overwrite **canonical facts**, cannot execute external actions, and returns decision authority to the owning role or qualified human. `TaskLedger` remains canonical state; ChatGPT uses `LOCAL_STDIO` through `MCPRuntime` with deny-by-default allowlists, human-only approval/override paths, `check-chatgpt-packages.py` drift enforcement, and the 100% branch-aware coverage gate. Historical references to an 11-agent roster or a local Devil's Advocate role describe superseded releases only.


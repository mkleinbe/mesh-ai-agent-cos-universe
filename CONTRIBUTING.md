# Contributing

Current stable repository release: **`v1.0.0 Production Readiness`**.

Changes must preserve the Phase 1 operating constitution and the production-readiness controls established in `1.0.0`. Use test-driven, short-loop engineering practices.

## Required workflow

1. Create a feature branch from current `main`.
2. Add/update tests first for behavioral changes, including negative authorization, failure-path, idempotency, human-principal, and replay-safety coverage when relevant.
3. Implement the minimum change required to satisfy the behavior.
4. Run the full release verification locally when possible.
5. Update schemas, registry policy, Workspace Agent manifests, role Skills, MCP allowlists, configuration, documentation, Mermaid diagrams, and release metadata in the same change when affected.
6. Run production preflight for changes that affect deployment/runtime readiness.
7. Open a pull request to `main`.
8. Merge only after CI passes and review comments are resolved.
9. Close superseded pull requests rather than leaving competing branches open.

## Local release verification

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pip check
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

`mesh_cos` branch-aware coverage is a 100% release gate. Do not weaken the threshold to make a build green. Add behavior-oriented tests for reachable paths or remove genuinely unreachable code through a test-backed refactor.

## Production preflight

Before production activation or release changes that affect activation semantics:

```bash
python scripts/production-preflight.py
```

Use `--require-slack`, `--require-answer-desk`, and `--require-ledger` when those surfaces are in scope.

## Governance-sensitive changes

Changes to decision rights, approvals, agent authority, human-only operations, source/tool permissions, delegation depth, prohibited actions, registry health, consequential persistence, Workspace app access, Connector Action Constraints, MCP tool allowlists, replay behavior, completion/verification boundaries, or external-write behavior require explicit positive and negative tests plus documentation updates. Do not infer new monetary thresholds or broader autonomy.

Workspace Agent Builder settings are subordinate to `agents/registry.json`. They may narrow access but may not widen accountable domain, authority, source truth, approval rights, prohibited actions, or delegation depth.

## Skill changes

ChatGPT role Skills live under `chatgpt/skills/`. Retain required `SKILL.md`, `agents/openai.yaml`, `references/role-contract.md`, and `references/production-readiness.md`. Validate/package affected Skills through the OpenAI skill-creator workflow before release. Skill packaging does not prove MCP or Workspace app connectivity.

## MCP changes

`chatgpt/mcp/mesh-cos-mcp.v1.json` maps Workspace Agent tools to the serialized `MCPRuntime`. New or changed tools require explicit read/write classification, authority enforcement, audit behavior, approval policy, fixed runtime handler, least-privilege per-agent allowlists, negative authorization tests, and package-drift coverage.

Human-only tools must remain separate from agent allowlists. Remote replay must never execute client-supplied code, import paths, shell commands, or callable names.

## Documentation standard

Documentation must describe what the runtime and deployment package actually implement. Planned, product-side, or environment-dependent behavior must be labeled accordingly. Keep Mermaid diagrams synchronized with executable paths and canonical state boundaries.

Historical Phase 1 gap/remediation/closure records remain historical snapshots. Current release and activation guidance belongs in `docs/release-1.0.0-production-readiness.md`, `docs/production-readiness.md`, `docs/runbook.md`, and `RELEASE.md`.

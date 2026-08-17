# Contributing

Changes to this repository must preserve the Phase 1 operating constitution and use test-driven, short-loop engineering practices.

## Required workflow

1. Create a feature branch from current `main`.
2. Add or update tests first for behavioral changes, including negative authorization and failure-path coverage when relevant.
3. Implement the minimum change required to make the test suite pass.
4. Run contract validation, runtime/documentation drift, ChatGPT Workspace Agent package drift, pytest/coverage, critical lint, high-severity security scanning, dependency integrity, and compileall locally when possible.
5. Update schemas, registry policy, Workspace Agent manifests, role Skills, MCP allowlists, configuration, documentation, and Mermaid diagrams in the same change when affected.
6. Open a pull request to `main`.
7. Merge only after CI passes and review comments are resolved.
8. Close superseded pull requests rather than leaving competing branches open.

## Local verification

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m pip check
python scripts/validate-contracts.py
python scripts/check-runtime-doc-drift.py
python scripts/check-chatgpt-packages.py
ruff check src tests scripts --select E9,F63,F7,F82
pytest --cov=mesh_cos --cov-report=term-missing --cov-fail-under=55
bandit -q -r src -lll
python -m compileall -q src
```

## Governance-sensitive changes

Changes to decision rights, approvals, agent authority, source/tool permissions, delegation depth, prohibited actions, registry health, consequential persistence, Workspace app access, Connector Action Constraints, MCP tool allowlists, or external-write behavior require explicit positive and negative test coverage plus documentation updates. Do not infer new monetary thresholds or broader autonomy.

Workspace Agent Builder settings are subordinate to `agents/registry.json`. They may narrow access but may not widen accountable domain, authority, source truth, approval rights, prohibited actions, or delegation depth.

## Skill changes

ChatGPT role Skills live under `chatgpt/skills/`. Keep `SKILL.md` concise, retain required `agents/openai.yaml`, and keep supporting references one level below the entrypoint. Before release, validate each affected Skill with the OpenAI skill-creator validator and package it as `skill.zip`. Skill packaging does not prove MCP or Workspace app connectivity.

## MCP changes

`chatgpt/mcp/mesh-cos-mcp.v1.json` maps Workspace Agent tools to existing runtime bindings. New tools must be necessary for a canonical role, have explicit read/write classification, authority enforcement, audit behavior, approval behavior, runtime binding, least-privilege per-agent allowlists, and negative authorization tests. `WorkspaceAgentMCPPolicy` must continue to deny unknown agents and unlisted tools by default.

## Documentation standard

Documentation must describe what the runtime and deployment package actually implement. Planned, product-side, or configuration-dependent behavior must be labeled accordingly. Keep Mermaid diagrams synchronized with code paths and canonical state boundaries. Do not document a remote MCP endpoint, Workspace app connection, Slack channel, or published Workspace Agent as live until it has been configured and tested in the target environment.

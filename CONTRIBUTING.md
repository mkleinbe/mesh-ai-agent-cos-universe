# Contributing

Changes to this repository must preserve the Phase 1 operating constitution and use test-driven, short-loop engineering practices.

## Required workflow

1. Create a feature branch from current `main`.
2. Add or update tests first for behavioral changes, including negative authorization and failure-path coverage when relevant.
3. Implement the minimum change required to make the test suite pass.
4. Run contract validation, pytest, and compileall locally when possible.
5. Update schemas, registry policy, configuration, documentation, and Mermaid diagrams in the same change when affected.
6. Open a pull request to `main`.
7. Merge only after CI passes and review comments are resolved.
8. Close superseded pull requests rather than leaving competing branches open.

## Local verification

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python scripts/validate-contracts.py
pytest
python -m compileall -q src
```

## Governance-sensitive changes

Changes to decision rights, approvals, agent authority, source/tool permissions, delegation depth, prohibited actions, registry health, or consequential persistence require explicit test coverage and documentation updates. Do not infer new monetary thresholds or broader autonomy.

## Documentation standard

Documentation must describe what the runtime actually implements. Planned or configuration-dependent behavior must be labeled accordingly. Keep Mermaid diagrams synchronized with code paths and canonical state boundaries.

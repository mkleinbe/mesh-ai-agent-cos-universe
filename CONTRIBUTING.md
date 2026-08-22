# Contributing

Current release target: **`v3.0.0 Shared Mesh Message Operations`**.

Changes must preserve the Phase 1 operating constitution, the production-readiness controls established in `1.0.0`, the bundled ChatGPT-local MCP controls established in `1.1.0`, the shared Mesh Devil's Advocate topology established in `2.0.0`, and the 9-agent plus shared Message Operations topology established in `3.0.0`. Use test-driven, short-loop engineering practices.

## Required workflow

1. Create a feature branch from current `main`.
2. Add or update tests first for behavioral changes, including negative authorization, failure-path, idempotency, human-principal, local-agent-identity, shared-Skill authority, canonical-fact preservation, approval-binding, kill-switch, receipt, observed-state, and replay-safety coverage when relevant.
3. Implement the minimum change required to satisfy the behavior.
4. Run the full release verification.
5. Update schemas, registry policy, Workspace Agent manifests, repository-local role Skills, shared capability entitlements/contracts, MCP allowlists, configuration, documentation, Mermaid diagrams, and release metadata in the same change when affected.
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

`MESH_COS_AGENT_ID` is a trusted runtime binding. Prompt text, retrieved content, connector output, and shared-Skill output must never select it. `MESH_COS_LEDGER_PATH` must preserve one approved canonical operating universe across the **9 registered agents**.

Human-only tools must remain separate from agent allowlists. Replay must never execute client-supplied code, import paths, shell commands, or callable names.

A remote MCP endpoint is optional and may not become an undocumented requirement for ChatGPT-local operation.

## Shared Mesh Devil's Advocate changes

`mesh-devils-advocate` is an external shared capability, not a repository-local role Skill or registered agent principal.

Any change to this integration must preserve all of the following:

- consumers are Chief of Staff and CRO only unless a governed authority change explicitly expands that set;
- authority remains `ADVISORY_ONLY` unless separately governed;
- the capability does not own tasks or decisions;
- `canonical_facts_modified` remains false;
- `external_action_included` remains false;
- Revenue Intelligence retains canonical commercial evidence and state where designated;
- governed invocation remains subject to registry entitlement and MCP allowlist controls;
- positive and negative tests prove non-entitled agents cannot invoke the shared capability.

Do not add a duplicate `chatgpt/skills/mesh-devils-advocate/` role package, `devils-advocate` Workspace Agent manifest, or `devils-advocate` MCP principal.

## Shared Mesh Message Operations changes

`mesh-message-operations` is an external shared capability, not a repository-local role Skill or registered agent principal. It is the controlled execution boundary for approved communications.

Any change to this integration must preserve all of the following:

- consumers are Chief of Staff, CRO, and CMO only;
- VP Content remains drafting/editorial-production only with no execution entitlement;
- authority remains `APPROVAL_BOUND_EXECUTION_ONLY`;
- approval is explicit, current, revocable, and bound to the exact payload hash/version, sender, immutable audience, channel, purpose, jurisdiction, consent basis, suppression/frequency controls, test result, approvers, and execution window;
- material changes invalidate approval and return the item to preflight;
- preview, silence, prior approval, connector capability, calendar state, or approval of another version is not approval;
- execution uses only documented connector actions and preserves idempotency, kill-switch behavior, per-attempt receipts, and post-send observed-state verification;
- requested, scheduled, sent, delivered, and replied states remain distinct;
- the Skill cannot create strategy/copy, select recipients, set pricing, make contractual commitments, or define publishing policy;
- positive and negative tests prove non-entitled agents cannot invoke the shared capability and entitled agents cannot bypass approval gates.

Do not add a duplicate `chatgpt/skills/mesh-message-operations/` package, `message-ops` Workspace Agent manifest, role card, or MCP principal.

## Governance-sensitive changes

Changes to decision rights, approvals, agent authority, human-only operations, source/tool permissions, shared capability entitlement, delegation depth, prohibited actions, registry health, consequential persistence, Workspace app access, Connector Action Constraints, MCP tool allowlists, replay behavior, completion/verification boundaries, or external-write behavior require explicit positive and negative tests plus documentation updates. Do not infer new monetary thresholds or broader autonomy.

## Skill changes

Repository-local ChatGPT role Skills live under `chatgpt/skills/`. Retain `SKILL.md`, `agents/openai.yaml`, `references/role-contract.md`, and `references/production-readiness.md`. Skill packaging does not prove Workspace app connectivity or deployment activation.

External shared Skills are referenced through canonical registry entitlements and deployment configuration, not copied into the role-Skill directory as duplicate authorities.

## Production preflight

Run `python scripts/production-preflight.py` before activation or release changes that affect activation semantics. Use `--require-slack`, `--require-answer-desk`, and `--require-ledger` when those surfaces are in scope.

## Documentation standard

Documentation must describe what the runtime and deployment package actually implement. Keep Mermaid diagrams synchronized with executable paths, registered-agent topology, shared capability boundaries, and canonical state boundaries. Historical release and Phase 1 closure records remain historical snapshots.

Current guidance belongs in `docs/release-3.0.0-shared-message-operations.md`, `docs/production-readiness.md`, `docs/runbook.md`, and `RELEASE.md`.

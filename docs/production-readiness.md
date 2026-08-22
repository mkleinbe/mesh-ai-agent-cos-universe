# Production Readiness

## Release status

Release **`v3.0.0 Shared Mesh Message Operations`** is the current production-readiness target. It preserves the governed CoS control plane and bundled `LOCAL_STDIO` MCP runtime while changing the workforce topology from 10 registered principals to **9 agents plus governed external shared Skills**.

Production readiness is fail closed. It does not claim that every external app, credential, approval owner, Slack channel, shared Skill credential, or source system is already activated.

## ChatGPT runtime model

```text
Workspace Agent -> LOCAL_STDIO -> node mcp/dist/index.js
                -> mesh_cos.mcp_stdio_bridge
                -> mesh_cos.mcp_runtime.MCPRuntime
                -> TaskLedger
```

Required runtime configuration:

```text
MESH_COS_AGENT_ID=<registered agent id>
MESH_COS_LEDGER_PATH=.mesh-cos/task-ledger.sqlite3
MESH_COS_PYTHON_BIN=python
```

A managed remote MCP service is optional and is not required for ChatGPT-local operation.

## Workforce and shared capability invariants

The canonical runtime roster contains exactly **9** registered agents. `devils-advocate` and `message-ops` are not registered principals, Workspace Agent manifests, local duplicate Skills, or MCP identities.

**Mesh Devil's Advocate** is an external shared Skill for Chief of Staff and CRO only. Its authority is `ADVISORY_ONLY`.

**Mesh Message Operations** is an external shared Skill for Chief of Staff, CRO, and CMO only. Its authority is `APPROVAL_BOUND_EXECUTION_ONLY`. VP Content remains drafting/editorial-production only.

Message Operations may execute only after explicit current approval is bound to the exact payload hash/version, sender, immutable audience, channel, purpose, jurisdiction, consent basis, suppressions/frequency controls, test result, approvers, and execution window. Material change invalidates approval. The Skill must preflight, recheck kill-switch/cancellation state, use a documented connector action, preserve idempotency, capture per-attempt receipts, and record observed provider state. Requested, scheduled, sent, delivered, and replied are distinct states.

## Release gates

```bash
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

The Python threshold remains **100% branch-aware `mesh_cos` coverage**. Node checks include TypeScript compilation, unit tests, MCP stdio smoke certification, canonical persistence, human-only exclusion, safe-denial behavior, and npm security audit.

## MCP invariants

- transport is `LOCAL_STDIO`;
- each process is bound to one registered `MESH_COS_AGENT_ID`;
- all 9 agents in one universe share an approved `MESH_COS_LEDGER_PATH`;
- per-agent tool access is deny-by-default;
- `devils-advocate` and `message-ops` are absent from the MCP principal roster;
- only entitled roles receive `skills.invoke_governed`;
- `approval.record_decision` and `reliability.human_override` remain human-only;
- L4 requires qualified human approval and L5 remains Michael-exclusive;
- `task.complete` and `task.verify` remain separate;
- `TaskLedger` is canonical before mirrors or interaction responses.

## Production preflight

Run before activation:

```bash
python scripts/production-preflight.py
```

When relevant:

```bash
python scripts/production-preflight.py --require-slack --require-answer-desk --require-ledger
```

Preflight must validate kill-switch state, the **9-agent** registry, both shared capability entitlements, bundled MCP contract/package integrity, runtime binding, canonical ledger configuration, optional Slack/Answer Desk dependencies, and audit-chain integrity where required.

## Workspace Agent readiness

Every remaining Workspace Agent manifest must:

- declare repository release `3.0.0`;
- use `LOCAL_STDIO` and `node mcp/dist/index.js`;
- bind the correct `MESH_COS_AGENT_ID` and approved `MESH_COS_LEDGER_PATH`;
- preserve exact deny-by-default allowlists;
- project Mesh Devil's Advocate only to CoS/CRO;
- project Mesh Message Operations only to CoS/CRO/CMO;
- preserve **Always ask** for write actions unless a reviewed narrower exception exists;
- remain private until positive and negative preview tests pass.

## Production activation boundary

External dependencies still requiring target-environment configuration include Workspace app authentication, Gmail/Slack credentials where used, dedicated Answer Desk Slack configuration, approved source/shared-Skill credentials, production approval-owner mappings, consent/jurisdiction decisions, Google Sheets write credentials where enabled, secrets management, monitoring, and publication/RBAC settings.

A separately deployed HTTPS MCP endpoint is not a production dependency for ChatGPT-local operation.

See `release-3.0.0-shared-message-operations.md`, `../RELEASE.md`, `../chatgpt/mcp/README.md`, and `runbook.md`.

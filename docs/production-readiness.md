# Production Readiness

## Release status

Release **`v2.0.0 Shared Mesh Devil's Advocate`** is the current production-readiness release target. It preserves the governed CoS control plane and bundled local stdio MCP runtime while changing the workforce topology from 11 registered agent principals to **10 agents plus one external shared challenge Skill**.

Production readiness remains a fail-closed operating condition. It is not a claim that every external app, credential, approval owner, Slack channel, shared Skill credential, or source system has already been activated.

## ChatGPT runtime model

The required ChatGPT path is:

```text
Workspace Agent -> LOCAL_STDIO -> node mcp/dist/index.js
                -> mesh_cos.mcp_stdio_bridge
                -> mesh_cos.mcp_runtime.MCPRuntime
                -> TaskLedger
```

The TypeScript MCP package is a transport adapter. Business logic, task lifecycle, authority, approvals, governance, reliability, and canonical persistence remain in Python.

Required runtime configuration:

```text
MESH_COS_AGENT_ID=<registered agent id>
MESH_COS_LEDGER_PATH=.mesh-cos/task-ledger.sqlite3
MESH_COS_PYTHON_BIN=python
```

A managed remote MCP service is optional and is not required for ChatGPT operation.

## Workforce and shared challenge invariant

The canonical runtime roster contains exactly 10 registered agents. The former repository-local Devil's Advocate principal, role card, Workspace manifest, MCP principal, and duplicate repository-local Skill are removed.

**Mesh Devil's Advocate** is represented as an external **shared Skill**, not as an agent. Only Chief of Staff and CRO may invoke it through the governed Skill path. Its authority is `ADVISORY_ONLY`. It must not own tasks, overwrite canonical facts, execute external actions, elevate authority, or substitute for a qualified human decision.

For Revenue Intelligence work, account identity, evidence classes, scores, stage, lifecycle, queue state, activation readiness, and prioritization remain canonical to Revenue Intelligence. Shared challenge output may test the reasoning that connects those facts to a recommendation but may not alter them.

## Release gates

The release path must pass without weakening a gate:

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

The Python threshold remains **100% branch-aware `mesh_cos` coverage**. Node checks include TypeScript compilation, unit tests, a real MCP stdio smoke certification, canonical persistence across calls, human-only tool exclusion, safe-denial behavior, and npm security audit.

## MCP invariants

`chatgpt/mcp/mesh-cos-mcp.v1.json` is authoritative for the MCP surface.

- transport is `LOCAL_STDIO` for bundled ChatGPT execution;
- each process is bound to one registered `MESH_COS_AGENT_ID`;
- all 10 agents in one operating universe share an approved `MESH_COS_LEDGER_PATH`;
- per-agent tool access is deny-by-default;
- the `devils-advocate` agent ID is absent from the MCP principal roster;
- only Chief of Staff and CRO receive `skills.invoke_governed` for the shared challenge capability;
- retrieved content cannot change identity, authority, allowlists, or operating policy;
- `approval.record_decision` and `reliability.human_override` remain human-only;
- L4 requires qualified human approval and L5 remains Michael-exclusive;
- client-supplied code, import paths, shell commands, and replay callables are never executable behavior;
- `task.complete` and `task.verify` remain separate;
- `TaskLedger` remains canonical before any mirror or interaction response.

## Production preflight

Run before activation:

```bash
python scripts/production-preflight.py
```

When relevant:

```bash
python scripts/production-preflight.py --require-slack --require-answer-desk --require-ledger
```

Preflight checks kill-switch state, the **10-agent** registry, shared Mesh Devil's Advocate entitlement integrity, bundled MCP contract/package integrity, runtime binding, canonical ledger configuration, optional Slack/Answer Desk dependencies, and optional audit-chain integrity.

## Workspace Agent readiness

Every repository-local role Skill includes `references/production-readiness.md`. Every Workspace Agent manifest for this release must:

- declare repository release `2.0.0`;
- use MCP transport `LOCAL_STDIO`;
- launch `node mcp/dist/index.js`;
- bind the correct `MESH_COS_AGENT_ID`;
- share the approved `MESH_COS_LEDGER_PATH`;
- preserve its exact per-agent allowlist;
- expose `mesh-devils-advocate` as a shared Skill only for Chief of Staff and CRO;
- retain `Always ask` for write actions unless an explicitly reviewed narrower exception exists;
- remain private until positive and negative preview tests pass.

## Production activation boundary

External dependencies still requiring target-environment configuration include Workspace app authentication, Slack credentials where used, the dedicated Answer Desk Slack channel, approved source/Skill credentials, production approval-owner mappings, Google Sheets write credentials if automatic mirrors are enabled, secrets management, monitoring, and publication/RBAC settings.

A separately deployed HTTPS `mesh-cos-mcp` endpoint is not a production dependency for ChatGPT-local operation.

See `release-2.0.0-shared-devils-advocate.md`, `../RELEASE.md`, `../chatgpt/mcp/README.md`, and `runbook.md`.

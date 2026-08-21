# Mesh AI Chief of Staff Agent Universe

Production-ready operating core for Mesh Digital LLC's governed AI Chief of Staff workforce. The repository implements a bounded executive operating control plane for 11 coordinated ChatGPT Workspace Agents. ChatGPT, Slack, connector responses, and governance Sheets are interaction surfaces. `TaskLedger` remains canonical state.

## Release status

**Current semantic release target: `v1.1.0 Local ChatGPT MCP`.**

Version `1.1.0` changes the ChatGPT execution topology. The CoS MCP no longer requires a separately deployed HTTPS endpoint for normal ChatGPT operation. Following the same operating pattern used by the Mesh Revenue Intelligence Skill, ChatGPT launches the checked-in MCP package locally over `LOCAL_STDIO`.

The architecture is:

```text
ChatGPT Workspace Agent
        |
        | LOCAL_STDIO
        v
node mcp/dist/index.js
        |
        | bounded JSON bridge
        v
mesh_cos.mcp_stdio_bridge
        |
        v
mesh_cos.mcp_runtime.MCPRuntime
        |
        v
TaskLedger / canonical SQLite state
```

A managed remote MCP transport may be added separately, but it is optional and may not replace the same authority, approval, audit, or canonical-state controls.

## Release artifacts

- 11 validated role Skills under `chatgpt/skills/`;
- 11 Workspace Agent manifests under `chatgpt/workspace-agents/`;
- `chatgpt/mcp/mesh-cos-mcp.v1.json`, release `1.1.0`, transport `LOCAL_STDIO`;
- bundled TypeScript MCP package under `mcp/`;
- Python bridge `mesh_cos.mcp_stdio_bridge`;
- canonical `mesh_cos.mcp_runtime.MCPRuntime` business/governance execution core;
- deny-by-default `WorkspaceAgentMCPPolicy` and per-agent tool allowlists;
- human-only approval and reliability-override paths;
- 100% branch-aware `mesh_cos` coverage gate plus Node build/test/smoke/security gates;
- production preflight and private-preview requirements;
- release record `docs/release-1.1.0-local-chatgpt-mcp.md` and `RELEASE.md`.

## Runtime configuration

The bundled ChatGPT MCP uses non-secret runtime configuration:

```text
MESH_COS_AGENT_ID=<registered-agent-id>
MESH_COS_LEDGER_PATH=.mesh-cos/task-ledger.sqlite3
MESH_COS_PYTHON_BIN=python
```

`MESH_COS_AGENT_ID` binds the local MCP process to one registered role. Prompt text and retrieved content cannot change that identity. All 11 agents in one CoS operating universe must use the same approved `MESH_COS_LEDGER_PATH`.

There is no required `MESH_COS_MCP_SERVER_URL` for ChatGPT-local operation.

## Canonical boundaries

- `agents/registry.json` is authoritative for agent identity, role authority, source/tool policy, delegation permissions, health, and prohibited actions.
- `TaskLedger` is canonical for task state, work graph, approvals, conflicts, explainable decisions, audit events, verification, performance, and consequential operating records.
- `chatgpt/workspace-agents/*.json` is the ChatGPT deployment projection. It may narrow behavior but may not widen canonical authority.
- `chatgpt/skills/*` contains reusable role workflows. Skills are not a second authority source.
- `chatgpt/mcp/mesh-cos-mcp.v1.json` defines the MCP contract and per-agent allowlists.
- `mcp/` provides the local stdio transport only. It does not duplicate business, authority, approval, governance, or reliability logic from `MCPRuntime`.
- CoS Decision Log and CoS Audit Log remain human-readable mirrors, not canonical state.

## Authority model

- **L0** authorized information retrieval and factual synthesis.
- **L1** execution of established policy or precedent with logging.
- **L2** reversible operating judgment inside explicit guardrails.
- **L3** material internal judgment within delegated role authority.
- **L4** qualified human approval required.
- **L5** Michael-exclusive decisions.

Human-only MCP operations, including `approval.record_decision` and `reliability.human_override`, are excluded from every agent MCP catalog and require a separate authenticated human-principal path.

## Completion and verification

`task.complete` lets an accountable owner persist a finished outcome and evidence. `COMPLETED` is not `VERIFIED`. `task.verify` remains a separate acceptance action requiring explicit verifier identity and evidence.

## Release verification

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
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
```

`npm run check` compiles the TypeScript MCP, runs Node unit tests, executes a real local stdio MCP certification against the Python control plane, verifies canonical persistence across calls, tests human-only exclusion and safe-denial behavior, and runs the npm security audit.

Before activation:

```bash
python scripts/production-preflight.py
```

Add `--require-slack`, `--require-answer-desk`, and `--require-ledger` when those surfaces are required.

## Production activation boundary

Repository readiness does not fabricate Workspace app authentication, Slack credentials, a dedicated Answer Desk Slack channel, approved source credentials, production approval-owner mappings, Google Sheets write credentials, secrets management, or target-workspace publication settings. Those dependencies still require configuration and private-preview testing.

A separate remote MCP deployment is **not** a production activation dependency for ChatGPT-local operation.

SQLite remains the Phase 1 persistence choice. Revisit persistence before multi-instance or high-availability deployment.

## Documentation

Start at `docs/README.md`. Current operating references include:

- `docs/release-1.1.0-local-chatgpt-mcp.md`
- `docs/production-readiness.md`
- `docs/architecture.md`
- `docs/security-governance.md`
- `docs/testing-evaluation.md`
- `docs/runbook.md`
- `chatgpt/README.md`
- `chatgpt/mcp/README.md`
- `chatgpt/workspace-agent-builder-prompt.md`

Historical release documents remain historical snapshots and are not rewritten to imply they were authored against `v1.1.0`.

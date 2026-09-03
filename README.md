# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository release candidate: `v4.4.1 Commercial Operations Orchestration`. Current production QNAP deployment: `4.4.0`. Canonical Phase 1 authority/runtime contract: `4.0.0`.**

v4.4.1 is an orchestration and operating-control patch. It does not modify or redeploy the healthy QNAP Mesh CoS MCP runtime.

## Canonical architecture

Phase 1 contains exactly 10 registered agents: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations. Mesh Devil's Advocate remains a governed shared Skill, not an eleventh agent.

Mesh CoS MCP TaskLedger is canonical for task ownership, delegation, approval, completion, verification, and audit. Google TaskLedger, Slack, Gmail, connectors, Workspace state, and conversation history are scheduling, interaction, evidence, or mirror surfaces. `COMPLETED` remains distinct from `VERIFIED`.

## v4.4.1 Commercial Operations correction

The Commercial Operations incidents were caused by caller-created work packages placing narrative prerequisite text in canonical task dependency arrays. The 4.4.0 runtime correctly treats each dependency as a canonical predecessor task ID and correctly failed closed.

v4.4.1 therefore fixes the caller/control-plane contract rather than weakening or redeploying the runtime:

- canonical dependencies contain only actual predecessor task IDs;
- narrative prerequisites move to job contracts, acceptance tests, constraints, trigger conditions, evidence, or operating mirrors;
- legacy malformed children are preserved and may be superseded once by a deterministic dependency-clean successor when provider state proves recovery is safe;
- business outcome and technical health are reported separately;
- CMO and VP Content participate through canonical parentage without gaining Revenue Intelligence commercial-truth authority;
- the central Commercial Operations scheduler is aligned to weekdays 08:00, 10:00, 12:00, and 16:00 America/New_York;
- `COM-EMAIL-SEND-DLY-001` remains isolated under the event-driven HITL loop and is never converted to polling.

The detailed architecture and operating runbook are:

- `docs/architecture-v4.4.1-commercial-operations.md`
- `docs/commercial-operations-orchestrator-v4.4.1.md`
- `docs/runbook-v4.4.1-commercial-operations.md`
- `docs/security-review-v4.4.1-commercial-operations.md`
- `docs/release-v4.4.1-commercial-operations.md`

## Production runtime and authority boundaries

The current QNAP Mesh CoS MCP 4.4.0 deployment remains production. Its current owner-execution, registry, audit, completion, verification, and Slack HITL boundaries are unchanged by v4.4.1.

Key invariants remain:

- server-derived agent identity;
- exactly 10 registered agents with canonical parentage;
- deny-by-default tool/capability authority;
- `mesh.cos.owner-execution.v2` for delegated owner execution;
- human-only operations excluded from agent action surfaces;
- Revenue Intelligence as the sole account-level commercial-truth authority;
- exact canonical approval before consequential external action;
- no autonomous public publishing, prospect email send, LinkedIn action, pricing/scope commitment, or approval on Michael's behalf;
- OpenAI Secure MCP Tunnel as the only remote MCP ingress;
- QNAP changes remain operator-proxied through Michael.

## Commercial Operations ownership

- Chief of Staff: occurrence orchestration, work-graph integrity, scoped recovery, cross-job coordination, and separate verification.
- CRO: commercial analysis and governed seller-support work.
- Revenue Intelligence: account fit, lifecycle, priority, buying groups, activation readiness, commercial evidence, and buyer-response interpretation.
- CMO: marketing and authority strategy that may inform commercial context.
- VP Content: bounded content production under CMO.
- GTM Orchestrator: governed activation.
- Messaging Governance and Message Operations: exact approval and execution boundaries.
- LinkedIn Authority OS: authority, relationship, content, and performance context only.

## Repository layout

- `src/mesh_cos/`: canonical Python operating core.
- `mcp/`: remote MCP transport and principal-specific tool/schema projection.
- `deployment/qnap/`: QNAP deployment, verification, backup, rollback, and acceptance assets for QNAP releases.
- `chatgpt/`: ChatGPT app contracts and package evidence.
- `config/`: governed capability and performance configuration.
- `specs/`: BDD behavior specifications.
- `tests/`: unit, integration, evaluation, security, scheduled-workflow, and production-readiness tests.
- `docs/`: architecture, material-turn, runbook, release, verification, security, and production-acceptance evidence.

## Verification

The v4.4.1 pull request must pass the repository's existing full CI plus the Commercial Operations regression suite. Core gates include:

```bash
python scripts/validate-contracts.py
python scripts/check-runtime-doc-drift.py
python scripts/check-chatgpt-packages.py
python scripts/check-owner-execution-readiness.py
python scripts/check-capability-closure.py
python scripts/check-published-action-surface.py
ruff check src
ruff check tests scripts --select E9,F63,F7,F82
mypy src --check-untyped-defs
pytest --cov=mesh_cos --cov-report=term-missing --cov-report=xml --cov-fail-under=100
bandit -q -r src -lll
pytest -q tests/evaluations/test_commercial_operations_orchestrator_v441.py
```

GitHub CI also retains the existing TypeScript/MCP, QNAP shell/security, container, packaging, and transport checks for repository regression protection. Passing those checks does not imply a new QNAP deployment.

## Release model

`v4.4.1` is a PATCH release because it corrects orchestration/control-plane behavior without changing the public MCP runtime contract or QNAP production binary. After the verified pull request is merged to `main`, the v4.4.1 release workflow creates the immutable semantic tag and GitHub Release from the merged main SHA.

No QNAP deployment is part of v4.4.1. If a future defect is proven to originate in runtime code rather than caller work-package construction, QNAP work requires a separately justified release and user-proxied operator steps.

## Historical release-train evidence

The `v4.4.0 Authority Closure` baseline and earlier v4.3.x evidence remain intentionally preserved. At the time of the v4.4.0 candidate, the historical statement was: **Current deployed QNAP release remains `v4.3.0`**. Historical v4.3.x documents remain retained as release-train evidence. These statements are preserved as historical evidence only; the current production QNAP deployment is 4.4.0.

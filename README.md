# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository candidate: `v4.4.0 Authority Closure`. Current deployed QNAP release remains `v4.3.0` until a human deployment is performed.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The release train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, event-triggered execution, Slack HITL, delegated owner execution, request contracts, transactional deployment recovery, backup integrity, and release evidence without widening the Phase 1 decision-rights model.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to authorized agents. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets remain interaction, evidence, or mirror surfaces. `COMPLETED` remains distinct from `VERIFIED`.

## v4.4.0 authority closure

v4.4.0 closes material authorization, delegation, provenance, and publication-attestation defects discovered during v4.3.x production acceptance work.

Key controls include:

- canonical TaskLedger approval resolution for L4/L5 operations;
- Michael-only canonical L5 approval actor;
- server-derived delegated owner identity;
- delegation-level `permitted_capabilities` intersection;
- bounded nested routes and task-local reads/writes;
- `mesh.cos.owner-execution.v2` with bounded legacy replay compatibility;
- durable success and denial receipts;
- explicit logical Skill-agent handoff provenance rather than a false claim of synchronous Workspace Agent execution;
- a 10-agent capability execution closure manifest;
- exact ChatGPT action + input-schema publication attestation;
- independent runtime contract, deployment release, source commit, and publication-schema digest provenance;
- release-neutral CI that builds the current v4.4.0 candidate rather than rebuilding historical releases.

The authority/execution architecture is documented in `docs/architecture-v4.4.0-authority-execution.md` and its Mermaid diagram was validated with the Mermaid Chart integration.

## Production ChatGPT topology

The published **Mesh CoS MCP** ChatGPT app remains the production ChatGPT surface. The currently deployed QNAP release remains **4.3.0** until a human deployment of v4.4.0 occurs, while the canonical MCP authority/runtime contract remains **4.0.0**.

The source CoS governed agent catalog contains **28 machine tools**, including `delegation.execute_owner`. Human-only `approval.record_decision` and `reliability.human_override` remain excluded from agent execution.

### Published action + schema gate

Source/runtime readiness and ChatGPT Workspace publication readiness are separate production gates. v4.4.0 extends the previous action-name gate to require exact equality of both **action names and input schemas**.

`python scripts/check-published-action-surface.py` without an actual Workspace snapshot reports `SOURCE_CONTRACT_ONLY`. It cannot establish production Workspace publication readiness. The administrator-provided action+schema snapshot must pass `--actual-file` before the Workspace gate can move to PASS.

The current expected CoS machine surface is exactly **28 actions** from a 30-operation catalog after excluding the two human-only tools.

### Runtime provenance

MCP response envelopes distinguish:

- `mcp_version` — canonical runtime contract;
- `deployment_release` — deployed release identity;
- `source_commit` — immutable source revision built into the container;
- `publication_schema_digest` — deterministic principal-specific action/input-schema digest.

These values must be evaluated independently. A matching runtime version alone is not proof of a matching deployment, source tree, or Workspace publication snapshot.

## Slack HITL

Governed Slack HITL continues to use the dedicated **ChatGPT Enterprise AI Agent** Slack bot for outbound approval notices and server-side provider reconciliation. New MK thread replies wake the ChatGPT-native event-triggered dispatcher. The trigger is not approval authority. Mesh CoS MCP rereads the exact Slack provider message and canonical TaskLedger state before a human decision can be recorded.

The provider-verified Slack App ID remains `A0B49RNE4K0`. QNAP does not own Slack event ingress and OpenAI Secure MCP Tunnel remains the only remote MCP ingress.

## Repository layout

- `src/mesh_cos/`: canonical Python operating core, governance runtime, delegated owner execution, Slack bot, and native-trigger reconciliation.
- `mcp/`: remote MCP transport and principal-specific tool/schema projection.
- `deployment/qnap/`: QNAP Container Station deployment, verification, backup, rollback, and acceptance assets.
- `chatgpt/`: published ChatGPT app contracts and package evidence.
- `config/capability-execution.v1.json`: declared execution-mode closure for every active agent capability/tool.
- `specs/`: ready BDD behavior specifications.
- `tests/`: unit, integration, evaluation, security, scheduled-workflow, and production-readiness tests.
- `docs/`: architecture, material-turn, release, verification, security, dispatcher, Skill-package, and acceptance evidence.

## v4.4.0 documentation

- `CHANGELOG-v4.4.0.md`
- `docs/material-turn-v4.4.0.md`
- `docs/architecture-v4.4.0-authority-execution.md`
- `docs/security-review-v4.4.0-authority-closure.md`
- `docs/runbook-v4.4.0-authority-execution.md`
- `docs/release-v4.4.0-authority-closure.md`
- `docs/chatgpt-published-app-production-acceptance-v4.4.0.md`
- `docs/skills-v4.4.0.md`
- `docs/verification-v4.4.0-authority-closure.md` after independent final-candidate verification

Historical v4.3.x documents remain retained as release-train evidence.

## Core verification commands

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
```

GitHub CI additionally runs TypeScript build/tests/security checks, QNAP POSIX shell regression tests, v4.4.0 QNAP and ChatGPT Skill artifact generation, a production-equivalent container build, modern MCP transport verification, and immutable source/checksum receipts.

## Manual gates

The following remain explicitly human-controlled when applicable and must never be inferred from source/CI success:

- semantic tag / GitHub Release;
- QNAP production deployment;
- ChatGPT Workspace custom-app refresh/recreation and publication;
- final exact action/input-schema snapshot attestation and live synthetic production acceptance.

Repository and release-candidate verification can be complete while these production/manual gates remain pending.
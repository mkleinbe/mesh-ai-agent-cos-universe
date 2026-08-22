# Operations Runbook

Current repository release target: **`v4.0.0 Chief of Staff Delegation Contract Remediation`**.

This runbook distinguishes repository readiness from target-environment activation. ChatGPT operation uses the bundled local stdio MCP. A separately deployed HTTPS MCP service is not required.

## Startup and activation path

1. Confirm the repository version, MCP package version, manifest release versions, and MCP contract all equal `4.0.0`.
2. Confirm `agents/registry.json` contains exactly 10 registered agents and only Mesh Devil's Advocate is externalized as a shared Skill.
3. Run the full release suite.
4. Run `ProductionPreflight` against the intended ledger and environment.
5. Confirm all 10 Workspace Agents use the same approved `MESH_COS_LEDGER_PATH` and their own immutable `MESH_COS_AGENT_ID`.
6. Confirm Workspace apps, connector restrictions, approval owners, secrets, Slack configuration, and source permissions in private preview.
7. Keep Workspace write policy at **Always ask** unless a narrower approved exception exists.

## Full release suite

```bash
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

## Authority checks

Before activation verify:

- no agent catalog contains `approval.record_decision` or `reliability.human_override`;
- the separately authenticated human path contains only the intended human tools;
- CoS is the only Phase 1 agent with `task.verify`;
- appropriate accountable owners have `task.complete`;
- Message Operations cannot record its own approval;
- Devil's Advocate is not an MCP principal;
- direct-child and delegation-depth restrictions are active.

## Task operation

Accountable owners progress work through normal lifecycle states. At QA, `task.complete` persists the outcome and evidence and transitions to `COMPLETED`. Completion without evidence fails. Duplicate completion does not silently mutate state.

A separate verifier evaluates the acceptance test. Passing `task.verify` requires explicit evidence. Phase 1 exposes that agent operation only to CoS. Failed verification routes to `REWORK`; passing routes to `VERIFIED`.

## Delegation operation

CoS delegates to registered direct children. COO may delegate to Consultant Network Steward at depth 2. The Steward is terminal. Authority widening, circular delegation, approval weakening, non-direct children, and depth-3 attempts fail closed.

## Incident controls

If the kill switch, ledger integrity, audit chain, identity binding, source authority, approval evidence, or MCP package is invalid, stop consequential execution. Do not improvise around a failed gate.

If a human-only operation appears in an agent catalog, treat it as a security defect and disable the affected agent until corrected.

If a completed task lacks evidence or a non-CoS agent reaches `VERIFIED`, treat it as a lifecycle/governance defect and preserve the audit trail for remediation.

## Historical state

Do not use the v3.0.0 9-agent topology as current deployment guidance. It remains a historical release snapshot and is superseded by v4.0.0.
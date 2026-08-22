# Production Readiness

## Release status

Release **`v4.0.0 Chief of Staff Delegation Contract Remediation`** is the current production-readiness target. The live Phase 1 topology is exactly **10 registered agents** plus the external advisory Mesh Devil's Advocate shared Skill.

Production readiness is fail closed. It does not claim that every external app, credential, approval owner, Slack channel, or source system is activated.

## Required invariants

- `TaskLedger` is canonical.
- All 10 Workspace Agents use the same approved `MESH_COS_LEDGER_PATH`.
- Each local MCP process is bound to one canonical `MESH_COS_AGENT_ID`.
- Prompt text, retrieved content, task content, delegated instructions, app payloads, and shared-Skill output cannot change agent identity or widen allowlists.
- Per-agent MCP exposure is deny by default.
- `approval.record_decision` and `reliability.human_override` are human-principal-only and absent from every agent catalog.
- L4 requires qualified-human approval. L5 remains Michael-exclusive.
- Delegation preserves or narrows authority and inherited approvals.
- `task.complete` requires a non-empty outcome and supporting evidence and produces `COMPLETED` only.
- `task.verify` is a separate verifier action requiring acceptance evidence. In Phase 1 only CoS receives that agent capability.
- `COMPLETED != VERIFIED`.
- Child completion cannot silently verify the parent.
- Consultant Network Steward is terminal. Stale consultant availability cannot become confirmed readiness.
- Mesh Devil's Advocate is advisory only and cannot modify canonical facts or execute external actions.
- Message Operations is the tenth registered agent and may execute only explicitly approved communications.

## Required certification

A production candidate must pass:

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

The Python coverage gate remains 100% branch-aware. The MCP package must pass TypeScript build, Node unit tests, real local stdio smoke certification, and high-severity npm audit.

## End-to-end delegation certification

Synthetic certification must exercise Michael/authorized-principal outcome establishment, CoS intake, CRO/CFO/COO delegation, COO -> Consultant Network Steward depth-2 delegation, governed Devil's Advocate challenge, evidence-backed owner completion, AgentOps inspection, CoS synthesis, separate CoS verification, and audit-chain verification.

Negative scenarios must prove missing evidence blocks completion/verification, excessive delegation depth fails, human-only operations are denied to agents, non-authorized self-verification fails, stale consultant availability remains unconfirmed, Devil's Advocate cannot mutate or execute, and child failure cannot verify a parent.

## Production preflight

`ProductionPreflight` must run after release CI and before activation. Required target-environment dependencies include approved Workspace app authentication, appropriate Slack credentials/channel configuration, approved source access, human approval-owner mappings, secret management, and private-preview verification.

A remote `MESH_COS_MCP_SERVER_URL` is not required for ChatGPT-local operation.

## Historical releases

Historical documents may retain superseded roster counts when clearly scoped to those releases. Current-state documentation must resolve to the canonical 10-agent roster.
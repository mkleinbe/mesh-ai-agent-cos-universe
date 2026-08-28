# Operations Runbook

Candidate repository/QNAP deployment release: **`v4.3.0 Cross-Agent Owner Execution`**.  
Canonical Phase 1 authority/runtime contract: **`4.0.0`**.

This runbook distinguishes repository readiness, QNAP deployment readiness, published ChatGPT app acceptance, delegated-owner execution, and production recovery.

## Repository certification path

1. Confirm the Python package and canonical MCP authority/runtime contract remain `4.0.0`.
2. Confirm `agents/registry.json` contains exactly 10 registered agents and Mesh Devil's Advocate remains the only external shared Skill.
3. Confirm the candidate deployment train is `4.3.0` across current release assets.
4. Confirm CoS has 28 governed agent tools, including `delegation.execute_owner`, and no agent catalog contains human-only operations.
5. Run the full release suite.
6. Require `OWNER_EXECUTION_READINESS=PASS` for every current downstream owner.
7. Confirm the direct-report registry matrix and both permitted nested delegation paths pass.
8. Confirm scheduled cross-agent execution passes under owner identity.
9. Confirm release-image provenance and governed response-envelope verification gates remain present.

## Full release suite

```bash
python -m pip check
cd mcp && npm ci && npm run check && cd ..
python scripts/validate-contracts.py
python scripts/check-runtime-doc-drift.py
python scripts/check-chatgpt-packages.py
python scripts/check-owner-execution-readiness.py
ruff check src
ruff check tests scripts --select E9,F63,F7,F82
mypy src --check-untyped-defs
pytest --cov=mesh_cos --cov-report=term-missing --cov-report=xml --cov-fail-under=100
bandit -q -r src -lll
python -m compileall -q src
bash scripts/build-qnap-release-bundle.sh 4.3.0
```

Repository CI additionally exercises the production image, OCI provenance, QNAP POSIX regressions, deterministic bundle/checksum, modern MCP discovery, sequential requests, least-privilege runtime controls, and SQLite backup/restart recovery.

## Delegated-owner operation

For delegated work, the parent orchestrator does not directly perform child lifecycle writes.

Normal sequence:

```text
parent owns parent task
-> parent creates/resumes child task
-> delegation.create validates canonical graph and owner readiness
-> owner route becomes OWNER_ROUTABLE
-> parent calls delegation.execute_owner
-> runtime derives canonical owner
-> owner-specific policy authorizes the requested operation
-> owner executes under owner identity
-> canonical result returns to parent
```

At QA:

```text
delegation.execute_owner(task.complete)
-> canonical owner executes completion
-> COMPLETED
-> parent observes result
-> separate authorized task.verify where required
```

Do not call `task.complete` directly as CoS for a child-owned task.

## Nested delegation operation

Current registry permits:

```text
cos -> cmo -> vp-content
cos -> coo -> consultant-network-steward
```

The functional executive creates the specialist child/delegation under its own derived owner execution context. Specialist execution then uses the same server-owned transport. After specialist completion, the result is available to the functional executive, which completes its own accountable outcome separately.

A terminal specialist cannot delegate further.

## Scheduled execution

A scheduled occurrence must use a deterministic intake idempotency key. The scheduler/CoS runtime acts as trigger and orchestrator only.

When a functional child owns work:

1. intake/resume the canonical scheduled parent;
2. create/resume the child and delegation;
3. use `delegation.execute_owner` for owner transitions, check-ins, Skills, nested delegation, and completion as permitted;
4. retry only with the same request-bound idempotency semantics;
5. observe the owner result;
6. verify separately where authorized;
7. release dependencies only from canonical state.

Do not replace delegated execution with direct `runtime.call_agent` test-only behavior or CoS child writes.

## Owner-routing incident handling

If delegated work cannot execute, inspect `owner_routing_failure`, `owner_execution_route`, and `owner_execution` records.

Capture:

- canonical task;
- parent task;
- delegation;
- orchestrator;
- accountable owner;
- expected execution principal;
- actual execution principal if any;
- task state;
- attempted operation;
- authorization result;
- failure classification;
- retry eligibility;
- remediation path.

Common classifications include owner runtime unavailable, owner execution transport unavailable, disabled/quarantined owner, invalid delegation, identity mismatch, authorization denial, invalid state, capability failure, and idempotency conflict.

Never substitute another agent identity to clear a routing failure.

## Idempotent retry

Reuse an owner execution idempotency key only for the exact same delegation, task, operation, and validated arguments. A successful retry returns the prior canonical response.

If an execution failed after the at-most-once claim and the effect may be ambiguous, do not blindly replay it. Use governed remediation to determine whether retry is safe.

## QNAP deployment path

1. Stage the authorized `mesh-cos-mcp-qnap-v4.3.0.zip` and checksum under the canonical releases root workflow.
2. Follow `deployment/qnap/DEPLOYMENT-STEPS.md`.
3. Preserve `/share/Docker/cos-mcp/state`, TaskLedger, tunnel identity, protected Slack configuration, logs, and backups.
4. Require pre-deploy SQLite backup integrity.
5. Require candidate release metadata to match image OCI version/revision labels.
6. Require Compose rendering, health/readiness, owner-execution readiness, modern MCP verification, ingress controls, and post-deploy backup.
7. Require status identity:

```text
mcp_version: 4.0.0
deployment_release: 4.3.0
agent_id: cos
transport: SECURE_MCP_TUNNEL
```

Production deployment remains a human-authorized operation.

## Published ChatGPT app acceptance

After local QNAP verification:

1. refresh the installed **Mesh CoS MCP** app;
2. scan tools and require 28 CoS agent tools;
3. confirm human-only operations are absent from the agent catalog;
4. run sequential read-only acceptance without restarting containers;
5. require exactly 10 registered agents;
6. require correct dual release identity;
7. execute one non-consequential delegated-owner validation per eligible functional owner;
8. validate nested paths with synthetic/non-consequential work;
9. validate scheduled cross-agent routing;
10. require valid audit attribution and no impersonation.

Do not use publishing, sending, pricing, staffing, contractual commitment, or other consequential action merely to test transport.

## Production recovery inventory

Before recovering PF-057 work, query canonical TaskLedger for:

- delegated tasks in QA awaiting owner completion;
- unresolved owner-completion/transport failures;
- delegated tasks stalled after successful execution;
- dependencies held open by incomplete delegated predecessors;
- repeated scheduled occurrences returning the same blocked task;
- tasks whose accountable owner differs from the orchestrating runtime and lack a completed owner route.

Do not recreate these tasks by default.

For `task-b0b613daff51`:

```text
existing QA state
-> derive/validate canonical cmo owner route
-> execute task.complete under cmo authority
-> COMPLETED
-> separate verification if required
-> dependency release
```

Recheck the task immediately before recovery. If canonical state changed, stop and reconcile rather than applying stale recovery instructions.

## Authority checks

Before activation or acceptance verify:

- no agent catalog contains human-only operations;
- CoS remains the only Phase 1 agent with `task.verify`;
- accountable owners have their required lifecycle surface;
- `delegation.execute_owner` is available only to registry parents that can delegate;
- target owner capabilities remain role-specific;
- approval inheritance is intact;
- Message Operations cannot record its own approval;
- Devil's Advocate is not an MCP principal;
- direct-child and registry-derived delegation depth restrictions are active;
- prompts/retrieved/model output cannot select identity;
- deployment metadata cannot affect authority.

## Rollback

Rollback restores the prior authorized immutable release and preserves canonical TaskLedger state. Software rollback must not delete or recreate canonical work.

If v4.3.0 is rolled back before stranded work is recovered, leave those tasks in their existing state. Resume them only after a corrected owner transport is again deployed and authorized.

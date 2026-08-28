# Release v4.3.0: Cross-Agent Owner Execution

## Release identity

- Deployment release: `4.3.0`
- Canonical MCP authority/runtime contract: `4.0.0`
- Production predecessor: `4.2.3`
- Workforce: 10 registered agents
- CoS governed agent tool surface: 28 tools
- New governed tool: `delegation.execute_owner`
- Security classification: `FULL_REVIEW`

## Objective

Repair PF-057 systemically so delegated canonical work can execute and complete under the accountable owner's identity without allowing parent/child impersonation, arbitrary principal selection, approval bypass, duplicate execution, or completion/verification conflation.

## SemVer rationale

This is a minor deployment release rather than a patch because the release adds a new governed MCP operation and a new closed-loop delegation/execution protocol. It is not a major authority-contract release because the 10-agent roster, decision-rights model, L4/L5 human authority, TaskLedger canonical state, and existing functional authority boundaries remain intact.

## Corrected execution flow

```text
scheduler / parent trigger
-> canonical task/delegation
-> server derives accountable owner
-> owner MCP policy authorization
-> owner-scoped execution
-> task.complete under owner identity
-> canonical result returned to parent
-> separate verification where authorized
```

## Release gates

The exact candidate commit must pass:

- npm build/test/smoke/security audit;
- Python dependency integrity;
- contract and package drift checks;
- owner execution readiness checker;
- Ruff and mypy;
- 100% branch-aware Python coverage;
- Bandit and compileall;
- direct-report registry matrix;
- nested CMO/VP Content and COO/Consultant Network Steward scenarios;
- scheduled cross-agent execution;
- approval and identity negative scenarios;
- QNAP POSIX regressions;
- deterministic v4.3.0 archive/checksum;
- OCI release version/revision provenance;
- modern MCP discovery and sequential request verification;
- independent final diff review for authority expansion.

## Production validation

After human-authorized deployment, use only non-consequential synthetic delegated tasks to validate one representative owner path per eligible functional owner, then both nested paths. Do not publish, send, price, contract, staff, or make another consequential commitment merely to validate transport.

## Recovery

After production transport validation, inventory all canonical tasks potentially stranded by PF-057 and resume eligible tasks in place. Do not recreate them by default.

`task-b0b613daff51` recovery remains:

```text
existing QA task
-> canonical owner cmo
-> governed owner completion
-> COMPLETED
-> separate verification where required
-> dependent gate release
```

## Rollback

Rollback restores the complete prior immutable release and preserves TaskLedger state. Do not delete or rewrite canonical tasks during software rollback. If v4.3.0 is rolled back before PF-057 recovery, leave blocked tasks untouched until a corrected transport is re-authorized.

## Human actions still required

- approve merge/release according to repository governance;
- deploy the authorized immutable v4.3.0 candidate to QNAP;
- execute production acceptance;
- authorize recovery of stranded canonical work after acceptance evidence is green.

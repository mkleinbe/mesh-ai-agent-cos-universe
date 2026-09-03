# Security Review v4.4.2: Data Intelligence Orchestration

## Disposition
**TARGETED REVIEW: PASS for repository and canonical control-plane release.** Live external scheduler activation remains a distinct provider-state gate and cannot be inferred from repository or Sheet state.

The QNAP Mesh CoS MCP 4.4.0 runtime is unchanged. This release changes orchestration contracts, documentation, TaskLedger operating controls, recovery behavior, reporting, tests, and release automation only.

## Threat boundary
The work touches MCP delegation, persistent task/audit state, Google Sheets, schedule transport, source evidence, and potential future external actions. Prompt text, Sheet cells, connector output, Skills, Slack content, and model output are untrusted data, not authority.

## Controls reviewed
### Identity and delegation
- Execution principal is server-derived.
- CoS delegates only to registered direct children.
- VP Content is reached only through CMO.
- Exactly 10 ACTIVE agents and canonical parentage remain required.
- Caller depth, ancestry, active owner, and parent authority are assertions only.
- Caller actions/capabilities cannot exceed registry allowlists.

### Dependency integrity
- Canonical dependencies are hard task-ID work-graph edges.
- Narrative prerequisites are prohibited from dependency arrays.
- Runtime continues to fail closed for unresolved or unverified predecessors.
- Recovery does not weaken this gate.

### Replay and idempotency
- Immutable occurrence keys are reused.
- Passed lifecycle states and terminal work are not replayed.
- Original malformed tasks remain in audit history.
- Exactly one deterministic clean successor is permitted.
- Provider effects, cell writes, approvals, and external actions are never replayed as metadata recovery.

### Data authority and integrity
- Revenue Intelligence remains authoritative for prospect/account commercial truth.
- CMO, VP Content, and LinkedIn Authority OS cannot create account intent, budget, sponsor, urgency, fit, lifecycle, priority, stage, or activation readiness.
- Monthly decay write path remains exact single-cell pre-read, write, readback, and row reconciliation.
- Ambiguous material entity/state decisions require Human Review.
- Apollo credit budget remains 0.

### External action
- External action is NOT_AUTHORIZED by default.
- Slack text is not canonical human approval.
- Exact approval, payload fingerprint, provider state, replay protection, audit state, and kill switch remain mandatory for consequential action.
- This release performs no outreach, LinkedIn action, CRM write, publication, pricing, scope, staffing, or commitment.

### Failure containment
- Runtime or audit failure blocks affected canonical mutation.
- Source or connector failure blocks only dependent jobs.
- Prospect write/reconciliation failure stops current full-universe transaction and preserves prior reconciled rows.
- Scheduler unavailability blocks autonomous wake activation, not verified repository or canonical runtime work.
- Scoped defects remain visible and do not freeze unrelated eligible work.

## Rejected unsafe alternatives
- Accept arbitrary text as a canonical dependency.
- Grant caller-invented delegation actions.
- Treat Sheet readback as canonical verification.
- Mark the September full-universe review successful because recovery controls passed.
- Batch prospect writes merely to make the monthly job faster.
- Retry a connector-blocked cell through a different method.
- Use LinkedIn authority or engagement context as buyer/account truth.
- Restart or redeploy QNAP without a proven runtime defect.

## Residual risks
- External scheduler is a separate provider surface and requires live enabled-state/schedule readback.
- A complete monthly review can be long-running because the authorized contract is single-cell and full-universe.
- Source freshness and connector safety can produce legitimate partial outcomes.
- Human Review volume can rise when entity/taxonomy evidence is ambiguous.

No security control was weakened to obtain a green test result.

# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository release candidate: `v4.4.2 Data Intelligence Orchestration`. Current production QNAP deployment: `4.4.0`. Canonical Phase 1 authority/runtime contract: `4.0.0`.**

v4.4.2 is an orchestration and operating-control patch. It does not modify or redeploy the healthy QNAP Mesh CoS MCP runtime.

## Canonical architecture
Phase 1 contains exactly 10 registered agents: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations. Mesh Devil's Advocate remains a governed shared Skill, not an eleventh agent.

Mesh CoS MCP TaskLedger is canonical for task ownership, delegation, approval, completion, verification, and audit. Google TaskLedger, Prospect Universe, Slack, Gmail, connectors, Workspace state, and conversation history are scheduling, interaction, evidence, or mirror surfaces. `COMPLETED` remains distinct from `VERIFIED`.

## v4.4.2 Data Intelligence correction
The September 2026 Data Intelligence incident was caused by caller-created work packages placing narrative source, lock, connector, and Skill prerequisites in canonical dependency arrays. Mesh CoS MCP 4.4.0 correctly treated those values as predecessor task IDs and failed closed. A caller attempt to provide friendly delegation action labels was also correctly denied because the labels exceeded the CRO registry allowlist.

v4.4.2 fixes the orchestration boundary instead of weakening the runtime: canonical dependencies contain only real predecessor task IDs; narrative prerequisites move to contracts/evidence; omitted delegation actions inherit the canonical owner allowlist; CoS orchestrates and verifies; CRO owns governed Data Intelligence execution; Revenue Intelligence remains authoritative for prospect/account commercial truth; CMO owns executive and authority-context framing and delegates production to VP Content; AgentOps independently evaluates reliability; LinkedIn Authority OS remains context only; deterministic defects are isolated with one clean successor and no provider replay; business outcome and technical health are separate; and the full-universe single-cell/Apollo-0 write contract remains intact.

Detailed release material:
- `docs/data-intelligence-orchestrator-v4.4.2.md`
- `docs/architecture-v4.4.2-data-intelligence.md`
- `docs/runbook-v4.4.2-data-intelligence.md`
- `docs/security-review-v4.4.2-data-intelligence.md`
- `docs/release-v4.4.2-data-intelligence.md`

## Production runtime and authority boundaries
The QNAP Mesh CoS MCP 4.4.0 deployment remains production. Key invariants remain server-derived identity, exactly 10 registered agents, deny-by-default authority, `mesh.cos.owner-execution.v2`, human-only operations excluded from agent surfaces, Revenue Intelligence account-level commercial truth, exact canonical approval for consequential external action, no autonomous publication/email/LinkedIn/pricing/scope/staffing/commitment, OpenAI Secure MCP Tunnel remote ingress, and operator-proxied QNAP changes.

## Verification
The v4.4.2 pull request must pass the repository's full Python, TypeScript/MCP, contract, security, packaging, QNAP shell, container, and transport CI plus the Data Intelligence regression suite. Passing repository CI does not itself prove the external monthly Scheduled Task is enabled. Production automation requires live provider readback of the existing automation ID, schedule, timezone, and prompt.

## Release model
`v4.4.2` is a PATCH release because it corrects caller, recovery, reporting, and control-plane behavior without changing the public MCP runtime contract or QNAP binary. After verified merge to `main`, the release workflow creates semantic tag `v4.4.2` and the immutable GitHub Release from that exact main SHA.

## Historical release train
`v4.4.1 Commercial Operations Orchestration` remains the prior repository release. `v4.4.0 Authority Closure` and earlier evidence remain preserved for audit and regression continuity.

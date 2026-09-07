# v4.7.0 Enterprise Consulting Skill Consumption

## Release intent

Integrate the released Mesh enterprise consulting capability enhancements into the canonical ten-agent operating model through bounded role guidance, without changing machine-readable agent authority or production runtime permissions.

## Shipped

- Chief of Staff guidance for Mesh PPMD Bot v1.1+ falsification-first hypotheses, decision-linked synthesis, governed decision memos, outcome-first meetings, and artifact-first workshops.
- CRO guidance for Revenue Intelligence v1.4+, Firm 360 v1.5+, Competitive Displacement v1.14+, GTM Orchestrator v2.3+, Buyer Psychology v3.1+, and Devil's Advocate v1.4+.
- CFO guidance for supplying evidence-bound financial inputs, risks, mitigations, sensitivities, reversal conditions, and next tests to executive decision packages without gaining a new Skill binding.
- COO guidance for artifact-first workshop and outcome-first meeting contributions without gaining a new Skill binding or staffing authority.
- CMO guidance for the existing Executive Communications binding to consume Mesh Messaging v1.2+ decision memos and for design-critic findings to remain subordinate to Mesh design authority.
- Answer & Decision Desk guidance preventing draft hypotheses, syntheses, memos, workshop artifacts, or critic findings from becoming policy or approval.
- BDD behavior specification and executable regression coverage proving skill capability is not agent authority.
- Mermaid architecture, security review, compatibility map, and verification contract.

## Preserved

- exactly 10 registered agents;
- canonical parentage;
- machine-readable direct Skill bindings and shared-capability set;
- L0-L5 decision authority;
- TaskLedger ownership and state semantics;
- `COMPLETED` versus `VERIFIED` separation;
- Revenue Intelligence canonical commercial and stakeholder truth;
- CFO supported financial authority boundary;
- COO delivery-feasibility authority boundary;
- CMO publication approval boundary;
- Message Operations as controlled approved-communications execution;
- human-only consequential approval paths;
- no autonomous public publishing, outreach, pricing/scope commitment, staffing commitment, proposal submission, or external send.

## Compatibility

- Repository capability release: `v4.7.0`
- Canonical Phase 1 authority/runtime contract: `4.0.0`, unchanged
- CFO implementation: `1.2.0`, unchanged
- Production QNAP deployment: `4.4.0`, unchanged
- New MCP tool: none
- New schema migration: none
- New credential: none
- New connector: none
- QNAP deployment/restart: none

## Security

Security applicability is `FULL_REVIEW`. Donor concepts are treated as untrusted method input. The release explicitly blocks donor-instruction override, authority confusion, unsupported stakeholder intent inference, hypothesis-to-fact promotion, memo self-approval, workshop/meeting commitment creep, critic-to-publication authority transfer, autonomous communication, and completion/verification collapse.

No critical or high security finding is accepted for release. No executable donor code or third-party dependency is added to the agent repository.

## Release gate

The exact final candidate and exact merged `main` commit must pass the repository's full CI, including contract validation, runtime/package drift controls, capability/action-surface controls, lint/type checks, 100% branch-aware coverage, Bandit, TypeScript/MCP checks, existing CFO regressions, Phase 1 role-model consistency, and `tests/evaluations/test_enterprise_consulting_skill_consumption_v470.py`.

Release publication must target the exact final `main` SHA under semantic tag `v4.7.0`.

## Rollback

Revert the v4.7.0 role-guidance commit and return the repository release pointer to v4.6.0. No QNAP rollback, database migration, credential rotation, or runtime restart is required because v4.7.0 does not change the deployed runtime or machine-readable registry.

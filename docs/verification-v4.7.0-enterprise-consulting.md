# v4.7.0 Enterprise Consulting Skill Verification

## Verification objective

Prove independently that the enhanced consulting-method consumption changes agent guidance only and preserves the canonical ten-agent authority model, machine-readable Skill bindings, TaskLedger semantics, approval boundaries, source ownership, and external-action controls.

## Acceptance evidence

### Functional and governance

- `specs/enterprise-consulting-skill-consumption-v4.7.0.feature` covers positive and negative behavior.
- `tests/evaluations/test_enterprise_consulting_skill_consumption_v470.py` proves roster, direct Skill arrays, shared-capability set, decision-authority strings, method guidance, stakeholder unknown state, financial/delivery boundaries, design authority, Answer Desk routing, and no capability-to-authority transitivity.
- Existing `tests/evaluations/test_phase1_role_model_consistency.py` must remain green without modification.

### Security

- full repository Bandit gate;
- published action-surface validation;
- owner-execution readiness and capability-closure checks;
- ChatGPT package drift validation;
- v4.7.0 security review tied to the exact candidate;
- no new package dependency, secret, connector, network path, MCP tool, database schema, or external-action implementation.

### Runtime compatibility

- canonical Phase 1 runtime stays `4.0.0`;
- production QNAP stays `4.4.0`;
- agent registry remains exactly ten agents;
- machine-readable direct Skill arrays remain unchanged;
- CFO remains implementation `1.2.0`;
- no QNAP deployment is required.

## Independent verification rule

Implementation evidence is not verification evidence. The final PR head must pass the full repository CI. After merge, the exact `main` SHA must pass the v4.7.0 release workflow before semantic tag and GitHub Release publication.

A release is not complete if the tag points to another SHA, the workflow is not green, the repository release pointer remains stale, or the marketplace references unreleased versions.

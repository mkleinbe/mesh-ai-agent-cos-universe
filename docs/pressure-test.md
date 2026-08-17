# Pre-PR Pressure Test

Independent challenge performed before PR:
- Not a chatbot: work centers on task records, contracts, authority and verification.
- CoS does not replace functional truth: domain authority is explicit and tested.
- Failed delegated work remains visible through lifecycle/check-ins; no fire-and-forget path.
- Authority cannot widen through delegation; L4/L5 fail closed.
- Slack is explicitly non-canonical and duplicate events are idempotent.
- Duplicate active ownership and circular/deep delegation are rejected.
- Coordination loops are detectable.
- COMPLETED differs from VERIFIED; evidence is required for verification.
- Escalation uses a decision brief format rather than forwarding debate.
- Performance scoring produces AgentOps health recommendations including WATCH and QUARANTINE.
- Answer Desk source classes are permission-gated.
- Retrieved content cannot alter operating policy.
- Approval records bind actor, action, owner, status and decision time.
- Phase 1 intentionally avoids brokers, microservices, dashboards and autonomous agent creation.

Material issues found during challenge and fixed before PR: verification originally mutated task state before evidence validation; corrected to fail before state mutation. Performance routing was adjusted so repeated moderate QA rejection first produces WATCH, while critical defects still quarantine immediately.

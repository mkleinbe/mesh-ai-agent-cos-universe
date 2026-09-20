# ChatGPT Skill Package v4.12.1

This PATCH release packages the one ChatGPT Skill materially changed by the CoS delegation and agent-reporting remediation:

1. `mesh-chief-of-staff`

The package teaches the canonical agent communications contract:

- create bounded agent delegation against canonical child work;
- omit server-derived `parent_authority`, `depth`, `ancestry`, and `active_owner` unless intentionally asserting drift;
- execute agent-owned work through `delegation.execute_owner`;
- never represent an agent principal as a Skill capability;
- reconcile returned child results to the parent through an explicit CoS check-in;
- keep completion separate from verification and preserve all L4/L5 approval boundaries.

No Commercial Growth OS decision logic, Phase 1 roster, authority level, or external-action authority changes.

Installation remains human controlled. A GitHub Release does not update the live ChatGPT Skill runtime or promote the QNAP MCP deployment.

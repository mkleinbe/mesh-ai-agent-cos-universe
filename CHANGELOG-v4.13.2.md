# v4.13.2

## Fixed

- Corrected QNAP release-asset identity so current source is published under a distinct deployment patch instead of reusing the `4.4.0` artifact name.
- Added commit-qualified local image tags and forced candidate container recreation.
- Added fail-closed verification that release metadata, running image OCI revision, and governed MCP `source_commit` are identical.
- Added source-identity BDD/regression evidence and updated QNAP operator/acceptance documentation.

## Unchanged

- Canonical MCP contract: `4.0.0`.
- Registered agent count: exactly 10.
- TaskLedger authority and L4/L5 human approval boundaries.
- Slack peer-HITL behavior introduced in v4.13.0.

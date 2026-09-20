# Changelog v4.12.1

## Fixed

- Removed required caller ownership of server-derived `parent_authority` and `depth` assertions from `delegation.create`.
- Added safe machine-readable delegation reason codes.
- Added explicit `unsupported-capability-type` handling when an agent principal is passed to `skills.invoke_governed`.
- Clarified the canonical CoS -> delegation -> owner execution -> parent reconciliation -> independent verification operating contract.

## Verification

- Added ready BDD scenarios CDR-001 through CDR-010.
- Added full CoS/CRO round-trip evaluation coverage.
- Added Python and Node error-contract regression tests.
- Preserved full repository, security, QNAP, provenance, and owner-execution gates.

## Governance

No agent, authority, approval, source-of-truth, external-action, Commercial Growth OS, or Phase 1 topology change.

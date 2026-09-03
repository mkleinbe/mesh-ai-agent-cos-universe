# Changelog v4.4.1

## 2026-09-03

### Commercial Operations orchestration correction

- Corrected the Commercial Operations caller contract so canonical task dependencies contain only real predecessor task IDs.
- Moved narrative prerequisites, evidence requirements, provider conditions, and source labels to the appropriate job contract, acceptance, constraint, trigger, or evidence fields.
- Added a bounded recovery rule for legacy malformed child work: preserve the failed child and audit history, then create one deterministic dependency-clean successor under the same parent, owner, authority, acceptance boundary, and approval gates.
- Restored the central Commercial Operations Scheduled Task to its TaskLedger-declared weekday 08:00, 10:00, 12:00, and 16:00 ET schedule.
- Added business-outcome-first executive reporting that separates business disposition from technical health and keeps scoped defects scoped.
- Formalized CMO and VP Content integration for authority-building context without transferring Revenue Intelligence commercial-truth authority.

### Production evidence

- Recovered the malformed Gmail-response and banking-intelligence CRO occurrences on the existing Mesh CoS MCP 4.4.0 deployment with no QNAP runtime change and no provider side-effect replay.
- Verified direct CoS-to-CMO and nested CMO-to-VP Content owner execution for the reengineered commercial operating model.
- Confirmed the live 4.4.0 Mesh CoS MCP remains the healthy production runtime and requires no deployment for this correction.

### Security and authority

- No MCP tool, schema, runtime code, QNAP container, network boundary, secret handling, human-approval boundary, or external-action authority changes.
- Revenue Intelligence remains the sole account-level commercial-truth authority.
- External action remains NOT_AUTHORIZED except through existing exact canonical approval paths.
- Completion and verification remain separate.

# v4.13.1 QNAP Operator Documentation Alignment

v4.13.1 is a PATCH release over v4.13.0. Runtime Slack HITL behavior is unchanged.

## Corrected

- QNAP operator release identity is consistently 4.4.0 across deployment steps, README, install/upgrade checklists, ChatGPT acceptance, and environment example.
- packaged commands now reference `mesh-cos-mcp-qnap-v4.4.0.zip`, extracted `v4.4.0/`, and the current 4.4.0 image/release identity.
- current production acceptance references the existing v4.4.0 published-app acceptance procedure.

## Preserved

- repository Slack HITL behavior from v4.13.0;
- canonical MCP authority/runtime contract 4.0.0;
- QNAP deployment identity 4.4.0;
- exact bot-versus-human authority separation;
- TaskLedger canonicality, replay controls, and completion-versus-verification separation.

## Verification

The patch must pass the full repository CI, 100% Python coverage, security gates, QNAP shell regressions, and exact-current-source QNAP 4.4.0 candidate build before release publication.

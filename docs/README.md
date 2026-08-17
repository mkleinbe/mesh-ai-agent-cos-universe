# Documentation Index

This directory documents the Phase 1 Mesh AI Chief of Staff operating core.

## Canonical specification

- `phase-1-operating-contract.md`: canonical human-readable Phase 1 operating contract

## Architecture and decision records

- `architecture.md`: architecture, agent hierarchy, lifecycle, escalation, Slack/ledger relationship, and pursuit example
- `adr/ADR-001-runtime.md`: runtime and implementation language
- `adr/ADR-002-task-ledger.md`: canonical ledger and persistence
- `adr/ADR-003-agent-communication.md`: structured agent-to-agent communication
- `adr/ADR-004-slack-identity.md`: Slack identity strategy
- `adr/ADR-005-approval-model.md`: approval and consequential external-action model

## Governance and operating controls

- `decision-rights.md`: L0-L5 authority model
- `delegation-model.md`: delegation contracts and depth rules
- `task-lifecycle.md`: task states and valid outcome lifecycle
- `agent-registry.md`: canonical agent definitions and health states
- `agent-performance.md`: performance scorecard and AgentOps recommendations
- `conflict-resolution.md`: functional truth and cross-functional arbitration
- `escalation-policy.md`: CoS versus Michael escalation rules
- `security-governance.md`: least privilege, provenance, prompt-injection, approvals, and kill-switch controls
- `observability.md`: auditability and operational telemetry

## Collaboration interfaces

- `slack-agent-protocol.md`: private agent-operations Slack protocol
- `answer-desk.md`: team-facing Answer Desk behavior and access controls

## Verification and operations

- `testing-evaluation.md`: test layers, local release verification, and 13 required evaluation scenarios
- `runbook.md`: startup, validation, incident response, quarantine, restoration, and controlled shutdown
- `pressure-test.md`: pre-PR independent challenge and corrected defects

## Supporting repository material

- `../contracts/`: versioned machine-readable schemas, examples, and compatibility policy
- `../agents/`: human-readable agent role definitions and canonical registry
- `../src/mesh_cos/`: Phase 1 implementation
- `../tests/`: contract, unit, integration, and evaluation tests
- `../CHANGELOG.md`: release history

## Documentation rule

Architecture, authority, agent scope, or operating-policy changes must update the corresponding documentation in the same change. Documentation is part of the deliverable, not post-release cleanup.

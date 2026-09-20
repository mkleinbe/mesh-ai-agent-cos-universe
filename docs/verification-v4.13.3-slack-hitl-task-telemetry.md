# Verification: v4.13.3 Slack HITL Task Telemetry

Independent verification must prove the implementation, not only the documentation.

## Behavior evidence

HITL-TELEM-001 through HITL-TELEM-010 cover:

- provider-confirmed canonical task/thread binding;
- verified DONE count 0 to 1;
- exact provider replay remains 1 with no second acknowledgment;
- a second distinct verified reply counts once more;
- bot acknowledgment does not count;
- wrong-user, app/bot, edited, unbound, and invalid state do not count;
- nonapproval APPROVE remains non-authoritative;
- strict approval remains independent of human-touch telemetry;
- task lifecycle remains unchanged by telemetry;
- task.get returns canonical persisted values.

## Required gates

- full Python test suite at the repository coverage threshold;
- Slack peer-HITL and approval regression suites;
- TaskLedger and task.get serialization;
- replay/idempotency;
- governance audit-chain tests;
- Ruff, mypy, Bandit;
- contract/runtime documentation drift checks;
- QNAP shell and source-identity regression checks;
- production-equivalent QNAP 4.4.2 bundle/image build.

## Release boundary

PASS in CI verifies the repository candidate. Production remains unverified until QNAP reports deployment_release=4.4.2 and source_commit equal to the final release commit, followed by the fresh dispatcher-only production UAT.

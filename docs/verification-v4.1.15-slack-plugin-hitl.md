# v4.1.15 Verification Record

Status: PENDING INDEPENDENT VERIFICATION

## Behavior traceability

- QNAP-104: connected Slack collaboration does not create approval authority.
- QNAP-105: provider-authenticated `/mesh-approval` from configured MK records canonical decision with immutable fingerprint.
- QNAP-106: ordinary message, wrong identity/route, and replay/conflict fail closed.
- QNAP-107: Slack provider/network outage does not terminate MCP HTTP process; readiness remains fail-closed and reconnect is bounded.
- QNAP-108: QNAP runtime has no verifier bot token dependency.
- QNAP-109: Docker Engine 27 network topology has deterministic MCP and tunnel egress without unsupported gateway-priority features.
- QNAP-110: failed candidate activation/health is rolled back before release promotion.

## Required independent evidence

- Python unit/integration/evaluation suite and 100% coverage.
- TypeScript build/type/test suite.
- Ruff, mypy, Bandit, compileall, pip check, npm lockfile install/check.
- QNAP POSIX shell syntax and regression suite.
- Contract/package/document drift checks.
- Exact v4.1.15 release bundle and SHA-256 verification.
- Production container build from exact bundle, OCI version/revision labels bound to candidate SHA.
- Modern MCP discovery and sequential request regression.
- Release-archive inspection for protected secret/state exclusion and current contract inclusion.
- Diff review for obsolete verifier/bot-author active dependencies, debug debris, temporary files, credential leakage, and authority widening.

This record must not be marked PASS until the exact candidate SHA satisfies every required check. Live QNAP and Slack production acceptance remains a separate post-release deployment gate.

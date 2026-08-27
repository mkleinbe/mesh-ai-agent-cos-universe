# QNAP Security Review: v4.1.14

## Applicability

TARGETED. The change touches protected Slack credentials, privileged QNAP shell execution, deployment/runtime configuration, file permissions, and MCP/Slack HITL readiness.

## Security properties

1. Normal upgrades do not request, echo, log, or re-create protected Slack credentials.
2. Missing or invalid protected credentials fail closed before candidate promotion.
3. Explicit provisioning never places a secret in argv, environment exports, source, release artifacts, or diagnostic logs.
4. Provisioning accepts secret input only when terminal echo can be disabled safely.
5. Protected credential files are written atomically with restrictive mode and normalized by the existing runtime permission helper during deployment.
6. The governed human approver stays bound to `U01KG3CNYHK`; `D...` conversation IDs remain rejected.
7. No agent, MCP-tool, network, approval, or commercial authority is widened.

## Review result

The v4.1.13 defect was a fail-closed availability defect, not evidence of credential disclosure. The v4.1.14 design removes interactive secret input from the ordinary deploy path and isolates it in an explicit operator-only provisioning command. The provisioning command prefers shell-native silent read, permits an explicitly resolved `stty` fallback only for that operator action, and refuses to capture a secret if no safe no-echo mechanism is available.

Diagnostics continue to record metadata only. Secret values are not intentionally emitted to stdout/stderr or deployment logs.

## Residual risk

Actual QNAP production acceptance must still prove the host's supported no-echo provisioning mechanism when credentials are absent. If safe provisioning cannot be established on the host, the command must fail closed and production remains blocked. Repository verification cannot substitute for that live check.

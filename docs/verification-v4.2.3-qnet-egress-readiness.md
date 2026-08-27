# Verification Receipt v4.2.3: QNAP qnet Egress Readiness

Status: `CANDIDATE VERIFICATION IN PROGRESS`

## Candidate scope

v4.2.3 changes only the QNAP post-deploy Slack provider-read readiness behavior. The release retains the v4.2.2 GET/query Slack transport repair and all native Slack HITL authority invariants.

## Production RED evidence

- Two consecutive v4.2.2 QNAP deployments reached locally healthy containers and then failed `conversations.history` with `slack_provider_read_failed:network_error` before any Slack provider response.
- Both attempts transactionally rolled back to v4.2.1.
- The exact v4.2.2 image, protected Slack bot token, channel ID, and GET/query call returned `ok:true` when the image shared the already-stable v4.2.1 `mesh-cos-mcp` network namespace.
- Connected Slack access independently confirmed the governed channel and installed bot collaboration surface remained available.

These observations establish the regression target: fresh QNAP/qnet external egress can lag local container health.

## Required GREEN evidence

The exact release candidate must prove:

1. Python suite passes with the repository coverage threshold unchanged at 100%.
2. Node checks, dependency integrity, contract validation, runtime/doc drift checks, Ruff, mypy, Bandit, and compileall pass.
3. QNAP POSIX shell regression/security gates pass.
4. The verifier contains exactly bounded network-readiness retry semantics: six attempts, five-second inter-attempt delay, retry only on pre-provider network exception.
5. Slack `ok:false` responses and malformed provider responses remain immediate hard failures.
6. Exact v4.2.3 ZIP/checksum build succeeds with release-root containment and exact commit metadata.
7. Production container built from the exact bundle has matching version/revision provenance.
8. Modern MCP discovery and sequential request verification pass.
9. Targeted security review has no unresolved technical blocker.
10. After deployment, live QNAP verification must show `deployment_release=4.2.3` and PASS the Slack provider-read/qnet egress readiness gate before ChatGPT acceptance.

## Security applicability

`TARGETED`. The patch touches external API/network egress and deployment/runtime behavior on an OAuth-bearing MCP authority path. No scope, credential, authorization, ingress, tool, or agent expansion is permitted.

## Current limitations

This receipt will be updated with exact PR/main CI run IDs, candidate SHA, release asset checksum, and merge SHA after fresh independent verification. Repository CI cannot prove the live QNAP/qnet timing behavior or the ChatGPT Work event trigger; those remain production acceptance requirements.

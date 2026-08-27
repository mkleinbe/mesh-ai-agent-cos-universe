# Verification Receipt v4.2.3: QNAP qnet Egress Readiness

Status: `VERIFIED FUNCTIONAL CANDIDATE; FINAL RECEIPT COMMIT REVERIFICATION REQUIRED`

## Candidate scope

v4.2.3 changes only the QNAP post-deploy Slack provider-read readiness behavior. The release retains the v4.2.2 GET/query Slack transport repair and all native Slack HITL authority invariants.

Functional candidate SHA: `7a9ff0b9cb38cf4bbdcf2a7e9d393fcae104a22d`  
Pull request: `#57`  
Repository: `mkleinbe/mesh-ai-agent-cos-universe`

## Production RED evidence

- Two consecutive v4.2.2 QNAP deployments reached locally healthy containers and then failed `conversations.history` with `slack_provider_read_failed:network_error` before any Slack provider response.
- Both attempts transactionally rolled back to v4.2.1.
- The exact v4.2.2 image, protected Slack bot token, channel ID, and GET/query call returned `ok:true` when the image shared the already-stable v4.2.1 `mesh-cos-mcp` network namespace.
- Connected Slack access independently confirmed the governed channel and installed bot collaboration surface remained available.

These observations establish the causal regression target: fresh QNAP/qnet external egress can lag local container health. The evidence falsifies image-content, Slack OAuth credential, Slack scope, channel membership, and Slack GET/query contract defects for this failure.

## Fresh GREEN evidence on the functional candidate

Authoritative PR verification completed successfully on the functional candidate.

### Normal CI

- Workflow run: `33124944133`
- Job: `98700701975`
- Result: `success`
- Python: `423 passed`
- Coverage: `100.00%`
- Coverage detail: 2,945 statements, 0 missed; 962 branches, 0 partial
- Node test suite: 18 passed, 0 failed
- npm audit: 0 vulnerabilities
- `python -m pip check`: PASS
- contract schema validation: PASS
- runtime/documentation drift: PASS
- ChatGPT package/authority/roster/lifecycle drift: PASS
- Ruff source checks: PASS
- Ruff fatal test/script checks: PASS
- mypy: 35 source files, no issues
- Bandit high-severity gate: PASS
- compileall: PASS
- QNAP Compose discovery: PASS
- QNAP structured observability and secret non-collection: PASS
- QNAP runtime permission controls: PASS
- QNAP image provenance: PASS
- QNAP Slack HITL protected configuration: PASS
- QNAP transactional promotion/rollback controls: PASS
- QNAP versioned release-root regression: PASS
- QNAP restarting-container backup regression: PASS
- exact v4.2.3 release ZIP/checksum construction: PASS
- archive root containment: PASS
- exact bundle release metadata: PASS
- production container build from exact bundle: PASS
- OCI version/revision provenance checks: PASS
- modern MCP discovery and 10 sequential stateless requests: PASS
- native Slack readiness, CoS identity, dual release identity, and tunnel-only ingress regression: PASS

The CI artifact `mesh-cos-mcp-qnap-v4.2.3-ci` was uploaded as artifact ID `9667974335`; the GitHub Actions artifact archive digest is `sha256:e687e343f89fa2d9ba0703c12e174d70bdf88595a71d0ecb9441b5254b8d5ff9`. This is CI artifact evidence, not the final immutable GitHub release asset checksum.

### v4.2.3 release-candidate workflow

- Workflow run: `33124944183`
- Job: `98700712021`
- Result: `success`
- Independent release-candidate verification repeated the full Python, Node, dependency, contract/doc drift, type/static analysis, security, QNAP shell/security, exact bundle, production container provenance, and modern MCP gates successfully.

### Retry regression contract

The verified candidate encodes the bounded QNAP/qnet readiness behavior:

1. up to six total provider-read attempts;
2. five-second delay between retry attempts;
3. retry only when `fetch()` raises before a Slack provider response exists;
4. Slack `ok:false` provider responses fail immediately with only a sanitized machine error code;
5. malformed provider responses fail immediately;
6. exhausted network readiness fails deployment and preserves transactional rollback;
7. no approval authority, Slack scope, credential, public MCP tool, registered agent, or ingress path is added.

## Security receipt

Applicability: `TARGETED`.

The patch touches external API/network egress and deployment/runtime behavior on an OAuth-bearing MCP authority path. The targeted review found no unresolved CRITICAL/HIGH technical blocker. The dispatcher remains locator-only and non-authoritative, Slack provider reread remains mandatory, actual Slack provider failures are never retried into success, and failures remain fail closed.

Codex Security was unavailable in this execution environment. No claim of Codex Security execution is made. Available automated evidence includes Bandit, npm audit, dependency integrity, contract and authority drift gates, QNAP shell/security regressions, exact artifact provenance, and negative authorization/provider-response tests.

## Commit-binding note

GitHub pull-request workflows build against GitHub's synthetic PR merge ref for exact integration testing. The functional branch candidate that introduced the verified behavior is `7a9ff0b9cb38cf4bbdcf2a7e9d393fcae104a22d`. This verification-receipt update necessarily creates a later documentation-only branch SHA and therefore requires one final exact-head PR verification pass before merge. After merge, the main-branch release workflow must rebuild the v4.2.3 ZIP/checksum from the exact main merge SHA before tag/release publication.

## Live production limitations

Repository verification does not prove the live QNAP/qnet timing behavior or the ChatGPT Work event trigger. Production remains **NOT VERIFIED** until all of the following occur:

1. v4.2.3 is deployed from the immutable release bundle;
2. local QNAP verification reports `deployment_release=4.2.3`;
3. the live Slack provider-read gate passes from the freshly recreated `mesh-cos-mcp` qnet namespace;
4. a fresh synthetic `*APPROVE*` reply traverses Slack -> Work dispatcher -> published MCP -> QNAP provider reread -> canonical APPROVED / READY_FOR_ACTION exactly once;
5. replay idempotency, DENY, CHANGE, negative security cases, and final audit-chain verification pass.

`COMPLETED != VERIFIED` remains the governing release rule.

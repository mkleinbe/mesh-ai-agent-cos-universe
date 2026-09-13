# Verification v4.9.1 Media OS Capability Registration

## Requirement to evidence

| Requirement | Required evidence |
|---|---|
| CMO has production, verification, distribution | registry read plus `test_media_os_capability_registration_v491.py` |
| VP Content has production only | registry read plus negative verification/distribution assertions |
| no authority expansion | decision authority, delegation permissions, ten-agent roster regressions |
| governed Skill handoff | `GovernedAdapterRegistry` returns `AUTHORIZED` and `CHATGPT_SKILL_HANDOFF` |
| legacy regression reconciled | full pytest no longer fails `test_enterprise_consulting_skill_consumption_v470.py` |
| release publisher singular | historical workflow and release-state regressions |
| source candidate deployable | canonical CI QNAP bundle, container provenance, POSIX and MCP transport gates |
| production runtime active | post-deploy Mesh CoS MCP source/registry readback |

## Candidate verification

A v4.9.1 repository candidate is not VERIFIED merely because the Media OS test subset passes. The full repository CI must pass, including 100% `mesh_cos` coverage, static/type/security checks, package/document drift checks, authority closure, QNAP build/regressions, and transport verification.

## Production verification

After QNAP deployment, verify through the published Secure MCP boundary:

- deployment release remains the expected QNAP runtime identity;
- source commit matches the promoted verified candidate;
- CMO lists all three Media OS Skills;
- VP Content lists production only;
- VP Content delegation permissions remain empty;
- governed `mesh-media-production` invocation no longer returns `not_found`;
- no public action occurred during the non-public acceptance canary.

Completion, verification, approval, publication, and release remain separate states.

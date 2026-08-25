# v4.1.5 QNAP Release Identity Preflight Reliability

## Purpose

v4.1.5 corrects the deployment preflight drift exposed by the live v4.1.4 QNAP upgrade. The new image and state/tunnel checks were valid, but preflight still compared generated deployment metadata to a hardcoded v4.1.3 literal and stopped before Compose replacement.

The canonical Mesh CoS authority/runtime contract remains `4.0.0`.

## Causal design change

`mesh-cos-mcp-preflight.sh` no longer owns an independent patch-release constant. It requires `$APP_ROOT/release-metadata.txt`, extracts the `version=` value, and compares generated `MESH_COS_DEPLOYMENT_RELEASE` to that bundle-owned release identity.

Failure remains fail closed:

- missing release metadata fails preflight;
- missing version metadata fails preflight;
- bundle/environment mismatch fails preflight;
- Compose replacement does not begin after a failed preflight.

## Preserved controls

- exactly 10 canonical agents;
- exactly 27 governed CoS tools;
- human-only `approval.record_decision` and `reliability.human_override` remain excluded;
- canonical TaskLedger and `COMPLETED != VERIFIED` remain unchanged;
- Secure MCP Tunnel source-IP trust boundary remains unchanged;
- runtime UID/GID 65532, read-only rootfs, dropped capabilities, no-new-privileges, no Docker socket;
- 2 CPU / 24 GiB main-container resource policy;
- v4.1.4 modern MCP stateless transport and `server/discover` support remain unchanged.

## Verification requirements

The exact release candidate must pass:

1. regression RED/GREEN for release-identity preflight;
2. QNAP-048 through QNAP-050 behavior coverage;
3. Python contracts/drift/static analysis and 100% coverage;
4. npm build/test/smoke/audit;
5. POSIX QNAP shell regressions;
6. deterministic v4.1.5 bundle and checksum;
7. bundle metadata inspection and stale-literal exclusion;
8. production image build;
9. modern MCP discovery and ten sequential request regression;
10. real Docker ownership handoff;
11. hardened runtime, restart, direct-ingress denial, and SQLite backup integrity;
12. targeted security review.

Final production acceptance requires a live v4.1.5 QNAP deployment and hosted ChatGPT/Secure MCP sequential acceptance.

# v4.1.5 QNAP Release Identity Preflight Reliability

`v4.1.5` is a corrective QNAP production release for the v4.1.4 upgrade failure observed during host preflight. The v4.1.4 image built successfully, the canonical TaskLedger and tunnel configuration validated, and the existing v4.1.3 containers remained healthy, but preflight stopped because it still required `MESH_COS_DEPLOYMENT_RELEASE=4.1.3`.

The canonical Mesh CoS authority/runtime contract remains `4.0.0`. The exact 10-agent roster, 27 governed tools, human-only operations, canonical TaskLedger, `COMPLETED != VERIFIED`, resource policy, modern MCP transport from v4.1.4, and Secure MCP Tunnel trust boundary are unchanged.

## Root cause fixed

The v4.1.4 release advanced the bundle builder, generated `.env`, image tag, release workflow, documentation, and transport implementation to 4.1.4, but `deployment/qnap/scripts/mesh-cos-mcp-preflight.sh` retained an independent hardcoded 4.1.3 comparison.

The live deployment therefore failed closed on a stale release literal even though the new v4.1.4 image and all surrounding preflight controls were valid. The later `prepare failed` messages were propagation of that one check failure.

## Causal correction

v4.1.5 removes the duplicated patch-release authority from preflight. Preflight now:

- requires the extracted bundle's `release-metadata.txt`;
- reads the authoritative `version=` value from that metadata;
- compares generated `MESH_COS_DEPLOYMENT_RELEASE` to that bundle version;
- fails closed when release metadata is missing, has no version, or disagrees with `.env`;
- no longer embeds a prior patch-release literal in the preflight gate.

This makes the release identity check self-consistent with the verified bundle and removes the mechanism that allowed the v4.1.4 drift defect.

## TDD and behavior evidence

The defect was reproduced with a new regression test before the implementation correction. RED demonstrated both missing bundle-metadata derivation and the stale 4.1.3 literal. GREEN then passed the same regression plus the full repository CI.

Ready behavior scenarios:

- QNAP-048 matching bundle/environment release identity passes;
- QNAP-049 mismatched identities fail closed before Compose replacement;
- QNAP-050 missing release metadata fails closed.

See `specs/qnap-release-identity-v4.1.5.feature` and `docs/qnap-release-identity-debugging-v4.1.5.md`.

## Security boundary

Security applicability is **TARGETED** because deployment/runtime validation is modified.

The correction does not expand authority. Release metadata is parsed as data, not sourced or evaluated as shell code. Existing controls remain unchanged:

- `MCP_AUTH_MODE=tunnel` only;
- private tunnel-client source-IP gate before MCP dispatch;
- no production host port publication;
- runtime UID/GID 65532 with read-only rootfs, all capabilities dropped, and no Docker socket;
- exactly 27 governed CoS tools and 10 canonical agents;
- human-only `approval.record_decision` and `reliability.human_override` remain excluded from agent projection;
- canonical SQLite persistence and audit-chain verification remain unchanged;
- tunnel runtime secret handling remains unchanged.

See `docs/qnap-security-review-v4.1.5.md`.

## v4.1.4 transport correction retained

The modern MCP transport remediation from v4.1.4 is carried forward unchanged: stable v2 split MCP packages, stateless HTTP request serving, current `server/discover` support, tunnel-private ingress gating, and readiness verification of modern protocol discovery.

## QNAP operator privilege

The current QNAP operator account requires `sudo` for Docker-bearing deployment commands. This is host-side deployment authority only. The long-running `mesh-cos-mcp` runtime remains UID/GID `65532:65532` with its least-privilege controls.

## Resource policy

- `mesh-cos-mcp`: 2 CPUs, 24 GiB RAM, no PID limit.
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit.

No resource increase is part of this correction.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.5.zip`
- `mesh-cos-mcp-qnap-v4.1.5.zip.sha256`

The release bundle contains the release-bound build context and QNAP operator tooling. It contains no runtime tunnel secret and no canonical TaskLedger data.

## Version identity

- Repository/QNAP deployment release: `4.1.5`
- Semantic tag: `v4.1.5`
- Container image label default: `4.1.5-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 agents
- Message Operations remains the tenth registered agent
- Mesh Devil's Advocate remains a governed shared Skill, not agent 11
- Production transport remains OpenAI Secure MCP Tunnel

## Production acceptance boundary

Repository and container verification cannot prove the final on-premises hosted path. After deploying v4.1.5 to QNAP, the operator must confirm the deployment completes through Compose replacement, both containers are healthy, post-deploy backup succeeds, and the published ChatGPT app passes the sequential Secure MCP acceptance suite.

See:

- `docs/qnap-release-identity-debugging-v4.1.5.md`
- `docs/qnap-security-review-v4.1.5.md`
- `docs/qnap-mcp-502-debugging-v4.1.4.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

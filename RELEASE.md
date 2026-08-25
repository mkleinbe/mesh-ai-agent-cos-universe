# v4.1.7 QNAP Image Provenance and Hosted Envelope Verification

`v4.1.7` is a corrective QNAP deployment-integrity release for the published **Mesh CoS MCP** ChatGPT app connected through the **OpenAI Secure MCP Tunnel**.

The canonical Mesh CoS Phase 1 authority/runtime contract remains **`4.0.0`**. The exact 10-agent roster, 27 governed CoS tools, human-only operations, canonical TaskLedger, `COMPLETED != VERIFIED`, resource policy, and Secure MCP Tunnel trust boundary are unchanged.

## Production evidence that drove this release

The v4.1.6 published app was functionally healthy across the governed MCP surface, but successful hosted tool responses consistently omitted the required `deployment_release` field while still reporting `mcp_version: 4.0.0` and `agent_id: cos`.

The final tagged v4.1.6 repository implementation and exact release artifact were inspected. Both contain the required `deployment_release` tool-envelope serialization, and the v4.1.6 bundle injects `MESH_COS_DEPLOYMENT_RELEASE` through Compose. The exact v4.1.6 release ZIP checksum is `003fc6363dc96aa642923fa9a38abffd155892bd36414b08c3f09a8d3218627f`.

Therefore the hosted response could not have been produced by the exact final v4.1.6 release-built MCP server implementation.

## Root-cause correction

The v4.1.6 QNAP preparation path could reuse any pre-existing local image under the final mutable tag without proving that image came from the final extracted release commit. Post-deploy verification also validated `/healthz` and `/readyz` identity but did not execute the governed `tools/call` boundary that failed in hosted acceptance.

v4.1.7 closes both gaps.

### Release-image provenance

Preparation now:

- reads `version=` and `commit=` from extracted `release-metadata.txt` as data;
- requires a valid release version and 40-character Git commit SHA;
- requires the requested deployment release to match the bundle metadata;
- compares any existing local Mesh image OCI `org.opencontainers.image.version` and `org.opencontainers.image.revision` labels with the extracted release identity;
- rebuilds from the extracted build context when either label differs;
- verifies the built or reused image labels before recording the image ID in `.env`.

A same-tag prerelease/stale image can no longer silently survive a final bundle deployment.

### Governed tool-envelope verification

Post-deploy verification now executes a real modern MCP read-only `registry.get_agent` `tools/call` against the running `mesh-cos-mcp` service from an ephemeral verifier sharing the tunnel client's network namespace.

PASS requires the actual returned governed envelope to contain:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
```

The verifier has no state mount, no tunnel secret, no Docker socket, no added Linux capability, and no persistent service lifetime. The production source-IP gate remains unchanged.

## BDD and TDD evidence

The release adds ready scenarios:

- QNAP-056 stale same-tag image is rebuilt from verified bundle provenance;
- QNAP-057 matching image is reusable only with version/revision evidence;
- QNAP-058 post-deploy verification exercises the governed tool envelope through the tunnel network boundary.

Regression evidence was added before the implementation correction to prove the old preparation and verification paths lacked these controls.

## Security boundary

Security applicability is **TARGETED** because deployment/runtime integrity and the MCP verification trust boundary are touched.

Preserved controls include:

- `MCP_AUTH_MODE=tunnel` for remote production;
- mandatory private tunnel-client source-IP gate before `/mcp` dispatch;
- no production host MCP port publication;
- immutable `MESH_COS_AGENT_ID=cos`;
- long-running runtime UID/GID 65532, read-only rootfs, all capabilities dropped, no-new-privileges, and no Docker socket;
- exactly 27 governed CoS tools and 10 registered agents;
- human-only `approval.record_decision` and `reliability.human_override` remain excluded;
- canonical SQLite TaskLedger and audit-chain semantics unchanged;
- tunnel runtime secret handling unchanged.

See `docs/qnap-security-review-v4.1.7.md`.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.7.zip`
- `mesh-cos-mcp-qnap-v4.1.7.zip.sha256`

The bundle contains the release-bound build context, QNAP operator tooling, current ChatGPT acceptance procedure, v4.1.7 BDD scenarios, debugging record, security review, and release handoff. It contains no tunnel runtime secret and no canonical TaskLedger data.

## Version identity

- Repository/QNAP deployment release: `4.1.7`
- Semantic tag: `v4.1.7`
- Container image label default: `4.1.7-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 agents
- Message Operations remains the tenth registered agent
- Mesh Devil's Advocate remains a governed shared Skill, not agent 11
- CoS production catalog: exactly 27 governed tools
- Production transport: OpenAI Secure MCP Tunnel
- Remediation issue: #41

## Post-deploy acceptance boundary

Repository/container verification cannot prove the newly deployed on-premises serving instance. After deploying v4.1.7 to QNAP, repeat the published-app sequential acceptance suite and require every successful governed response to report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
```

Do not mark the release accepted until both local post-deploy governed-envelope verification and hosted Mesh CoS MCP app acceptance are green.

See:

- `docs/qnap-image-provenance-envelope-debugging-v4.1.7.md`
- `docs/qnap-security-review-v4.1.7.md`
- `docs/release-4.1.7-qnap-image-provenance-envelope.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

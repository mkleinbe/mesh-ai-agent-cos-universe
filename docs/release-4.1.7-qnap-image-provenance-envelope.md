# v4.1.7 QNAP Image Provenance and Hosted Envelope Verification

## Purpose

v4.1.7 corrects the release-integrity gap exposed after v4.1.6 deployment acceptance: the published Mesh CoS MCP app remained functionally healthy but governed tool responses did not include the required `deployment_release` field.

The final v4.1.6 repository and release artifact already contained the correct response-envelope implementation. v4.1.7 therefore does not redesign the MCP authority/runtime contract. It hardens the QNAP image-selection boundary and post-deploy verification so a stale same-tag image cannot silently survive and the failed hosted envelope contract is directly exercised before deployment is reported successful.

## Release identity

- QNAP deployment release: `4.1.7`
- semantic tag: `v4.1.7`
- image label: `4.1.7-qnap`
- canonical MCP authority/runtime contract: `4.0.0` unchanged
- bound production agent: `cos`
- production transport: OpenAI Secure MCP Tunnel

## Corrective controls

### Release-image provenance

Preparation reads `version=` and `commit=` from the extracted `release-metadata.txt`. Existing local Mesh images are reusable only when both OCI labels match:

- `org.opencontainers.image.version = 4.1.7-qnap`
- `org.opencontainers.image.revision = <release metadata commit>`

A mismatch forces a rebuild from the extracted release build context. After either build or reuse, the same labels are revalidated before the image ID is recorded in `.env`.

### Governed response-envelope verification

Post-deploy verification now performs an actual modern MCP `tools/call` for read-only `registry.get_agent` against the running service from an ephemeral verifier sharing the tunnel client's network namespace.

PASS requires the returned tool envelope to contain:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
```

The verifier has no tunnel secret, no state volume, no Docker socket, no added Linux capability, and no persistent runtime. The production source-IP gate remains unchanged.

## Acceptance

Repository and container CI can verify the release artifact and local runtime behavior but cannot prove the published ChatGPT path. After QNAP deployment, repeat the hosted sequential acceptance suite and require `deployment_release: 4.1.7` on every successful governed response.

The release blocker is closed only when the published app passes that hosted acceptance without restart or reconnect.

## References

- `docs/qnap-image-provenance-envelope-debugging-v4.1.7.md`
- `docs/qnap-security-review-v4.1.7.md`
- `specs/qnap-image-provenance-envelope-v4.1.7.feature`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

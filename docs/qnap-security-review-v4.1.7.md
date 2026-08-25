# QNAP Security Review v4.1.7

Security applicability: **TARGETED**.

The change touches deployment/runtime integrity and the MCP trust boundary used for post-deploy verification. It does not alter the canonical authority model, tool catalog, decision rights, TaskLedger semantics, or tunnel secret model.

## Trust boundaries reviewed

- verified QNAP release bundle -> local Docker image build/reuse decision;
- release metadata -> OCI image version/revision labels;
- host Docker authority -> long-running non-root application containers;
- `mesh-cos-tunnel` private source identity `172.30.60.3` -> `mesh-cos-mcp` ingress gate;
- ephemeral deployment verifier -> one hardcoded read-only MCP `registry.get_agent` call;
- canonical TaskLedger persistence and tunnel runtime secret paths.

## Findings

### SEC-QNAP-027: mutable local image tag was trusted without release provenance

- Severity: Medium
- Status: Remediated in v4.1.7 candidate
- Surface: deployment/runtime supply-chain integrity
- Evidence: v4.1.6 preparation reused any existing `mesh-cos-mcp:qnap-v4.1.6` image without checking OCI release version or revision against `release-metadata.txt`.
- Consequence: a prerelease or stale same-tag image could survive a final bundle deployment and serve code that does not match the published release.
- Remediation: compare `org.opencontainers.image.version` and `org.opencontainers.image.revision` with the extracted release version and commit; rebuild on mismatch; verify labels after build/reuse before recording the image ID.
- Retest: QNAP-056 and QNAP-057 plus CI inspection of release metadata and image labels.

### SEC-QNAP-028: post-deploy verification did not exercise the governed tool-envelope boundary

- Severity: Medium
- Status: Remediated in v4.1.7 candidate
- Surface: MCP runtime verification
- Evidence: v4.1.6 verifier checked health/readiness identity but did not execute `tools/call` against the running service.
- Consequence: transport/status metadata could pass while hosted governed responses violate the release identity contract.
- Remediation: execute a modern MCP read-only `registry.get_agent` call against the running service from the tunnel network namespace and fail unless the governed envelope reports the expected canonical/runtime/deployment identities.
- Retest: QNAP-058 and published-app hosted acceptance after deployment.

### SEC-QNAP-029: trusted-source verification must not create a new persistent bypass

- Severity: Informational control requirement
- Status: Satisfied by design
- Surface: Secure MCP Tunnel source-IP gate
- Property: the verifier may originate from the trusted tunnel network identity only while invoked by the host-authorized deployment verifier; it must not weaken the application ingress check or create a long-running alternate trusted client.
- Implementation: a short-lived container uses `--network container:mesh-cos-tunnel`, no volume mounts, no tunnel secret, non-root UID/GID 65532, read-only root filesystem, dropped capabilities, and no Docker socket. It executes only a hardcoded read-only `registry.get_agent` request and exits.
- Authority analysis: a QNAP Docker administrator already has authority to create network namespaces/containers. The verifier does not grant application authority to an unprivileged principal and does not persist after verification.

## Preserved security properties

- `MCP_AUTH_MODE=tunnel` remains mandatory for the remote production adapter.
- `MCP_TRUSTED_CLIENT_IP=172.30.60.3` remains enforced before `/mcp` dispatch.
- no host MCP port is published by production Compose.
- `MESH_COS_AGENT_ID=cos` remains immutable process identity.
- long-running `mesh-cos-mcp` remains UID/GID 65532, read-only rootfs, all capabilities dropped, no-new-privileges, and no Docker socket.
- exactly 27 governed CoS tools and 10 registered agents remain projected.
- `approval.record_decision` and `reliability.human_override` remain human-only.
- canonical SQLite TaskLedger and audit-chain semantics are unchanged.
- tunnel runtime secret storage and backup exclusion are unchanged.
- release metadata is parsed as data and never sourced or evaluated as shell code.

## Required evidence before integration

- regression evidence for same-tag provenance mismatch and match handling;
- shell syntax/regression checks on QNAP scripts;
- deterministic v4.1.7 bundle and checksum;
- production image label verification against release commit/version;
- modern MCP discovery and tool-call identity tests;
- non-tunnel direct ingress denial;
- non-root/runtime/backup/restart checks;
- full repository CI green on the exact candidate;
- post-deploy hosted acceptance remains required and cannot be substituted by CI.

No unresolved critical or high security finding is identified in this scoped change. Residual uncertainty is limited to the actual on-premises runtime until v4.1.7 is deployed and the published ChatGPT app is retested.

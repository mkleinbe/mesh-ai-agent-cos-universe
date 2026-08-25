# QNAP Security Review v4.1.5

## Applicability

Security applicability: **TARGETED**.

The change touches QNAP deployment/runtime validation and therefore receives targeted review. It does not alter MCP authentication, authorization, agent authority, secrets, canonical persistence semantics, container privilege, network topology, or the OpenAI Secure MCP Tunnel trust boundary.

## Security properties

### SEC-QNAP-024: release identity validation fails closed

**Property:** An extracted QNAP bundle must not be deployed when its generated `.env` release identity disagrees with the release metadata shipped in that same bundle.

**Evidence:** `mesh-cos-mcp-preflight.sh` reads the bundle `version=` record and compares it to `MESH_COS_DEPLOYMENT_RELEASE`. Missing metadata, missing version, or mismatch sets the preflight failure state before Compose replacement.

**Result:** PASS on the candidate after the regression RED was corrected.

### SEC-QNAP-025: release metadata is data, not executable input

**Property:** Release metadata must not be evaluated as shell code or used to expand deployment authority.

**Evidence:** Preflight extracts only the first `version` field through `awk` and performs string comparison. It does not `source`, `eval`, execute, interpolate into a command, modify credentials, or change Docker authority based on metadata content.

**Result:** PASS.

### SEC-QNAP-026: existing privilege and secret boundaries remain unchanged

**Property:** Correcting release-identity validation must not weaken the existing QNAP least-privilege runtime or secret handling.

**Evidence:** The change does not modify runtime UID/GID 65532, capability drops, read-only root filesystem, no-new-privileges, Docker-socket exclusion, tunnel secret file handling, source-IP gate, canonical TaskLedger ownership, or human-only tool exclusions. Existing full CI surrounding checks remain required.

**Result:** PASS subject to exact-candidate CI.

## Findings

No critical or high security finding was identified in the v4.1.5 corrective scope.

The live failure was a fail-closed release/code drift defect. It prevented an otherwise valid upgrade and did not bypass a security control. The new design reduces recurrence risk by removing a duplicated hardcoded release literal from preflight.

## Residual risk

- QNAP filesystem capacity remains an operational concern when utilization is high, but it was not causal to this incident and the absolute free-space gate remained satisfied.
- Final production acceptance still requires deploying the v4.1.5 artifact to the actual QNAP and re-running hosted ChatGPT/Secure MCP acceptance.
- No Codex Security scan is claimed from this ChatGPT runtime. Targeted review uses repository diff/CI evidence and the existing hardened QNAP controls.

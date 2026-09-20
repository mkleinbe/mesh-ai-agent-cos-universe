# QNAP 4.4.1 Source Identity Repair

QNAP deployment 4.4.1 is a deployment-integrity PATCH. It does not change the canonical MCP authority contract or expand agent authority.

## Defect

Multiple repository releases published a QNAP payload under the same deployment filename and inner release directory. A locally retained ZIP/checksum pair could therefore remain internally valid while containing an older source revision. The deployment verifier validated deployment identity and prepared image identity but did not compare the running governed MCP `source_commit` with the release metadata commit.

## Correction

- QNAP deployment identity advances to `4.4.1`, producing a distinct archive and release directory.
- The Mesh image tag is commit-qualified: `mesh-cos-mcp:qnap-v4.4.1-<12-char-source-sha>`.
- Candidate Compose startup uses `--force-recreate`.
- Post-deploy verification requires the active release metadata commit, running image OCI revision, and governed MCP `source_commit` to match exactly.

Canonical MCP contract remains `4.0.0`.

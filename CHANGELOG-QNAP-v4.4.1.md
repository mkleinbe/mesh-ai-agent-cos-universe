# QNAP Deployment 4.4.1

## Fixed

- Eliminates ambiguous reuse of the `mesh-cos-mcp-qnap-v4.4.0.zip` deployment artifact.
- Binds the local Mesh runtime image tag to both deployment release and source commit.
- Forces Compose candidate recreation so a prior container cannot survive promotion.
- Verifies the active release metadata commit against the running image OCI revision and governed MCP `source_commit` before deployment can commit.
- Adds regression coverage for source-identity drift.

Canonical MCP authority contract remains `4.0.0`.

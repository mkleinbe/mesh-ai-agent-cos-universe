# Mesh CoS v4.13.2 QNAP Source Identity Repair

v4.13.2 is a PATCH release that closes a production deployment-integrity defect discovered during Slack HITL acceptance.

## Problem

The v4.13.0 and v4.13.1 repository releases both published QNAP payloads under the same deployment identity and artifact name, `4.4.0` / `mesh-cos-mcp-qnap-v4.4.0.zip`. A retained ZIP plus its retained checksum could therefore remain internally valid while carrying an older source revision. In addition, candidate Compose startup did not force recreation and post-deploy verification did not compare the running governed MCP `source_commit` with release metadata.

## Changes

- advances QNAP deployment identity to `4.4.1` with a distinct archive and release directory;
- binds local Mesh image tags to deployment release plus source commit prefix;
- forces candidate container recreation;
- requires active release metadata, running OCI revision, and governed MCP `source_commit` to match exactly;
- adds BDD and deterministic regression evidence for stale-runtime rejection;
- updates active QNAP operator and acceptance documentation.

The canonical MCP authority/runtime contract remains `4.0.0`. The Phase 1 organization remains exactly 10 agents. Slack, TaskLedger, Secure MCP Tunnel, L4/L5 approval, completion/verification, and external-action authority boundaries are unchanged.

## Deployment artifact

Use only the v4.13.2 release assets:

- `mesh-cos-mcp-qnap-v4.4.1.zip`
- `mesh-cos-mcp-qnap-v4.4.1.zip.sha256`

The extracted deployment root is `v4.4.1/`.

## Production acceptance

Production is accepted only after a live governed read reports both `deployment_release=4.4.1` and `source_commit` equal to the exact v4.13.2 release commit, followed by the Slack peer-HITL acceptance in `docs/chatgpt-published-app-production-acceptance-qnap-v4.4.1.md`.

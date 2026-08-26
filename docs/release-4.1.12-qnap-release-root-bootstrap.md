# v4.1.12 QNAP Release-Root Bootstrap

v4.1.12 supersedes v4.1.11 for QNAP deployment packaging and operator pathing. v4.1.11 corrected staged candidate identity and helper self-resolution, but its published ZIP still extracted release contents directly into the caller directory while the deployment instructions expected `/share/Docker/cos-mcp/releases/v4.1.11` to already exist.

## Correction

- canonical operator working directory is `/share/Docker/cos-mcp/releases`;
- the ZIP contains a single top-level `v4.1.12/` directory;
- extraction creates `/share/Docker/cos-mcp/releases/v4.1.12` automatically;
- no manual `mkdir`, `cp`, `mv`, `chmod`, or `cd` into the release directory is required;
- all operator scripts continue to self-resolve relative to their own script directory;
- deployment validates that the resolved `v4.1.12` folder is directly beneath the canonical releases root and agrees with staged semantic release metadata;
- genuine path/metadata mismatches fail before candidate preparation;
- historical already-published v4.1.11 archive behavior remains reproducible and is not rewritten in place.

## Preserved behavior

v4.1.12 carries forward v4.1.10 scheduled execution and Slack HITL behavior and v4.1.11 active/candidate separation. Canonical TaskLedger, Secure MCP Tunnel, protected Slack and tunnel secrets, OCI provenance, post-health promotion, backup/restore, qnet networking, non-root runtime, and direct-ingress denial remain unchanged.

## Version boundary

- QNAP deployment release: `4.1.12`
- semantic tag: `v4.1.12`
- image label: `4.1.12-qnap`
- canonical Phase 1 authority/runtime contract: `4.0.0`
- registered agents: exactly 10
- governed CoS tools: exactly 27

## Acceptance boundary

Repository and container verification do not prove the actual QNAP deployment or hosted ChatGPT/Slack path. Production acceptance still requires the deployed instance to report `mcp_version=4.0.0`, `deployment_release=4.1.12`, `agent_id=cos`, and `slack_hitl_ready=true`, followed by the governed hosted acceptance procedure.

# QNAP 4.4.2 Slack HITL Task Telemetry

This immutable deployment patch packages the v4.13.3 runtime repair under a new QNAP identity so a prior 4.4.1 archive cannot be mistaken for current source.

The extracted root is v4.4.2 and the release assets are:

- mesh-cos-mcp-qnap-v4.4.2.zip
- mesh-cos-mcp-qnap-v4.4.2.zip.sha256

Production Compose topology, network interfaces, static application IP, Secure MCP Tunnel, secret mounts, TaskLedger volume, UID/GID, resource limits, health checks, and logging remain unchanged.

Acceptance requires exact release metadata, OCI revision, and governed MCP source_commit agreement plus the fresh Slack telemetry UAT.

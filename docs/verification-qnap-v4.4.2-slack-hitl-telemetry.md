# Verification: QNAP 4.4.2 Slack HITL Telemetry

The 4.4.2 candidate must pass the full repository gates plus:

- shell syntax and existing QNAP deployment regression tests;
- release metadata version=4.4.2;
- release metadata commit equal to the exact candidate SHA;
- image version label 4.4.2-qnap;
- image OCI revision equal to the exact candidate SHA;
- governed MCP source_commit equal to the same SHA;
- SHA-256 verification of mesh-cos-mcp-qnap-v4.4.2.zip.

No local or CI result is production proof. Production requires operator deployment, exact-source readback, and the fresh Slack task telemetry UAT.

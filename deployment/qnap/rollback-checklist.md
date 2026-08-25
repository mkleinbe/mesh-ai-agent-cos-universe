# Rollback Checklist
- [ ] Stop new consequential MCP work
- [ ] Capture current logs and state metadata without secrets
- [ ] Confirm previous image and `/share/Docker/cos-mcp/compose.yaml` configuration are available
- [ ] Confirm ledger/schema compatibility with the previous image
- [ ] Select a verified compatible backup from `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` only if state rollback is required
- [ ] Recreate the Container Station application with the previous immutable image digest
- [ ] Verify `MESH_COS_AGENT_ID=cos`, readiness, audit integrity, tool catalog, and tunnel recovery
- [ ] Record rollback reason, evidence, operator, and resulting image digest

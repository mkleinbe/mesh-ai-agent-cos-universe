# Rollback Checklist
- [ ] Stop new consequential MCP work
- [ ] Capture current logs and state metadata without secrets
- [ ] Confirm previous image and Compose configuration are available
- [ ] Confirm ledger/schema compatibility with previous image
- [ ] Restore compatible canonical backup only when required
- [ ] Recreate Container Station Application with previous immutable digest
- [ ] Verify `MESH_COS_AGENT_ID=cos`, readiness, audit integrity, tool catalog, and tunnel recovery
- [ ] Record rollback reason, evidence, operator, and resulting image digest

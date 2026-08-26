# Rollback Checklist

- [ ] Stop new consequential MCP work
- [ ] Capture current deployment diagnostic logs and state metadata without secrets
- [ ] Determine whether failure occurred before `candidate_promote`; if so, do not replace canonical state or active descriptors merely because the candidate failed
- [ ] Confirm the retained previous versioned release directory is available under `/share/Docker/cos-mcp/releases/vX.Y.Z`
- [ ] Use `/share/Docker/cos-mcp/releases` as the rollback working directory and address the retained release as `./vX.Y.Z/<script>.sh`; do not copy helpers to `/share/Docker` or move release payload files
- [ ] Confirm the previous compatible image and active `/share/Docker/cos-mcp/compose.yaml`, `.env`, and `release-metadata.txt` configuration set are available
- [ ] Confirm ledger/schema compatibility with the previous image
- [ ] Select the most recent verified compatible `pre-deploy` or explicit manual backup from `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` only if state rollback is actually required
- [ ] Verify the selected backup with `sha256sum -c SHA256SUMS` before any restore
- [ ] Preserve the existing tunnel runtime key and Slack protected files; do not recover secrets from a backup because they are intentionally excluded
- [ ] Recreate/deploy from `/share/Docker/cos-mcp/releases` through the retained previous release path using `sudo sh ./vX.Y.Z/mesh-cos-mcp-deploy.sh`
- [ ] Verify `MESH_COS_AGENT_ID=cos`, the expected previous `deployment_release`, readiness, audit integrity, exact 27-tool CoS catalog, 10-agent roster, and tunnel recovery
- [ ] Confirm direct non-tunnel MCP ingress remains denied and `COMPLETED != VERIFIED` remains enforced
- [ ] Record rollback reason, evidence, operator, resulting image digest, restored release identity, and backup path if state was restored
- [ ] Re-run hosted ChatGPT and Slack HITL acceptance before resuming consequential work

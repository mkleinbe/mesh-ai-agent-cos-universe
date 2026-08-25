# Upgrade Checklist

- [ ] Candidate passes BDD, unit, integration, bundle, container, security, and preflight checks
- [ ] SQLite schema compatibility evaluated
- [ ] Approved release ZIP extracted into `/share/Docker` without deleting `/share/Docker/cos-mcp/state` or `secrets`
- [ ] Human release approval recorded
- [ ] Run `cd /share/Docker && sh mesh-cos-mcp-deploy.sh`
- [ ] Automated pre-deploy backup completes when an existing service is running
- [ ] Existing canonical TaskLedger is preserved
- [ ] Release-bound Mesh image ID and tunnel RepoDigest/image ID are generated and verified automatically
- [ ] Automated host preflight passes
- [ ] Automated deployment, health wait, least-privilege/image/resource verification, and post-deploy backup pass
- [ ] Verified dated backup exists under `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"`
- [ ] ChatGPT action refresh/review is required only if the MCP tool contract changed
- [ ] Re-run `CHATGPT-ACCEPTANCE.md` after any transport/runtime upgrade

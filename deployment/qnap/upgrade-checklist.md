# Upgrade Checklist

- [ ] Candidate passes BDD, unit, integration, bundle, container, security, and preflight checks
- [ ] SQLite schema compatibility evaluated
- [ ] Approved v4.1.5 release ZIP extracted into `/share/Docker` without deleting `/share/Docker/cos-mcp/state` or `secrets`
- [ ] Human release approval recorded
- [ ] QNAP operator uses `sudo` for Docker authority: `cd /share/Docker && sudo sh mesh-cos-mcp-deploy.sh`
- [ ] Automated pre-deploy backup completes when an existing service is running
- [ ] Existing canonical TaskLedger is preserved
- [ ] Existing Secure MCP tunnel ID and runtime-key file are preserved
- [ ] Release-bound Mesh image ID and tunnel RepoDigest/image ID are generated and verified automatically
- [ ] `release-metadata.txt` exists and matches generated `MESH_COS_DEPLOYMENT_RELEASE=4.1.5`
- [ ] Automated host preflight passes without a stale patch-release literal
- [ ] Automated deployment, health wait, least-privilege/image/resource verification, and post-deploy backup pass
- [ ] Verified dated backup exists under `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"`
- [ ] Long-running `mesh-cos-mcp` remains UID/GID 65532 despite host-side sudo deployment invocation
- [ ] Re-run `CHATGPT-ACCEPTANCE.md`, including release-identity checks and the ten-call sequential transport regression
- [ ] Close the production deployment blocker only after v4.1.5 local deployment and hosted ChatGPT/Tunnel acceptance pass without container restart between calls

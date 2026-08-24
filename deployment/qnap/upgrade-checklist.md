# Upgrade Checklist
- [ ] Candidate passes BDD, unit, integration, container, security, and preflight checks
- [ ] Candidate image digest and SBOM/provenance recorded
- [ ] SQLite schema compatibility evaluated
- [ ] Consistent canonical-state backup completed and verified
- [ ] Prior Compose, `.env` variable names, and image digest retained for rollback
- [ ] Human release approval recorded
- [ ] Container Station Application recreated with immutable candidate image
- [ ] Readiness, identity, catalog, audit-chain, persistence, and tunnel recovery verified
- [ ] ChatGPT action refresh/review completed if tool contract changed

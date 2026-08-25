# v4.1.2 QNAP Compose Discovery Fix

## Defects corrected

1. **DEF-QNAP-CLI-001:** v4.1.1 assumed that an installed Compose V2 package was necessarily callable through `docker compose` in every QNAP SSH environment. A live deployment disproved that assumption. v4.1.2 resolves Compose V2 from the Docker subcommand, Docker client plugin metadata, standard Docker plugin paths, or the Container Station QPKG installation. Compose V1 is rejected.
2. **DEF-QNAP-CLI-002:** the prior copy/paste wrapper used a top-level `exit` after deployment failure. In an interactive SSH shell that exits the login shell. v4.1.2 documents and tests a subshell wrapper so deployment failure returns a status without terminating the operator session.

## Regression evidence

`deployment/qnap/tests/test-compose-discovery.sh` proves the normal `docker compose` path, the direct Compose V2 plugin fallback path, and rejection of Compose V1. CI executes the regression before building the release bundle.

## Security boundary

The fix does not expand MCP authority, container privileges, network exposure, state authority, or secret handling. Plugin discovery is local-only and restricted to an executable path reported by the local Docker client or known Docker/Container Station installation locations. The canonical Phase 1 authority/runtime contract remains 4.0.0.

## Release identity

- QNAP deployment release: 4.1.2
- semantic tag: v4.1.2
- image label default: 4.1.2-qnap
- Phase 1 agent/runtime authority contract: 4.0.0 unchanged
- workforce: exactly 10 registered agents
- Message Operations remains the tenth registered agent
- Mesh Devil's Advocate remains an external governed shared Skill

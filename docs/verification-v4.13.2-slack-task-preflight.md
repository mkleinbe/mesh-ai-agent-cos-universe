# Verification v4.13.2 Slack Interaction Task Preflight

Status: IN PROGRESS until final main-branch release gates pass.

Required evidence:

- missing task fails before any Slack API call;
- valid task behavior remains unchanged;
- full pytest passes with 100% `mesh_cos` coverage;
- Ruff, mypy, Bandit, compile, contract, doc-drift, owner-readiness, capability-closure, and published-surface checks pass;
- QNAP POSIX deployment regressions pass;
- exact-current-source QNAP 4.4.0 candidate and checksum pass;
- production-equivalent container and MCP discovery/sequential request checks pass;
- tag, GitHub Release, assets, and final `main` SHA agree.

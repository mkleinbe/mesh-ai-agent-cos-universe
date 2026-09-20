# Verification: QNAP 4.4.1 Source Identity

Independent verification must bind to the exact candidate commit.

Required evidence:

- QNAP POSIX and source-identity regression tests pass.
- Bundle metadata commit equals candidate Git SHA.
- Production-equivalent image OCI revision equals candidate Git SHA.
- Modern MCP test observes the exact governed `source_commit`.
- QNAP verifier rejects any mismatch between release metadata, running OCI revision, and MCP `source_commit`.
- Candidate Compose startup forces recreation.
- Full Python tests retain 100% `mesh_cos` coverage.
- Ruff, mypy, Bandit, contract drift, capability closure, and published-action-surface checks pass.
- Live production readback reports `deployment_release=4.4.1` and the exact merged/released source commit.

A local script PASS without exact source-commit readback is insufficient.

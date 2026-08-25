# Operations Runbook

Current repository/QNAP deployment release: **`v4.1.7 QNAP Image Provenance and Hosted Envelope Verification`**.  
Canonical Phase 1 authority/runtime contract: **`4.0.0`**.

This runbook distinguishes repository readiness, QNAP deployment readiness, and published ChatGPT app acceptance. Local engineering uses bundled stdio. Production ChatGPT operation uses the installed **Mesh CoS MCP** app through the **OpenAI Secure MCP Tunnel** to the QNAP-hosted runtime.

## Repository certification path

1. Confirm the Python package, MCP package, Workspace manifests, and canonical MCP authority contract remain `4.0.0`.
2. Confirm `agents/registry.json` contains exactly 10 registered agents and only Mesh Devil's Advocate is externalized as a shared Skill.
3. Confirm the QNAP deployment train is `4.1.7` in `Dockerfile`, `.env.example`, prepare defaults, release bundle, CI, and release workflow.
4. Run the full release suite.
5. Confirm no agent catalog contains human-only operations and the CoS production catalog remains exactly 27 tools.
6. Confirm release-image provenance and the running governed response-envelope verification gates are present.

## Full release suite

```bash
python -m pip check
cd mcp && npm ci && npm run check && cd ..
python scripts/validate-contracts.py
python scripts/check-runtime-doc-drift.py
python scripts/check-chatgpt-packages.py
ruff check src
ruff check tests scripts --select E9,F63,F7,F82
mypy src --check-untyped-defs
pytest --cov=mesh_cos --cov-report=term-missing --cov-report=xml --cov-fail-under=100
bandit -q -r src -lll
python -m compileall -q src
bash scripts/build-qnap-release-bundle.sh 4.1.7
```

Repository CI additionally builds and exercises the production image, validates its OCI release version/revision against the exact candidate commit, renders QNAP Compose, proves dual release identity, runs modern MCP discovery and governed tool-envelope checks, validates direct-ingress denial, checks non-root/read-only/no-capability/no-Docker-socket controls, and verifies SQLite backup/restart recovery.

## QNAP deployment path

1. Place `mesh-cos-mcp-qnap-v4.1.7.zip` and its `.sha256` receipt in `/share/Docker`.
2. Follow `deployment/qnap/DEPLOYMENT-STEPS.md` using the SSH-safe subshell block and host-side `sudo` required by the QNAP Docker operator account.
3. Preserve `/share/Docker/cos-mcp/state`, the canonical TaskLedger, existing Secure MCP tunnel ID, and tunnel runtime-key file.
4. Require pre-deploy backup and release-metadata/environment equality.
5. Before local image reuse, require OCI `org.opencontainers.image.version=4.1.7-qnap` and `org.opencontainers.image.revision=<bundle commit>`. A mismatch must rebuild from the extracted release build context.
6. Require image provenance revalidation, Compose rendering, container health, runtime preflight, actual governed `registry.get_agent` envelope verification, ingress denial, and post-deploy backup.
7. Verify `/healthz` and `/readyz` report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
transport: SECURE_MCP_TUNNEL
```

The remote process must fail closed if `MESH_COS_DEPLOYMENT_RELEASE` is missing or blank. The deployment must also fail if the real governed tool response omits or mismatches `deployment_release`.

## Published ChatGPT app acceptance

After local QNAP deployment verification passes:

1. Open/refresh the installed **Mesh CoS MCP** app and confirm it points to the intended OpenAI Secure MCP Tunnel.
2. Run Scan Tools and require exactly 27 CoS tools.
3. Confirm `approval.record_decision` and `reliability.human_override` are absent.
4. Run the sequential read-only acceptance in `deployment/qnap/CHATGPT-ACCEPTANCE.md` without restarting either container.
5. Require no HTTP 502, `invalid_session`, reconnect, or restart.
6. Require exactly 10 registered agents, `message-ops` present, and no Devil's Advocate agent principal.
7. Require every successful governed tool envelope to report `mcp_version=4.0.0`, `deployment_release=4.1.7`, and `agent_id=cos`.
8. Run the optional idempotent governed-write acceptance only when a production write is explicitly intended.

Any successful hosted response that omits `deployment_release` is a release blocker even when the underlying tool result is correct.

## Authority checks

Before activation or acceptance verify:

- no agent catalog contains `approval.record_decision` or `reliability.human_override`;
- the separately authenticated human path contains only the intended human tools;
- CoS is the only Phase 1 agent with `task.verify`;
- appropriate accountable owners have `task.complete`;
- Message Operations cannot record its own approval;
- Devil's Advocate is not an MCP principal;
- direct-child and delegation-depth restrictions are active;
- deployment-release metadata and image-provenance metadata do not affect tool selection or authority.

## Task operation

Accountable owners progress work through normal lifecycle states. At QA, `task.complete` persists the outcome and evidence and transitions to `COMPLETED`. Completion without evidence fails. Duplicate completion does not silently mutate state.

A separate verifier evaluates the acceptance test. Passing `task.verify` requires explicit evidence. Phase 1 exposes that agent operation only to CoS. Failed verification routes to `REWORK`; passing routes to `VERIFIED`.

## Delegation operation

CoS delegates to registered direct children. COO may delegate to Consultant Network Steward at depth 2. The Steward is terminal. Authority widening, circular delegation, approval weakening, non-direct children, and depth-3 attempts fail closed.

## Incident controls

If the kill switch, ledger integrity, audit chain, identity binding, source authority, approval evidence, MCP package, deployment identity, image provenance, governed response envelope, or Secure MCP Tunnel ingress boundary is invalid, stop consequential execution. Do not improvise around a failed gate.

If a human-only operation appears in an agent catalog, treat it as a security defect and disable the affected agent until corrected.

If a completed task lacks evidence or a non-CoS agent reaches `VERIFIED`, treat it as a lifecycle/governance defect and preserve the audit trail for remediation.

If hosted calls regress to HTTP 502, `invalid_session`, or missing `deployment_release`, capture the QNAP diagnostic log, running image ID, OCI version/revision labels, bundle release metadata, and container health first. Do not rotate tunnel credentials, delete TaskLedger state, or rebuild the environment until the boundary is isolated.

## Historical state

Do not use the v3.0.0 9-agent topology as current deployment guidance. It remains a historical release snapshot and is superseded by the v4.0.0 authority contract. The v4.1.x deployment train adds production transport and QNAP hardening without changing that 10-agent authority model.

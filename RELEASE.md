# v4.1.14 QNAP Protected-Secret Provisioning Remediation

`v4.1.14` supersedes v4.1.13 for QNAP deployment. v4.1.13 correctly established the governed Slack human approver, but a real QNAP upgrade exposed an operator-path portability defect when the protected Slack verifier credential was absent: normal deployment entered hidden secret input and required PATH-resolved `stty`, failing with `stty is required for hidden secret input` after the staged candidate preflight had already passed.

v4.1.14 separates ordinary deployment from first-time or deliberate protected-secret provisioning. Normal upgrades validate and preserve existing credentials non-interactively. Missing protected credentials fail closed and direct the operator to an explicit provisioning command.

The full deployment-path pressure test also found the same hidden-input assumption in first-time OpenAI tunnel runtime-key handling. That sibling defect is remediated in the same release so the normal deployment path contains no hidden secret-entry dependency.

The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly 10 registered agents and 27 governed CoS MCP tools. Human-only operations remain human-only. Message Operations remains one of the 10 agents; Mesh Devil's Advocate remains a governed shared Skill and is not an agent principal.

## Core changes

- `mesh-cos-slack-hitl-configure.sh` is non-interactive for protected Slack credentials.
- Existing Slack verifier `xoxb-...` and Socket Mode `xapp-...` files are validated and preserved.
- Missing or invalid Slack credentials fail closed and direct the operator to `mesh-cos-slack-hitl-provision.sh`.
- The verified human approver remains `U01KG3CNYHK`; `D...` conversation IDs remain rejected as human principals.
- `mesh-cos-qnap-secret-input.sh` centralizes QNAP/BusyBox-compatible no-echo secret input for explicit provisioning commands only.
- The helper prefers shell-native silent read, can fall back to an explicitly resolved `/bin/stty` or `/usr/bin/stty`, and refuses to capture a secret if terminal echo cannot be disabled safely.
- `mesh-cos-tunnel-key-provision.sh` isolates first-time or deliberate OpenAI tunnel runtime-key entry from ordinary deployment.
- `mesh-cos-mcp-prepare.sh` now preserves an existing tunnel key or fails closed with the explicit provisioning instruction. It no longer performs hidden secret input.
- Provisioned secrets are written atomically, excluded from logs and release artifacts, and normalized to runtime ownership `65532:65532` with mode `0400`.
- Existing release-root, TaskLedger, tunnel identity, qnet/static IP, container hardening, and backup controls remain intact.

## Security boundary

Security applicability is **TARGETED**. See `docs/qnap-security-review-v4.1.14.md`.

Secret values are not accepted through command-line arguments, source files, release metadata, generated runtime environment, or ordinary deployment logs. Explicit provisioning requires safe no-echo terminal capture and fails closed if that cannot be established. No network, MCP-tool, agent, approval, persistence, or commercial authority is widened.

## BDD and TDD evidence

Ready scenarios QNAP-100 through QNAP-103 in `specs/qnap-slack-secret-provisioning-v4.1.14.feature` cover non-interactive upgrades, missing-credential fail-closed behavior, safe explicit provisioning, and continued Slack principal validation.

A behavior-level regression recreates the original missing-verifier condition with `stty` removed from PATH and proves the old deployment error cannot recur in the normal Slack configuration path. Existing v4.1.13 approver-bootstrap and earlier QNAP behavior specifications remain retained as regression evidence.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.14.zip`
- `mesh-cos-mcp-qnap-v4.1.14.zip.sha256`

## Version identity

- Repository/QNAP deployment release: `4.1.14`
- Semantic tag: `v4.1.14`
- Container image label default: `4.1.14-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Workforce: exactly 10 agents
- CoS agent-facing catalog: 27 governed tools
- Production transport: OpenAI Secure MCP Tunnel
- Human Slack approval ingress: authenticated Slack Socket Mode `/mesh-approval`

Successful hosted readiness after deployment must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.14
agent_id: cos
slack_hitl_ready: true
```

## Verification gate

The exact final candidate must pass dependency integrity, TypeScript/npm checks, contract/document/package drift checks, Ruff, mypy, 100 percent branch-aware Python coverage, Bandit, compileall, QNAP POSIX shell regressions, the behavior-level missing-`stty` regression, exact v4.1.14 archive-prefix inspection, protected-secret artifact inspection, deterministic checksum generation, Compose validation, OCI provenance, modern MCP discovery/sequential requests, protected Slack HITL controls, non-root/read-only runtime controls, direct-ingress denial, restart/persistence, and Docker-mediated SQLite backup integrity.

## QNAP deployment

Normal upgrade when all protected files already exist:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.14/mesh-cos-mcp-deploy.sh
```

If the deploy reports a missing Slack verifier or Socket Mode credential, provision only the missing protected credential(s), then rerun deployment:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.14/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.1.14/mesh-cos-mcp-deploy.sh
```

If the OpenAI tunnel runtime key is missing, use the dedicated tunnel-key provisioner and rerun deployment. Existing production upgrades should preserve the current tunnel key.

## Post-deploy acceptance boundary

Repository, container, and release-package verification cannot prove the actual on-premises serving instance, official OpenAI Workspace Agent Slack delivery, or live Slack Socket Mode human interaction.

After deploying v4.1.14, execute `docs/chatgpt-published-app-production-acceptance-v4.1.14.md`. Do not certify production while any CRITICAL/HIGH defect or required live acceptance blocker remains open.

See:

- `docs/qnap-security-review-v4.1.14.md`
- `docs/verification-v4.1.14-qnap-slack-secret-provisioning.md`
- `docs/release-4.1.14-qnap-slack-secret-provisioning.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.14.md`
- `specs/qnap-slack-secret-provisioning-v4.1.14.feature`
- `docs/qnap-slack-approver-bootstrap-v4.1.13.md`
- `specs/qnap-slack-approver-bootstrap-v4.1.13.feature`
- `docs/slack-agent-protocol.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

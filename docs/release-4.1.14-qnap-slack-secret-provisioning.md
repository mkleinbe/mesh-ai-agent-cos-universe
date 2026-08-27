# v4.1.14 QNAP Slack Protected-Secret Provisioning Remediation

## Scope

v4.1.14 fixes the QNAP deployment failure observed in v4.1.13 after the staged candidate preflight passed and Slack HITL configuration entered `verifier_token`.

## Root cause

The v4.1.13 normal deployment path combined two concerns that must be separate on QNAP: upgrade-time validation/preservation of protected credentials and first-time interactive secret provisioning. When the verifier token file was missing or empty, `mesh-cos-slack-hitl-configure.sh` entered `read_secret_tty`, confirmed `/dev/tty` was readable, then required `command -v stty` before reading the secret. On the observed QNAP sudo/BusyBox execution path that command did not resolve, so deployment failed with `stty is required for hidden secret input`.

The evidence does not prove whether the host lacks every `stty` binary or whether sudo/PATH excluded it. That distinction is no longer deployment-critical in v4.1.14 because the normal deploy path has no `stty` dependency and performs no interactive secret entry.

The v4.1.13 regression suite missed this path because its Slack test pre-created valid verifier and Socket Mode credentials and only exercised non-interactive approver bootstrap.

## Remediation

- Normal deployment is strictly non-interactive for protected Slack credentials.
- Existing verifier and Socket Mode files are validated and preserved.
- Missing or invalid credentials fail closed with an explicit instruction to run `mesh-cos-slack-hitl-provision.sh`.
- First-time or deliberate credential replacement is isolated in `mesh-cos-slack-hitl-provision.sh`.
- Provisioning prefers shell-native silent input when supported, falls back to an explicitly resolved `stty` binary only inside the provisioning command, and refuses input if terminal echo cannot be disabled safely.
- The governed Michael approver remains `U01KG3CNYHK`; Slack `D...` conversation IDs remain invalid human principals.
- Secret values remain excluded from logs, artifacts, command lines, process arguments, and release metadata.

## Preserved invariants

- Canonical Phase 1 runtime/authority contract remains `4.0.0`.
- Exactly 10 agents remain registered.
- Message Operations remains agent 10.
- Devil's Advocate remains a governed shared Skill, not agent 11.
- CoS agent-facing MCP catalog remains exactly 27 governed tools.
- Human-only operations remain excluded from agent catalogs.
- `COMPLETED != VERIFIED`.
- Canonical persistence remains the SQLite TaskLedger.
- OpenAI Secure MCP Tunnel remains production ingress.

## QNAP operator sequence

After downloading and checksum-verifying the v4.1.14 bundle, extract it under the canonical releases directory.

If both protected Slack credential files already exist and are valid, run only the normal deployment command:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.14/mesh-cos-mcp-deploy.sh
```

If deployment reports a missing verifier or Socket Mode token, provision the protected credentials once and rerun deployment:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.14/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.1.14/mesh-cos-mcp-deploy.sh
```

Do not place Slack tokens on a command line, in shell variables exported by the operator, or in release files.

## Acceptance boundary

Repository and release verification do not constitute production acceptance. After QNAP deployment, complete QNAP runtime, Secure MCP Tunnel, published ChatGPT app, and live Slack `/mesh-approval` acceptance before declaring production accepted.

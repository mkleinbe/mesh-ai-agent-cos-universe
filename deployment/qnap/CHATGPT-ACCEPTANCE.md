# ChatGPT Secure MCP Tunnel Connection and Acceptance

Run this only after the **v4.1.16** deployment reports successful release-root validation, pre-deploy backup, candidate health, transactional promotion, verification, and post-deploy backup.

The production ChatGPT surface is the published **Mesh CoS MCP** app connected to the QNAP-hosted runtime through the **OpenAI Secure MCP Tunnel**. The canonical Phase 1 authority/runtime contract remains **4.0.0**. The QNAP deployment release is independently identified as **4.1.16**.

v4.1.16 retains the v4.1.15 connected-Slack collaboration boundary and authenticated `/mesh-approval` Socket Mode human ingress, and adds the restarting-runtime backup remediation.

## 1. Local deployment identity

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/healthz').then(r=>r.text()).then(console.log)"
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires application image `mesh-cos-mcp:qnap-v4.1.16`, both containers healthy, and:

```text
mcp_version: 4.0.0
deployment_release: 4.1.16
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_ready: true
```

Do not print protected Slack or tunnel files.

## 2. Restarting-runtime backup evidence

If the prior runtime was restarting, the pre-deploy backup receipt must show `state_export_method=quiesced_helper` and source state `restarting`. The backup path must not use `docker exec` against that restarting source. The old runtime must be quiesced before SQLite backup, the one-shot helper must be network-isolated and credential-free, and the resulting TaskLedger backup must pass integrity/SHA-256 checks.

Do not manually copy, replace, truncate, or delete the canonical TaskLedger to make acceptance pass.

## 3. Release-root and promotion evidence

Confirm operator release root `/share/Docker/cos-mcp/releases`, retained release directory `/share/Docker/cos-mcp/releases/v4.1.16`, staged and active `version=4.1.16`, no state/secrets beneath the release directory, and no unresolved `.release-rollback.*` snapshot after successful deployment.

## 4. QNAP network evidence

PASS requires MCP qnet `192.168.7.60`, tunnel private source `172.30.60.3`, internal-only `mesh-cos-private`, tunnel egress `172.30.61.2`, no second tunnel qnet address, and no direct MCP host port.

## 5. Slack protected configuration

The governed user principal is `U01KG3CNYHK`. Only `U...` or `W...` user-principal forms are eligible. The protected Socket Mode app-level token must be `xapp-...`. No `xoxb-` verifier token is required, mounted, validated, prompted for, or used.

## 6. Tool catalog and authority

The CoS-bound published app must expose exactly **27 agent-facing tools** and exactly 10 registered agents. Human-principal-only `approval.record_decision` and `reliability.human_override` must not appear. Mesh Devil's Advocate remains a shared Skill, not an agent principal.

## 7. Request-contract and lifecycle acceptance

Synthetic `task.intake` idempotency must return the same canonical task for the same explicit key. Invalid request fields must return bounded `validation_failed` details. Lifecycle must preserve `COMPLETED != VERIFIED` through separate `task.complete` and authorized `task.verify` operations.

## 8. Governed Skill and connected Slack handoff acceptance

A CoS Slack handoff using `operation: handoff`, channel `C0BRL4GCL3A`, and synthetic payload must return:

```text
execution_mode: CHATGPT_CONNECTOR_HANDOFF
authority: COLLABORATION_ONLY
```

It must not change canonical approval state. Authority-like fields or decision operations must fail closed.

## 9. Audit integrity

Call `governance.verify_audit_chain` before and after synthetic acceptance writes. PASS requires `valid: true` both times.

## 10. Slack authenticated human-interaction gate

Create a synthetic PENDING L4 approval owned by canonical principal `michael` with an immutable 64-hex `payload_fingerprint`.

PASS requires ordinary Slack text and connected Slack writes to remain non-authoritative; provider-authenticated `/mesh-approval APPROVE <Approval ID>` from user `U01KG3CNYHK` in the governed channel records the canonical decision; wrong user/channel/command, missing fingerprint, or conflicting second interaction fails closed; same-envelope replay is idempotent; and fresh canonical readback reflects the exact decision.

## 11. Provider-degradation gate

Slack provider/network outage must not terminate the MCP HTTP process. `/healthz` remains available, `/readyz` fails closed for required Slack HITL, consequential approval remains blocked, and reconnect remains bounded.

## 12. Consequential-action exclusion

Do not perform prospect sends, public publishing, client commitments, pricing/discount approvals, final staffing commitments, reliability human overrides, or other consequential real-world actions during acceptance.

## 13. Pass rule

Base v4.1.16 hosted acceptance passes only when the actual Mesh CoS MCP app demonstrates correct release identity, restarting-runtime backup remediation where applicable, release-root provenance, deterministic QNAP network identity, `slack_hitl_ready=true`, schema/validation behavior, canonical TaskLedger lookup, lifecycle separation, governed Skill/Slack handoff enforcement, authorization boundaries, and valid audit chain.

Full production certification additionally requires `chatgpt-published-app-production-acceptance-v4.1.16.md`, zero open CRITICAL/HIGH defects, and no required acceptance blocker.
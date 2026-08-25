# QNAP mesh-cos-mcp Security Review

Status: v4.1.3 targeted remediation candidate. Live QNAP acceptance remains operator-executed after repository, bundle, and container verification.

| ID | Severity | Component | Evidence / consequence | Remediation / retest | Residual risk | Owner |
|---|---|---|---|---|---|---|
| SEC-QNAP-001 | High | TaskLedger persistence | A missing SQLite file could create a duplicate operating universe | `MESH_COS_REQUIRE_EXISTING_LEDGER=true` rejects missing/in-memory ledgers; prepare only stages an explicitly selected existing source when the canonical target is absent and preserves an existing target | Source selection is a human canonical-truth decision | Platform owner / human operator |
| SEC-QNAP-002 | High | SQLite concurrency | Multiple overlapping Python bridge writers could contend on SQLite | Process-wide bounded bridge queue serializes MCP calls; multi-agent shared-write container fan-out remains prohibited | External writers outside this service remain an operational risk | Platform owner |
| SEC-QNAP-003 | High | Remote MCP ingress | A LAN-addressed MCP listener could otherwise be callable by ordinary LAN clients | `/mcp` accepts only `172.30.60.3`, the tunnel sidecar on the isolated bridge; no host ports are published; verify proves direct non-tunnel denial | Docker private-network compromise could reach MCP | Platform owner |
| SEC-QNAP-004 | High | Tunnel credential | Environment or command-line injection could expose the runtime key | Key capture uses terminal echo disabled; value is stored only in the 0400 file and excluded from `.env`, release assets, logs, and backups | QNAP administrator/root can access the secret file by design | Human operator |
| SEC-QNAP-005 | High | Identity | Caller-controlled identity would break agent isolation | `MESH_COS_AGENT_ID=cos` remains process-bound and validated against canonical allowlists | Environment mutation requires container-control authority | Platform owner |
| SEC-QNAP-006 | High | Human-principal boundary | Human-only operations must never become agent-callable | Canonical MCPRuntime excludes `approval.record_decision` and `reliability.human_override` from all agent catalogs | Contract changes require action refresh/review | Governance owner |
| SEC-QNAP-007 | High | Reliability replay | Client-controlled replay content could become RCE | Runtime only invokes server-registered replay executors; arbitrary shell/source/import/callable payloads remain rejected | New replay executors require security review | Platform owner |
| SEC-QNAP-008 | Medium | Long-running container privilege | QNAP application could gain NAS authority through root/capabilities/socket | Application remains UID/GID 65532, read-only rootfs, `cap_drop: ALL`, no-new-privileges, no Docker socket, no host PID/IPC/network, no devices | Live Container Station behavior must match rendered Compose | Human operator |
| SEC-QNAP-009 | Medium | Resource exhaustion | Model-controlled payloads/sessions could consume CPU/RAM or spawn unbounded bridge work | Existing request/response/session/queue bounds and 2 CPU/24 GiB main limit remain; no PID limit by explicit operator requirement | Process-count exhaustion is not independently capped | Platform owner |
| SEC-QNAP-010 | Medium | Deployment/runtime logging | Naive diagnostics could capture secrets or excessive sensitive state | v4.1.3 structured diagnostics omit secret-file contents, `.env`, process environments, credential-bearing argv, and tunnel logs; bounded app-log tails are defensively redacted | Future commands must continue using safe labels and must not intentionally emit secrets to stdout/stderr | Platform owner |
| SEC-QNAP-011 | Medium | Supply chain / image identity | Mutable tags could change without review | Mesh image is built from release-bound bundled context and recorded by image ID; tunnel-client resolves to RepoDigest/image ID; Compose uses `pull_policy: never` | Mesh image is not separately signed/published | Release owner |
| SEC-QNAP-012 | Medium | Backup integrity | Active SQLite file copy can be inconsistent or host ownership can block export | Online backup uses SQLite backup API; v4.1.3 exports via Docker daemon and verifies SHA-256/integrity while excluding secrets | Same-NAS destination does not protect total NAS loss | Human operator |
| SEC-QNAP-013 | Medium | Network exposure | QNAP admin UI or raw port exposure would expand attack surface | Outbound-only Secure MCP Tunnel; no router forwarding, host networking, or published MCP port | LAN health/readiness may remain reachable where policy permits | Network owner |
| SEC-QNAP-014 | Medium | Controlled HTTPS fallback | Weak custom auth could be introduced | Runtime refuses remote auth modes other than `tunnel` | None until fallback is implemented | Security owner |
| SEC-QNAP-015 | Medium | Prompt injection | Untrusted text could attempt authority expansion | Canonical allowlists, identity, lifecycle, approvals, delegation, replay, and Skill governance remain server-side | New tools/Skills require continuing review | Governance owner |
| SEC-QNAP-016 | Medium | Deployment automation | Automation could overwrite state or leak credentials | Existing ledger is preserved, source selection is explicit, ledger staging uses UID-65532 stdin streaming, secret input is hidden, and secret material is absent from `.env`/backups/log collection | Operator can intentionally select the wrong canonical source | Human operator |
| SEC-QNAP-017 | Low | QNAP Compose executable discovery | PATH-only assumptions can fail or broad search could create local execution risk | Resolver is bounded to Docker-reported and known Docker/Container Station locations, requires executable permission and Compose V2, and rejects V1 | Host administrator can replace local Docker binaries, equivalent to existing host authority | Platform owner |
| SEC-QNAP-018 | Medium | QNAP filesystem authority | v4.1.2 assumed Docker access implied host `chown`; live QTS rejected the ownership operation, blocking deployment. A broad privileged helper would overcorrect | v4.1.3 uses a one-shot helper with `--network none`, read-only rootfs, no Docker socket, `--cap-drop ALL`, only required ownership/mode capabilities, validated numeric identity, and only explicit state or secrets bind mount. Actual bind-mount integration is required in CI | Docker-authorized operator already has substantial container-host authority; helper scope must remain bounded in future edits | Platform owner |
| SEC-QNAP-019 | Medium | Canonical-state permission verification | Host-user `[ -r ]/[ -w ]` checks would incorrectly require SSH-user access to runtime-owned state and encourage weakening file modes | v4.1.3 validates owner/mode and actual read/write access through UID/GID 65532 in a network-disabled container | QNAP ACL semantics can still vary across firmware; live acceptance remains required | Platform owner |
| SEC-QNAP-020 | Low | Docker CLI configuration | Container Station default Docker config path is unreadable to the SSH operator, producing warnings and environment ambiguity | v4.1.3 sets deployment-local `DOCKER_CONFIG` under the app root with operator ownership | Private registry credentials would require a separately governed credential design; current images are public/local | Platform owner |

## v4.1.3 targeted review receipt

Security applicability: **TARGETED**.

Changed trust/sensitive surfaces: Docker operator execution, QNAP shared-folder ownership, canonical persistence, backup export, secret-adjacent file ownership, and diagnostic logging.

Required properties:

1. no host root or `sudo` requirement;
2. no privileged helper and no Docker socket in helper/application containers;
3. helper network disabled and root filesystem read-only;
4. all helper capabilities dropped before only required ownership/mode capabilities are added;
5. helper bind mounts limited to state or secrets;
6. runtime remains UID/GID 65532;
7. canonical ledger preserved and source selection remains human-owned;
8. no secret value, `.env`, process environment, credential argv, or tunnel logs in automated diagnostics;
9. no MCP/network/authority expansion;
10. Docker-mediated backup preserves SQLite integrity and secret exclusion.

The candidate requires shell regression evidence plus actual Docker bind-mount/runtime/backup evidence before this receipt can be classified verified. No design-level critical/high defect is introduced by the proposed remediation. Live QNAP filesystem behavior remains an external acceptance boundary until the v4.1.3 bundle is run on the target NAS.

## Threat-boundary conclusions

ChatGPT/model content remains untrusted for authority. The one-shot permission helper is operator-side deployment infrastructure only and is not MCP-callable. Secure MCP Tunnel, tool allowlists, the 10-agent roster, human-only operations, `COMPLETED != VERIFIED`, and the single canonical SQLite writer remain unchanged.

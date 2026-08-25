# QNAP mesh-cos-mcp Security Review

Status: v4.1.2 release candidate. Repository/container controls and the QNAP Compose-discovery regression are independently verified in CI; live QNAP and ChatGPT product-surface acceptance remain operator-executed.

| ID | Severity | Component | Evidence / consequence | Remediation / retest | Residual risk | Owner |
|---|---|---|---|---|---|---|
| SEC-QNAP-001 | High | TaskLedger persistence | A missing SQLite file could create a duplicate operating universe | `MESH_COS_REQUIRE_EXISTING_LEDGER=true` rejects missing/in-memory ledgers; prepare only stages an explicitly selected existing source when the canonical target is absent and preserves an existing target | Source selection is a human canonical-truth decision | Platform owner / human operator |
| SEC-QNAP-002 | High | SQLite concurrency | Multiple overlapping Python bridge writers could contend on SQLite | Process-wide bounded bridge queue serializes MCP calls; multi-agent shared-write container fan-out remains prohibited | External writers outside this service remain an operational risk | Platform owner |
| SEC-QNAP-003 | High | Remote MCP ingress | A LAN-addressed MCP listener could otherwise be callable by ordinary LAN clients | `/mcp` accepts only `172.30.60.3`, the tunnel sidecar on the isolated bridge; no host ports are published; verify proves direct non-tunnel denial and tests LAN denial when qnet host routing permits | Docker private-network compromise could reach MCP | Platform owner |
| SEC-QNAP-004 | High | Tunnel credential | Environment or command-line injection could expose the runtime key | The key is captured with terminal echo disabled, written only to the approved 0400 file, mounted read-only, and excluded from `.env` and backups | QNAP administrator/root can access the secret file by design | Human operator |
| SEC-QNAP-005 | High | Identity | Caller-controlled identity would break agent isolation | `MESH_COS_AGENT_ID=cos` is process-bound and validated against canonical allowlists | Environment mutation requires container-control authority | Platform owner |
| SEC-QNAP-006 | High | Human-principal boundary | Human-only operations must never become agent-callable | Canonical MCPRuntime excludes `approval.record_decision` and `reliability.human_override` from all agent catalogs | Contract changes require action refresh/review | Governance owner |
| SEC-QNAP-007 | High | Reliability replay | Client-controlled replay content could become RCE | Runtime only invokes server-registered replay executors; arbitrary shell/source/import/callable payloads remain rejected | New replay executors require security review | Platform owner |
| SEC-QNAP-008 | Medium | Container privilege | QNAP container could gain NAS authority through root/capabilities/socket | Non-root UID/GID, read-only rootfs, `cap_drop: ALL`, no-new-privileges, no Docker socket, no host PID/IPC/network, no devices | Live Container Station behavior must match rendered Compose | Human operator |
| SEC-QNAP-009 | Medium | Resource exhaustion | Model-controlled payloads/sessions could consume CPU/RAM or spawn unbounded bridge work | 1 MB requests, 2 MB bridge responses, 30 s timeout, bounded bridge queue, max 8 MCP sessions, 2 CPU/24 GiB main limit, tunnel CPU/RAM limit, log rotation; no PID limit by explicit operator requirement | Process-count exhaustion is not independently capped | Platform owner |
| SEC-QNAP-010 | Medium | Logging | Raw args/secrets could leak through NAS logs | Structured logs omit arguments/raw errors; tunnel key is never placed in `.env` | Dependencies must continue avoiding secret logging | Platform owner |
| SEC-QNAP-011 | Medium | Supply chain / image identity | Mutable tags could change without review | Mesh image is built from the release-bound bundled context and recorded by image ID; tunnel-client resolves to RepoDigest/image ID; Compose uses `pull_policy: never` | Mesh image is not separately signed/published | Release owner |
| SEC-QNAP-012 | Medium | Backup integrity | Active SQLite file copy can be inconsistent or secrets could be copied | Online backup uses SQLite backup API and integrity verification; backup excludes `secrets/` | Same-NAS destination does not protect total NAS loss | Human operator |
| SEC-QNAP-013 | Medium | Network exposure | QNAP admin UI or raw port exposure would expand attack surface | Outbound-only Secure MCP Tunnel; no router forwarding, host networking, or published MCP port | LAN health/readiness may remain reachable where policy permits | Network owner |
| SEC-QNAP-014 | Medium | Controlled HTTPS fallback | Weak custom auth could be introduced | Runtime refuses remote auth modes other than `tunnel` | None until fallback is implemented | Security owner |
| SEC-QNAP-015 | Medium | Prompt injection | Untrusted text could attempt authority expansion | Canonical allowlists, identity, lifecycle, approvals, delegation, replay, and Skill governance remain server-side | New tools/Skills require continuing review | Governance owner |
| SEC-QNAP-016 | Medium | Deployment automation | Automation could overwrite state or leak credentials | Existing ledger is preserved, source selection is explicit when target is absent, secret input is hidden, and secrets are absent from `.env`/backups | Operator can intentionally select the wrong canonical source | Human operator |
| SEC-QNAP-017 | Low | QNAP Compose executable discovery | A PATH-only assumption caused fail-closed deployment even though Compose V2 was installed. Broad executable search would create a local execution risk | v4.1.2 restricts fallback to the Docker-reported Compose plugin path and known Docker/Container Station installation locations, requires executable permission, and validates a Compose V2 version response. Regression tests cover subcommand, plugin fallback, and V1 rejection | A QNAP administrator with filesystem control can replace Docker/Compose binaries, which is already equivalent to container-host authority | Platform owner |

## Threat-boundary conclusions

- Trust model: ChatGPT and model-controlled/retrieved text remain untrusted for authority. Registry, role contracts, TaskLedger state, approval records, and runtime policy remain authoritative.
- Network model: Secure MCP Tunnel remains outbound-only and `/mcp` remains restricted to the private sidecar address.
- Execution model: no generic shell or arbitrary code path is introduced to MCP callers. The Compose resolver is an operator-side local deployment helper with a bounded candidate set and V2 validation.
- Persistence model: one writable MCP process remains authoritative for SQLite.
- Authentication model: tunnel authentication continues to use the official tunnel client and file-mounted runtime key.
- Release model: the bundle carries the exact Mesh build context and verifies prepared image IDs.

## Targeted v4.1.2 review receipt

Security applicability is **TARGETED** because deployment/runtime shell execution changed. The changed trust boundary is limited to local Compose executable resolution on the QNAP host. Required properties are: no network exposure change, no secret-handling change, no authority expansion, no arbitrary PATH traversal, executable candidate must be locally bounded, and Compose V1 must fail closed. The regression test and CI shell/build/container gates provide the required candidate evidence. No new unresolved high/critical finding was identified by this targeted review.

## Live acceptance still required

Product/operator-side checks remain: OpenAI tunnel creation/association/permissions, runtime credential issuance, canonical-ledger source selection if needed, QNAP firewall/access-control policy outside Docker, total-NAS-loss backup policy, and end-to-end ChatGPT MCP acceptance.

# QNAP mesh-cos-mcp Security Review

Status: candidate review, not production certification. Production remains human-approved and blocked on live QNAP acceptance.

| ID | Severity | Component | Evidence / consequence | Remediation / retest | Residual risk | Owner |
|---|---|---|---|---|---|---|
| SEC-QNAP-001 | High | TaskLedger persistence | Production bridge previously could create a missing SQLite file, risking a duplicate operating universe | `MESH_COS_REQUIRE_EXISTING_LEDGER=true` now rejects missing and in-memory ledgers; unit and container readiness tests | QNAP mount availability and filesystem behavior still require live test | Platform owner |
| SEC-QNAP-002 | High | SQLite concurrency | One Python process was spawned per call, allowing overlapping writers | Process-wide bounded bridge queue serializes calls; multi-agent shared-write deployment is prohibited | External writers outside this service remain an operational risk | Platform owner |
| SEC-QNAP-003 | High | Remote MCP ingress | A LAN-addressed MCP listener could otherwise be callable by ordinary LAN clients | `/mcp` accepts only `172.30.60.3`, the tunnel sidecar on the isolated bridge; no host ports are published | Docker private-network compromise could reach MCP | Platform owner |
| SEC-QNAP-004 | High | Tunnel credential | Environment injection would expose the runtime key through container metadata | Runtime key is mounted read-only and consumed through official `file:` configuration | QNAP file ACLs still require live verification | Human operator |
| SEC-QNAP-005 | High | Identity | Caller-controlled identity would break agent isolation | `MESH_COS_AGENT_ID=cos` is process-bound, validated against canonical allowlists, and request metadata cannot override it | Environment mutation requires container-control authority | Platform owner |
| SEC-QNAP-006 | High | Human-principal boundary | Human-only operations must never become agent-callable | Canonical MCPRuntime and contract exclude `approval.record_decision` and `reliability.human_override`; existing security tests and smoke certification enforce this | Contract changes require ChatGPT action refresh/review | Governance owner |
| SEC-QNAP-007 | High | Reliability replay | Client-controlled replay content could become RCE | Canonical runtime only invokes registered replay executors; arbitrary shell/source/import/callable payloads remain rejected | New replay executors require security review | Platform owner |
| SEC-QNAP-008 | Medium | Container privilege | QNAP container could gain NAS authority through root/capabilities/socket | Non-root UID/GID, read-only rootfs, `cap_drop: ALL`, no-new-privileges, no Docker socket, no host PID/IPC/network, no devices | Container Station support for every control must be proven live | Human operator |
| SEC-QNAP-009 | Medium | Resource exhaustion | Model-controlled payloads/sessions could consume CPU/RAM/PIDs or spawn unbounded bridge work | 1 MB requests, 2 MB bridge responses, 30 s timeout, bounded queue, max 8 MCP sessions, CPU/RAM/PID limits, log rotation | Application-level rate limiting is delegated to tunnel/control plane; live workload tuning required | Platform owner |
| SEC-QNAP-010 | Medium | Logging | Raw args/secrets could leak through NAS logs | Structured stderr logs include correlation ID, agent, tool, result classification, latency only; arguments and raw errors are omitted | Canonical Python dependencies must continue avoiding secret logging | Platform owner |
| SEC-QNAP-011 | Medium | Supply chain | Mutable images could change without review | Production Compose requires explicit image values; runbook requires immutable digests and OpenAI provenance/SBOM verification | Mesh image signing/provenance workflow is not yet a production release artifact | Release owner |
| SEC-QNAP-012 | Medium | Backup integrity | File copy of active SQLite can be inconsistent | Online SQLite backup utility uses `sqlite3.Connection.backup()` and `integrity_check`; stop/snapshot alternative documented | Actual QNAP snapshot semantics and encryption/retention remain unverified | Human operator |
| SEC-QNAP-013 | Medium | Network exposure | QNAP admin UI or raw port exposure would materially expand attack surface | Selected mode is outbound-only Secure MCP Tunnel; no UPnP, router forwarding, host networking, or published MCP port | `192.168.7.60` still exposes health/readiness to trusted LAN by design | Network owner |
| SEC-QNAP-014 | Medium | Controlled HTTPS fallback | Weak custom auth could be introduced for convenience | Candidate refuses any remote mode other than `tunnel`; HTTPS fallback requires separate OAuth/TLS/reverse-proxy security approval | None until fallback is implemented | Security owner |
| SEC-QNAP-015 | Medium | Prompt injection | Untrusted natural language could attempt authority expansion | Canonical allowlists, process identity, lifecycle, approval, delegation, replay, and Skill governance remain server-side | New tools/Skills require continuing adversarial review | Governance owner |

## Threat-boundary conclusions

- Trust model: ChatGPT and all model-controlled or retrieved text are untrusted for authority. Canonical registry, role contracts, TaskLedger state, approval records, and runtime policy remain authoritative.
- Network model: OpenAI Secure MCP Tunnel is outbound-only. The MCP protocol endpoint is restricted to the dedicated private sidecar IP and is not published on a QNAP host port.
- Execution model: no generic shell, source-code, module-import, callable, Docker-socket, privileged-container, or host-namespace execution path is introduced.
- Persistence model: Phase 1 uses one writable MCP process against canonical SQLite. Future 10-agent container fan-out is blocked until a single ledger-owner service exists or QNAP filesystem locking/concurrency is proven.
- Authentication model: tunnel runtime authentication uses the official OpenAI tunnel client and runtime key. No custom bearer-token scheme was invented.

## Production blockers

The security review cannot be marked complete until live QNAP evidence verifies UID/GID, share ACLs, filesystem behavior, free space, Container Station support for the Compose security controls, `lan7` and private-subnet non-overlap, IP availability, DNS/HTTPS egress, NTP, firewall state, tunnel-client non-root behavior, restart persistence, backup/restore, and end-to-end ChatGPT operation.

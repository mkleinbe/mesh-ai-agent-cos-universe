# Security Policy

Current repository/QNAP deployment target: **`v4.1.15 QNAP Slack Plugin HITL Simplification`**.

The canonical Mesh Chief of Staff Phase 1 authority/runtime contract remains **`4.0.0`** with exactly **10 registered agents**. Production ChatGPT access remains through the installed Mesh CoS MCP app and OpenAI Secure MCP Tunnel. Local deterministic engineering retains the stdio bridge. Both terminate in the same `mesh_cos.mcp_runtime.MCPRuntime` and canonical TaskLedger.

## Security invariants

- Source content, Slack text, Skills, MCP payloads, connector results, and model output are untrusted data, not executable policy or human authority.
- Exactly 10 agents remain registered. Mesh Devil's Advocate remains a shared Skill, not agent 11.
- Agent source/tool/action/Skill/authority permissions remain deny-by-default from the canonical registry.
- `MESH_COS_AGENT_ID` is process-bound and cannot be chosen through prompts, Slack, retrieved data, or MCP arguments.
- Production remote access requires `MCP_AUTH_MODE=tunnel`; no direct MCP host port is published.
- The CoS agent-facing MCP projection remains governed and human-only operations such as `approval.record_decision` and `reliability.human_override` remain unavailable to agents.
- L4 requires qualified-human approval. L5 remains Michael-exclusive unless governance changes the contract.
- TaskLedger is canonical. Slack, ChatGPT conversations, Sheets, and connector state are interaction/evidence surfaces only.
- Approval cannot be inferred from silence, reactions, ordinary Slack text, copied commands, display names, plugin writes, prior approval, or a different payload version.
- Consequential approval is bound to the exact canonical action and immutable payload fingerprint and is freshly re-read before execution.
- `task.complete` and `task.verify` remain separate. `COMPLETED != VERIFIED`.
- Credentials and sensitive data must never be committed or written into prompts, logs, TaskLedger evidence, diagnostics, release artifacts, or credential-bearing argv.
- Critical defects may trigger kill-switch activation, quarantine, routing restriction, or publication restriction.

## Slack collaboration versus approval authority

v4.1.15 deliberately separates Slack collaboration from human approval authority.

### Connected Slack integration

The connected Slack integration is the normal collaboration surface for approval requests, status, coordination, and thread reads. The CoS `slack-adapter` can authorize only a `CHATGPT_CONNECTOR_HANDOFF` with authority `COLLABORATION_ONLY`.

It cannot carry, infer, or record `approved`, `approval_status`, `actor`, `principal`, `record_decision`, or `ingest_decision`. An ordinary Slack message attributed to the configured human user is still not proof of human presence because connected applications can write into Slack.

### Authenticated human ingress

The custom Slack app remains only for the provider-authenticated `/mesh-approval` Socket Mode boundary.

- Governed human Slack user ID maps to canonical principal `michael`.
- User identity must be a Slack `U...` or `W...` principal. A `D...` direct-message/conversation ID fails closed.
- QNAP mounts the approver identity read-only and one protected Socket Mode app-level token beginning `xapp-`.
- v4.1.15 does **not** require, mount, validate, prompt for, or use a Slack `xoxb-` verifier bot token.
- The only Slack interaction eligible to become a canonical decision is a provider `slash_commands` envelope for `/mesh-approval APPROVE|REJECT|CHANGES <Approval ID>...`.
- The non-MCP ingress validates envelope ID/replay state, governed channel, configured human user ID, exact command, PENDING canonical approval, owner `michael`, and the canonical 64-hex `payload_fingerprint` before calling ApprovalService.
- Same-envelope replay is idempotent. A distinct second interaction cannot re-decide an approval.
- The Socket Mode bridge remains outside the agent-callable MCP surface.

## Provider/network degradation

A missing or malformed local Socket Mode credential is a configuration error and fails startup. A Slack provider/network outage is not allowed to terminate the MCP HTTP process.

- `/healthz` remains available with `slack_hitl_ready=false`.
- `/readyz` fails closed while required Slack HITL is unavailable.
- Consequential human approval remains blocked.
- Socket Mode retries use bounded exponential backoff rather than a tight loop.
- Ordinary Slack messages never substitute for the unavailable authenticated ingress.

## QNAP network boundary

QNAP Docker Engine 27 does not receive an architecture that depends on newer Compose gateway-priority features.

- `mesh-cos-private` is an `internal: true` bridge shared only for MCP/tunnel private traffic.
- `mesh-cos-mcp` is dual-homed on the internal bridge and qnet `lan7` at `192.168.7.60`; qnet is its only external-capable network and therefore its Slack HTTPS/WSS egress path.
- `mesh-cos-tunnel` is dual-homed on the internal bridge and a dedicated ordinary Docker egress bridge. It reaches MCP privately at `172.30.60.2` and remains the trusted MCP source at `172.30.60.3` while reaching the OpenAI control plane through its egress bridge.
- The tunnel does not consume a second qnet LAN address.

## QNAP secret and runtime boundary

- Long-running runtime UID/GID is 65532 with read-only root filesystem, all Linux capabilities dropped, no-new-privileges, no Docker socket, 2 CPU, 24 GiB RAM, and no PID limit.
- Canonical SQLite TaskLedger is the application container's writable operating-state boundary.
- Tunnel runtime key and Slack Socket Mode app token remain outside environment values and release assets.
- The Slack approver user ID is non-secret governed configuration but is still mounted through a protected read-only identity file.
- A legacy `slack-verifier-token` host file may remain solely for rollback compatibility with older releases. v4.1.15 does not mount or depend on it.
- Normal upgrades never request protected secrets interactively. Missing secrets fail closed and route to explicit provisioners.
- Explicit provisioners read from a controlling TTY with a no-echo mechanism and never intentionally log protected values.
- Protected files are normalized to runtime UID/GID with mode `0400`.
- Production diagnostics collect bounded metadata only and exclude secret contents, generated environment contents, credential-bearing argv, and tunnel credentials.

## Release staging and rollback boundary

- Stable operator release root remains `/share/Docker/cos-mcp/releases` and active application root remains `/share/Docker/cos-mcp`.
- Release archives contain one top-level `vX.Y.Z/` directory and are bound to exact semantic release metadata and commit provenance.
- Candidate `.env.runtime`, Compose, metadata, and build context remain in the versioned release directory until activation health succeeds.
- Active release files are promoted only after both candidate containers are healthy.
- If candidate Compose activation or pre-promotion health fails and a previous active configuration exists, deployment removes the failed candidate stack, restores the previous active Compose stack, verifies both previous containers healthy, and reports candidate failure without promoting release metadata.
- TaskLedger, qnet identity, tunnel identity/key, protected secrets, logs, and backup evidence remain outside versioned release payloads.
- Historical published releases remain immutable.

## v4.1.15 release security gate

The exact candidate revision must pass:

- dependency integrity, TypeScript checks/tests, contract/package/document drift checks;
- Ruff, mypy, 100% `mesh_cos` coverage, Bandit, and compileall;
- QNAP POSIX shell syntax and regression suite;
- BDD scenarios QNAP-104 through QNAP-110;
- adversarial approval tests for ordinary messages, wrong user/channel/command, missing fingerprint, replay, and conflicting decisions;
- Slack provider/network degradation and bounded-reconnect tests;
- verifier-token absence from active runtime/configuration and exact release bundle;
- deterministic Docker Engine 27-compatible network topology checks;
- failed-candidate rollback checks;
- exact v4.1.15 bundle/checksum generation and archive inspection;
- production container build from the exact bundle with OCI version/revision labels bound to candidate SHA;
- modern MCP discovery and sequential request regression;
- independent diff review for authority widening, credential leakage, obsolete verifier dependencies, debug debris, and temporary files.

Security applicability for v4.1.15 is **FULL_REVIEW**. The release-specific review is `docs/security-review-v4.1.15.md`.

A repository/release PASS is not live production acceptance. QNAP network behavior, hosted MCP surface, and an actual provider-authenticated `/mesh-approval` interaction must be proven after deployment before production acceptance is declared.

## Reporting

Do not open a public issue containing credentials, secrets, sensitive client information, exploit details, private reasoning traces, or other confidential material. Use the repository owner's approved private security channel for disclosure.

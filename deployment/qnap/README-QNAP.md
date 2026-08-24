# mesh-cos-mcp on QNAP Container Station

## Selected production topology

Mode A uses OpenAI Secure MCP Tunnel. `mesh-cos-mcp` has the requested LAN identity `192.168.7.60` on the existing external `lan7` macvlan, while tunnel traffic uses dedicated bridge `172.30.60.0/29`. `/mcp` accepts only the tunnel sidecar at `172.30.60.3`. No host ports are published and no router port-forwarding or UPnP is required.

The canonical Python `MCPRuntime` remains in the same image and is invoked through the existing Node/Python bridge. No parallel business logic, Redis, PostgreSQL, NGINX, queue, message bus, or second TaskLedger was introduced.

## Production prerequisites

Before deployment, complete `deployment/qnap-environment.md` from fresh NAS evidence. The included `qnap-environment-probe.sh` is read-only and BusyBox-compatible. Verify `lan7`, confirm `192.168.7.60` is unused, confirm `172.30.60.0/29` does not overlap Docker/VPN networks, resolve the narrow shared-folder path and UID/GID, and verify free space and filesystem behavior.

The canonical file `/var/lib/mesh/ledger/taskledger.sqlite3` must already exist in the mounted QNAP state root. Production mode refuses to create a missing ledger. Resolve both images to immutable digests before production. Do not use `latest` or another moving tag.

Create the OpenAI tunnel and a separate runtime API key with Tunnels Read + Use. Do not use an admin key for the long-running runtime. Store the runtime key in a dedicated QNAP file outside Git, readable only by the required operator/container principal. The Compose application mounts it read-only and passes it to the official tunnel client through `file:/run/secrets/openai_tunnel_api_key`.

## Container Station installation runbook

1. In QTS, verify Container Station is installed and running. Record its exact version in `deployment/qnap-environment.md`.
2. Reconfirm `uname -m` is `x86_64` and that the candidate image is `linux/amd64`.
3. Run the read-only QNAP environment probe or collect equivalent UI evidence. Record CPU, RAM, storage pool, filesystem, free space, hostname, interfaces, Virtual Switch, DNS, NTP, firewall, snapshot/backup, and existing port/IP usage.
4. Verify the external Docker macvlan network `lan7` is the approved `192.168.7.0/24` network and that `192.168.7.60` is unused.
5. Verify `172.30.60.0/29` does not overlap existing Docker, VPN, LAN, or routed networks.
6. Create or select one narrow Mesh state folder. Do not mount all of `/share`.
7. Create the state structure required by the canonical runtime, including `ledger/`, governance/audit/runtime locations already used by the repository, and an operator-controlled backup destination.
8. Resolve the exact QNAP owner UID/GID required for the state folder. Grant only the access necessary for the Mesh runtime. Record owner, group, mode, read paths, and write paths.
9. Stage the approved canonical `taskledger.sqlite3` at `<QNAP_MESH_ROOT>/ledger/taskledger.sqlite3`. Do not initialize an empty production database as a workaround.
10. Create a separate narrow secret file containing only the OpenAI tunnel runtime API key. Restrict its host permissions and record only the path, never the value.
11. Build the Mesh candidate from the reviewed commit for `linux/amd64`. Run the repository verification suite and record the resulting image digest and provenance/SBOM evidence.
12. Pull/verify OpenAI `tunnel-client` release `v0.0.12` or the then-approved reviewed release. Verify official provenance/SBOM evidence and resolve its immutable image digest.
13. Copy `.env.example` to a local `.env` outside Git. Replace all placeholders, including the two image digests, QNAP state root, secret-file path, runtime UID/GID, and tunnel ID.
14. Run `docker compose -f deployment/qnap/compose.yaml config` from an expert shell, or use Container Station's application YAML validation, before creation. Any unsupported security control is a release blocker until explicitly resolved.
15. Run the QNAP ProductionPreflight using the candidate image and mounted state. It must report `ok:true`. Do not bypass a failed check.
16. In Container Station, choose **Applications** and create a new application named `mesh-cos-mcp` from `deployment/qnap/compose.yaml`, supplying the approved environment values.
17. Confirm the rendered application contains exactly two services: `mesh-cos-mcp` and `tunnel-client`; one private bridge `mesh-cos-private`; and external network `lan7`. Confirm no `ports:` mappings, privileged mode, host networking, Docker socket, devices, host PID/IPC, or broad share mounts exist.
18. Deploy only after human release approval. Confirm `mesh-cos-mcp` becomes healthy before the tunnel sidecar starts.
19. Inspect Container Station logs. Confirm structured Mesh tool logs contain correlation ID, agent ID, tool name, result classification, and latency without arguments, secrets, tokens, or raw sensitive payloads.
20. Verify `http://192.168.7.60:8080/healthz` and `/readyz` from an authorized LAN operator workstation. Because macvlan can isolate the QNAP host itself from the container IP, use Container Station health status or an authorized LAN workstation rather than treating host-to-macvlan reachability as mandatory.
21. Verify a direct LAN POST to `http://192.168.7.60:8080/mcp` is rejected with HTTP 403. The MCP protocol path is reserved for the tunnel sidecar's private IP.
22. Confirm tunnel-client health/readiness inside Container Station. It must have outbound HTTPS access to `api.openai.com:443` and private reachability to `http://mesh-cos-mcp:8080/mcp`; it requires no inbound tunnel port.
23. In OpenAI Platform Tunnels management, verify the approved tunnel ID and that the runtime identity has Tunnels Read + Use. Associate the intended ChatGPT workspace according to current OpenAI controls.
24. In ChatGPT Settings > Connectors/Apps, create the custom MCP app using **Connection = Tunnel** and select the approved tunnel. Scan tools and compare the result to the canonical `cos` allowlist. Human-only operations must be absent.
25. Execute one controlled read-only CoS operation and verify the result, canonical TaskLedger state, and audit record. Then execute one approved governed write that does not cross an L4/L5 human-only boundary. Confirm `COMPLETED != VERIFIED` where applicable.
26. Restart the `mesh-cos-mcp` container. Verify `cos` identity, readiness, ledger integrity, and canonical state remain unchanged.
27. Recreate the Container Station application using the same approved Compose and state root. Verify no duplicate operating universe is created.
28. Perform an online SQLite backup using `deployment/qnap/sqlite_backup.py`, verify its hash and integrity, and perform the documented restore drill before production certification.
29. Reboot the QNAP during the controlled acceptance window. Verify Container Station/application auto-start, remount, `cos` identity, TaskLedger integrity, tunnel recovery, and readiness.
30. Record the deployed Mesh image digest, tunnel image digest, Compose revision, state-root path, tunnel ID, acceptance evidence, operator, and approval record. Treat any subsequent tool-contract change as requiring ChatGPT action refresh/review.

## Useful expert commands

The routine operating path is Container Station UI. CLI commands are diagnostic and verification alternatives only.

```sh
# Read-only host discovery
sh deployment/qnap/qnap-environment-probe.sh

# Render Compose without changing the NAS
docker compose --env-file deployment/qnap/.env -f deployment/qnap/compose.yaml config

# Runtime preflight inside the running application
docker exec mesh-cos-mcp python3 deployment/qnap/runtime_preflight.py

# Safe online SQLite backup
docker exec mesh-cos-mcp python3 deployment/qnap/sqlite_backup.py \
  --source /var/lib/mesh/ledger/taskledger.sqlite3 \
  --destination /var/lib/mesh/backups/taskledger-YYYYMMDD-HHMMSS.sqlite3
```

## QNAP shell constraints

QNAP host automation must remain compatible with the platform's BusyBox shell. Do not assume GNU-only host utilities. Routine deployment should use Container Station UI; shell commands are for diagnosis and expert operation.

## Controlled HTTPS fallback

Mode B is intentionally not implemented or activated by this candidate. It requires explicit human approval, a dedicated FQDN, trusted TLS, approved OAuth/OIDC resource-server configuration, QNAP reverse-proxy validation, firewall/access controls, and rate limiting. The runtime fails closed for remote modes other than `tunnel`. Do not substitute a static bearer token or expose raw container port 8080 to the internet.

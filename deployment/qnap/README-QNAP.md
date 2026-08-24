# mesh-cos-mcp on QNAP Container Station

## Selected topology
Mode A, OpenAI Secure MCP Tunnel. `mesh-cos-mcp` has the requested LAN identity `192.168.7.60` on existing external `lan7`, while tunnel traffic uses dedicated bridge `172.30.60.0/29`. `/mcp` accepts only the tunnel sidecar at `172.30.60.3`. No host ports are published and no router port-forwarding or UPnP is required.

The canonical Python `MCPRuntime` remains in the same image and is invoked through the existing bridge. No parallel business logic, Redis, PostgreSQL, NGINX, queue, or message bus was introduced.

## Before deployment
1. Complete `deployment/qnap-environment.md` from fresh NAS evidence.
2. Verify `lan7` exists and `192.168.7.60` is unused.
3. Select a narrow QNAP shared folder and UID/GID. Do not mount `/share` broadly.
4. Create `ledger/taskledger.sqlite3` from the approved canonical state before startup. Production mode refuses a missing ledger.
5. Build and test the image for `linux/amd64`; record its digest. Do not use `latest`.
6. Verify the OpenAI tunnel image provenance and record its digest before production.
7. Copy `.env.example` to `.env`, set real values locally, and restrict permissions.
8. Create the OpenAI tunnel and runtime API key with Tunnels Read + Use. Associate the target ChatGPT workspace.
9. In Container Station, create an Application from `compose.yaml` plus `.env`.
10. Confirm both services are healthy, then create the ChatGPT custom app using Connection = Tunnel and scan tools.

## QNAP shell constraints
QNAP host automation must remain compatible with the platform's BusyBox shell. Routine deployment should use Container Station UI. Shell commands in this package are diagnostic alternatives, not required for normal operation.

## Controlled HTTPS fallback
Mode B is intentionally not activated. It requires explicit human approval, a dedicated FQDN, trusted TLS, approved OAuth/OIDC resource-server configuration, QNAP reverse-proxy validation, firewall/access controls, and rate limiting. The runtime fails closed for remote modes other than `tunnel`; do not substitute a static bearer token.

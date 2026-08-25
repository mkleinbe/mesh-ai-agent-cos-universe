# Mesh CoS MCP Contract

`mesh-cos-mcp.v1.json` remains the canonical Phase 1 **4.0.0 authority contract**. It defines the 10 registered agent principals, deny-by-default tool allowlists, immutable agent identity, human-only catalog, delegation rules, and completion/verification boundary.

Repository release **v4.1.0** adds the production QNAP transport without changing those authority semantics.

## Transport model

Local Workspace engineering/certification retains `LOCAL_STDIO`:

```text
Workspace Agent -> node mcp/dist/index.js -> canonical MCPRuntime -> TaskLedger
```

The QNAP deployment packages the same MCP server logic behind the MCP SDK Streamable HTTP transport:

```text
ChatGPT -> OpenAI Secure MCP Tunnel -> /mcp -> canonical MCPRuntime -> TaskLedger
```

The production HTTP transport does not accept caller-selected agent identity and does not expand the contract's tool allowlist. In the initial Phase 1 QNAP deployment the immutable process identity is `cos`.

## Agent versus human catalogs

`agent_tool_allowlists` is deny-by-default. `human_tool_allowlist` contains exactly `approval.record_decision` and `reliability.human_override`; neither may appear in an agent catalog.

## Completion contract

`task.complete` produces `COMPLETED` only and requires outcome plus evidence. `task.verify` is separate, exposed only to CoS in Phase 1, and requires explicit acceptance evidence.

## Certification

Local stdio certification remains part of `npm run check`. QNAP production acceptance adds container, persistence, tunnel, backup/restore, restart, and ChatGPT end-to-end verification before production activation.

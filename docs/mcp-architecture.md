# mesh-cos-mcp Remote Architecture

```text
ChatGPT custom app
  -> OpenAI Secure MCP Tunnel
  -> tunnel-client (172.30.60.3)
  -> Streamable HTTP /mcp
  -> mesh-cos-mcp (172.30.60.2, LAN 192.168.7.60)
  -> existing Node allowlist and Python bridge
  -> canonical MCPRuntime
  -> canonical SQLite TaskLedger + governance/audit state
```

The existing stdio entrypoint remains supported for engineering certification. Remote transport adds no parallel business logic. Runtime agent identity remains process-bound through `MESH_COS_AGENT_ID=cos`; caller text, headers, request arguments, Skills, retrieved content, and connectors cannot alter it.

The selected Phase 1 deployment is one writable MCP process. `TaskLedger` is SQLite with the canonical implementation's current journaling/locking behavior. The Node gateway serializes Python bridge calls to avoid overlapping writers inside this process. Multi-agent containers must not share-write this database until QNAP filesystem locking/concurrency is independently proven or a single ledger-owner service is introduced.

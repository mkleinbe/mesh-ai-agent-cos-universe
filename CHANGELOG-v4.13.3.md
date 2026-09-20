# v4.13.3

## Fixed

- Persist Slack provider-confirmed channel and root thread identity into the canonical TaskRecord as well as the secondary task thread index.
- Count each provider-authenticated, manually authored human Slack interaction exactly once in TaskRecord.human_touches.
- Make human-touch persistence replay-safe by atomically recording the provider event and incrementing the canonical task.
- Preserve strict approval authority, lifecycle separation, provider reread, manual-authorship checks, and the locator-only dispatcher.
- Advance the immutable QNAP deployment candidate identity to 4.4.2 because runtime source changes.

No production Compose topology, Secure MCP Tunnel trust boundary, Slack secret mount, principal, approval grammar, or L0-L5 authority is changed.

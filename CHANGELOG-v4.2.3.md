# Changelog v4.2.3

## Fixed

- Added bounded QNAP/qnet egress-readiness retries to the post-deploy Slack provider-read gate.
- Retries are limited to transport-level network exceptions. Slack provider responses with `ok:false`, invalid provider responses, and internal verifier failures remain immediate hard failures.
- Preserved the v4.2.2 Slack GET/query provider transport repair, corrected Slack App ID `A0B49RNE4K0`, native event-triggered HITL authority model, and fail-closed rollback behavior.

## Production evidence

Two consecutive v4.2.2 deployments built and promoted the correct candidate, reached local container health, then failed the first Slack `conversations.history` provider-read check with `network_error` and rolled back to v4.2.1. The same v4.2.2 image, mounted with the same protected bot token but sharing the already-stable v4.2.1 `mesh-cos-mcp` network namespace, immediately returned `ok:true` from Slack. This isolates the defect to fresh QNAP/qnet external-egress readiness timing rather than the v4.2.2 image, Slack OAuth token, Slack scopes, channel membership, or Slack API contract.

## Security

- No new Slack scopes, credentials, ingress paths, MCP tools, agents, or authority surfaces.
- Trigger remains locator-only.
- Provider text and identity remain untrusted until QNAP rereads Slack.
- Only network exceptions are retried; provider authorization and policy failures remain fail-closed.
- Retry logs contain only bounded attempt metadata and sanitized machine error codes.

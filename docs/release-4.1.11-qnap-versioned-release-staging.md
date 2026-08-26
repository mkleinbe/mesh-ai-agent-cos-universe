# v4.1.11 QNAP Versioned Release Staging Remediation

v4.1.11 supersedes the defective v4.1.10 QNAP deployment artifact without changing the v4.1.10 scheduled-automation or Slack HITL product behavior.

## Why this patch exists

The v4.1.10 bundle was generated successfully and matched its published checksum, but its operator scripts assumed helpers lived directly under `/share/Docker` while release payload metadata was read from the canonical `/share/Docker/cos-mcp` root. That violated the established versioned staging convention and caused a real deployment attempt to fail first on helper lookup and then on a release-identity mismatch after scripts were manually copied.

## Corrected release contract

- Git tag: `v4.1.11`
- runtime deployment release: `4.1.11`
- OCI image version: `4.1.11-qnap`
- canonical MCP/runtime authority contract: `4.0.0`
- canonical runtime root: `/share/Docker/cos-mcp`
- versioned staging root: `/share/Docker/cos-mcp/releases/v4.1.11`
- exactly 10 registered Mesh agents
- exactly 27 governed CoS MCP tools
- Message Operations remains agent 10
- Devil's Advocate remains a governed shared Skill, not an agent
- human-only operations remain human-only
- `COMPLETED != VERIFIED`

## Deployment behavior

The extracted bundle is self-contained at its versioned release root. Operator scripts self-resolve that root and do not require helper files to be copied to `/share/Docker`.

Preparation reads candidate release metadata and build context from the versioned release payload. It derives the normal runtime release from staged metadata rather than a patch-specific constant or the active `.env`. An explicitly supplied `vX.Y.Z` is normalized to `X.Y.Z`, while a true requested-versus-staged mismatch still fails closed.

The canonical TaskLedger, tunnel runtime key, Slack protected files, and qnet/static networking remain in their existing canonical paths. The candidate gets a staged `.env.runtime`; active `.env`, Compose, and release metadata are promoted only after the application and tunnel containers become healthy.

## v4.1.10 behavior retained

The scheduled execution and Slack HITL security behavior introduced by v4.1.10 is carried forward unchanged: explicit scheduled idempotency, canonical lifecycle transitions, official OpenAI bot notice binding, non-authoritative ordinary Slack text, authenticated Socket Mode `/mesh-approval`, provider verification, protected Slack runtime files, and fail-closed readiness.

## Verification boundary

Repository and release-package verification can establish a corrected candidate and artifact. It cannot establish actual QNAP production acceptance or live OpenAI Workspace Agent and Slack Socket Mode behavior. Those require deployment of the v4.1.11 artifact and hosted acceptance against the real serving instance.

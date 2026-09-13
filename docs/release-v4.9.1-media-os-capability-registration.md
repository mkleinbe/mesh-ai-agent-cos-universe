# v4.9.1 Media OS Capability Registration

Release date: September 13, 2026

## Purpose

v4.9.1 makes the already-approved Mesh Media Production OS capability registration a coherent, verified repository release. It closes the stale regression that caused `main` CI to fail after PR #77 and preserves the existing authority model.

## Capability contract

CMO receives:

- `mesh-media-production`
- `mesh-media-verification`
- `mesh-media-distribution`

VP Content receives:

- `mesh-media-production`

VP Content does not receive Media OS verification or distribution and retains zero delegation authority. CMO remains L3 for marketing recommendation and bounded L2 internal execution. Public publishing remains human-gated.

## Runtime identity

- Repository release: `v4.9.1`
- Canonical authority/runtime contract: `4.0.0`, unchanged
- Production QNAP deployment before operator promotion: `4.4.0`
- Registered agents: exactly 10, unchanged
- Database/schema migration: none
- New principal: none
- New public-publishing authority: none

The release produces a current-source QNAP `4.4.0` candidate through canonical CI. That candidate must be deployed through the existing transactional QNAP deployment procedure and independently read back before production runtime activation is claimed.

## Verification

Required evidence includes:

1. full repository CI at 100% `mesh_cos` coverage;
2. Media OS registry tests and the reconciled historical direct-binding regression;
3. capability closure, owner-execution readiness, runtime/document drift, ChatGPT package drift, published action surface, Ruff, mypy, Bandit, QNAP POSIX regressions, current-source QNAP bundle, container provenance, and MCP transport tests;
4. exact-SHA v4.9.1 publication after verification;
5. post-deployment live CoS registry readback before Media OS runtime acceptance.

## Rollback

Repository rollback is the prior verified source/tag. QNAP rollback uses the existing transactional deployment backup and immutable prior runtime state. Do not rewrite TaskLedger, approvals, or audit history to roll back this capability registration.

# Mesh CoS v4.13.4 Marketing Authority Delegation Hardening

This PATCH release packages the verified PR #91 remediation for download.

## Source identity

- Release tag: `v4.13.4`
- Runtime source commit: `0968d7acd603d9164e174648d32139561673e015`
- QNAP deployment identity: `4.4.2`
- Canonical MCP authority/runtime contract: `4.0.0`

## Runtime asset

`mesh-cos-mcp-qnap-v4.4.2.zip` is rebuilt from the exact PR #91 merge commit and retains exact source provenance.

## CMO Skill asset

`skill.zip` is the standalone `mesh-cmo` Skill from the same exact source commit. It includes the hardened CMO -> VP Content delegation contract, including canonical server-derived ownership metadata, fail-closed compatibility assertions, same-graph bounded recovery, and preserved inherited approval gates.

## Verification

The exact runtime target passed repository CI run 35787140306. The standalone CMO Skill was independently validated with the Skill validator and a representative deterministic behavior probe before release publication.

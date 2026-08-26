# QNAP Release-Root Bootstrap v4.1.12

## Purpose

v4.1.12 removes the remaining operator path choreography from QNAP deployment. The stable operator working directory is:

```text
/share/Docker/cos-mcp/releases
```

The release ZIP itself creates the version directory. For v4.1.12 the archive contains one top-level prefix:

```text
v4.1.12/
```

After extraction, the candidate is therefore located at:

```text
/share/Docker/cos-mcp/releases/v4.1.12
```

The operator does not create that directory manually and does not copy, move, or chmod release payload files.

## Artifact contract

`mesh-cos-mcp-qnap-v4.1.12.zip` contains:

```text
v4.1.12/
  mesh-cos-mcp-deploy.sh
  mesh-cos-mcp-preflight.sh
  mesh-cos-mcp-prepare.sh
  mesh-cos-mcp-backup.sh
  mesh-cos-mcp-verify.sh
  mesh-cos-slack-hitl-configure.sh
  mesh-cos-qnap-*.sh
  cos-mcp/
    compose.yaml
    release-metadata.txt
    build-context/
    documentation and acceptance evidence
```

There are no loose release scripts at `/share/Docker/cos-mcp/releases` after extraction.

## Script path contract

Operator scripts resolve their own directory with POSIX `dirname`, `cd`, and `pwd -P`. They do not depend on the caller's current directory and do not use QNAP-incompatible `realpath` or `readlink -f` requirements.

The deployment orchestrator validates before candidate preparation that:

- its resolved parent is `/share/Docker/cos-mcp/releases`;
- its resolved basename is `v4.1.12`;
- staged `cos-mcp/release-metadata.txt` declares runtime release `4.1.12`.

A genuine mismatch fails closed.

`QNAP_RELEASES_ROOT` exists only to support an explicit isolated test fixture or governed non-production root. Production defaults to `/share/Docker/cos-mcp/releases`.

## Canonical runtime separation

Release payloads are immutable staging inputs. Canonical runtime data remains outside the release directory:

- application root: `/share/Docker/cos-mcp`
- state: `/share/Docker/cos-mcp/state`
- secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

The candidate `.env.runtime`, build context, Compose descriptor, and release metadata remain within the versioned release folder until deployment health checks pass. Active runtime descriptors are promoted only after candidate health.

## Operator flow

With the ZIP and checksum already placed in `/share/Docker/cos-mcp/releases`:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.1.12.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.12.zip
sudo sh ./v4.1.12/mesh-cos-mcp-deploy.sh
```

The deployment orchestrator performs pre-deploy backup, preparation, Slack HITL protected configuration, preflight, Compose deployment, health waits, promotion, verification, and post-deploy backup.

## Authority boundary

This is a release-engineering correction only. The canonical Phase 1 authority/runtime contract remains `4.0.0`, with exactly 10 agents and 27 governed CoS tools. Human-only operations remain excluded from agent catalogs, Message Operations remains agent 10, Mesh Devil's Advocate remains a governed shared Skill, and `COMPLETED != VERIFIED` remains mandatory.

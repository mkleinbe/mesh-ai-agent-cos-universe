# Security Review v4.1.16

Status: IN PROGRESS
Applicability: FULL_REVIEW
Subject: QNAP restarting-runtime pre-deploy backup hotfix

## Security properties

1. Canonical TaskLedger integrity must not be weakened to bypass a broken active runtime.
2. A restarting container must never be treated as a stable `docker exec` target merely because Docker reports `.State.Running=true`.
3. Fallback backup must quiesce potential writers before reading canonical SQLite state.
4. The one-shot helper must use the exact already-trusted active Mesh image, no network, non-root UID/GID, read-only root filesystem, dropped capabilities, and no-new-privileges.
5. The helper may write only the governed state mount required to materialize a temporary SQLite backup.
6. The SQLite backup helper must open the canonical source read-only, use SQLite backup semantics, and pass `PRAGMA integrity_check` before export.
7. A failed helper or export must remove temporary and partial backup artifacts and must not claim success.
8. If the source runtime had running intent before quiescence, that intent must be restored after either success or failure.
9. No protected Slack or tunnel credential may be mounted into or exposed to the backup helper.
10. Existing v4.1.15 authentication, approval, network-ingress, secret, and transactional-promotion controls remain unchanged.

## Trust boundaries reviewed

- QNAP host root deployment process -> Docker daemon
- Docker daemon -> exact active Mesh image
- helper container -> canonical TaskLedger bind mount
- canonical state -> governed backup root
- deployment backup gate -> candidate preparation

## Required evidence

- RED evidence from QNAP-112..QNAP-115 before implementation
- behavioral shell regression for `status=restarting` with `.State.Running=true`
- behavioral failure regression proving helper failure restores running intent and leaves no successful partial backup
- stable online backup path retained
- POSIX shell syntax regression
- 100% Python test gate retained
- Bandit and dependency gates retained
- exact v4.1.16 bundle and container provenance verification
- no secret mounts or network access in the quiesced helper command

## Release rule

This receipt may move to PASS only when the exact release candidate has fresh evidence for every required check and no open CRITICAL/HIGH security finding. Live QNAP production acceptance remains separate from repository security verification.

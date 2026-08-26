# QNAP Versioned Release Staging Remediation v4.1.11

## Incident

The published v4.1.10 QNAP bundle was valid by checksum but violated the established versioned release-directory convention. A deployment attempt from `/share/Docker/cos-mcp/releases/v4.1.10` first failed because helper scripts were resolved from `/share/Docker`. After helper scripts were manually copied there, preparation failed the release identity gate because the scripts then read active v4.1.8 metadata from `/share/Docker/cos-mcp` instead of staged v4.1.10 metadata.

The active v4.1.8 containers and canonical TaskLedger remained intact. The pre-deployment Docker-mediated online SQLite backup completed successfully. Application filesystem utilization was 96 percent; the absolute free-space gate passed. Capacity remains an operational risk, but it was not the causal deployment failure.

## Falsifiable hypotheses and findings

### H1 CONFIRMED

Root cause is hard-coded helper-root binding because v4.1.10 operator scripts defaulted `QNAP_SCRIPT_ROOT` to `/share/Docker`, which predicts a missing helper when the script is executed from a versioned release directory. The observed failure was `observability helper missing: /share/Docker/mesh-cos-qnap-observability.sh` while the helper existed in the extracted release root.

### H2 CONFIRMED

Root cause is active-runtime configuration being read as candidate configuration because v4.1.10 preflight defaulted `APP_ROOT` to `/share/Docker/cos-mcp`, which predicts that a preflight launched from a v4.1.10 staging directory can still report v4.1.8. The observed preflight reported release 4.1.8 and rendered the v4.1.8 image.

### H3 NOT REQUIRED TO EXPLAIN INCIDENT

`sudo` environment filtering is not needed to reproduce the failure. v4.1.10 preparation hard-coded a 4.1.10 default while reading metadata from the active application root. v4.1.11 removes the normal dependency on a release environment variable so standard `sudo sh ./mesh-cos-mcp-deploy.sh` is deterministic.

### H4 CONFIRMED

Root cause is moving scripts away from their bundle because v4.1.10 used script-root-relative helpers but application-root-relative metadata. Copying scripts to `/share/Docker` satisfied helper lookup while leaving candidate metadata lookup bound to the active root. That predicts the observed mismatch gate failure.

### H5 PARTIALLY CONFIRMED

The v4.1.10 release artifact is structurally defective for the required execution model, but its internal release metadata is not stale. The published asset was generated for v4.1.10 and its checksum matched the release. The defect is path/layout binding, not a corrupted download.

### H6 CONFIRMED AS A CONTRACT GAP

Git tag `vX.Y.Z` and runtime deployment `X.Y.Z` were conceptually distinct but scripts had no generic normalization helper and relied on release-specific defaults. v4.1.11 normalizes only a leading `v`, validates semantic version form, and retains a fail-closed mismatch assertion.

## Corrected layout contract

- Canonical runtime root remains `/share/Docker/cos-mcp`.
- Release staging root is `/share/Docker/cos-mcp/releases/vX.Y.Z`.
- Operator/helper scripts resolve from their own extracted release root by default.
- Staged application payload is `<release-root>/cos-mcp`.
- Staged release metadata is `<release-root>/cos-mcp/release-metadata.txt`.
- Staged runtime environment is `<release-root>/cos-mcp/.env.runtime`.
- Staged Compose is `<release-root>/cos-mcp/compose.yaml`.
- Canonical state and secrets remain under `/share/Docker/cos-mcp/state` and `/share/Docker/cos-mcp/secrets`.
- Candidate release identity defaults from staged metadata, not active `.env` and not a hard-coded patch version.
- An explicitly supplied release may use `vX.Y.Z` or `X.Y.Z`; only the leading `v` is normalized.
- A genuine requested-versus-staged mismatch remains a hard failure.
- Candidate runtime descriptors are promoted to the canonical application root only after both containers become healthy.
- Verification and post-deploy backup occur after promotion.

## Rollback and failure behavior

The deployment performs an online pre-deploy SQLite backup before candidate preparation when the current application is running. Candidate preparation preserves the canonical TaskLedger, tunnel identity, runtime key, Slack protected files, qnet/static networking, and active runtime descriptors. Failure before candidate promotion leaves active descriptors unchanged. The operator must not delete state or secrets in response to a failed candidate.

## Capacity note

The incident host reported 96 percent application-filesystem utilization while retaining more than the required 20 GiB free-space floor. That is not classified as the root cause of this failure. It remains an advisory operational risk because QNAP snapshots, image builds, and future releases require headroom beyond the absolute gate.

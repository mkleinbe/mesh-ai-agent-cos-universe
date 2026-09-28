# Mesh CoS v4.15.2 Skill Version Governance

Release date: 2026-09-28

## Outcome

Establishes deterministic version identity for all 10 repository-local ChatGPT role Skills so deployed and built versions can be reconciled without content diffing.

## Version contract

Every deployable Skill now includes:

- a SemVer `VERSION` file;
- catalog-visible `Skill version <semver>` text at the start of the allowed `SKILL.md` description metadata;
- a canonical entry in `chatgpt/skills/versions.json`.

CI fails on missing or invalid versions, description/version mismatch, version-index drift, or skill-roster drift.

## Packaging

`scripts/package-chatgpt-skills.py` produces one ZIP per Skill. Each archive contains the Skill's own `VERSION` file. The distribution manifest records:

- Skill ID;
- Skill version;
- source commit;
- asset name;
- byte size;
- SHA-256 digest.

The release includes all 10 Skill ZIPs as the baseline versioned deployment set plus `distribution-manifest.json` and `SHA256SUMS.txt`.

## Versioning rule

Repository/runtime versions and Skill versions are independent. This release establishes `4.15.2` as the baseline version for the current content of all 10 role Skills. Future releases increment only the Skill or Skills whose deployable package changes.

## Runtime boundary

Canonical MCP authority/runtime contract remains 4.0.0. QNAP deployment remains 4.4.2. No runtime redeployment is required.

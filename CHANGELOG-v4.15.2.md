# v4.15.2

## Added

- Per-Skill SemVer `VERSION` files for all 10 repository-local ChatGPT role Skills.
- Catalog-visible Skill version metadata in every `SKILL.md` description.
- Canonical `chatgpt/skills/versions.json` version index.
- CI enforcement for SemVer, metadata, index, and roster consistency.
- Deterministic one-Skill-per-ZIP packaging with source-commit and SHA-256 distribution evidence.

## Versioning policy

Skill versions are independent from MCP runtime and repository release versions after this baseline. Only materially changed Skill packages require future Skill version increments and redeployment.

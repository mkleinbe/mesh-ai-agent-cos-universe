# ChatGPT Skill Version Contract

## Canonical identity

Each repository-local ChatGPT Skill must expose the same semantic version in three places:

1. `chatgpt/skills/<skill>/VERSION`
2. the start of `SKILL.md` frontmatter `description`: `Skill version <version>. `
3. `chatgpt/skills/versions.json`

`VERSION` is the canonical per-Skill version. The other locations are indexed or discovery metadata and must match it.

## Why the description carries the version

ChatGPT exposes Skill name and description in the installed Skill catalog. Keeping the version in `description` makes the deployed version inspectable through Skill discovery while preserving the supported SKILL.md frontmatter contract of only `name` and `description`.

## Version increments

Use SemVer per Skill.

- PATCH: packaging, metadata, defect correction, or backward-compatible instruction refinement.
- MINOR: backward-compatible material capability addition.
- MAJOR: incompatible behavior, contract, authority, or invocation semantics.

Increment only a Skill whose deployable directory changes. Repository release, MCP runtime, QNAP deployment, and Skill versions are separate identities.

## Release evidence

Every distributable Skill ZIP must include its `VERSION`. The distribution manifest must bind Skill ID, Skill version, source commit, asset filename, byte count, and SHA-256.

## Reconciliation

For each installed Skill:

1. read the installed catalog description version;
2. compare it with the GitHub `VERSION` or `versions.json` entry at the intended release tag;
3. treat a mismatch as deployment drift;
4. update only mismatched Skills;
5. re-read the installed Skill catalog after deployment to verify convergence.

Content diffing is a fallback for legacy packages only.

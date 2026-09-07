# Release Authorization v4.5.0

## Authority source

Michael D. Kleinberg authorized the CFO capability enhancement in this project and has an active project-level Engineering Execution & Release Standard requiring material engineering work to proceed through implementation, verification, documentation, repository integration, semantic versioning, tag creation, GitHub Release publication, and final repository/release verification.

This receipt records that standing human authorization for the bounded `v4.5.0 CFO Financial Analysis Capability` release.

## Authorized actions

Subject to all technical, security, and verification gates passing for the exact candidate, the authorized repository lifecycle is:

1. update the CFO agent, Skill, reference modules, Workspace Agent projection, behavior specifications, tests, and required documentation;
2. commit and push the bounded change on an isolated branch;
3. create and update pull request `#65`;
4. resolve legitimate review findings, conflicts, and failing checks without weakening security or acceptance criteria;
5. merge the verified change to `main`;
6. create semantic tag `v4.5.0` from the verified integrated main commit;
7. create the GitHub Release from that same commit;
8. verify main, tag, release, documentation, CFO implementation version `1.1.0`, and release metadata are aligned.

## Explicitly not authorized by this receipt

- QNAP deployment or restart;
- expansion of the canonical 10-agent roster;
- new MCP tools or connector permissions;
- enterprise GL, treasury, bank-balance, tax, audit, trading, or personal investment authority;
- autonomous pricing, discount, investment, spend, hiring, contract, transfer, or trading action;
- external communication or public publishing unrelated to the GitHub repository release;
- destructive rewriting of existing tags, releases, canonical task state, or historical evidence.

## Conditions

Merge and release remain blocked until:
- full repository CI is green on the exact candidate;
- `CFA-001` through `CFA-008` pass;
- the targeted security review has no unresolved release-blocking finding;
- independent verification confirms authority, source, connector, MCP, and completion boundaries are preserved;
- no unresolved material review thread or merge conflict remains.

The release workflow must create `v4.5.0` only after the merged `main` SHA passes its release verification job. The tag and GitHub Release are immutable historical evidence once published.

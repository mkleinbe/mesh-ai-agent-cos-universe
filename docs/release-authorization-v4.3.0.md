# v4.3.0 Release Authorization Receipt

Date: 2026-08-28
Release: `v4.3.0`
Repository: `mkleinbe/mesh-ai-agent-cos-universe`

## Authorized actions

The human release authority explicitly authorized this release turn to:

- complete all material-turn documentation;
- commit and push the documentation and release changes;
- merge the verified v4.3.0 PR to `main`;
- close out superseded or completed PRs related to this turn;
- create semantic tag `v4.3.0` against the integrated `main` commit;
- publish the GitHub Release for v4.3.0 with the immutable QNAP ZIP and checksum;
- use the repository release workflow to create the tag and release if a direct GitHub connector release action is unavailable.

## Explicit exclusions

This receipt does not authorize:

- QNAP production deployment;
- production task recovery;
- autonomous consequential email, Slack, publishing, pricing, staffing, or commercial commitments;
- mutation of canonical TaskLedger state merely to make release evidence appear successful.

## Release binding

The v4.3.0 GitHub Release and semantic tag must resolve to the integrated `main` commit produced by merging the verified v4.3.0 pull request. The release workflow must rebuild the exact artifacts from that main-branch SHA before publishing.

This file is used as a one-time GitHub Actions `push` path trigger for the v4.3.0 release workflow. Future unrelated `main` pushes do not trigger the v4.3.0 workflow unless this authorization receipt itself changes.

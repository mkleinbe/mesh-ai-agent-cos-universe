# Mesh CoS MCP v4.2.1 Verification Receipt

## Bound candidate

- Release candidate: `v4.2.1 Native Slack HITL Decision Compatibility`
- Functional candidate SHA: `42ee1cb956ade5166f434b748cb046125566b70c`
- CI run: `33117903491`
- CI job: `98677236458`
- Repository base: v4.2.0 merge commit `226821c0b89a0a319b4f1d20d5789a7e9759d391`
- Canonical MCP runtime contract: `4.0.0`
- Security applicability: **FULL REVIEW**
- Verification classification for repository candidate: **PASS**
- Production deployment/acceptance classification: **BLOCKED UNTIL LIVE v4.2.1 QNAP + CHATGPT WORK ACCEPTANCE**

This receipt binds the behavior-bearing candidate before the receipt itself is packaged. Any later receipt-only or release-plumbing commit must pass the same CI/release verification gates before merge. The main-branch v4.2.1 release workflow must rebuild and verify the exact merge SHA before publishing the immutable tag and assets.

## Incident reproduced and corrected

The first live v4.2.0 production acceptance proved the ChatGPT Work Slack event trigger fired and reached Mesh CoS MCP, but reconciliation failed closed with `INVALID_ARGUMENT / execution_failed`. The provider-visible human reply was `*APPROVE*`, while the v4.2.0 exact parser accepted only bare `APPROVE`.

v4.2.1 makes the smallest causal correction: it removes exactly one whole-message Slack `*...*` wrapper and then applies the pre-existing exact APPROVE / DENY / CHANGE grammar. It does not introduce fuzzy interpretation, general Markdown stripping, trigger-side parsing, or new authority-bearing fields.

## Behavior evidence

CI run `33117903491` executed the full Python suite against candidate SHA `42ee1cb956ade5166f434b748cb046125566b70c`:

- **417 passed**
- **0 failed**
- **100.00% coverage**
- 2,880 statements, 0 missed
- 950 branches, 0 partial branches

Regression coverage includes:

- provider text `*APPROVE*` reaches canonical APPROVED / READY_FOR_ACTION;
- `*DENY*`, `*CHANGE*`, and one-layer formatted CHANGE details are accepted by the same exact grammar;
- `**APPROVE**`, `*APPROVE* extra`, `*looks good*`, and fuzzy natural-language approval remain rejected;
- wrong user, app/bot-authored message, edited message, wrong/unbound thread, invalid locator, provider ambiguity, stale fingerprint, and conflicting replay remain fail closed;
- duplicate delivery remains idempotent;
- CHANGE remains a two-stage revision workflow requiring a new approval/fingerprint before consequential action.

The ready BDD contract is `specs/native-slack-event-hitl-v4.2.1.feature`, scenarios `SLACK-NATIVE-421-001` through `SLACK-NATIVE-421-008`.

## Engineering gates

Fresh evidence from CI run `33117903491`:

| Gate | Evidence | Result |
| --- | --- | --- |
| Python dependency integrity | `python -m pip check` | PASS, no broken requirements |
| Node dependency/build/test/smoke/security | `npm ci`, `npm run check` | PASS, 18 Node tests, 0 failures, 0 npm vulnerabilities |
| Contract schemas | `python scripts/validate-contracts.py` | PASS |
| Runtime/documentation drift | `python scripts/check-runtime-doc-drift.py` | PASS |
| ChatGPT package/authority drift | `python scripts/check-chatgpt-packages.py` | PASS |
| Ruff source | `ruff check src` | PASS |
| Ruff tests/scripts critical rules | `ruff check tests scripts --select E9,F63,F7,F82` | PASS |
| mypy | `mypy src --check-untyped-defs` | PASS, 35 source files |
| Python suite | `pytest --cov=mesh_cos ... --cov-fail-under=100` | PASS, 417 tests |
| Coverage | same pytest gate | PASS, 100.00% |
| Bandit high-severity gate | `bandit -q -r src -lll` | PASS |
| Python compile | `python -m compileall -q src` | PASS |
| QNAP POSIX shell syntax/regressions | QNAP shell regression suite | PASS |
| QNAP Compose discovery | `test-compose-discovery.sh` | PASS |
| QNAP observability | `test-observability.sh` | PASS |
| QNAP runtime permissions | `test-runtime-permissions.sh` | PASS |
| Image provenance | `test-image-provenance.sh` | PASS |
| Native Slack HITL configuration | `test-slack-hitl-configure.sh` | PASS |
| Transactional promotion | `test-transactional-promotion.sh` | PASS |
| Versioned release layout | `test-versioned-release-layout.sh` | PASS |
| Restarting-container backup | `test-restarting-container-backup.sh` | PASS |
| Socket Mode exclusion | compose/scripts grep assertions | PASS |
| Stale `/mesh-approval Socket Mode ingress` output exclusion | deploy-script assertion | PASS |
| Exact v4.2.1 ZIP/checksum | `build-qnap-release-v4.2.1.sh` + `sha256sum -c` | PASS |
| Release root containment | ZIP entry assertions | PASS |
| Container build/provenance | `mesh-cos-mcp:ci-v4.2.1`, version/revision labels | PASS |
| Modern MCP/native Slack readiness | `test-modern-mcp-transport.sh` | PASS for deployment 4.2.1 |
| Artifact upload | GitHub artifact ID `9665274222` | PASS |

## Security verification

The patch touches the human-approval decision parser and therefore required FULL REVIEW handling. Independent review of the changed trust path confirms:

1. ChatGPT Work remains a wake-up/locator surface, not approval authority.
2. The governed adapter still rejects authority-bearing trigger fields.
3. QNAP still re-reads the exact Slack provider message before parsing.
4. Manual-human authorship, protected approver identity, channel/thread binding, edited-message rejection, PENDING state, approval owner, immutable payload fingerprint, and replay checks remain mandatory.
5. The compatibility normalization is one layer only; the unchanged exact grammar remains the final text gate.
6. No new Slack OAuth scope, credential class, MCP tool, agent principal, Socket Mode listener, or `xapp-` secret was introduced.
7. The canonical Phase 1 authority/runtime contract remains `4.0.0`, with exactly 10 agents and 27 CoS tools.
8. Failure remains fail closed: no provider/state proof means no canonical approval mutation.

Available automated security evidence includes Bandit high-severity scanning, npm audit at high severity, dependency integrity, authorization/package drift checks, QNAP secret/configuration regression gates, exact artifact provenance, and the negative security regression suite.

**Codex Security limitation:** no Codex Security scanning capability is exposed in this conversation environment. No Codex Security scan is claimed. This limitation does not replace the executed FULL REVIEW evidence above and remains visible to human release authority.

No unresolved CRITICAL or HIGH technical defect is demonstrated by the available repository evidence for this candidate.

## Documentation and diagram evidence

Updated current-release documentation includes:

- `README.md`
- `RELEASE.md`
- `CHANGELOG-v4.2.1.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
- `docs/release-4.2.1-slack-rendered-decision.md`
- `docs/security-review-v4.2.1.md`
- `docs/chatgpt-native-slack-dispatcher-v4.2.1.md`
- `docs/chatgpt-published-app-production-acceptance-v4.2.1.md`
- `specs/native-slack-event-hitl-v4.2.1.feature`

Mermaid Chart was used to validate the documented authority-flow, security trust-boundary, and production-acceptance sequence diagrams before release preparation.

## Release artifact evidence

Candidate CI produced:

- `dist/mesh-cos-mcp-qnap-v4.2.1.zip`
- `dist/mesh-cos-mcp-qnap-v4.2.1.zip.sha256`
- CI artifact: `mesh-cos-mcp-qnap-v4.2.1-ci`
- GitHub artifact ID: `9665274222`
- uploaded artifact envelope SHA-256: `550d8fc1b05be1200db3f5a0c09f73c5b52faa9b5ba81ad80b3053b3d5fb941a`

The release workflow must rebuild rather than promote the CI artifact so release metadata and OCI revision labels bind to the exact main-branch merge SHA.

## Remaining production acceptance

Repository verification cannot prove the external ChatGPT Work event delivery plus live Slack provider reconciliation path. After v4.2.1 is published and deployed to QNAP, production acceptance must begin by reproducing the v4.2.0 incident shape with a new synthetic non-consequential approval and provider text `*APPROVE*`.

PASS requires:

- Work dispatcher fires autonomously;
- Mesh CoS MCP reconciliation succeeds;
- the approval becomes APPROVED exactly once;
- the task becomes READY_FOR_ACTION;
- replay is idempotent;
- DENY and CHANGE succeed as specified;
- nested/partial/fuzzy formatting and wrong-user/root/unbound/bot/edited/unavailable/fingerprint cases fail closed;
- no Socket Mode/xapp path is active;
- final canonical audit chain verifies.

Until that matrix passes, release state may be **PUBLISHED** but production acceptance remains **NOT VERIFIED**.

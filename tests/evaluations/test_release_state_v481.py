from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v481_is_documentation_and_release_control_only() -> None:
    notes = _read("docs/release-v4.8.1-release-state-finalization.md")
    assert "documentation and release-control PATCH" in notes
    assert "no agent behavior change" in notes
    assert "Canonical Phase 1 authority/runtime contract: `4.0.0`, unchanged" in notes
    assert "Production QNAP deployment: `4.4.0`, unchanged" in notes
    assert "v4.8.0" in notes
    assert "fec9abd4e3cd44f66eeddf3c33f05cc52745c225" in notes


def test_v480_verification_receipt_is_final_not_pending() -> None:
    receipt = _read("docs/verification-v4.8.0-functional-method-expansion.md")
    assert "Verification status: **PASS**" in receipt
    assert "Final publication status: **PASS**" in receipt
    assert "fec9abd4e3cd44f66eeddf3c33f05cc52745c225" in receipt
    assert "34723652446" in receipt
    assert "PENDING publication only" not in receipt
    assert "must still be observed after merge" not in receipt
    assert "only remaining release gate" not in receipt


def test_v481_verification_receipt_is_durable_and_governed() -> None:
    receipt = _read("docs/verification-v4.8.1-release-state-finalization.md")
    assert "Verification status: **PASS**" in receipt
    assert "Verification status: **PASS for release candidate**" not in receipt
    assert "Final publication status: **PENDING" not in receipt
    assert "Publication binding: **EXACT-SHA ENFORCED BY RELEASE WORKFLOW**" in receipt
    assert "f1fa3601e373515950e61ead7c6b9cbdb37fdb28" in receipt
    assert "31063070a5794c40eb76fc3a27138c87e60740e3" in receipt
    assert "34724550131" in receipt
    assert "34724552349" in receipt
    assert "runtime contract: `4.0.0`, unchanged" in receipt
    assert "production QNAP: `4.4.0`, unchanged" in receipt
    assert "V481-01" in receipt
    assert "V481-02" in receipt
    assert "V481-03" in receipt
    assert "V481-04" in receipt


def test_v481_security_receipt_is_durable() -> None:
    security = _read("docs/security-review-v4.8.1-release-state-finalization.md")
    assert "Security result: **PASS**" in security
    assert "Security result: **PASS for release candidate**" not in security
    assert "Publication binding: **EXACT-SHA ENFORCED BY RELEASE WORKFLOW**" in security
    assert "SEC-481-06" in security


def test_v481_is_current_repository_release() -> None:
    readme = _read("README.md")
    release = _read("RELEASE.md")
    assert "Current repository release: `v4.8.1 Release State Finalization`" in readme
    assert release.startswith("# v4.8.1 Release State Finalization")
    assert "# v4.8.0 Functional Method Expansion" in release


def test_v480_publisher_is_historical_only_and_v481_owns_main() -> None:
    old = _read(".github/workflows/release-v4.8.0.yml")
    new = _read(".github/workflows/release-v4.8.1.yml")
    assert "branches: [main]" not in old
    assert "workflow_dispatch:" in old
    assert "branches: [main]" in new
    assert "gh release create v4.8.1" in new
    assert "--target \"$GITHUB_SHA\"" in new
    assert "test_release_state_v481.py" in new
    assert "docs/verification-v4.8.1-release-state-finalization.md" in new
    assert "docs/security-review-v4.8.1-release-state-finalization.md" in new
    assert "Verification status: \\*\\*PASS\\*\\*" in new
    assert "Security result: \\*\\*PASS\\*\\*" in new


def test_v481_changelog_records_only_release_state_correction() -> None:
    changelog = _read("CHANGELOG-v4.8.1.md")
    assert "Release State Finalization" in changelog
    assert "No agent behavior" in changelog
    assert "No QNAP deployment" in changelog
    assert "v4.8.0" in changelog

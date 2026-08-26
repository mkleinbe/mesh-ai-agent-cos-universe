from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QNAP = ROOT / "deployment" / "qnap"
SCRIPTS = QNAP / "scripts"
FEATURE = ROOT / "specs" / "qnap-slack-approver-bootstrap-v4.1.13.feature"


def text(path: Path) -> str:
    return path.read_text()


def test_v4113_bdd_contract_is_ready_and_complete() -> None:
    feature = text(FEATURE)
    assert "@ready" in feature
    for scenario_id in range(92, 100):
        assert f"Scenario: QNAP-{scenario_id:03d}" in feature


def test_verified_human_approver_is_built_in_as_slack_user_id() -> None:
    script = text(SCRIPTS / "mesh-cos-slack-hitl-configure.sh")
    assert "U01KG3CNYHK" in script
    assert "D01K4CL2F8F" not in script
    assert "DEFAULT_APPROVER_USER_ID" in script


def test_approver_bootstrap_never_prompts_for_user_id() -> None:
    script = text(SCRIPTS / "mesh-cos-slack-hitl-configure.sh")
    assert "read_visible_tty" not in script
    assert "Slack user ID for the human approval principal" not in script
    assert "APPROVER_VALUE=$DEFAULT_APPROVER_USER_ID" in script


def test_conversation_ids_fail_with_specific_diagnostic() -> None:
    script = text(SCRIPTS / "mesh-cos-slack-hitl-configure.sh")
    assert 'case "$APPROVER_VALUE" in' in script
    assert 'D*)' in script
    assert "Slack conversation/DM channel ID is not a user ID" in script
    assert "grep -Eq '^[UW][A-Z0-9]+$'" in script


def test_existing_identity_is_preserved_unless_reconfigure_requested() -> None:
    script = text(SCRIPTS / "mesh-cos-slack-hitl-configure.sh")
    assert 'MESH_COS_FORCE_SLACK_HITL_RECONFIGURE:-0' in script
    assert '[ ! -s "$APPROVER_FILE" ]' in script
    assert "preserving existing Slack approver identity file" in script


def test_secret_tokens_remain_hidden_runtime_inputs() -> None:
    script = text(SCRIPTS / "mesh-cos-slack-hitl-configure.sh")
    assert "Slack read-only verifier bot token (input hidden)" in script
    assert "Slack Socket Mode app-level token (input hidden)" in script
    assert "stty -echo" in script
    assert "xoxb-" in script
    assert "xapp-" in script
    assert "U01KG3CNYHK" not in text(ROOT / "deployment" / "qnap" / "compose.yaml")


def test_v4113_release_defaults_advance_without_authority_change() -> None:
    builder = text(ROOT / "scripts" / "build-qnap-release-bundle.sh")
    workflow = text(ROOT / ".github" / "workflows" / "release-production-readiness.yml")
    assert 'VERSION=${1:-4.1.13}' in builder
    assert "Build v4.1.13 QNAP deployment bundle" in workflow
    assert "TAG: v4.1.13" in workflow
    readme = text(ROOT / "README.md")
    assert "4.1.13" in readme
    assert "exactly 10" in readme.lower()
    assert "27" in readme

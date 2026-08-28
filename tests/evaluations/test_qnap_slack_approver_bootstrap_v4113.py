from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QNAP = ROOT / "deployment" / "qnap"
SCRIPTS = QNAP / "scripts"
FEATURE = ROOT / "specs" / "qnap-slack-approver-bootstrap-v4.1.13.feature"


def text(path: Path) -> str:
    return path.read_text()


def test_v4113_bdd_contract_remains_historical_and_complete() -> None:
    feature = text(FEATURE)
    assert "@ready" in feature
    for scenario_id in range(92, 100):
        assert f"Scenario: QNAP-{scenario_id:03d}" in feature


def test_verified_human_approver_remains_built_in_as_slack_user_id() -> None:
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
    assert 'case "$APPROVER_VALUE_TO_VALIDATE" in' in script
    assert 'D*)' in script
    assert "Slack conversation/DM channel ID is not a user ID" in script
    assert "grep -Eq '^[UW][A-Z0-9]+$'" in script


def test_existing_identity_is_preserved_and_forced_secret_reconfigure_is_separate() -> None:
    script = text(SCRIPTS / "mesh-cos-slack-hitl-configure.sh")
    assert 'MESH_COS_FORCE_SLACK_HITL_RECONFIGURE:-0' in script
    assert '[ ! -s "$APPROVER_FILE" ]' in script
    assert "preserving existing Slack approver identity file" in script
    assert "forced Slack credential reconfiguration is not allowed in the deploy path" in script
    assert "mesh-cos-slack-hitl-provision.sh" in script


def test_current_release_requires_native_trigger_and_dedicated_bot_protected_credentials() -> None:
    configure = text(SCRIPTS / "mesh-cos-slack-hitl-configure.sh")
    provision = text(SCRIPTS / "mesh-cos-slack-hitl-provision.sh")
    secret_input = text(SCRIPTS / "mesh-cos-qnap-secret-input.sh")
    compose = text(QNAP / "compose.yaml")
    assert "read_secret_tty" not in configure
    assert "command -v stty" not in configure
    assert "CHATGPT_NATIVE_EVENT_TRIGGER" in configure
    assert "legacy Slack Socket Mode must not be configured" in configure
    assert "Slack bot OAuth token file is missing" in configure
    assert "Slack Socket Mode app-level token (input hidden)" not in provision
    assert "Slack bot OAuth token (input hidden)" in provision
    assert "mesh_read_secret_tty" in provision
    assert "mesh_shell_supports_silent_read" in secret_input
    assert "/bin/stty /usr/bin/stty" in secret_input
    assert "xoxb-" in provision
    assert "xapp-" not in provision
    assert "slack-verifier-token" not in configure + provision
    assert "MESH_COS_SLACK_VERIFIER_TOKEN_FILE" not in compose
    assert "MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE" not in compose
    assert "U01KG3CNYHK" not in compose


def test_v4113_and_v420_release_evidence_remain_historical_while_current_is_v430() -> None:
    wrapper = text(ROOT / "scripts" / "build-qnap-release-v4.2.0.sh")
    legacy_workflow = text(ROOT / ".github" / "workflows" / "release-production-readiness.yml")
    historical_v423 = text(ROOT / ".github" / "workflows" / "release-v4.2.3.yml")
    current_v430 = text(ROOT / ".github" / "workflows" / "release-v4.3.0.yml")
    assert "VERSION=4.2.0" in wrapper
    assert "TAG: v4.1.13" in legacy_workflow
    assert "v4.1.13 Slack Approver Bootstrap" in legacy_workflow
    assert "v4.2.3 QNAP qnet egress readiness release candidate" in historical_v423
    assert "v4.3.0 cross-agent owner execution release candidate" in current_v430
    readme = text(ROOT / "README.md")
    assert "v4.3.0 Cross-Agent Owner Execution" in readme
    assert "Historical versioned documents remain retained as release-train evidence" in readme
    contract = json.loads(text(ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"))
    assert contract["runtime_release"] == "4.0.0"
    assert len(contract["agent_tool_allowlists"]) == 10
    assert len(contract["agent_tool_allowlists"]["cos"]) == 28
    assert "delegation.execute_owner" in contract["agent_tool_allowlists"]["cos"]

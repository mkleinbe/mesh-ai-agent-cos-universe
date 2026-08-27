from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_v4115_contract_has_ready_scenarios() -> None:
    feature = (ROOT / "specs/qnap-slack-plugin-hitl-v4.1.15.feature").read_text(encoding="utf-8")
    for scenario_id in ("QNAP-104", "QNAP-105", "QNAP-106", "QNAP-107", "QNAP-108", "QNAP-109", "QNAP-110", "QNAP-111"): assert f"@{scenario_id}" in feature
    assert "@ready" in feature


def test_qnap_104_108_active_runtime_has_no_legacy_verifier_dependency() -> None:
    active_paths = [ROOT / "deployment/qnap/compose.yaml", ROOT / "deployment/qnap/scripts/mesh-cos-slack-hitl-configure.sh", ROOT / "deployment/qnap/scripts/mesh-cos-slack-hitl-provision.sh", ROOT / "deployment/qnap/runtime_preflight.py", ROOT / "src/mesh_cos/preflight.py"]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
    assert "MESH_COS_SLACK_VERIFIER_TOKEN_FILE" not in joined; assert "slack-verifier-token" not in joined; assert "LEGACY_VERIFIER" not in joined


def test_qnap_104_protocol_preserves_connector_as_non_authoritative_collaboration() -> None:
    protocol = (ROOT / "docs/slack-agent-protocol.md").read_text(encoding="utf-8")
    assert "connected Slack" in protocol; assert "collaboration" in protocol.lower(); assert "does not create approval authority" in protocol.lower()


def test_qnap_107_socket_mode_startup_failure_is_non_fatal_by_contract() -> None:
    source = (ROOT / "mcp/src/slack-socket-mode.ts").read_text(encoding="utf-8"); assert "await this.connect(true)" not in source; assert "scheduleReconnect" in source


def test_qnap_110_111_promotion_is_snapshot_backed_through_postdeploy_verification() -> None:
    deploy = (ROOT / "deployment/qnap/scripts/mesh-cos-mcp-deploy.sh").read_text(encoding="utf-8"); helper = (ROOT / "deployment/qnap/scripts/mesh-cos-qnap-promotion.sh").read_text(encoding="utf-8")
    for token in ("mesh_snapshot_active_configuration", "mesh_promote_candidate_configuration", "mesh_restore_active_configuration", "PROMOTION_IN_FLIGHT", "fail_after_promotion", "post-deploy verification failed", "candidate_promotion_commit"): assert token in deploy
    for token in ("mesh_snapshot_active_configuration", "mesh_promote_candidate_configuration", "mesh_restore_active_configuration", "mesh_cleanup_configuration_snapshot", ".absent"): assert token in helper

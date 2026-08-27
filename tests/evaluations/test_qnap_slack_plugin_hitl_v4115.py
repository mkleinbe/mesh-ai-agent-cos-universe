from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_qnap_104_108_active_runtime_has_no_verifier_bot_dependency() -> None:
    active_paths = [
        ROOT / "deployment/qnap/compose.yaml",
        ROOT / "deployment/qnap/scripts/mesh-cos-slack-hitl-configure.sh",
        ROOT / "deployment/qnap/scripts/mesh-cos-slack-hitl-provision.sh",
        ROOT / "deployment/qnap/runtime_preflight.py",
        ROOT / "src/mesh_cos/preflight.py",
    ]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
    assert "MESH_COS_SLACK_VERIFIER_TOKEN_FILE" not in joined
    assert "slack-verifier-token" not in joined
    assert "xoxb-" not in joined


def test_qnap_104_protocol_assigns_collaboration_to_connected_slack_integration() -> None:
    protocol = (ROOT / "docs/slack-agent-protocol.md").read_text(encoding="utf-8")
    assert "connected Slack" in protocol
    assert "collaboration" in protocol.lower()
    assert "does not create approval authority" in protocol.lower()


def test_qnap_107_socket_mode_startup_failure_is_non_fatal_by_contract() -> None:
    source = (ROOT / "mcp/src/slack-socket-mode.ts").read_text(encoding="utf-8")
    # Startup must not directly await a required first connection that can reject the MCP bootstrap.
    assert "await this.connect(true)" not in source
    assert "scheduleReconnect" in source

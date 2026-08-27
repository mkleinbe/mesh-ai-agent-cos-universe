from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_v4117_supersedes_v4115_slash_command_with_bound_socket_events() -> None:
    source = (ROOT / "src/mesh_cos/slack_socket_approval.py").read_text(encoding="utf-8")
    assert "approval_slack_binding" not in source
    assert "notice_author_user_id" not in source
    assert "DEFAULT_ALLOWED_NOTICE_AUTHORS" not in source
    assert "provider-verified Slack notice binding" not in source
    assert "payload_fingerprint" in source
    assert "slash_commands" not in source
    assert 'envelope_type == "events_api"' in source
    assert 'envelope_type == "interactive"' in source
    assert "approval_slack_thread_binding" not in source
    assert "THREAD_BINDING_KIND" in source
    assert "approver_user_id" in source
    assert "channel_id" in source
    assert "envelope_id" in source

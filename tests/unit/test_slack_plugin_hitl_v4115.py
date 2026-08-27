from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_qnap_105_106_canonical_socket_approval_does_not_require_notice_binding() -> None:
    source = (ROOT / "src/mesh_cos/slack_socket_approval.py").read_text(encoding="utf-8")
    assert "approval_slack_binding" not in source
    assert "notice_author_user_id" not in source
    assert "DEFAULT_ALLOWED_NOTICE_AUTHORS" not in source
    assert "provider-verified Slack notice binding" not in source
    assert "payload_fingerprint" in source
    assert "slash_commands" in source
    assert "approver_user_id" in source
    assert "channel_id" in source
    assert "envelope_id" in source

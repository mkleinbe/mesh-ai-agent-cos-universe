from __future__ import annotations

import pytest

from mesh_cos.slack_hitl import SlackHITLConfig, _parse_decision, _parse_thread_decision

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"


def test_config_from_env_requires_runtime_human_identity_and_canonical_principal() -> None:
    config = SlackHITLConfig.from_env(
        {
            "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
            "MESH_COS_SLACK_APPROVER_USER_ID": APPROVER_USER_ID,
            "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
        }
    )
    assert config == SlackHITLConfig(
        channel_id=CHANNEL_ID,
        approver_user_id=APPROVER_USER_ID,
        approver_principal="michael",
    )

    with pytest.raises(RuntimeError, match="begin with U or W"):
        SlackHITLConfig.from_env(
            {
                "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
                "MESH_COS_SLACK_APPROVER_USER_ID": "D0DIRECTMESSAGE",
                "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
            }
        )

    with pytest.raises(RuntimeError, match="canonical principal michael"):
        SlackHITLConfig(
            channel_id=CHANNEL_ID,
            approver_user_id=APPROVER_USER_ID,
            approver_principal="other",
        )


def test_exact_human_command_parser_accepts_only_bound_approval_id() -> None:
    assert _parse_decision("APPROVE approval-abc123", "approval-abc123") == ("APPROVE", None)
    assert _parse_decision("REJECT APR-123:abc", "APR-123:abc") == ("REJECT", None)
    assert _parse_decision("CHANGES approval-abc123: remove recipient", "approval-abc123") == (
        "CHANGES",
        "remove recipient",
    )

    with pytest.raises(PermissionError, match="Approval ID mismatch"):
        _parse_decision("APPROVE approval-other", "approval-abc123")
    with pytest.raises(PermissionError, match="not exact"):
        _parse_decision("please APPROVE approval-abc123", "approval-abc123")


def test_thread_reply_parser_is_case_insensitive_and_requires_minimal_vocabulary() -> None:
    assert _parse_thread_decision("APPROVE") == ("APPROVE", None)
    assert _parse_thread_decision("approve") == ("APPROVE", None)
    assert _parse_thread_decision("DeNy") == ("DENY", None)
    assert _parse_thread_decision("reject") == ("DENY", None)
    assert _parse_thread_decision("change") == ("CHANGE", None)
    assert _parse_thread_decision("CHANGES: remove recipient") == (
        "CHANGE",
        "remove recipient",
    )

    with pytest.raises(PermissionError, match="APPROVE, DENY, or CHANGE"):
        _parse_thread_decision("looks good")
    with pytest.raises(PermissionError, match="Only CHANGE"):
        _parse_thread_decision("APPROVE: because I said so")


def test_thread_reply_parser_accepts_one_slack_whole_message_bold_wrapper_only() -> None:
    assert _parse_thread_decision("*APPROVE*") == ("APPROVE", None)
    assert _parse_thread_decision("*deny*") == ("DENY", None)
    assert _parse_thread_decision("*CHANGE*") == ("CHANGE", None)
    assert _parse_thread_decision("*CHANGES: remove recipient*") == (
        "CHANGE",
        "remove recipient",
    )

    with pytest.raises(PermissionError, match="APPROVE, DENY, or CHANGE"):
        _parse_thread_decision("**APPROVE**")
    with pytest.raises(PermissionError, match="APPROVE, DENY, or CHANGE"):
        _parse_thread_decision("*looks good*")
    with pytest.raises(PermissionError, match="APPROVE, DENY, or CHANGE"):
        _parse_thread_decision("*APPROVE* extra")

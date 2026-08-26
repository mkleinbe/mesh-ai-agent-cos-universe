from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.slack_hitl import (
    CHATGPT_AGENTS_SLACK_USER_ID,
    CHATGPT_SLACK_USER_ID,
    SlackApprovalHITLService,
)

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"


def _env(token_file: str) -> dict[str, str]:
    return {
        "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
        "MESH_COS_SLACK_APPROVER_USER_ID": APPROVER_USER_ID,
        "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
        "MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS": (
            f"{CHATGPT_SLACK_USER_ID},{CHATGPT_AGENTS_SLACK_USER_ID}"
        ),
        "MESH_COS_SLACK_VERIFIER_TOKEN_FILE": token_file,
    }


def test_service_factory_requires_secret_file_path() -> None:
    with pytest.raises(RuntimeError, match="VERIFIER_TOKEN_FILE is required"):
        SlackApprovalHITLService.from_env(TaskLedger(), {})


def test_service_factory_rejects_missing_and_empty_secret_files(tmp_path: Path) -> None:
    missing = tmp_path / "missing-token"
    with pytest.raises(RuntimeError, match="unavailable"):
        SlackApprovalHITLService.from_env(TaskLedger(), _env(str(missing)))

    empty = tmp_path / "empty-token"
    empty.write_text("\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="empty"):
        SlackApprovalHITLService.from_env(TaskLedger(), _env(str(empty)))


def test_service_factory_reads_token_without_persisting_secret(tmp_path: Path) -> None:
    token_file = tmp_path / "slack-verifier-token"
    token_file.write_text("xoxb-test-verifier\n", encoding="utf-8")
    ledger = TaskLedger()

    service = SlackApprovalHITLService.from_env(ledger, _env(str(token_file)))

    assert service.client.token == "xoxb-test-verifier"
    assert service.config.channel_id == CHANNEL_ID
    assert service.config.approver_user_id == APPROVER_USER_ID
    assert ledger.list_records("approval_slack_binding") == []
    assert ledger.list_records("approval_slack_decision") == []

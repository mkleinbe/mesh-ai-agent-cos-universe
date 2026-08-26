from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.registry import load_registry

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"


def test_slack_adapter_is_registered_only_for_cos() -> None:
    registry = GovernedAdapterRegistry(load_registry(), GovernanceJournal(TaskLedger()))
    assert ("cos", "slack-adapter") in registry.adapters
    assert ("cro", "slack-adapter") not in registry.adapters

    with pytest.raises(PermissionError, match="Capability not allowed"):
        registry.execute(
            "cro",
            "slack-adapter",
            {"operation": "bind_notice", "approval_id": "approval-x"},
        )


def test_slack_adapter_accepts_only_notice_binding_operation() -> None:
    registry = GovernedAdapterRegistry(load_registry(), GovernanceJournal(TaskLedger()))

    with pytest.raises(ValueError, match="Missing Slack HITL payload fields"):
        registry.execute(
            "cos",
            "slack-adapter",
            {"operation": "bind_notice", "approval_id": "approval-x"},
        )
    with pytest.raises(PermissionError, match="cannot record human decisions"):
        registry.execute(
            "cos",
            "slack-adapter",
            {
                "operation": "ingest_decision",
                "approval_id": "approval-x",
                "approved": True,
            },
        )
    with pytest.raises(PermissionError, match="cannot record human decisions"):
        registry.execute(
            "cos",
            "slack-adapter",
            {"operation": "record_approval", "approval_id": "approval-x"},
        )


def test_lazy_slack_service_requires_governance() -> None:
    registry = GovernedAdapterRegistry(load_registry())
    with pytest.raises(RuntimeError, match="canonical governance persistence"):
        registry._slack_hitl_service()


def test_lazy_slack_service_loads_secret_file_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token_file = tmp_path / "slack-verifier-token"
    token_file.write_text("xoxb-test-verifier\n", encoding="utf-8")
    monkeypatch.setenv("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", CHANNEL_ID)
    monkeypatch.setenv("MESH_COS_SLACK_APPROVER_USER_ID", APPROVER_USER_ID)
    monkeypatch.setenv("MESH_COS_SLACK_APPROVER_PRINCIPAL", "michael")
    monkeypatch.setenv(
        "MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS",
        "U0BKV7Z8M96,U0BN8V2BU9Z",
    )
    monkeypatch.setenv("MESH_COS_SLACK_VERIFIER_TOKEN_FILE", str(token_file))
    registry = GovernedAdapterRegistry(load_registry(), GovernanceJournal(TaskLedger()))

    first = registry._slack_hitl_service()
    second = registry._slack_hitl_service()

    assert first is second
    assert first.client.token == "xoxb-test-verifier"


def test_required_slack_hitl_fails_runtime_construction_without_verifier_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MESH_COS_SLACK_HITL_REQUIRED", "true")
    with pytest.raises(RuntimeError, match="VERIFIER_TOKEN_FILE is required"):
        GovernedAdapterRegistry(load_registry(), GovernanceJournal(TaskLedger()))


def test_required_slack_hitl_initializes_provider_verifier_during_runtime_construction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    identity_file = tmp_path / "slack-approver-user-id"
    identity_file.write_text(APPROVER_USER_ID + "\n", encoding="utf-8")
    token_file = tmp_path / "slack-verifier-token"
    token_file.write_text("xoxb-test-verifier\n", encoding="utf-8")
    monkeypatch.setenv("MESH_COS_SLACK_HITL_REQUIRED", "yes")
    monkeypatch.setenv("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", CHANNEL_ID)
    monkeypatch.setenv("MESH_COS_SLACK_APPROVER_USER_ID_FILE", str(identity_file))
    monkeypatch.setenv("MESH_COS_SLACK_APPROVER_PRINCIPAL", "michael")
    monkeypatch.setenv(
        "MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS",
        "U0BKV7Z8M96,U0BN8V2BU9Z",
    )
    monkeypatch.setenv("MESH_COS_SLACK_VERIFIER_TOKEN_FILE", str(token_file))

    registry = GovernedAdapterRegistry(load_registry(), GovernanceJournal(TaskLedger()))

    assert registry._slack_hitl is not None
    assert registry._slack_hitl.config.approver_user_id == APPROVER_USER_ID
    assert registry._slack_hitl.client.token == "xoxb-test-verifier"


def test_server_owned_tool_binding_is_absent_without_cos_or_declared_tool() -> None:
    no_cos = {
        "worker": {
            "agent_id": "worker",
            "skills": [],
            "tools": [],
            "role": "worker",
            "version": "1",
        }
    }
    registry = GovernedAdapterRegistry(no_cos, GovernanceJournal(TaskLedger()))
    assert registry.adapters == {}

    cos_without_slack = {
        "cos": {
            "agent_id": "cos",
            "skills": [],
            "tools": [],
            "role": "cos",
            "version": "1",
        }
    }
    registry = GovernedAdapterRegistry(cos_without_slack, GovernanceJournal(TaskLedger()))
    assert ("cos", "slack-adapter") not in registry.adapters

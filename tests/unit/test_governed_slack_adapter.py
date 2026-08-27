from __future__ import annotations

import pytest

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.registry import load_registry

CHANNEL_ID = "C0BRL4GCL3A"


def test_slack_adapter_is_registered_only_for_cos() -> None:
    registry = GovernedAdapterRegistry(load_registry(), GovernanceJournal(TaskLedger()))
    assert ("cos", "slack-adapter") in registry.adapters
    assert ("cro", "slack-adapter") not in registry.adapters

    with pytest.raises(PermissionError, match="Capability not allowed"):
        registry.execute(
            "cro",
            "slack-adapter",
            {"operation": "handoff", "channel_id": CHANNEL_ID, "payload": {}},
        )


def test_slack_adapter_returns_connected_connector_handoff_without_executing_slack() -> None:
    registry = GovernedAdapterRegistry(load_registry(), GovernanceJournal(TaskLedger()))
    result = registry.execute(
        "cos",
        "slack-adapter",
        {
            "operation": "handoff",
            "channel_id": CHANNEL_ID,
            "payload": {"intent": "post approval request", "approval_id": "approval-x"},
        },
    )

    assert result == {
        "status": "AUTHORIZED",
        "execution_mode": "CHATGPT_CONNECTOR_HANDOFF",
        "connector": "Slack",
        "channel_id": CHANNEL_ID,
        "authority": "COLLABORATION_ONLY",
        "payload": {"intent": "post approval request", "approval_id": "approval-x"},
    }


def test_slack_adapter_cannot_record_or_ingest_human_approval() -> None:
    registry = GovernedAdapterRegistry(load_registry(), GovernanceJournal(TaskLedger()))

    for operation in ("bind_notice", "ingest_decision", "record_approval"):
        with pytest.raises(PermissionError, match="collaboration-only"):
            registry.execute(
                "cos",
                "slack-adapter",
                {"operation": operation, "channel_id": CHANNEL_ID, "payload": {}},
            )

    for forbidden_field in ("approved", "approval_status", "actor", "principal"):
        with pytest.raises(PermissionError, match="cannot carry canonical approval authority"):
            registry.execute(
                "cos",
                "slack-adapter",
                {
                    "operation": "handoff",
                    "channel_id": CHANNEL_ID,
                    "payload": {},
                    forbidden_field: True,
                },
            )


def test_slack_adapter_rejects_wrong_channel_and_non_object_payload() -> None:
    registry = GovernedAdapterRegistry(load_registry(), GovernanceJournal(TaskLedger()))

    with pytest.raises(PermissionError, match="channel mismatch"):
        registry.execute(
            "cos",
            "slack-adapter",
            {"operation": "handoff", "channel_id": "C0OTHER", "payload": {}},
        )

    with pytest.raises(TypeError, match="payload must be an object"):
        registry.execute(
            "cos",
            "slack-adapter",
            {"operation": "handoff", "channel_id": CHANNEL_ID, "payload": "not-an-object"},
        )


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

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.registry import load_registry
from mesh_cos.reliability import ExecutionLeaseManager


def test_registry_rejects_non_scalar_authority_representation(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "agents").mkdir(parents=True)
    (root / "config").mkdir()
    (root / "agents" / "registry.json").write_text(
        json.dumps(
            {
                "agents": [
                    {
                        "agent_id": "a",
                        "display_name": "Agent A",
                        "version": "1.0.0",
                        "status": "ACTIVE",
                        "parent_agent_id": None,
                        "decision_authority": None,
                    }
                ]
            }
        )
    )
    with pytest.raises(ValueError, match="Invalid decision authority"):
        load_registry(root / "agents" / "registry.json")


def test_execution_lease_accepts_legacy_naive_expiry_timestamp() -> None:
    ledger = TaskLedger()
    future = (datetime.now() + timedelta(minutes=5)).replace(microsecond=0).isoformat()
    ledger.save_record(
        "execution_lease",
        "T",
        {"task_id": "T", "owner": "agent-a", "acquired_at": future, "expires_at": future},
    )
    leases = ExecutionLeaseManager(ledger)
    assert leases.acquire("T", "agent-b", ttl_seconds=30) is False

from __future__ import annotations

from mesh_cos.ledger import TaskLedger
from mesh_cos.reliability import ReplayManager


def test_failure_record_can_name_server_registered_replay_executor() -> None:
    ledger = TaskLedger()
    record = ReplayManager(ledger).record_failure(
        "effect-1",
        "task-1",
        agent_id="cro",
        error=ConnectionError("temporary"),
        payload={"record_id": "R1"},
        replay_key="crm-write-v1",
    )
    assert record["replay_key"] == "crm-write-v1"
    assert ledger.get_record("execution_failure", "effect-1")["replay_key"] == "crm-write-v1"


def test_failure_record_defaults_to_nonreplayable_without_replay_key() -> None:
    record = ReplayManager(TaskLedger()).record_failure(
        "effect-2",
        "task-2",
        agent_id="cro",
        error=RuntimeError("permanent"),
    )
    assert record["replay_key"] is None

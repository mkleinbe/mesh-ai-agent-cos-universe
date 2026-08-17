from __future__ import annotations

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.slack import SlackCoordinator, SlackInboundService


def test_atomic_idempotent_record_rolls_back_claim_when_record_write_fails() -> None:
    ledger = TaskLedger()
    real_conn = ledger.conn

    class FailingConnection:
        def execute(self, sql: str, params=()):
            if "INSERT INTO records" in sql:
                raise RuntimeError("simulated record failure")
            return real_conn.execute(sql, params)

        def commit(self):
            return real_conn.commit()

        def rollback(self):
            return real_conn.rollback()

    ledger.conn = FailingConnection()  # type: ignore[assignment]
    with pytest.raises(RuntimeError, match="simulated record failure"):
        ledger.save_idempotent_record("slack:E1", "slack_event", "E1", {"event_id": "E1"})
    ledger.conn = real_conn

    assert ledger.claim_idempotency_key("slack:E1") is True


def test_slack_inbound_claim_and_record_are_one_canonical_transaction() -> None:
    ledger = TaskLedger()
    inbound = SlackInboundService(SlackCoordinator(ledger, "COPS"))
    message = "[UPDATE] T1\nAgent: cro\nAction: working"

    assert inbound.handle("E1", message) is not None
    assert inbound.handle("E1", message) is None
    assert ledger.get_record("slack_event", "E1")["task_id"] == "T1"

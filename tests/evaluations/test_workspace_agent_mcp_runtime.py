from __future__ import annotations

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService


def _completed_task(service: ChiefOfStaffService):
    task = service.intake(
        objective="Deliver verified Workspace Agent outcome",
        expected_outcome="Acceptance evidence is recorded",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L3,
        acceptance_test="Evidence demonstrates the requested outcome",
    )
    for status in (
        TaskStatus.TRIAGED,
        TaskStatus.PLANNED,
        TaskStatus.ASSIGNED,
        TaskStatus.IN_PROGRESS,
        TaskStatus.QA,
    ):
        service.advance(task.task_id, status)
    return service.complete(task.task_id, outcome="done", evidence=["artifact:primary"])


def test_mcp_safe_verification_fails_closed_without_evidence() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    task = _completed_task(service)

    with pytest.raises(ValueError, match="evidence"):
        service.record_verification_result(
            task.task_id,
            passed=True,
            reason="Looks complete",
            verifier_id="workspace-agent:cos",
            evidence_references=[],
        )

    assert ledger.get_task(task.task_id).status == TaskStatus.COMPLETED


def test_mcp_safe_verification_persists_verifier_and_result() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    task = _completed_task(service)

    verified = service.record_verification_result(
        task.task_id,
        passed=True,
        reason="Acceptance evidence directly supports the expected outcome",
        verifier_id="workspace-agent:cos",
        evidence_references=["artifact:primary", "review:acceptance"],
    )

    assert verified.status == TaskStatus.VERIFIED
    record = ledger.get_record("verification", task.task_id)
    assert record["verifier_id"] == "workspace-agent:cos"
    assert record["verification_source"] == "WORKSPACE_AGENT_MCP"
    assert record["evidence"] == ["artifact:primary", "review:acceptance"]

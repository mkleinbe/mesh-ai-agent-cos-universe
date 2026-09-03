from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService

ROOT = Path(__file__).resolve().parents[2]


def _parent(service: ChiefOfStaffService, key: str):
    return service.intake(
        "Commercial occurrence",
        "Governed result",
        "michael",
        "michael",
        "cos",
        "michael",
        AuthorityLevel.L2,
        "evidence accepted",
        idempotency_key=key,
    )


def _advance_to_assigned(service: ChiefOfStaffService, task_id: str) -> None:
    for status in (TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED):
        service.advance(task_id, status)


def _complete_and_verify(service: ChiefOfStaffService, task_id: str) -> None:
    service.advance(task_id, TaskStatus.QA)
    service.complete(task_id, outcome="done", evidence=[f"task://{task_id}"])
    service.verify(task_id, lambda _: (True, "accepted"))


def test_narrative_dependency_reproduces_fail_closed_runtime_behavior() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    parent = _parent(service, "COM-DEP-REGRESSION:1")
    child = service.decompose(
        parent.task_id,
        [
            {
                "objective": "Evaluate current evidence",
                "expected_outcome": "Current evidence",
                "accountable_agent": "cro",
                "dependencies": ["current authoritative primary-source evidence"],
                "acceptance_test": "evidence current",
            }
        ],
    )[0]
    _advance_to_assigned(service, child.task_id)
    with pytest.raises(RuntimeError, match="dependencies are not verified"):
        service.advance(child.task_id, TaskStatus.IN_PROGRESS)
    assert ledger.get_task(child.task_id).status == TaskStatus.ASSIGNED


def test_dependency_clean_successor_advances_without_runtime_patch() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    parent = _parent(service, "COM-DEP-REGRESSION:2")
    child = service.decompose(
        parent.task_id,
        [
            {
                "objective": "Evaluate current evidence",
                "expected_outcome": "Current evidence",
                "accountable_agent": "cro",
                "dependencies": [],
                "acceptance_test": "evidence current",
            }
        ],
    )[0]
    _advance_to_assigned(service, child.task_id)
    service.advance(child.task_id, TaskStatus.IN_PROGRESS)
    assert ledger.get_task(child.task_id).status == TaskStatus.IN_PROGRESS


def test_real_canonical_predecessor_gate_remains_enforced() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    parent = _parent(service, "COM-DEP-REGRESSION:3")
    predecessor, dependent = service.decompose(
        parent.task_id,
        [
            {
                "objective": "Predecessor",
                "expected_outcome": "Verified predecessor",
                "accountable_agent": "cro",
                "acceptance_test": "verified",
            },
            {
                "objective": "Dependent",
                "expected_outcome": "Runs after predecessor",
                "accountable_agent": "cro",
                "acceptance_test": "verified",
            },
        ],
    )
    dependent.dependencies = [predecessor.task_id]
    ledger.save_task(dependent)
    _advance_to_assigned(service, dependent.task_id)
    with pytest.raises(RuntimeError, match="dependencies are not verified"):
        service.advance(dependent.task_id, TaskStatus.IN_PROGRESS)

    _advance_to_assigned(service, predecessor.task_id)
    service.advance(predecessor.task_id, TaskStatus.IN_PROGRESS)
    _complete_and_verify(service, predecessor.task_id)
    service.advance(dependent.task_id, TaskStatus.IN_PROGRESS)
    assert ledger.get_task(dependent.task_id).status == TaskStatus.IN_PROGRESS


def test_release_documentation_keeps_qnap_runtime_unchanged() -> None:
    architecture = (ROOT / "docs" / "commercial-operations-orchestrator-v4.4.1.md").read_text()
    security = (ROOT / "docs" / "security-review-v4.4.1-commercial-operations.md").read_text()
    release = (ROOT / "docs" / "release-v4.4.1-commercial-operations.md").read_text()
    for text in (architecture, security, release):
        assert "QNAP" in text
        assert "4.4.0" in text
    assert "No QNAP action is required" in architecture
    assert "No QNAP deployment is part of this release" in release
    assert "runtime is unchanged" in security


def test_release_documentation_preserves_commercial_truth_and_approval_boundaries() -> None:
    architecture = (ROOT / "docs" / "commercial-operations-orchestrator-v4.4.1.md").read_text()
    assert "Revenue Intelligence" in architecture
    assert "cannot create account-level commercial truth" in architecture
    assert "human approval" in architecture

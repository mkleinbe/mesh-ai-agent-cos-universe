from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService

ROOT = Path(__file__).resolve().parents[2]


def _parent(service: ChiefOfStaffService, key: str):
    return service.intake(
        "Data Intelligence occurrence",
        "Governed data outcome",
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


def test_narrative_data_dependency_reproduces_fail_closed_behavior() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    parent = _parent(service, "DATA-DEP-REGRESSION:1")
    child = service.decompose(parent.task_id, [{
        "objective": "Review the full universe",
        "expected_outcome": "Reconciled data",
        "accountable_agent": "cro",
        "dependencies": ["Prospect Run Ledger has no non-expired ACTIVE write lock"],
        "acceptance_test": "universe reconciled",
    }])[0]
    _advance_to_assigned(service, child.task_id)
    with pytest.raises(RuntimeError, match="dependencies are not verified"):
        service.advance(child.task_id, TaskStatus.IN_PROGRESS)
    assert ledger.get_task(child.task_id).status == TaskStatus.ASSIGNED


def test_dependency_clean_data_successor_advances_without_runtime_patch() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    parent = _parent(service, "DATA-DEP-REGRESSION:2")
    child = service.decompose(parent.task_id, [{
        "objective": "Review provider state",
        "expected_outcome": "Reconciled provider evidence",
        "accountable_agent": "cro",
        "dependencies": [],
        "acceptance_test": "evidence reconciled",
    }])[0]
    _advance_to_assigned(service, child.task_id)
    service.advance(child.task_id, TaskStatus.IN_PROGRESS)
    assert ledger.get_task(child.task_id).status == TaskStatus.IN_PROGRESS


def test_real_canonical_predecessor_gate_remains_enforced() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    parent = _parent(service, "DATA-DEP-REGRESSION:3")
    predecessor, dependent = service.decompose(parent.task_id, [
        {"objective": "Predecessor", "expected_outcome": "Verified predecessor", "accountable_agent": "cro", "acceptance_test": "verified"},
        {"objective": "Dependent", "expected_outcome": "Runs after predecessor", "accountable_agent": "cro", "acceptance_test": "verified"},
    ])
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


def test_release_documents_keep_qnap_runtime_unchanged() -> None:
    orchestrator = (ROOT / "docs" / "data-intelligence-orchestrator-v4.4.2.md").read_text()
    security = (ROOT / "docs" / "security-review-v4.4.2-data-intelligence.md").read_text()
    release = (ROOT / "docs" / "release-v4.4.2-data-intelligence.md").read_text()
    for text in (orchestrator, security, release):
        assert "QNAP" in text and "4.4.0" in text
    assert "No QNAP action is required" in orchestrator
    assert "No QNAP deployment is part of this release" in release
    assert "runtime is unchanged" in security


def test_business_outcome_and_technical_health_are_separate() -> None:
    text = (ROOT / "docs" / "data-intelligence-orchestrator-v4.4.2.md").read_text()
    assert "Business Outcome" in text
    assert "Technical Health" in text
    assert "FAILED_OCCURRENCE_ISOLATED" in text
    assert "Technical PASS never manufactures business success" in text


def test_data_authority_and_reporting_routes_are_preserved() -> None:
    text = (ROOT / "docs" / "data-intelligence-orchestrator-v4.4.2.md").read_text()
    for term in ("Revenue Intelligence", "CMO", "VP Content", "AgentOps", "LinkedIn Authority OS"):
        assert term in text
    assert "cannot create account-level commercial truth" in text
    assert "Prospect Universe Steward" in text and "not a registered agent" in text


def test_monthly_write_and_external_action_boundaries_are_preserved() -> None:
    runbook = (ROOT / "docs" / "runbook-v4.4.2-data-intelligence.md").read_text()
    orchestrator = (ROOT / "docs" / "data-intelligence-orchestrator-v4.4.2.md").read_text()
    assert "single-cell" in runbook
    assert "Apollo budget is 0" in runbook
    assert "Never archive, delete, auto-merge" in runbook
    assert "human approval" in orchestrator
    assert "Slack text alone is never approval authority" in orchestrator


def test_scheduler_activation_requires_live_provider_readback() -> None:
    architecture = (ROOT / "docs" / "architecture-v4.4.2-data-intelligence.md").read_text()
    release = (ROOT / "docs" / "release-v4.4.2-data-intelligence.md").read_text()
    assert "activation requires live provider readback" in architecture
    assert "production automation is claimed only" in release.lower()
    assert "scoped production activation blocker" in release


def test_release_workflow_targets_v442() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-v4.4.2.yml").read_text()
    assert "gh release create v4.4.2" in workflow
    assert "test_data_intelligence_orchestrator_v442.py" in workflow

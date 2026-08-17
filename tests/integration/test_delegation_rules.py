from __future__ import annotations

import pytest

from mesh_cos.delegation_service import DelegationService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, Delegation, TaskRecord
from mesh_cos.registry import AgentRegistry


def base_task() -> TaskRecord:
    return TaskRecord(
        task_id="T1",
        objective="Preserve pursuit objective",
        expected_outcome="Decision ready",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cro",
        decision_owner="michael",
        authority_level=AuthorityLevel.L3,
        acceptance_test="decision ready",
        approval_owner="michael",
        approval_status="REQUIRED",
    )


def delegation(**overrides) -> Delegation:
    values = dict(
        delegation_id="D1",
        task_id="T1",
        delegating_agent="cos",
        accountable_agent="cro",
        business_objective="Preserve pursuit objective",
        expected_outcome="Decision ready",
        deliverable="brief",
        success_criteria=["accepted"],
        priority="P1",
        authority_level=AuthorityLevel.L3,
        acceptance_test="decision ready",
        permitted_actions=["commercial_analysis"],
        prohibited_actions=["pricing_approval", "discount_approval", "contract_commitment", "final_scope"],
        approval_gates=["michael"],
    )
    values.update(overrides)
    return Delegation(**values)


def test_all_delegation_rules_are_enforced(tmp_path):
    ledger = TaskLedger(tmp_path / "db.sqlite")
    registry = AgentRegistry.from_file("agents/registry.json")
    service = DelegationService(ledger=ledger, registry=registry)
    task = base_task()
    ledger.save_task(task)
    service.create(task, delegation(), depth=1, ancestry=["cos"])

    with pytest.raises(ValueError, match="objective"):
        service.create(task, delegation(delegation_id="D2", business_objective="Different objective"), depth=1, ancestry=["cos"])
    with pytest.raises(PermissionError, match="approval"):
        service.create(task, delegation(delegation_id="D3", approval_gates=[]), depth=1, ancestry=["cos"])
    with pytest.raises(PermissionError, match="authority"):
        service.create(task, delegation(delegation_id="D4", authority_level=AuthorityLevel.L4), depth=1, ancestry=["cos"])
    with pytest.raises(ValueError, match="Circular"):
        service.create(task, delegation(delegation_id="D5", accountable_agent="cos"), depth=1, ancestry=["cos"])
    with pytest.raises(ValueError, match="depth"):
        service.create(task, delegation(delegation_id="D6"), depth=3, ancestry=["cos"])

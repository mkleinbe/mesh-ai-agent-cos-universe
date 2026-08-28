from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from mesh_cos.adapters import SkillAdapter
from mesh_cos.delegation import validate_delegation
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.models import AuthorityLevel, Delegation, TaskStatus
from mesh_cos.staffing import readiness


def advance_to_qa(runtime: MCPRuntime, task_id: str, owner: str = "cos") -> None:
    for target in ("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"):
        runtime.call_agent(owner, "task.transition", {"task_id": task_id, "target": target})


def delegation_payload(task_id: str, accountable_agent: str, objective: str) -> dict:
    return {
        "delegation_id": f"D-{accountable_agent}-{task_id}",
        "task_id": task_id,
        "delegating_agent": "spoofed-by-client",
        "accountable_agent": accountable_agent,
        "business_objective": objective,
        "expected_outcome": f"evidence-backed {objective}",
        "deliverable": f"{objective} brief",
        "success_criteria": ["evidence supplied", "acceptance test addressable"],
        "priority": "P1",
        "authority_level": 2,
        "acceptance_test": f"{objective} evidence is sufficient",
        "approval_gates": [],
    }


def test_synthetic_phase1_delegation_tree_certifies_canonical_state_and_audit_chain() -> None:
    runtime = MCPRuntime(TaskLedger())

    root = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "Michael establishes a synthetic governed client outcome",
            "expected_outcome": "decision-ready synthesis with commercial, economic, delivery, and readiness evidence",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": "cos",
            "decision_owner": "michael",
            "authority_level": 2,
            "acceptance_test": "all delegated evidence is synthesized and independently accepted",
            "idempotency_key": "v4-e2e-root",
        },
    )
    children = runtime.call_agent(
        "cos",
        "task.decompose",
        {
            "parent_task_id": root["task_id"],
            "work_packages": [
                {
                    "objective": "commercial analysis",
                    "expected_outcome": "commercial recommendation",
                    "accountable_agent": "cro",
                    "authority_level": 2,
                    "acceptance_test": "commercial evidence is present",
                },
                {
                    "objective": "engagement economics",
                    "expected_outcome": "economic recommendation",
                    "accountable_agent": "cfo",
                    "authority_level": 2,
                    "acceptance_test": "economic evidence is present",
                },
                {
                    "objective": "delivery feasibility",
                    "expected_outcome": "delivery recommendation",
                    "accountable_agent": "coo",
                    "authority_level": 2,
                    "acceptance_test": "delivery evidence is present",
                },
            ],
        },
    )
    by_owner = {task["accountable_agent"]: task for task in children}

    for agent_id in ("cro", "cfo", "coo"):
        runtime.call_agent(
            "cos",
            "delegation.create",
            {
                "delegation": delegation_payload(
                    by_owner[agent_id]["task_id"], agent_id, by_owner[agent_id]["objective"]
                ),
                "parent_authority": 2,
                "depth": 1,
                "ancestry": ["cos"],
                "parent_approval_gates": [],
            },
        )

    steward = runtime.cos.decompose(
        by_owner["coo"]["task_id"],
        [
            {
                "objective": "consultant readiness",
                "expected_outcome": "evidence-backed staffing readiness",
                "accountable_agent": "consultant-network-steward",
                "authority_level": 2,
                "acceptance_test": "fresh consultant-readiness evidence is present",
            }
        ],
    )[0]
    runtime.call_agent(
        "coo",
        "delegation.create",
        {
            "delegation": delegation_payload(
                steward.task_id, "consultant-network-steward", "consultant readiness"
            ),
            "parent_authority": 2,
            "depth": 2,
            "ancestry": ["cos", "coo"],
            "parent_approval_gates": [],
        },
    )

    runtime.adapters.register(
        SkillAdapter(
            "cos",
            "mesh-devils-advocate",
            lambda payload: {
                "advisory": True,
                "canonical_facts_modified": False,
                "external_action_included": False,
                "challenged_task": payload["task_id"],
            },
        )
    )
    before = runtime.call_agent("cos", "task.get", {"task_id": root["task_id"]})
    challenge = runtime.call_agent(
        "cos",
        "skills.invoke_governed",
        {
            "capability": "mesh-devils-advocate",
            "payload": {
                "task_id": root["task_id"],
                "correlation_id": root["correlation_id"],
                "authority_level": 2,
                "evidence_references": ["synthetic://root"],
            },
        },
    )
    after = runtime.call_agent("cos", "task.get", {"task_id": root["task_id"]})
    assert challenge["advisory"] is True
    assert challenge["canonical_facts_modified"] is False
    assert challenge["external_action_included"] is False
    assert before == after

    for owner, task in (
        ("cro", by_owner["cro"]),
        ("cfo", by_owner["cfo"]),
        ("consultant-network-steward", steward.to_dict()),
    ):
        advance_to_qa(runtime, task["task_id"], owner)
        completed = runtime.call_agent(
            owner,
            "task.complete",
            {
                "task_id": task["task_id"],
                "outcome": f"{owner} completed synthetic work",
                "evidence": [f"synthetic://{owner}/evidence"],
            },
        )
        assert completed["status"] == "COMPLETED"

    advance_to_qa(runtime, by_owner["coo"]["task_id"], "coo")
    coo_completed = runtime.call_agent(
        "coo",
        "task.complete",
        {
            "task_id": by_owner["coo"]["task_id"],
            "outcome": "delivery feasible with fresh staffing evidence",
            "evidence": ["synthetic://coo/feasibility", "synthetic://consultant-network-steward/evidence"],
        },
    )
    assert coo_completed["status"] == "COMPLETED"

    observed = runtime.call_agent("agentops", "task.list", {})
    assert {item["task_id"] for item in observed} >= {
        root["task_id"],
        by_owner["cro"]["task_id"],
        by_owner["cfo"]["task_id"],
        by_owner["coo"]["task_id"],
        steward.task_id,
    }
    assert runtime.call_agent("agentops", "task.get", {"task_id": root["task_id"]})["status"] == "INTAKE"

    advance_to_qa(runtime, root["task_id"], "cos")
    completed_root = runtime.call_agent(
        "cos",
        "task.complete",
        {
            "task_id": root["task_id"],
            "outcome": "CoS synthesized all synthetic functional evidence",
            "evidence": [
                "synthetic://cro/evidence",
                "synthetic://cfo/evidence",
                "synthetic://coo/feasibility",
                "synthetic://consultant-network-steward/evidence",
                "synthetic://devils-advocate/challenge",
            ],
        },
    )
    assert completed_root["status"] == "COMPLETED"
    verified_root = runtime.call_agent(
        "cos",
        "task.verify",
        {
            "task_id": root["task_id"],
            "passed": True,
            "reason": "synthetic acceptance test passed against all required evidence",
            "evidence_references": ["synthetic://acceptance/root"],
        },
    )
    assert verified_root["status"] == "VERIFIED"
    verification = runtime.ledger.get_record("verification", root["task_id"])
    assert verification["verifier_id"] == "cos"
    assert verification["evidence"] == ["synthetic://acceptance/root"]

    chain = runtime.call_agent("cos", "governance.verify_audit_chain", {})
    assert chain["valid"] is True
    assert chain["event_count"] >= 1


def test_completion_and_verification_fail_closed_without_evidence_and_duplicate_completion_is_safe() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "completion negative test",
            "expected_outcome": "controlled completion",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": "cro",
            "decision_owner": "michael",
            "authority_level": 2,
            "acceptance_test": "evidence required",
        },
    )
    advance_to_qa(runtime, task["task_id"], "cro")
    with pytest.raises(ValueError, match="evidence"):
        runtime.call_agent(
            "cro",
            "task.complete",
            {"task_id": task["task_id"], "outcome": "claim without evidence", "evidence": []},
        )
    assert runtime.call_agent("cro", "task.get", {"task_id": task["task_id"]})["status"] == "QA"

    runtime.call_agent(
        "cro",
        "task.complete",
        {"task_id": task["task_id"], "outcome": "supported", "evidence": ["synthetic://evidence"]},
    )
    with pytest.raises(ValueError, match="Invalid transition"):
        runtime.call_agent(
            "cro",
            "task.complete",
            {"task_id": task["task_id"], "outcome": "duplicate", "evidence": ["synthetic://duplicate"]},
        )
    assert runtime.call_agent("cro", "task.get", {"task_id": task["task_id"]})["status"] == "COMPLETED"

    with pytest.raises(PermissionError):
        runtime.call_agent(
            "cro",
            "task.verify",
            {
                "task_id": task["task_id"],
                "passed": True,
                "reason": "self verification",
                "evidence_references": ["synthetic://evidence"],
            },
        )
    with pytest.raises(ValueError, match="requires evidence"):
        runtime.call_agent(
            "cos",
            "task.verify",
            {
                "task_id": task["task_id"],
                "passed": True,
                "reason": "attempt without acceptance evidence",
                "evidence_references": [],
            },
        )
    assert runtime.call_agent("cos", "task.get", {"task_id": task["task_id"]})["status"] == "COMPLETED"


def test_delegation_depth_authority_and_approval_inheritance_fail_closed() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "delivery parent",
            "expected_outcome": "delivery readiness",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": "cos",
            "decision_owner": "michael",
            "authority_level": 2,
            "acceptance_test": "delivery evidence exists",
        },
    )
    coo_task = runtime.call_agent(
        "cos",
        "task.decompose",
        {
            "parent_task_id": root["task_id"],
            "work_packages": [
                {
                    "objective": "delivery readiness",
                    "expected_outcome": "delivery readiness evidence",
                    "accountable_agent": "coo",
                    "authority_level": 2,
                    "acceptance_test": "delivery readiness evidence is sufficient",
                }
            ],
        },
    )[0]
    coo_delegation = delegation_payload(coo_task["task_id"], "coo", "delivery readiness")
    coo_delegation["approval_gates"] = ["L4 qualified human"]
    runtime.call_agent(
        "cos",
        "delegation.create",
        {
            "delegation": coo_delegation,
            "parent_authority": 2,
            "depth": 1,
            "ancestry": ["cos"],
            "parent_approval_gates": [],
        },
    )
    steward_task = runtime.cos.decompose(
        coo_task["task_id"],
        [
            {
                "objective": "readiness",
                "expected_outcome": "evidence-backed readiness",
                "accountable_agent": "consultant-network-steward",
                "authority_level": 2,
                "acceptance_test": "readiness evidence is sufficient",
            }
        ],
    )[0]
    payload = delegation_payload(steward_task.task_id, "consultant-network-steward", "readiness")
    payload["approval_gates"] = ["L4 qualified human"]
    created = runtime.call_agent(
        "coo",
        "delegation.create",
        {
            "delegation": payload,
            "parent_authority": 2,
            "depth": 2,
            "ancestry": ["cos", "coo"],
            "parent_approval_gates": ["L4 qualified human"],
        },
    )
    assert created["delegating_agent"] == "coo"
    assert created["accountable_agent"] == "consultant-network-steward"
    assert "L4 qualified human" in created["approval_gates"]

    too_deep = Delegation(
        **{
            **delegation_payload("T-depth3", "message-ops", "illegal depth"),
            "delegating_agent": "consultant-network-steward",
            "authority_level": AuthorityLevel.L2,
        }
    )
    with pytest.raises(ValueError, match="depth exceeded"):
        validate_delegation(too_deep, parent_authority=2, depth=3)

    widened = Delegation(
        **{
            **delegation_payload("T-wide", "cro", "authority widening"),
            "delegating_agent": "cos",
            "authority_level": AuthorityLevel.L3,
        }
    )
    with pytest.raises(PermissionError, match="widen authority"):
        validate_delegation(widened, parent_authority=2, depth=1)

    dropped_gate = Delegation(
        **{
            **delegation_payload("T-gate", "cro", "approval inheritance"),
            "delegating_agent": "cos",
            "authority_level": AuthorityLevel.L2,
        }
    )
    with pytest.raises(PermissionError, match="drop parent approval"):
        validate_delegation(
            dropped_gate,
            parent_authority=2,
            depth=1,
            parent_approval_gates=["L4 qualified human"],
        )

    with pytest.raises(PermissionError):
        runtime.call_agent(
            "consultant-network-steward",
            "delegation.create",
            {
                "delegation": delegation_payload("T-depth3-runtime", "message-ops", "illegal"),
                "parent_authority": 2,
                "depth": 3,
            },
        )


def test_stale_consultant_availability_cannot_become_confirmed_readiness() -> None:
    stale = (datetime.now(UTC) - timedelta(days=90)).isoformat()
    assert readiness(
        capability_match=True,
        availability_checked_at=stale,
        max_age_days=30,
        rate_valid=True,
        contracting_ready=True,
        availability_confirmed=True,
    ) == "REQUIRES_REFRESH"


def test_child_failure_cannot_silently_verify_parent() -> None:
    runtime = MCPRuntime(TaskLedger())
    parent = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "parent outcome",
            "expected_outcome": "parent accepted only after child succeeds",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": "cos",
            "decision_owner": "michael",
            "authority_level": 2,
            "acceptance_test": "child success is evidenced",
        },
    )
    child = runtime.cos.decompose(
        parent["task_id"],
        [
            {
                "objective": "child work",
                "expected_outcome": "child evidence",
                "accountable_agent": "cro",
                "authority_level": 2,
                "acceptance_test": "child evidence exists",
            }
        ],
    )[0]
    advance_to_qa(runtime, child.task_id, "cro")
    runtime.call_agent(
        "cro",
        "task.complete",
        {"task_id": child.task_id, "outcome": "child failed acceptance", "evidence": ["synthetic://bad"]},
    )
    runtime.call_agent(
        "cos",
        "task.verify",
        {
            "task_id": child.task_id,
            "passed": False,
            "reason": "child acceptance failed",
            "evidence_references": ["synthetic://bad"],
        },
    )
    assert runtime.call_agent("cos", "task.get", {"task_id": child.task_id})["status"] == "REWORK"
    assert runtime.call_agent("cos", "task.get", {"task_id": parent["task_id"]})["status"] == "INTAKE"
    with pytest.raises(ValueError, match="Invalid transition"):
        runtime.call_agent(
            "cos",
            "task.verify",
            {
                "task_id": parent["task_id"],
                "passed": True,
                "reason": "cannot bypass failed child",
                "evidence_references": ["synthetic://parent"],
            },
        )
    assert runtime.call_agent("cos", "task.get", {"task_id": parent["task_id"]})["status"] == "INTAKE"

from __future__ import annotations

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime, OWNER_EXECUTION_PROTOCOL
from mesh_cos.mcp_validation import RequestValidationError, load_input_schemas, validate_tool_arguments


def intake(runtime: MCPRuntime, *, owner: str = "cos", authority: int = 2, key: str = "root") -> dict:
    return runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": f"{owner} authority closure work",
            "expected_outcome": "bounded evidence-backed result",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": owner,
            "decision_owner": "michael",
            "authority_level": authority,
            "acceptance_test": "bounded result is evidenced",
            "idempotency_key": key,
        },
    )


def child(runtime: MCPRuntime, parent: dict, owner: str, *, authority: int | None = None) -> dict:
    return runtime.call_agent(
        parent["accountable_agent"],
        "task.decompose",
        {
            "parent_task_id": parent["task_id"],
            "work_packages": [
                {
                    "objective": f"{owner} delegated work",
                    "expected_outcome": "bounded delegated result",
                    "accountable_agent": owner,
                    "authority_level": authority if authority is not None else parent["authority_level"],
                    "acceptance_test": "delegated result is evidenced",
                }
            ],
        },
    )[0]


def delegate(
    runtime: MCPRuntime,
    task: dict,
    *,
    delegation_id: str = "D1",
    permitted_actions: list[str] | None = None,
    permitted_capabilities: list[str] | None = None,
) -> dict:
    parent = runtime.call_agent("cos", "task.get", {"task_id": task["parent_task_id"]})
    return runtime.call_agent(
        parent["accountable_agent"],
        "delegation.create",
        {
            "delegation": {
                "delegation_id": delegation_id,
                "task_id": task["task_id"],
                "parent_task_id": task["parent_task_id"],
                "accountable_agent": task["accountable_agent"],
                "business_objective": task["objective"],
                "expected_outcome": task["expected_outcome"],
                "deliverable": "governed result",
                "success_criteria": ["evidence supplied"],
                "priority": "P1",
                "authority_level": task["authority_level"],
                "acceptance_test": task["acceptance_test"],
                "permitted_actions": list(permitted_actions or []),
                "permitted_capabilities": list(permitted_capabilities or []),
                "approval_gates": [],
            },
            "parent_authority": parent["authority_level"],
            "depth": 1,
            "ancestry": ["cos"],
            "parent_approval_gates": [],
        },
    )


def execute_owner(
    runtime: MCPRuntime,
    task: dict,
    delegation_id: str,
    tool_name: str,
    arguments: dict,
    *,
    key: str,
    approval_references: list[str] | None = None,
) -> dict:
    return runtime.call_agent(
        "cos",
        "delegation.execute_owner",
        {
            "protocol_version": OWNER_EXECUTION_PROTOCOL,
            "delegation_id": delegation_id,
            "task_id": task["task_id"],
            "tool_name": tool_name,
            "arguments": arguments,
            "approval_references": list(approval_references or []),
            "idempotency_key": key,
        },
    )


def owner_to_qa(runtime: MCPRuntime, task: dict, delegation_id: str) -> None:
    for index, target in enumerate(("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"), start=1):
        execute_owner(
            runtime,
            task,
            delegation_id,
            "task.transition",
            {"task_id": task["task_id"], "target": target},
            key=f"transition-{index}",
        )


def request_and_decide(
    runtime: MCPRuntime,
    task: dict,
    *,
    authority: int = 4,
    action: str = "TASK_COMPLETION",
    owner: str = "Michael",
    approved: bool = True,
) -> dict:
    approval = runtime.call_agent(
        "cos",
        "approval.request",
        {
            "task_id": task["task_id"],
            "approval_owner": owner,
            "authority_level": authority,
            "action": action,
        },
    )
    runtime.call_human(
        owner,
        "approval.record_decision",
        {
            "approval_id": approval["approval_id"],
            "approved": approved,
            "reason": "synthetic authority closure decision",
        },
    )
    return runtime.call_agent("cos", "approval.get", {"approval_id": approval["approval_id"]})


def decision_payload(task: dict, approval_id: str, *, human_approver: str = "Michael") -> dict:
    return {
        "decision_type": "TEST_DECISION",
        "decision_title": "Authority closure decision",
        "task_id": task["task_id"],
        "correlation_id": task["correlation_id"],
        "decision_owner": "michael",
        "authority_level": 4,
        "human_approval_required": True,
        "approval_reference": approval_id,
        "human_approver": human_approver,
        "decision": "proceed",
        "disposition": "APPROVED_PATH",
        "decision_basis_summary": "Canonical approval and evidence support the bounded decision.",
        "evidence_references": ["synthetic://authority-closure/evidence"],
        "source_systems": ["TaskLedger"],
        "alternatives_considered": ["do not proceed"],
        "selection_criteria": ["canonical approval"],
        "confidence": "HIGH",
        "risk_level": "MEDIUM",
        "affected_entities": [task["task_id"]],
        "reversibility": "REVERSIBLE",
        "reversal_condition": "approval is withdrawn",
        "policy_rule_ids": ["canonical-approval-v2"],
        "model_provider": None,
        "model_id_version": None,
        "prompt_template_version": None,
        "data_classification": "INTERNAL",
        "outcome_validation": "review after execution",
        "outcome_status": "IN_PROGRESS",
        "retention_class": "GOVERNANCE_LONG_TERM",
    }


def test_dlg018_and_dlg019_canonical_approval_is_resolved_not_asserted_by_string() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime, authority=4)
    delegated = child(runtime, root, "cmo", authority=4)
    delegate(runtime, delegated, delegation_id="D-CMO")
    owner_to_qa(runtime, delegated, "D-CMO")

    pending = runtime.call_agent(
        "cos",
        "approval.request",
        {
            "task_id": delegated["task_id"],
            "approval_owner": "Michael",
            "authority_level": 4,
            "action": "TASK_COMPLETION",
        },
    )
    with pytest.raises(PermissionError, match="approval state blocks"):
        execute_owner(
            runtime,
            delegated,
            "D-CMO",
            "task.complete",
            {"task_id": delegated["task_id"], "outcome": "done", "evidence": ["synthetic://done"]},
            key="pending",
            approval_references=[pending["approval_id"]],
        )

    runtime.call_human(
        "Michael",
        "approval.record_decision",
        {"approval_id": pending["approval_id"], "approved": True, "reason": "approve completion"},
    )
    with pytest.raises(PermissionError, match="not found"):
        execute_owner(
            runtime,
            delegated,
            "D-CMO",
            "task.complete",
            {"task_id": delegated["task_id"], "outcome": "done", "evidence": ["synthetic://done"]},
            key="fake-ref",
            approval_references=["approval-does-not-exist"],
        )

    other_root = intake(runtime, authority=4, key="other-root")
    other = child(runtime, other_root, "cfo", authority=4)
    wrong_task_approval = request_and_decide(runtime, other, action="TASK_COMPLETION")
    with pytest.raises(PermissionError, match="canonical task"):
        execute_owner(
            runtime,
            delegated,
            "D-CMO",
            "task.complete",
            {"task_id": delegated["task_id"], "outcome": "done", "evidence": ["synthetic://done"]},
            key="wrong-task",
            approval_references=[wrong_task_approval["approval_id"]],
        )

    completed = execute_owner(
        runtime,
        delegated,
        "D-CMO",
        "task.complete",
        {"task_id": delegated["task_id"], "outcome": "done", "evidence": ["synthetic://done"]},
        key="approved",
        approval_references=[pending["approval_id"]],
    )
    assert completed["result"]["status"] == "COMPLETED"
    assert completed["approval_reference"] == pending["approval_id"]
    event = runtime.ledger.list_records("audit_event_v2")[-1]
    assert event["approval_reference"] == pending["approval_id"]
    assert event["human_approver"] == "Michael"


def test_dlg018_rejected_and_tampered_approval_fail_closed() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime, authority=4)
    delegated = child(runtime, root, "cmo", authority=4)
    delegate(runtime, delegated, delegation_id="D-CMO")
    owner_to_qa(runtime, delegated, "D-CMO")

    rejected = request_and_decide(runtime, delegated, action="TASK_COMPLETION", approved=False)
    with pytest.raises(PermissionError, match="approval state blocks"):
        execute_owner(
            runtime,
            delegated,
            "D-CMO",
            "task.complete",
            {"task_id": delegated["task_id"], "outcome": "done", "evidence": ["synthetic://done"]},
            key="rejected",
            approval_references=[rejected["approval_id"]],
        )

    approved = request_and_decide(runtime, delegated, action="TASK_COMPLETION")
    tampered = dict(approved)
    tampered["decided_by"] = "NotMichael"
    runtime.ledger.save_record("approval", approved["approval_id"], tampered)
    with pytest.raises(PermissionError, match="decision actor"):
        runtime._validate_approval_reference(
            approved["approval_id"],
            task_id=delegated["task_id"],
            minimum_authority=4,
        )


def test_l4_governance_decision_requires_action_bound_canonical_approval() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = intake(runtime, authority=4)
    approval = request_and_decide(runtime, task, action="TEST_DECISION")

    payload = decision_payload(task, approval["approval_id"])
    decided = runtime.call_agent("cos", "governance.record_decision", payload)
    assert decided["approval_reference"] == approval["approval_id"]
    assert decided["human_approver"] == "Michael"

    wrong_action = request_and_decide(runtime, task, action="OTHER_DECISION")
    with pytest.raises(PermissionError, match="action"):
        runtime.call_agent(
            "cos",
            "governance.record_decision",
            decision_payload(task, wrong_action["approval_id"]),
        )
    with pytest.raises(PermissionError, match="human approver"):
        runtime.call_agent(
            "cos",
            "governance.record_decision",
            decision_payload(task, approval["approval_id"], human_approver="FakeMichael"),
        )


def test_l5_approval_owner_is_server_constrained_to_michael() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = intake(runtime, authority=5)
    with pytest.raises(PermissionError, match="owned by Michael"):
        runtime.call_agent(
            "cos",
            "approval.request",
            {
                "task_id": task["task_id"],
                "approval_owner": "OtherHuman",
                "authority_level": 5,
                "action": "L5_TEST",
            },
        )


def test_dlg020_capability_scope_is_intersection_not_role_allowlist() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    created = delegate(
        runtime,
        delegated,
        delegation_id="D-CMO",
        permitted_capabilities=["mesh-marketing-messaging"],
    )
    assert created["permitted_capabilities"] == ["mesh-marketing-messaging"]

    allowed = execute_owner(
        runtime,
        delegated,
        "D-CMO",
        "skills.invoke_governed",
        {"capability": "mesh-marketing-messaging", "payload": {}},
        key="allowed-skill",
    )
    assert allowed["result"]["status"] == "AUTHORIZED"
    assert allowed["result"]["agent_id"] == "cmo"
    assert allowed["result"]["payload"]["execution_mode"] == "LOGICAL_SKILL_AGENT"

    with pytest.raises(PermissionError, match="explicitly permitted"):
        execute_owner(
            runtime,
            delegated,
            "D-CMO",
            "skills.invoke_governed",
            {"capability": "mesh-executive-communications", "payload": {}},
            key="denied-skill",
        )


def test_dlg021_nested_execution_requires_explicit_delegate_action() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    delegate(
        runtime,
        delegated,
        delegation_id="D-CMO",
        permitted_actions=["marketing_strategy"],
    )
    with pytest.raises(PermissionError, match="nested delegation"):
        execute_owner(
            runtime,
            delegated,
            "D-CMO",
            "task.decompose",
            {
                "parent_task_id": delegated["task_id"],
                "work_packages": [
                    {
                        "objective": "content work",
                        "expected_outcome": "content result",
                        "accountable_agent": "vp-content",
                        "authority_level": 2,
                        "acceptance_test": "content result evidenced",
                    }
                ],
            },
            key="nested-denied",
        )
    assert runtime.ledger.get_record("work_graph", delegated["task_id"]) is None


def test_dlg022_invalid_owners_are_rejected_before_canonical_mutation() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="Unknown agent"):
        intake(runtime, owner="not-an-agent")
    assert runtime.ledger.list_tasks() == []

    root = intake(runtime)
    with pytest.raises(PermissionError, match="direct child"):
        runtime.call_agent(
            "cos",
            "task.decompose",
            {
                "parent_task_id": root["task_id"],
                "work_packages": [
                    {
                        "objective": "invalid nested owner",
                        "expected_outcome": "none",
                        "accountable_agent": "vp-content",
                        "authority_level": 2,
                        "acceptance_test": "never written",
                    }
                ],
            },
        )
    assert runtime.ledger.get_record("work_graph", root["task_id"]) is None

    runtime.registry["cmo"]["runtime_health"] = "QUARANTINED"
    with pytest.raises(PermissionError, match="not routable"):
        runtime.call_agent(
            "cos",
            "task.reassign",
            {
                "task_id": root["task_id"],
                "expected_owner": "cos",
                "new_owner": "cmo",
                "reason": "must fail before mutation",
            },
        )
    assert runtime.ledger.get_task(root["task_id"]).accountable_agent == "cos"


def test_dlg023_public_owner_execution_schema_is_versioned_and_bounded() -> None:
    schemas = load_input_schemas()
    schema = schemas["delegation.execute_owner"]
    assert "protocol_version" in schema["required"]
    assert schema["properties"]["protocol_version"]["enum"] == [OWNER_EXECUTION_PROTOCOL]
    assert "task.list" not in schema["properties"]["tool_name"]["enum"]
    assert "task.verify" not in schema["properties"]["tool_name"]["enum"]
    assert "permitted_capabilities" in schemas["delegation.create"]["properties"]["delegation"]["properties"]

    with pytest.raises(RequestValidationError) as error:
        validate_tool_arguments(
            "delegation.execute_owner",
            {
                "delegation_id": "D1",
                "task_id": "T1",
                "tool_name": "task.list",
                "arguments": {},
                "idempotency_key": "K1",
            },
        )
    reasons = {(item["field"], item["reason"]) for item in error.value.details}
    assert ("protocol_version", "required") in reasons
    assert ("tool_name", "enum") in reasons


def test_dlg024_skill_handoff_does_not_claim_synchronous_workspace_agent_execution() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    delegate(
        runtime,
        delegated,
        delegation_id="D-CMO",
        permitted_capabilities=["mesh-marketing-messaging"],
    )
    response = execute_owner(
        runtime,
        delegated,
        "D-CMO",
        "skills.invoke_governed",
        {"capability": "mesh-marketing-messaging", "payload": {}},
        key="logical-skill-agent",
    )["result"]
    assert response["execution_mode"] == "CHATGPT_SKILL_HANDOFF"
    assert response["payload"]["execution_mode"] == "LOGICAL_SKILL_AGENT"
    assert "result" not in response


def test_owner_executor_rejects_global_list_and_verifier_surfaces() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    delegate(runtime, delegated, delegation_id="D-CMO")
    for tool_name in ("task.list", "task.verify"):
        with pytest.raises(PermissionError, match="not available|verifier"):
            execute_owner(runtime, delegated, "D-CMO", tool_name, {}, key=f"deny-{tool_name}")

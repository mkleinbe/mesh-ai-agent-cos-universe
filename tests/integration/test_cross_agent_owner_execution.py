from __future__ import annotations

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.mcp_validation import RequestValidationError, validate_tool_arguments
from mesh_cos.registry import load_registry

REGISTRY = load_registry()
DIRECT_REPORTS = sorted(
    agent_id
    for agent_id, record in REGISTRY.items()
    if record.get("parent_agent_id") == "cos" and record.get("status") == "ACTIVE"
)


def intake(runtime: MCPRuntime, owner: str = "cos", *, key: str = "root") -> dict:
    return runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": f"{owner} governed work",
            "expected_outcome": "evidence-backed result",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": owner,
            "decision_owner": "michael",
            "authority_level": 2,
            "acceptance_test": "result is supported by evidence",
            "idempotency_key": key,
        },
    )


def child(
    runtime: MCPRuntime,
    parent: dict,
    owner: str,
    *,
    dependencies: list[str] | None = None,
) -> dict:
    return runtime.call_agent(
        parent["accountable_agent"],
        "task.decompose",
        {
            "parent_task_id": parent["task_id"],
            "work_packages": [
                {
                    "objective": f"{owner} child work",
                    "expected_outcome": f"{owner} evidence",
                    "accountable_agent": owner,
                    "authority_level": 2,
                    "acceptance_test": f"{owner} evidence is present",
                    "dependencies": list(dependencies or []),
                }
            ],
        },
    )[0]


def delegation_payload(task: dict, delegation_id: str) -> dict:
    return {
        "delegation_id": delegation_id,
        "task_id": task["task_id"],
        "parent_task_id": task["parent_task_id"],
        "accountable_agent": task["accountable_agent"],
        "business_objective": task["objective"],
        "expected_outcome": task["expected_outcome"],
        "deliverable": "governed result",
        "success_criteria": ["evidence supplied"],
        "priority": "P1",
        "authority_level": 2,
        "acceptance_test": task["acceptance_test"],
        "approval_gates": [],
    }


def delegate(runtime: MCPRuntime, parent_owner: str, task: dict, delegation_id: str, *, depth: int) -> dict:
    return runtime.call_agent(
        parent_owner,
        "delegation.create",
        {
            "delegation": delegation_payload(task, delegation_id),
            "parent_authority": 2,
            "depth": depth,
            "ancestry": ["cos"] if depth == 1 else ["cos", parent_owner],
            "parent_approval_gates": [],
        },
    )


def execute_owner(
    runtime: MCPRuntime,
    caller: str,
    delegation_id: str,
    task_id: str,
    tool_name: str,
    arguments: dict,
    key: str,
) -> dict:
    return runtime.call_agent(
        caller,
        "delegation.execute_owner",
        {
            "delegation_id": delegation_id,
            "task_id": task_id,
            "tool_name": tool_name,
            "arguments": arguments,
            "idempotency_key": key,
        },
    )


def owner_transition(
    runtime: MCPRuntime,
    caller: str,
    delegation_id: str,
    task_id: str,
    target: str,
    *,
    key: str,
) -> dict:
    return execute_owner(
        runtime,
        caller,
        delegation_id,
        task_id,
        "task.transition",
        {"task_id": task_id, "target": target},
        key,
    )


def owner_to_qa(runtime: MCPRuntime, caller: str, delegation_id: str, task_id: str) -> None:
    for index, target in enumerate(("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"), start=1):
        owner_transition(
            runtime,
            caller,
            delegation_id,
            task_id,
            target,
            key=f"{delegation_id}-transition-{index}",
        )


def owner_complete(
    runtime: MCPRuntime,
    caller: str,
    delegation_id: str,
    task_id: str,
    owner: str,
    *,
    key: str | None = None,
) -> dict:
    return execute_owner(
        runtime,
        caller,
        delegation_id,
        task_id,
        "task.complete",
        {
            "task_id": task_id,
            "outcome": f"{owner} completed delegated work",
            "evidence": [f"synthetic://{owner}/evidence"],
        },
        key or f"{delegation_id}-complete",
    )


def create_nested_child(
    runtime: MCPRuntime,
    top_delegation_id: str,
    parent_task: dict,
    owner: str,
    *,
    key: str,
) -> dict:
    return execute_owner(
        runtime,
        "cos",
        top_delegation_id,
        parent_task["task_id"],
        "task.decompose",
        {
            "parent_task_id": parent_task["task_id"],
            "work_packages": [
                {
                    "objective": f"{owner} nested work",
                    "expected_outcome": f"{owner} nested evidence",
                    "accountable_agent": owner,
                    "authority_level": 2,
                    "acceptance_test": f"{owner} nested evidence is present",
                }
            ],
        },
        key,
    )["result"][0]


def create_nested_delegation(
    runtime: MCPRuntime,
    top_delegation_id: str,
    parent_task: dict,
    nested_task: dict,
    nested_delegation_id: str,
    parent_owner: str,
) -> dict:
    return execute_owner(
        runtime,
        "cos",
        top_delegation_id,
        parent_task["task_id"],
        "delegation.create",
        {
            "delegation": delegation_payload(nested_task, nested_delegation_id),
            "parent_authority": 2,
            "depth": 2,
            "ancestry": ["cos", parent_owner],
            "parent_approval_gates": [],
        },
        f"{top_delegation_id}-create-{nested_delegation_id}",
    )


def nested_owner_operation(
    runtime: MCPRuntime,
    top_delegation_id: str,
    parent_task: dict,
    nested_delegation_id: str,
    nested_task: dict,
    tool_name: str,
    arguments: dict,
    key: str,
) -> dict:
    return execute_owner(
        runtime,
        "cos",
        top_delegation_id,
        parent_task["task_id"],
        "delegation.execute_owner",
        {
            "delegation_id": nested_delegation_id,
            "task_id": nested_task["task_id"],
            "tool_name": tool_name,
            "arguments": arguments,
            "idempotency_key": key,
        },
        f"{top_delegation_id}-route-{key}",
    )["result"]


def nested_owner_to_qa(
    runtime: MCPRuntime,
    top_delegation_id: str,
    parent_task: dict,
    nested_delegation_id: str,
    nested_task: dict,
) -> None:
    for index, target in enumerate(("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"), start=1):
        result = nested_owner_operation(
            runtime,
            top_delegation_id,
            parent_task,
            nested_delegation_id,
            nested_task,
            "task.transition",
            {"task_id": nested_task["task_id"], "target": target},
            f"{nested_delegation_id}-transition-{index}",
        )
        assert result["executing_principal"] == nested_task["accountable_agent"]
        assert result["result"]["status"] == target


def nested_owner_complete(
    runtime: MCPRuntime,
    top_delegation_id: str,
    parent_task: dict,
    nested_delegation_id: str,
    nested_task: dict,
) -> dict:
    return nested_owner_operation(
        runtime,
        top_delegation_id,
        parent_task,
        nested_delegation_id,
        nested_task,
        "task.complete",
        {
            "task_id": nested_task["task_id"],
            "outcome": f"{nested_task['accountable_agent']} completed nested work",
            "evidence": [f"synthetic://{nested_task['accountable_agent']}/evidence"],
        },
        f"{nested_delegation_id}-complete",
    )


def test_dlg001_cos_owned_work_completes_under_cos_identity() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = intake(runtime)
    for target in ("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"):
        runtime.call_agent("cos", "task.transition", {"task_id": task["task_id"], "target": target})
    completed = runtime.call_agent(
        "cos",
        "task.complete",
        {
            "task_id": task["task_id"],
            "outcome": "CoS completed owned work",
            "evidence": ["synthetic://cos/evidence"],
        },
    )
    assert completed["status"] == "COMPLETED"
    assert any(
        event["event_type"] == "task_complete" and event["actor_agent"] == "cos"
        for event in runtime.ledger.list_events()
    )


@pytest.mark.parametrize("owner", DIRECT_REPORTS)
def test_dlg002_registry_driven_cos_direct_report_matrix(owner: str) -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime, key=f"root-{owner}")
    delegated = child(runtime, root, owner)
    delegation_id = f"D-{owner}"
    created = delegate(runtime, "cos", delegated, delegation_id, depth=1)
    assert created["accountable_agent"] == owner
    route = runtime.ledger.get_record("owner_execution_route", delegation_id)
    assert route is not None
    assert route["status"] == "OWNER_ROUTABLE"
    assert route["expected_execution_principal"] == owner

    owner_to_qa(runtime, "cos", delegation_id, delegated["task_id"])
    completed = owner_complete(runtime, "cos", delegation_id, delegated["task_id"], owner)
    assert completed["executing_principal"] == owner
    assert completed["orchestrating_agent"] == "cos"
    assert completed["result"]["status"] == "COMPLETED"
    assert runtime.call_agent("cos", "task.get", {"task_id": delegated["task_id"]})["status"] == "COMPLETED"
    assert any(
        event["event_type"] == "task_complete" and event["actor_agent"] == owner
        for event in runtime.ledger.list_events()
    )


def test_dlg003_cmo_to_vp_content_nested_execution_and_return_path() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    cmo_task = child(runtime, root, "cmo")
    delegate(runtime, "cos", cmo_task, "D-CMO", depth=1)
    for index, target in enumerate(("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS"), start=1):
        owner_transition(runtime, "cos", "D-CMO", cmo_task["task_id"], target, key=f"cmo-start-{index}")

    vp = create_nested_child(runtime, "D-CMO", cmo_task, "vp-content", key="cmo-decompose-vp")
    create_nested_delegation(runtime, "D-CMO", cmo_task, vp, "D-VP", "cmo")
    nested_owner_to_qa(runtime, "D-CMO", cmo_task, "D-VP", vp)
    nested_completed = nested_owner_complete(runtime, "D-CMO", cmo_task, "D-VP", vp)
    assert nested_completed["executing_principal"] == "vp-content"
    assert nested_completed["result"]["status"] == "COMPLETED"

    owner_transition(runtime, "cos", "D-CMO", cmo_task["task_id"], "QA", key="cmo-qa")
    executive_completed = owner_complete(runtime, "cos", "D-CMO", cmo_task["task_id"], "cmo")
    assert executive_completed["executing_principal"] == "cmo"
    assert runtime.call_agent("cos", "task.get", {"task_id": cmo_task["task_id"]})["status"] == "COMPLETED"


def test_dlg004_coo_to_consultant_network_steward_nested_execution_and_depth_zero() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    coo_task = child(runtime, root, "coo")
    delegate(runtime, "cos", coo_task, "D-COO", depth=1)
    steward = create_nested_child(runtime, "D-COO", coo_task, "consultant-network-steward", key="coo-decompose-steward")
    create_nested_delegation(runtime, "D-COO", coo_task, steward, "D-STEW", "coo")
    nested_owner_to_qa(runtime, "D-COO", coo_task, "D-STEW", steward)
    completed = nested_owner_complete(runtime, "D-COO", coo_task, "D-STEW", steward)
    assert completed["executing_principal"] == "consultant-network-steward"
    with pytest.raises(PermissionError):
        runtime.call_agent(
            "consultant-network-steward",
            "delegation.create",
            {"delegation": delegation_payload(steward, "D-ILLEGAL")},
        )


def test_dlg005_zero_depth_agent_cannot_delegate() -> None:
    runtime = MCPRuntime(TaskLedger())
    for agent_id in ("agentops", "answer-desk", "vp-content", "consultant-network-steward", "message-ops"):
        assert int(runtime.registry[agent_id]["max_delegation_depth"]) == 0
        with pytest.raises(PermissionError):
            runtime.call_agent(agent_id, "delegation.create", {"delegation": {}})


def test_dlg006_owner_identity_cannot_be_selected_by_request_data() -> None:
    payload = {
        "delegation_id": "D1",
        "task_id": "T1",
        "tool_name": "task.get",
        "arguments": {"task_id": "T1"},
        "idempotency_key": "K1",
        "owner": "cmo",
    }
    with pytest.raises(RequestValidationError) as error:
        validate_tool_arguments("delegation.execute_owner", payload)
    assert {item["field"] for item in error.value.details} == {"owner"}


def test_dlg007_cfo_cannot_inherit_cmo_capability() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    cfo_task = child(runtime, root, "cfo")
    delegate(runtime, "cos", cfo_task, "D-CFO", depth=1)
    with pytest.raises(PermissionError, match="Capability not allowed"):
        execute_owner(
            runtime,
            "cos",
            "D-CFO",
            cfo_task["task_id"],
            "skills.invoke_governed",
            {"capability": "mesh-marketing-messaging", "payload": {}},
            "cfo-cmo-capability",
        )
    failure = runtime.ledger.get_record("owner_execution", "D-CFO:cfo-cmo-capability")
    assert failure is not None
    assert failure["status"] == "OWNER_EXECUTION_FAILED"
    assert failure["failure_classification"] == "PermissionError"


def test_dlg008_owner_completion_attribution_is_canonical() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    delegate(runtime, "cos", delegated, "D-CMO", depth=1)
    owner_to_qa(runtime, "cos", "D-CMO", delegated["task_id"])
    completed = owner_complete(runtime, "cos", "D-CMO", delegated["task_id"], "cmo")
    assert completed["accountable_owner"] == "cmo"
    assert completed["executing_principal"] == "cmo"
    event = [event for event in runtime.ledger.list_events() if event["event_type"] == "task_complete"][-1]
    assert event["actor_agent"] == "cmo"


def test_dlg009_parent_direct_completion_of_child_is_rejected() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    for target in ("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"):
        runtime.call_agent("cmo", "task.transition", {"task_id": delegated["task_id"], "target": target})
    with pytest.raises(PermissionError, match="accountable owner"):
        runtime.call_agent(
            "cos",
            "task.complete",
            {
                "task_id": delegated["task_id"],
                "outcome": "false parent completion",
                "evidence": ["synthetic://invalid"],
            },
        )


def test_dlg010_completion_and_verification_remain_separate() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    delegate(runtime, "cos", delegated, "D-CMO", depth=1)
    owner_to_qa(runtime, "cos", "D-CMO", delegated["task_id"])
    owner_complete(runtime, "cos", "D-CMO", delegated["task_id"], "cmo")
    assert runtime.call_agent("cos", "task.get", {"task_id": delegated["task_id"]})["status"] == "COMPLETED"
    with pytest.raises(PermissionError):
        runtime.call_agent(
            "cmo",
            "task.verify",
            {
                "task_id": delegated["task_id"],
                "passed": True,
                "reason": "self verification",
                "evidence_references": ["synthetic://cmo/evidence"],
            },
        )
    verified = runtime.call_agent(
        "cos",
        "task.verify",
        {
            "task_id": delegated["task_id"],
            "passed": True,
            "reason": "independent acceptance evidence satisfied",
            "evidence_references": ["synthetic://cmo/evidence"],
        },
    )
    assert verified["status"] == "VERIFIED"


def test_dlg011_owner_execution_retry_is_idempotent_and_key_is_request_bound() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    delegate(runtime, "cos", delegated, "D-CMO", depth=1)
    first = owner_transition(
        runtime,
        "cos",
        "D-CMO",
        delegated["task_id"],
        "TRIAGED",
        key="retry-key",
    )
    second = owner_transition(
        runtime,
        "cos",
        "D-CMO",
        delegated["task_id"],
        "TRIAGED",
        key="retry-key",
    )
    assert second == first
    assert len(runtime.ledger.list_records("owner_execution")) == 1
    assert len(runtime.ledger.list_records("audit_event_v2")) == 1
    with pytest.raises(PermissionError, match="idempotency key"):
        owner_transition(
            runtime,
            "cos",
            "D-CMO",
            delegated["task_id"],
            "PLANNED",
            key="retry-key",
        )


def test_dlg012_unavailable_owner_fails_before_delegation_and_records_recovery_path() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    runtime.registry["cmo"]["runtime_health"] = "WATCH"
    with pytest.raises(RuntimeError, match="OWNER_RUNTIME_UNAVAILABLE"):
        delegate(runtime, "cos", delegated, "D-CMO", depth=1)
    assert runtime.ledger.get_record("delegation", "D-CMO") is None
    failure = runtime.ledger.list_records("owner_routing_failure")[-1]
    assert failure["failure_classification"] == "OWNER_RUNTIME_UNAVAILABLE"
    assert failure["retry_eligibility"] is True
    assert failure["canonical_task"] == delegated["task_id"]
    assert failure["executing_principal"] is None


def test_dlg013_quarantined_owner_is_not_silently_activated() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    runtime.registry["cmo"]["runtime_health"] = "QUARANTINED"
    with pytest.raises(PermissionError, match="not routable"):
        delegate(runtime, "cos", delegated, "D-CMO", depth=1)
    assert runtime.registry["cmo"]["runtime_health"] == "QUARANTINED"
    assert runtime.ledger.get_record("delegation", "D-CMO") is None
    failure = runtime.ledger.list_records("owner_routing_failure")[-1]
    assert failure["failure_classification"] == "OWNER_DISABLED_OR_QUARANTINED"
    assert failure["retry_eligibility"] is False


def test_dlg014_approval_requirements_are_inherited_through_nested_delegation() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    cmo_task = child(runtime, root, "cmo")
    direct = delegate(runtime, "cos", cmo_task, "D-CMO", depth=1)
    assert set(runtime.registry["cmo"]["required_approvals"]).issubset(set(direct["approval_gates"]))

    vp = create_nested_child(runtime, "D-CMO", cmo_task, "vp-content", key="approval-decompose-vp")
    create_nested_delegation(runtime, "D-CMO", cmo_task, vp, "D-VP", "cmo")
    nested = runtime.ledger.get_record("delegation", "D-VP")
    assert nested is not None
    expected = set(direct["approval_gates"]) | set(runtime.registry["vp-content"]["required_approvals"])
    assert expected.issubset(set(nested["approval_gates"]))


def test_dlg015_message_ops_transport_cannot_fabricate_human_approval() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    task = child(runtime, root, "message-ops")
    delegate(runtime, "cos", task, "D-MSG", depth=1)
    with pytest.raises(PermissionError, match="human-only"):
        execute_owner(
            runtime,
            "cos",
            "D-MSG",
            task["task_id"],
            "approval.record_decision",
            {"approval_id": "A1", "approved": True, "reason": "fabricated"},
            "fabricate-approval",
        )
    assert runtime.ledger.list_records("approval") == []


def test_dlg016_dependency_release_requires_verified_predecessor_and_occurs_once() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    predecessor = child(runtime, root, "cmo")
    dependent = child(runtime, root, "cos", dependencies=[predecessor["task_id"]])
    delegate(runtime, "cos", predecessor, "D-CMO", depth=1)
    owner_to_qa(runtime, "cos", "D-CMO", predecessor["task_id"])
    owner_complete(runtime, "cos", "D-CMO", predecessor["task_id"], "cmo")

    for target in ("TRIAGED", "PLANNED", "ASSIGNED"):
        runtime.call_agent("cos", "task.transition", {"task_id": dependent["task_id"], "target": target})
    with pytest.raises(RuntimeError, match="dependencies are not verified"):
        runtime.call_agent("cos", "task.transition", {"task_id": dependent["task_id"], "target": "IN_PROGRESS"})

    runtime.call_agent(
        "cos",
        "task.verify",
        {
            "task_id": predecessor["task_id"],
            "passed": True,
            "reason": "predecessor acceptance satisfied",
            "evidence_references": ["synthetic://cmo/evidence"],
        },
    )
    progressed = runtime.call_agent("cos", "task.transition", {"task_id": dependent["task_id"], "target": "IN_PROGRESS"})
    assert progressed["status"] == "IN_PROGRESS"
    with pytest.raises(ValueError, match="Invalid transition"):
        runtime.call_agent("cos", "task.transition", {"task_id": dependent["task_id"], "target": "IN_PROGRESS"})


def test_dlg017_nested_specialist_completion_returns_to_executive_then_cos() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    cmo_task = child(runtime, root, "cmo")
    delegate(runtime, "cos", cmo_task, "D-CMO", depth=1)
    for index, target in enumerate(("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS"), start=1):
        owner_transition(runtime, "cos", "D-CMO", cmo_task["task_id"], target, key=f"exec-{index}")
    vp = create_nested_child(runtime, "D-CMO", cmo_task, "vp-content", key="return-decompose")
    create_nested_delegation(runtime, "D-CMO", cmo_task, vp, "D-VP", "cmo")
    nested_owner_to_qa(runtime, "D-CMO", cmo_task, "D-VP", vp)
    nested = nested_owner_complete(runtime, "D-CMO", cmo_task, "D-VP", vp)
    assert nested["result"]["status"] == "COMPLETED"
    assert runtime.ledger.get_record("owner_execution_route", "D-VP")["status"] == "OWNER_COMPLETED"

    owner_transition(runtime, "cos", "D-CMO", cmo_task["task_id"], "QA", key="exec-qa")
    executive = owner_complete(runtime, "cos", "D-CMO", cmo_task["task_id"], "cmo")
    assert executive["result"]["status"] == "COMPLETED"
    assert runtime.ledger.get_record("owner_execution_route", "D-CMO")["status"] == "OWNER_COMPLETED"
    observed = runtime.call_agent("cos", "task.get", {"task_id": cmo_task["task_id"]})
    assert observed["accountable_agent"] == "cmo"
    assert observed["status"] == "COMPLETED"


def test_delegation_caller_hints_cannot_override_canonical_authority_or_lineage() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    base = {
        "delegation": delegation_payload(delegated, "D-CMO"),
        "parent_authority": 2,
        "depth": 1,
        "ancestry": ["cos"],
        "parent_approval_gates": [],
    }
    for field, value, match in (
        ("parent_authority", 3, "parent authority"),
        ("depth", 2, "depth"),
        ("ancestry", ["cos", "cro"], "ancestry"),
        ("active_owner", "cfo", "active owner"),
    ):
        payload = dict(base)
        payload[field] = value
        with pytest.raises(PermissionError, match=match):
            runtime.call_agent("cos", "delegation.create", payload)


def test_delegation_idempotent_reuse_is_exact_and_conflicting_reuse_fails() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    first_task = child(runtime, root, "cmo")
    first = delegate(runtime, "cos", first_task, "D-SAME", depth=1)
    assert delegate(runtime, "cos", first_task, "D-SAME", depth=1) == first

    second_task = child(runtime, root, "cfo")
    with pytest.raises(ValueError, match="already bound"):
        runtime.call_agent(
            "cos",
            "delegation.create",
            {
                "delegation": delegation_payload(second_task, "D-SAME"),
                "parent_authority": 2,
                "depth": 1,
                "ancestry": ["cos"],
                "parent_approval_gates": [],
            },
        )


def test_owner_execution_route_tampering_fails_closed() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    delegate(runtime, "cos", delegated, "D-CMO", depth=1)
    route = runtime.ledger.get_record("owner_execution_route", "D-CMO")
    assert route is not None
    route["accountable_owner"] = "cfo"
    runtime.ledger.save_record("owner_execution_route", "D-CMO", route)
    with pytest.raises(PermissionError, match="does not match"):
        execute_owner(
            runtime,
            "cos",
            "D-CMO",
            delegated["task_id"],
            "task.get",
            {"task_id": delegated["task_id"]},
            "tampered-route",
        )


def test_nested_owner_executor_cannot_cross_to_sibling_task() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    cmo_task = child(runtime, root, "cmo")
    cfo_task = child(runtime, root, "cfo")
    delegate(runtime, "cos", cmo_task, "D-CMO", depth=1)
    delegate(runtime, "cos", cfo_task, "D-CFO", depth=1)
    with pytest.raises(PermissionError, match="canonical delegator"):
        execute_owner(
            runtime,
            "cos",
            "D-CMO",
            cmo_task["task_id"],
            "delegation.execute_owner",
            {
                "delegation_id": "D-CFO",
                "task_id": cfo_task["task_id"],
                "tool_name": "task.get",
                "arguments": {"task_id": cfo_task["task_id"]},
                "idempotency_key": "cross-sibling-inner",
            },
            "cross-sibling-outer",
        )


def test_owner_unavailable_after_delegation_records_actionable_routing_failure() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    delegate(runtime, "cos", delegated, "D-CMO", depth=1)
    runtime.registry["cmo"]["runtime_health"] = "WATCH"
    with pytest.raises(RuntimeError, match="OWNER_RUNTIME_UNAVAILABLE"):
        execute_owner(
            runtime,
            "cos",
            "D-CMO",
            delegated["task_id"],
            "task.get",
            {"task_id": delegated["task_id"]},
            "owner-down",
        )
    failure = runtime.ledger.list_records("owner_routing_failure")[-1]
    assert failure["canonical_task"] == delegated["task_id"]
    assert failure["delegation"] == "D-CMO"
    assert failure["orchestrator"] == "cos"
    assert failure["accountable_owner"] == "cmo"
    assert failure["expected_execution_principal"] == "cmo"
    assert failure["attempted_operation"] == "task.get"
    assert failure["failure_classification"] == "OWNER_RUNTIME_UNAVAILABLE"
    assert failure["retry_eligibility"] is True
    assert runtime.ledger.get_record("owner_execution_route", "D-CMO")["status"] == "OWNER_ROUTING_FAILED"

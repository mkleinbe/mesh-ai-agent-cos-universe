from __future__ import annotations

import json
from copy import deepcopy

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.mcp_validation import _apply_schema_patches
from mesh_cos.models import AuthorityLevel, TaskRecord


def make_task(
    task_id: str = "T1",
    owner: str = "cro",
    *,
    parent_task_id: str | None = None,
    authority: AuthorityLevel = AuthorityLevel.L2,
) -> TaskRecord:
    return TaskRecord(
        task_id=task_id,
        objective="objective",
        expected_outcome="outcome",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent=owner,
        decision_owner="michael",
        authority_level=authority,
        acceptance_test="accepted",
        parent_task_id=parent_task_id,
    )


def approval_record(
    approval_id: str,
    *,
    task_id: str = "T1",
    status: str = "APPROVED",
    authority_level: int = 4,
    approval_owner: str = "qualified-human",
    decided_by: str = "qualified-human",
    action: str = "OPERATING_JUDGMENT",
) -> dict:
    return {
        "approval_id": approval_id,
        "task_id": task_id,
        "status": status,
        "authority_level": authority_level,
        "approval_owner": approval_owner,
        "decided_by": decided_by,
        "action": action,
    }


def delegation_payload(task: TaskRecord, delegation_id: str, **overrides) -> dict:
    payload = {
        "delegation_id": delegation_id,
        "task_id": task.task_id,
        "parent_task_id": task.parent_task_id,
        "accountable_agent": task.accountable_agent,
        "business_objective": task.objective,
        "expected_outcome": task.expected_outcome,
        "deliverable": "brief",
        "success_criteria": ["supported"],
        "priority": "P1",
        "authority_level": int(task.authority_level),
        "acceptance_test": task.acceptance_test,
    }
    payload.update(overrides)
    return payload


def test_owner_candidate_can_explicitly_forbid_self_assignment() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="Self assignment"):
        runtime._validate_owner_candidate("cro", parent_agent_id="cro", allow_self=False)


@pytest.mark.parametrize(
    ("record", "kwargs", "message"),
    [
        (approval_record("A1", status="PENDING"), {}, "not approved"),
        (approval_record("A2", authority_level=3), {}, "below"),
        (
            approval_record("A3", approval_owner="qualified-human", decided_by="other-human"),
            {},
            "does not match",
        ),
        (approval_record("A4", action="OTHER"), {"required_action": "OPERATING_JUDGMENT"}, "action"),
        (
            approval_record("A5"),
            {"human_approver": "other-human"},
            "Caller-supplied human approver",
        ),
        (
            approval_record(
                "A6",
                authority_level=5,
                approval_owner="qualified-human",
                decided_by="qualified-human",
            ),
            {"minimum_authority": 5},
            "Michael",
        ),
    ],
)
def test_canonical_approval_validation_denial_edges(record: dict, kwargs: dict, message: str) -> None:
    runtime = MCPRuntime(TaskLedger())
    runtime.ledger.save_record("approval", record["approval_id"], record)
    call_kwargs = {
        "task_id": "T1",
        "minimum_authority": 4,
        "required_action": None,
        "human_approver": None,
    }
    call_kwargs.update(kwargs)
    with pytest.raises(PermissionError, match=message):
        runtime._validate_approval_reference(record["approval_id"], **call_kwargs)


def test_approved_authority_reference_iteration_and_fallback_are_fail_closed() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = make_task()
    runtime.ledger.save_task(task)
    bad = approval_record("A-BAD", status="REJECTED")
    good = approval_record("A-GOOD")
    runtime.ledger.save_record("approval", good["approval_id"], good)
    runtime.ledger.save_record("approval", bad["approval_id"], bad)

    resolved = runtime._find_approved_task_authority(
        task,
        minimum_authority=4,
        approval_references=["A-BAD", "A-GOOD"],
    )
    assert resolved["approval_id"] == "A-GOOD"

    with pytest.raises(PermissionError, match="not approved"):
        runtime._find_approved_task_authority(
            task,
            minimum_authority=4,
            approval_references=["A-BAD"],
        )

    resolved_fallback = runtime._find_approved_task_authority(task, minimum_authority=4)
    assert resolved_fallback["approval_id"] == "A-GOOD"

    empty_runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="No canonical approved authority"):
        empty_runtime._find_approved_task_authority(make_task(), minimum_authority=4)


def test_l4_governance_event_requires_canonical_task() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="canonical task"):
        runtime._authorize_governance_authority(
            "cro",
            {
                "authority_level": 4,
                "approval_reference": "A1",
                "action": "REVIEW",
            },
            decision=False,
        )


def test_stall_remediation_validates_requested_new_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = MCPRuntime(TaskLedger())
    monkeypatch.setattr(
        runtime.cos,
        "remediate_stalled",
        lambda *args, **kwargs: make_task("T1", "cmo"),
    )
    result = runtime._task_remediate_stall(
        "cos",
        {"task_id": "T1", "new_owner": "cmo", "reason": "capacity"},
    )
    assert result["accountable_agent"] == "cmo"


def test_existing_delegation_id_cannot_rebind_canonical_work() -> None:
    runtime = MCPRuntime(TaskLedger())
    runtime.ledger.save_task(make_task("P1", "cos"))
    runtime.ledger.save_task(make_task("T1", "cro", parent_task_id="P1"))
    runtime.ledger.save_record(
        "delegation",
        "D1",
        {
            "delegation_id": "D1",
            "task_id": "OTHER",
            "delegating_agent": "cos",
            "accountable_agent": "cro",
        },
    )
    payload = {
        "delegation": delegation_payload(runtime.ledger.get_task("T1"), "D1"),
        "parent_authority": 2,
        "depth": 1,
        "ancestry": ["cos"],
    }
    with pytest.raises(ValueError, match="already bound"):
        runtime._delegation_create("cos", payload)


def test_delegation_rejects_capability_outside_owner_registry() -> None:
    runtime = MCPRuntime(TaskLedger())
    parent = make_task("P1", "cos")
    child = make_task("T1", "cfo", parent_task_id="P1")
    runtime.ledger.save_task(parent)
    runtime.ledger.save_task(child)
    payload = {
        "delegation": delegation_payload(
            child,
            "D-CFO",
            permitted_capabilities=["mesh-marketing-messaging"],
        ),
        "parent_authority": 2,
        "depth": 1,
        "ancestry": ["cos"],
    }
    with pytest.raises(PermissionError, match="capabilities outside owner authority"):
        runtime._delegation_create("cos", payload)


def test_owner_scoped_arguments_reject_cross_boundary_reads_and_nested_routes() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = make_task("T1", "cmo")

    with pytest.raises(KeyError):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "delegation.execute_owner",
            {"delegation_id": "MISSING", "task_id": "C1"},
        )

    base_nested = {
        "delegation_id": "D-NEST",
        "delegating_agent": "cmo",
        "parent_task_id": "T1",
        "task_id": "C1",
        "accountable_agent": "vp-content",
    }
    wrong_delegator = deepcopy(base_nested)
    wrong_delegator["delegating_agent"] = "coo"
    runtime.ledger.save_record("delegation", "D-WRONG-DELEGATOR", wrong_delegator)
    with pytest.raises(PermissionError, match="canonical delegator"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "delegation.execute_owner",
            {"delegation_id": "D-WRONG-DELEGATOR", "task_id": "C1"},
        )

    wrong_parent = deepcopy(base_nested)
    wrong_parent["parent_task_id"] = "OTHER"
    runtime.ledger.save_record("delegation", "D-WRONG-PARENT", wrong_parent)
    with pytest.raises(PermissionError, match="descend"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "delegation.execute_owner",
            {"delegation_id": "D-WRONG-PARENT", "task_id": "C1"},
        )

    runtime.ledger.save_record("delegation", "D-NEST", base_nested)
    with pytest.raises(PermissionError, match="canonical child delegation"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "delegation.execute_owner",
            {"delegation_id": "D-NEST", "task_id": "OTHER"},
        )

    with pytest.raises(PermissionError, match="cross canonical task"):
        runtime._owner_scoped_arguments(task, "cmo", "task.get", {"task_id": "OTHER"})
    with pytest.raises(PermissionError, match="decomposition"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "task.decompose",
            {"parent_task_id": "OTHER", "work_packages": []},
        )

    with pytest.raises(KeyError):
        runtime._owner_scoped_arguments(task, "cmo", "approval.get", {"approval_id": "A-MISSING"})
    runtime.ledger.save_record("approval", "A-OTHER", approval_record("A-OTHER", task_id="OTHER"))
    with pytest.raises(PermissionError, match="another task"):
        runtime._owner_scoped_arguments(task, "cmo", "approval.get", {"approval_id": "A-OTHER"})

    with pytest.raises(KeyError):
        runtime._owner_scoped_arguments(task, "cmo", "registry.get_agent", {"agent_id": "missing"})
    with pytest.raises(PermissionError, match="self or direct children"):
        runtime._owner_scoped_arguments(task, "cmo", "registry.get_agent", {"agent_id": "cfo"})

    with pytest.raises(PermissionError, match="Skill invocation"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "skills.invoke_governed",
            {
                "capability": "mesh-marketing-messaging",
                "payload": {"task_id": "OTHER"},
            },
        )


def test_owner_scoped_arguments_accept_valid_nested_and_local_reads() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = make_task("T1", "cmo")
    nested = {
        "delegation_id": "D-NEST",
        "delegating_agent": "cmo",
        "parent_task_id": "T1",
        "task_id": "C1",
        "accountable_agent": "vp-content",
    }
    runtime.ledger.save_record("delegation", "D-NEST", nested)
    nested_args = runtime._owner_scoped_arguments(
        task,
        "cmo",
        "delegation.execute_owner",
        {
            "delegation_id": "D-NEST",
            "task_id": "C1",
            "tool_name": "task.get",
            "arguments": {"task_id": "C1"},
            "idempotency_key": "nested-read",
        },
    )
    assert nested_args["protocol_version"] == "mesh.cos.owner-execution.v2"

    same_task = runtime._owner_scoped_arguments(task, "cmo", "task.get", {"task_id": "T1"})
    assert same_task["task_id"] == "T1"

    runtime.ledger.save_record("approval", "A1", approval_record("A1", task_id="T1"))
    local_approval = runtime._owner_scoped_arguments(
        task,
        "cmo",
        "approval.get",
        {"approval_id": "A1"},
    )
    assert local_approval["approval_id"] == "A1"

    self_record = runtime._owner_scoped_arguments(
        task,
        "cmo",
        "registry.get_agent",
        {"agent_id": "cmo"},
    )
    assert self_record["agent_id"] == "cmo"
    child_record = runtime._owner_scoped_arguments(
        task,
        "cmo",
        "registry.get_agent",
        {"agent_id": "vp-content"},
    )
    assert child_record["agent_id"] == "vp-content"

    skill = runtime._owner_scoped_arguments(
        task,
        "cmo",
        "skills.invoke_governed",
        {"capability": "mesh-marketing-messaging", "payload": {}},
    )
    assert skill["payload"]["task_id"] == "T1"
    assert skill["payload"]["execution_mode"] == "LOGICAL_SKILL_AGENT"


def test_owner_execution_requires_nonempty_idempotency_key() -> None:
    runtime = MCPRuntime(TaskLedger())
    runtime.ledger.save_task(make_task("T1", "cro"))
    runtime.ledger.save_record(
        "delegation",
        "D1",
        {
            "delegation_id": "D1",
            "task_id": "T1",
            "parent_task_id": "P1",
            "delegating_agent": "cos",
            "accountable_agent": "cro",
            "approval_gates": [],
            "permitted_actions": [],
            "permitted_capabilities": [],
        },
    )
    with pytest.raises(ValueError, match="idempotency_key"):
        runtime._delegation_execute_owner(
            "cos",
            {
                "delegation_id": "D1",
                "task_id": "T1",
                "tool_name": "task.get",
                "arguments": {"task_id": "T1"},
                "idempotency_key": "",
            },
        )


def test_owner_execution_validates_optional_approval_reference() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = make_task("T1", "cro")
    runtime.ledger.save_task(task)
    runtime.ledger.save_record(
        "delegation",
        "D1",
        {
            "delegation_id": "D1",
            "task_id": "T1",
            "parent_task_id": "P1",
            "delegating_agent": "cos",
            "accountable_agent": "cro",
            "approval_gates": [],
            "permitted_actions": [],
            "permitted_capabilities": [],
        },
    )
    runtime.ledger.save_record("approval", "A1", approval_record("A1", task_id="T1"))
    result = runtime._delegation_execute_owner(
        "cos",
        {
            "delegation_id": "D1",
            "task_id": "T1",
            "tool_name": "task.get",
            "arguments": {"task_id": "T1"},
            "approval_references": ["A1"],
            "idempotency_key": "approved-read",
        },
    )
    assert result["approval_reference"] == "A1"
    assert result["result"]["task_id"] == "T1"


def test_approval_request_rejects_agent_owner_and_non_michael_l5() -> None:
    runtime = MCPRuntime(TaskLedger())
    runtime.ledger.save_task(make_task("T1", "cro"))
    with pytest.raises(PermissionError, match="qualified human"):
        runtime._approval_request(
            "cro",
            {"task_id": "T1", "approval_owner": "cmo", "authority_level": 4, "action": "pricing"},
        )
    with pytest.raises(PermissionError, match="Michael"):
        runtime._approval_request(
            "cro",
            {
                "task_id": "T1",
                "approval_owner": "qualified-human",
                "authority_level": 5,
                "action": "commitment",
            },
        )


def test_high_authority_conflict_resolution_requires_canonical_approval(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(KeyError):
        runtime._conflict_decide(
            "cos",
            {"conflict_id": "MISSING", "authority_level": 4, "disposition": "resolve"},
        )

    runtime.ledger.save_record("conflict", "C1", {"conflict_id": "C1", "task_id": "T1"})
    approval = approval_record(
        "A1",
        action="CONFLICT_RESOLUTION",
        approval_owner="qualified-human",
        decided_by="qualified-human",
    )
    runtime.ledger.save_record("approval", "A1", approval)
    monkeypatch.setattr(
        runtime.conflicts,
        "decide",
        lambda conflict_id, **kwargs: {"conflict_id": conflict_id, **kwargs},
    )
    resolved = runtime._conflict_decide(
        "cos",
        {
            "conflict_id": "C1",
            "authority_level": 4,
            "approval_reference": "A1",
            "human_approver": "qualified-human",
            "disposition": "resolve",
        },
    )
    assert resolved["owner"] == "cos"
    assert resolved["human_approver"] == "qualified-human"


def test_schema_patch_loader_covers_missing_invalid_unknown_and_valid_patch(tmp_path) -> None:
    schemas = {
        "tool": {
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": [],
            "additionalProperties": False,
        }
    }
    original = deepcopy(schemas)
    _apply_schema_patches(schemas, tmp_path / "missing.json")
    assert schemas == original

    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps({"schema_version": "wrong", "tools": {}}))
    with pytest.raises(ValueError, match="Unsupported"):
        _apply_schema_patches(schemas, invalid)

    unknown = tmp_path / "unknown.json"
    unknown.write_text(
        json.dumps(
            {
                "schema_version": "mesh.cos.mcp-tool-input-schema-patches.v1",
                "tools": {"other": {"required": ["x"]}},
            }
        )
    )
    with pytest.raises(ValueError, match="unknown tools"):
        _apply_schema_patches(schemas, unknown)

    valid = tmp_path / "valid.json"
    valid.write_text(
        json.dumps(
            {
                "schema_version": "mesh.cos.mcp-tool-input-schema-patches.v1",
                "tools": {
                    "tool": {
                        "properties": {"value": {"minLength": 1}},
                        "required": ["value"],
                    }
                },
            }
        )
    )
    _apply_schema_patches(schemas, valid)
    assert schemas["tool"]["required"] == ["value"]
    assert schemas["tool"]["properties"]["value"] == {"type": "string", "minLength": 1}

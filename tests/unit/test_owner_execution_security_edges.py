from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.mcp_validation import load_input_schemas
from mesh_cos.models import AuthorityLevel, TaskRecord


def make_task(
    task_id: str,
    owner: str,
    *,
    parent_task_id: str | None = None,
    authority: AuthorityLevel = AuthorityLevel.L2,
) -> TaskRecord:
    return TaskRecord(
        task_id=task_id,
        objective=f"{owner} objective",
        expected_outcome="supported result",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent=owner,
        decision_owner="michael",
        authority_level=authority,
        acceptance_test="evidence exists",
        parent_task_id=parent_task_id,
    )


def delegation_args(
    task: TaskRecord,
    owner: str,
    *,
    delegation_id: str = "D1",
    parent_task_id: str | None = None,
    authority: int = 2,
    permitted_actions: list[str] | None = None,
) -> dict:
    return {
        "delegation": {
            "delegation_id": delegation_id,
            "task_id": task.task_id,
            "parent_task_id": parent_task_id if parent_task_id is not None else task.parent_task_id,
            "accountable_agent": owner,
            "business_objective": "bounded work",
            "expected_outcome": "supported result",
            "deliverable": "result",
            "success_criteria": ["evidence exists"],
            "priority": "P1",
            "authority_level": authority,
            "acceptance_test": "evidence exists",
            "approval_gates": [],
            "permitted_actions": list(permitted_actions or []),
        },
        "parent_authority": 2,
        "depth": 1,
        "ancestry": ["cos"],
        "parent_approval_gates": [],
    }


def canonical_pair(runtime: MCPRuntime, owner: str = "cmo") -> tuple[TaskRecord, TaskRecord]:
    parent = make_task("P1", "cos")
    child = make_task("C1", owner, parent_task_id=parent.task_id)
    runtime.ledger.save_task(parent)
    runtime.ledger.save_task(child)
    return parent, child


def create_valid_delegation(runtime: MCPRuntime, owner: str = "cmo") -> tuple[TaskRecord, dict]:
    _, child = canonical_pair(runtime, owner)
    created = runtime._delegation_create("cos", delegation_args(child, owner))
    return child, created


def test_active_owner_fails_when_registry_agent_lacks_required_lifecycle_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = MCPRuntime(TaskLedger())
    monkeypatch.setattr(
        WorkspaceAgentMCPPolicy,
        "allowed_tools",
        lambda self, agent_id: ("task.get",),
    )
    with pytest.raises(RuntimeError, match="OWNER_EXECUTION_TRANSPORT_UNAVAILABLE"):
        runtime._active_owner_record("cmo")


def test_non_cos_non_owner_verification_write_guard_fails_closed() -> None:
    runtime = MCPRuntime(TaskLedger())
    runtime.ledger.save_task(make_task("T1", "cfo"))
    with pytest.raises(PermissionError, match="accountable owner or Chief of Staff"):
        runtime._require_task_write_access("cro", "T1")


def test_zero_depth_handler_fails_before_accepting_delegation_payload() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="not permitted"):
        runtime._delegation_create("agentops", {"delegation": {}})


def test_delegation_rejects_missing_child_owner_mismatch_and_missing_parent() -> None:
    runtime = MCPRuntime(TaskLedger())
    missing = make_task("MISSING", "cmo", parent_task_id="P1")
    with pytest.raises(KeyError, match="MISSING"):
        runtime._delegation_create("cos", delegation_args(missing, "cmo"))

    parent = make_task("P1", "cos")
    child = make_task("C1", "cmo", parent_task_id="P1")
    runtime.ledger.save_task(parent)
    runtime.ledger.save_task(child)
    with pytest.raises(PermissionError, match="owner must match"):
        runtime._delegation_create("cos", delegation_args(child, "cfo"))

    orphan = make_task("ORPHAN", "cmo")
    runtime.ledger.save_task(orphan)
    with pytest.raises(ValueError, match="canonical parent"):
        runtime._delegation_create("cos", delegation_args(orphan, "cmo"))


def test_delegation_rejects_missing_or_wrong_parent_graph_and_authority_mismatch() -> None:
    runtime = MCPRuntime(TaskLedger())
    child = make_task("C1", "cmo", parent_task_id="NO-PARENT")
    runtime.ledger.save_task(child)
    with pytest.raises(KeyError, match="NO-PARENT"):
        runtime._delegation_create("cos", delegation_args(child, "cmo"))

    wrong_parent = make_task("P2", "cfo")
    child.parent_task_id = "P2"
    runtime.ledger.save_task(wrong_parent)
    runtime.ledger.save_task(child)
    with pytest.raises(PermissionError, match="must own"):
        runtime._delegation_create("cos", delegation_args(child, "cmo"))

    parent = make_task("P1", "cos")
    child.parent_task_id = "P1"
    runtime.ledger.save_task(parent)
    runtime.ledger.save_task(child)
    with pytest.raises(PermissionError, match="parent task"):
        runtime._delegation_create(
            "cos",
            delegation_args(child, "cmo", parent_task_id="P-OTHER"),
        )
    with pytest.raises(PermissionError, match="authority"):
        runtime._delegation_create(
            "cos",
            delegation_args(child, "cmo", authority=1),
        )


def test_delegation_fails_if_registry_depth_changes_between_guard_and_derivation() -> None:
    runtime = MCPRuntime(TaskLedger())
    _, child = canonical_pair(runtime)

    class FlippingDepth(dict):
        def get(self, key, default=None):
            if key == "max_delegation_depth":
                return 1
            return super().get(key, default)

        def __getitem__(self, key):
            if key == "max_delegation_depth":
                return 0
            return super().__getitem__(key)

    runtime.registry["cos"] = FlippingDepth(runtime.registry["cos"])
    with pytest.raises(PermissionError, match="depth exceeds"):
        runtime._delegation_create("cos", delegation_args(child, "cmo"))


def test_delegation_cannot_grant_owner_actions_not_present_in_registry() -> None:
    runtime = MCPRuntime(TaskLedger())
    _, child = canonical_pair(runtime)
    with pytest.raises(PermissionError, match="outside owner authority"):
        runtime._delegation_create(
            "cos",
            delegation_args(child, "cmo", permitted_actions=["approve_price_or_discount"]),
        )


def test_owner_scoping_rejects_missing_or_malformed_nested_delegation() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = make_task("P-CMO", "cmo")
    runtime.ledger.save_task(task)
    with pytest.raises(KeyError, match="D-MISSING"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "delegation.execute_owner",
            {
                "delegation_id": "D-MISSING",
                "task_id": "C1",
                "tool_name": "task.get",
                "arguments": {"task_id": "C1"},
                "idempotency_key": "K1",
            },
        )

    base = {
        "delegation_id": "D-NEST",
        "task_id": "C1",
        "parent_task_id": task.task_id,
        "delegating_agent": "cmo",
        "accountable_agent": "vp-content",
    }
    runtime.ledger.save_record("delegation", "D-NEST", base)
    wrong_parent = dict(base, parent_task_id="OTHER")
    runtime.ledger.save_record("delegation", "D-NEST", wrong_parent)
    with pytest.raises(PermissionError, match="descend"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "delegation.execute_owner",
            {
                "delegation_id": "D-NEST",
                "task_id": "C1",
                "tool_name": "task.get",
                "arguments": {"task_id": "C1"},
                "idempotency_key": "K1",
            },
        )

    runtime.ledger.save_record("delegation", "D-NEST", base)
    with pytest.raises(PermissionError, match="child delegation"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "delegation.execute_owner",
            {
                "delegation_id": "D-NEST",
                "task_id": "WRONG",
                "tool_name": "task.get",
                "arguments": {"task_id": "C1"},
                "idempotency_key": "K1",
            },
        )


def test_owner_scoping_rejects_cross_task_decompose_and_skill_payloads() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = make_task("T1", "cmo")
    runtime.ledger.save_task(task)
    with pytest.raises(PermissionError, match="cross canonical task"):
        runtime._owner_scoped_arguments(task, "cmo", "task.get", {"task_id": "T2"})
    with pytest.raises(PermissionError, match="decomposition"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "task.decompose",
            {"parent_task_id": "T2", "work_packages": []},
        )
    with pytest.raises(PermissionError, match="Skill invocation"):
        runtime._owner_scoped_arguments(
            task,
            "cmo",
            "skills.invoke_governed",
            {"capability": "mesh-marketing-messaging", "payload": {"task_id": "T2"}},
        )


def test_owner_executor_rejects_missing_delegation_wrong_caller_task_and_owner() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(KeyError, match="D-MISSING"):
        runtime._delegation_execute_owner(
            "cos",
            {
                "delegation_id": "D-MISSING",
                "task_id": "C1",
                "tool_name": "task.get",
                "arguments": {"task_id": "C1"},
                "idempotency_key": "K1",
            },
        )

    child, created = create_valid_delegation(runtime)
    args = {
        "delegation_id": created["delegation_id"],
        "task_id": child.task_id,
        "tool_name": "task.get",
        "arguments": {"task_id": child.task_id},
        "idempotency_key": "K1",
    }
    with pytest.raises(PermissionError, match="canonical delegating"):
        runtime._delegation_execute_owner("cfo", args)
    with pytest.raises(PermissionError, match="task does not match"):
        runtime._delegation_execute_owner("cos", dict(args, task_id="WRONG"))

    runtime.ledger.conn.execute("DELETE FROM tasks WHERE task_id=?", (child.task_id,))
    runtime.ledger.conn.commit()
    with pytest.raises(KeyError, match=child.task_id):
        runtime._delegation_execute_owner("cos", args)

    runtime.ledger.save_task(make_task(child.task_id, "cfo", parent_task_id="P1"))
    with pytest.raises(PermissionError, match="owner no longer matches"):
        runtime._delegation_execute_owner("cos", args)


def test_owner_executor_rejects_blank_key_and_nonretryable_prior_execution() -> None:
    runtime = MCPRuntime(TaskLedger())
    child, created = create_valid_delegation(runtime)
    base = {
        "delegation_id": created["delegation_id"],
        "task_id": child.task_id,
        "tool_name": "task.get",
        "arguments": {"task_id": child.task_id},
        "idempotency_key": "",
    }
    with pytest.raises(ValueError, match="idempotency_key"):
        runtime._delegation_execute_owner("cos", base)

    failing = dict(base, idempotency_key="failed-key", tool_name="task.transition")
    failing["arguments"] = {"task_id": child.task_id, "target": "QA"}
    with pytest.raises(ValueError, match="Invalid transition"):
        runtime._delegation_execute_owner("cos", failing)
    with pytest.raises(RuntimeError, match="OWNER_EXECUTION_NOT_RETRYABLE"):
        runtime._delegation_execute_owner("cos", failing)


def test_owner_executor_handles_concurrent_claim_without_duplicate_execution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = MCPRuntime(TaskLedger())
    child, created = create_valid_delegation(runtime)
    args = {
        "delegation_id": created["delegation_id"],
        "task_id": child.task_id,
        "tool_name": "task.get",
        "arguments": {"task_id": child.task_id},
        "idempotency_key": "race",
    }
    fingerprint = hashlib.sha256(
        json.dumps(
            {
                "delegation_id": created["delegation_id"],
                "task_id": child.task_id,
                "tool_name": "task.get",
                "arguments": {"task_id": child.task_id},
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    response = {"status": "OWNER_RESULT_RECORDED", "result": {"task_id": child.task_id}}
    prior = {
        "request_fingerprint": fingerprint,
        "status": "OWNER_RESULT_RECORDED",
        "response": response,
    }
    original_get = runtime.ledger.get_record
    seen = {"owner_execution": 0}

    def get_record(record_type: str, record_id: str):
        if record_type == "owner_execution":
            seen["owner_execution"] += 1
            if seen["owner_execution"] == 1:
                return None
            return prior
        return original_get(record_type, record_id)

    monkeypatch.setattr(runtime.ledger, "get_record", get_record)
    monkeypatch.setattr(runtime.ledger, "save_idempotent_record", lambda *args, **kwargs: False)
    assert runtime._delegation_execute_owner("cos", args) == response


def test_owner_executor_fails_closed_when_concurrent_claim_has_no_reusable_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = MCPRuntime(TaskLedger())
    child, created = create_valid_delegation(runtime)
    args = {
        "delegation_id": created["delegation_id"],
        "task_id": child.task_id,
        "tool_name": "task.get",
        "arguments": {"task_id": child.task_id},
        "idempotency_key": "race-fail",
    }
    original_get = runtime.ledger.get_record
    seen = {"owner_execution": 0}

    def get_record(record_type: str, record_id: str):
        if record_type == "owner_execution":
            seen["owner_execution"] += 1
            return None if seen["owner_execution"] == 1 else {"status": "OWNER_EXECUTING"}
        return original_get(record_type, record_id)

    monkeypatch.setattr(runtime.ledger, "get_record", get_record)
    monkeypatch.setattr(runtime.ledger, "save_idempotent_record", lambda *args, **kwargs: False)
    with pytest.raises(RuntimeError, match="ALREADY_CLAIMED"):
        runtime._delegation_execute_owner("cos", args)


def test_schema_extension_loader_rejects_bad_version_shape_and_overlap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import mesh_cos.mcp_validation as validation

    default = json.loads(validation.DEFAULT_SCHEMA_PATH.read_text())
    base_path = tmp_path / "base.json"
    base_path.write_text(json.dumps(default))
    monkeypatch.setattr(validation, "DEFAULT_SCHEMA_PATH", base_path)

    bad_version = tmp_path / "bad-version.json"
    bad_version.write_text(json.dumps({"schema_version": "bad", "tools": {}}))
    monkeypatch.setattr(validation, "DEFAULT_SCHEMA_EXTENSIONS", (bad_version,))
    with pytest.raises(ValueError, match="extension version"):
        load_input_schemas()

    bad_shape = tmp_path / "bad-shape.json"
    bad_shape.write_text(
        json.dumps(
            {
                "schema_version": "mesh.cos.mcp-tool-input-schema-extension.v1",
                "tools": [],
            }
        )
    )
    monkeypatch.setattr(validation, "DEFAULT_SCHEMA_EXTENSIONS", (bad_shape,))
    with pytest.raises(TypeError, match="extension must contain tools"):
        load_input_schemas()

    duplicate_name = next(iter(default["tools"]))
    overlap = tmp_path / "overlap.json"
    overlap.write_text(
        json.dumps(
            {
                "schema_version": "mesh.cos.mcp-tool-input-schema-extension.v1",
                "tools": {duplicate_name: {"type": "object"}},
            }
        )
    )
    monkeypatch.setattr(validation, "DEFAULT_SCHEMA_EXTENSIONS", (overlap,))
    with pytest.raises(ValueError, match="duplicates tools"):
        load_input_schemas()


def test_policy_custom_schema_registry_absolute_and_relative_paths_fail_closed(tmp_path: Path) -> None:
    policy = WorkspaceAgentMCPPolicy.from_file()
    contract = deepcopy(policy.contract)
    malformed = tmp_path / "malformed.json"
    malformed.write_text(
        json.dumps(
            {
                "schema_version": "mesh.cos.mcp-tool-input-schemas.v1",
                "tools": [],
            }
        )
    )
    contract["input_schema_registry"] = str(malformed)
    with pytest.raises(ValueError, match="exactly match"):
        WorkspaceAgentMCPPolicy(contract).validate()

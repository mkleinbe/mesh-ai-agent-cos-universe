from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.mcp_validation import (
    RequestValidationError,
    _path,
    _reject_executable_payload,
    _type_matches,
    _validate_object,
    _validate_value,
    load_input_schemas,
    validate_tool_arguments,
)
from mesh_cos.registry import load_registry


def _write_registry(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "schemas.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_schema_loader_rejects_bad_registry_version_and_shape(tmp_path: Path) -> None:
    bad_version = _write_registry(tmp_path, {"schema_version": "wrong", "tools": {}})
    with pytest.raises(ValueError, match="Unsupported"):
        load_input_schemas(bad_version)

    bad_shape = _write_registry(
        tmp_path,
        {"schema_version": "mesh.cos.mcp-tool-input-schemas.v1", "tools": []},
    )
    with pytest.raises(TypeError, match="contain tools"):
        load_input_schemas(bad_shape)

    valid = _write_registry(
        tmp_path,
        {
            "schema_version": "mesh.cos.mcp-tool-input-schemas.v1",
            "tools": {"probe": {"type": "object", "properties": {}, "required": [], "additionalProperties": False}},
        },
    )
    assert set(load_input_schemas(valid)) == {"probe"}


def test_validation_helpers_cover_supported_json_types_and_paths() -> None:
    assert _path("", "x") == "x"
    assert _path("parent", "x") == "parent.x"
    assert _type_matches(None, "null")
    assert _type_matches(True, "boolean")
    assert _type_matches(1, "integer")
    assert not _type_matches(True, "integer")
    assert _type_matches(1.5, "number")
    assert not _type_matches(False, "number")
    assert _type_matches("x", "string")
    assert _type_matches([], "array")
    assert _type_matches({}, "object")
    assert not _type_matches("x", "unknown")


def test_value_validation_reports_type_enum_length_range_and_array_constraints() -> None:
    details: list[dict[str, str]] = []
    _validate_value({"type": "integer"}, "wrong", "integer", details)
    _validate_value({"type": "string", "enum": ["A"]}, "B", "enum", details)
    _validate_value({"type": "string", "minLength": 3}, "x", "short", details)
    _validate_value({"type": "number", "minimum": 1, "maximum": 2}, 0, "low", details)
    _validate_value({"type": "number", "minimum": 1, "maximum": 2}, 3, "high", details)
    _validate_value({"type": "array", "minItems": 2, "items": {"type": "string"}}, [1], "items", details)
    reasons = {(item["field"], item["reason"]) for item in details}
    assert ("integer", "type") in reasons
    assert ("enum", "enum") in reasons
    assert ("short", "min_length") in reasons
    assert ("low", "minimum") in reasons
    assert ("high", "maximum") in reasons
    assert ("items", "min_items") in reasons
    assert ("items[0]", "type") in reasons


def test_object_validation_covers_required_unknown_properties_and_nested_values() -> None:
    details: list[dict[str, str]] = []
    _validate_object(
        {
            "type": "object",
            "properties": {"known": {"type": "string"}, "ignored": "not-a-schema"},
            "required": ["missing"],
            "additionalProperties": False,
        },
        {"known": 1, "ignored": "x", "extra": True},
        "parent",
        details,
    )
    assert {tuple(item.values()) for item in details} == {
        ("parent.missing", "required"),
        ("parent.extra", "unknown_field"),
        ("parent.known", "type"),
    }

    details = []
    _validate_object(
        {"type": "object", "properties": "bad", "required": "bad", "additionalProperties": True},
        {"free": "value"},
        "",
        details,
    )
    assert details == []


def test_executable_payload_rejection_walks_dicts_and_lists_without_executing_anything() -> None:
    details: list[dict[str, str]] = []
    _reject_executable_payload(
        {"nested": [{"shell_command": "never"}, "data"], "safe": {"value": 1}},
        "payload",
        details,
    )
    assert details == [{"field": "payload.nested[0].shell_command", "reason": "forbidden_field"}]


def test_validate_tool_arguments_handles_unknown_tool_success_and_bounded_sorted_details() -> None:
    schemas = {
        "probe": {
            "type": "object",
            "properties": {"name": {"type": "string", "minLength": 1}},
            "required": ["name"],
            "additionalProperties": False,
        },
        "skills.invoke_governed": {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "minLength": 1},
                "payload": {"type": "object", "properties": {}, "required": [], "additionalProperties": True},
            },
            "required": ["capability"],
            "additionalProperties": False,
        },
    }
    with pytest.raises(KeyError):
        validate_tool_arguments("missing", {}, schemas=schemas)
    assert validate_tool_arguments("probe", {"name": "ok"}, schemas=schemas) == {"name": "ok"}
    with pytest.raises(RequestValidationError) as caught:
        validate_tool_arguments("probe", {"z": 1}, schemas=schemas)
    assert caught.value.details == [
        {"field": "name", "reason": "required"},
        {"field": "z", "reason": "unknown_field"},
    ]

    with pytest.raises(RequestValidationError) as executable:
        validate_tool_arguments(
            "skills.invoke_governed",
            {"capability": "mesh-ppmd-bot", "payload": {"code": "print('never')"}},
            schemas=schemas,
        )
    assert executable.value.details == [{"field": "payload.code", "reason": "forbidden_field"}]

    many = RequestValidationError([{"field": str(index), "reason": "invalid"} for index in range(40)])
    assert len(many.details) == 32


def _base_contract() -> dict:
    return copy.deepcopy(WorkspaceAgentMCPPolicy.from_file().contract)


def test_policy_rejects_input_schema_registry_reference_and_version_drift(tmp_path: Path) -> None:
    contract = _base_contract()
    contract["input_schema_registry"] = ""
    with pytest.raises(ValueError, match="reference"):
        WorkspaceAgentMCPPolicy(contract).validate()

    contract = _base_contract()
    schema = json.loads((Path(__file__).resolve().parents[2] / "chatgpt" / "mcp" / "tool-input-schemas.v1.json").read_text())
    schema["schema_version"] = "wrong"
    path = _write_registry(tmp_path, schema)
    contract["input_schema_registry"] = str(path)
    with pytest.raises(ValueError, match="registry version"):
        WorkspaceAgentMCPPolicy(contract).validate()


def test_policy_rejects_input_schema_tool_set_object_and_closedness_drift(tmp_path: Path) -> None:
    original = json.loads((Path(__file__).resolve().parents[2] / "chatgpt" / "mcp" / "tool-input-schemas.v1.json").read_text())

    contract = _base_contract()
    schema = copy.deepcopy(original)
    schema["tools"] = []
    path = _write_registry(tmp_path, schema)
    contract["input_schema_registry"] = str(path)
    with pytest.raises(ValueError, match="exactly match"):
        WorkspaceAgentMCPPolicy(contract).validate()

    contract = _base_contract()
    schema = copy.deepcopy(original)
    first = next(iter(schema["tools"]))
    schema["tools"][first] = []
    path = _write_registry(tmp_path, schema)
    contract["input_schema_registry"] = str(path)
    with pytest.raises(ValueError, match="must be an object"):
        WorkspaceAgentMCPPolicy(contract).validate()

    contract = _base_contract()
    schema = copy.deepcopy(original)
    first = next(iter(schema["tools"]))
    schema["tools"][first]["additionalProperties"] = True
    path = _write_registry(tmp_path, schema)
    contract["input_schema_registry"] = str(path)
    with pytest.raises(ValueError, match="must be closed"):
        WorkspaceAgentMCPPolicy(contract).validate()


def test_governed_adapter_registry_denies_unknown_principals_and_detects_missing_server_registration() -> None:
    adapters = GovernedAdapterRegistry(load_registry())
    with pytest.raises(PermissionError, match="Unknown agent principal"):
        adapters.execute("not-an-agent", "mesh-ppmd-bot", {})

    del adapters.adapters[("cos", "mesh-ppmd-bot")]
    with pytest.raises(RuntimeError, match="not server-registered"):
        adapters.execute("cos", "mesh-ppmd-bot", {})

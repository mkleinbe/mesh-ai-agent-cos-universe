from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = ROOT / "chatgpt" / "mcp" / "tool-input-schemas.v1.json"
DEFAULT_SCHEMA_EXTENSIONS = (
    ROOT / "chatgpt" / "mcp" / "tool-input-schemas.owner-execution.v1.json",
)
FORBIDDEN_EXECUTION_FIELDS = {
    "code",
    "source_code",
    "import_path",
    "callable",
    "shell",
    "shell_command",
    "command",
    "plugin_executable",
    "skill_implementation",
    "executable",
}


class RequestValidationError(ValueError):
    """Safe public request-validation failure with bounded field metadata."""

    def __init__(self, details: list[dict[str, str]]) -> None:
        super().__init__("MCP request validation failed")
        self.details = list(details[:32])


def _schema_map(raw: Any, *, registry_label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, dict):
        raise TypeError(f"{registry_label} must contain tools")
    schemas: dict[str, dict[str, Any]] = {}
    for name, schema in raw.items():
        if not isinstance(schema, dict):
            raise ValueError(f"MCP input schema must be an object: {name}")
        schemas[str(name)] = dict(schema)
    return schemas


def load_input_schemas(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    target = Path(path) if path is not None else DEFAULT_SCHEMA_PATH
    payload = json.loads(target.read_text())
    if payload.get("schema_version") != "mesh.cos.mcp-tool-input-schemas.v1":
        raise ValueError("Unsupported MCP input-schema registry version")
    schemas = _schema_map(payload.get("tools"), registry_label="MCP input-schema registry")
    if path is None:
        for extension_path in DEFAULT_SCHEMA_EXTENSIONS:
            extension = json.loads(extension_path.read_text())
            if extension.get("schema_version") != "mesh.cos.mcp-tool-input-schema-extension.v1":
                raise ValueError("Unsupported MCP input-schema extension version")
            extension_tools = _schema_map(
                extension.get("tools"),
                registry_label="MCP input-schema extension",
            )
            overlap = set(schemas).intersection(extension_tools)
            if overlap:
                raise ValueError(f"MCP input-schema extension duplicates tools: {sorted(overlap)}")
            schemas.update(extension_tools)
    return schemas


def _path(parent: str, field: str) -> str:
    return f"{parent}.{field}" if parent else field


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return False


def _validate_value(schema: dict[str, Any], value: Any, field: str, details: list[dict[str, str]]) -> None:
    expected = schema.get("type")
    expected_types = [expected] if isinstance(expected, str) else list(expected or [])
    if expected_types and not any(_type_matches(value, item) for item in expected_types):
        details.append({"field": field, "reason": "type"})
        return

    if "enum" in schema and value not in schema["enum"]:
        details.append({"field": field, "reason": "enum"})
        return

    if isinstance(value, str):
        minimum_length = schema.get("minLength")
        if isinstance(minimum_length, int) and len(value) < minimum_length:
            details.append({"field": field, "reason": "min_length"})

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            details.append({"field": field, "reason": "minimum"})
        if isinstance(maximum, (int, float)) and value > maximum:
            details.append({"field": field, "reason": "maximum"})

    if isinstance(value, list):
        minimum_items = schema.get("minItems")
        if isinstance(minimum_items, int) and len(value) < minimum_items:
            details.append({"field": field, "reason": "min_items"})
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_value(item_schema, item, f"{field}[{index}]", details)

    if isinstance(value, dict):
        _validate_object(schema, value, field, details)


def _validate_object(
    schema: dict[str, Any],
    value: dict[str, Any],
    parent: str,
    details: list[dict[str, str]],
) -> None:
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        properties = {}
    required = schema.get("required", [])
    if isinstance(required, list):
        for key in required:
            if key not in value:
                details.append({"field": _path(parent, str(key)), "reason": "required"})
    if schema.get("additionalProperties") is False:
        for key in value:
            if key not in properties:
                details.append({"field": _path(parent, str(key)), "reason": "unknown_field"})
    for key, item in value.items():
        child_schema = properties.get(key)
        if isinstance(child_schema, dict):
            _validate_value(child_schema, item, _path(parent, str(key)), details)


def _reject_executable_payload(value: Any, parent: str, details: list[dict[str, str]]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            field = _path(parent, str(key))
            if str(key).lower() in FORBIDDEN_EXECUTION_FIELDS:
                details.append({"field": field, "reason": "forbidden_field"})
            _reject_executable_payload(item, field, details)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_executable_payload(item, f"{parent}[{index}]", details)


def validate_tool_arguments(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    schemas: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    active = schemas if schemas is not None else load_input_schemas()
    schema = active.get(tool_name)
    if schema is None:
        raise KeyError(tool_name)
    details: list[dict[str, str]] = []
    _validate_value(schema, arguments, "", details)
    if tool_name == "skills.invoke_governed" and isinstance(arguments.get("payload"), dict):
        _reject_executable_payload(arguments["payload"], "payload", details)
    if details:
        ordered = sorted(
            ({"field": str(item["field"]), "reason": str(item["reason"])} for item in details),
            key=lambda item: (item["field"], item["reason"]),
        )
        raise RequestValidationError(ordered[:32])
    return dict(arguments)

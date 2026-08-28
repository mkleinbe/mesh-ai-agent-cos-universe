from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.mcp_validation import load_input_schemas


def _write_registry(path: Path, schemas: dict) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "mesh.cos.mcp-tool-input-schemas.v1",
                "tools": schemas,
            }
        )
    )


def test_policy_rejects_non_object_schema_before_catalog_completeness(tmp_path: Path) -> None:
    policy = WorkspaceAgentMCPPolicy.from_file()
    contract = deepcopy(policy.contract)
    schemas = load_input_schemas()
    name = next(iter(schemas))
    schemas[name] = {"type": "string", "additionalProperties": False}
    registry = tmp_path / "non-object.json"
    _write_registry(registry, schemas)
    contract["input_schema_registry"] = str(registry)

    with pytest.raises(ValueError, match=f"object: {name}"):
        WorkspaceAgentMCPPolicy(contract).validate()


def test_policy_rejects_open_schema_before_catalog_completeness(tmp_path: Path) -> None:
    policy = WorkspaceAgentMCPPolicy.from_file()
    contract = deepcopy(policy.contract)
    schemas = load_input_schemas()
    name = next(iter(schemas))
    schemas[name] = dict(schemas[name])
    schemas[name]["additionalProperties"] = True
    registry = tmp_path / "open-schema.json"
    _write_registry(registry, schemas)
    contract["input_schema_registry"] = str(registry)

    with pytest.raises(ValueError, match=f"closed: {name}"):
        WorkspaceAgentMCPPolicy(contract).validate()

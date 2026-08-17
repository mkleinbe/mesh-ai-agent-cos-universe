from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


class ContractValidator:
    def __init__(self, contracts_dir: str | Path) -> None:
        self.contracts_dir = Path(contracts_dir)
        self._validators: dict[str, Draft202012Validator] = {}

    @classmethod
    def default(cls) -> "ContractValidator":
        configured = os.getenv("MESH_COS_CONTRACTS_DIR")
        if configured:
            return cls(configured)
        return cls(Path(__file__).resolve().parents[2] / "contracts")

    def validator(self, schema_name: str) -> Draft202012Validator:
        if schema_name not in self._validators:
            path = self.contracts_dir / f"{schema_name}.schema.json"
            schema = json.loads(path.read_text())
            self._validators[schema_name] = Draft202012Validator(schema)
        return self._validators[schema_name]

    def validate(self, schema_name: str, payload: dict[str, Any]) -> None:
        self.validator(schema_name).validate(payload)

    def validate_versioned(self, payload: dict[str, Any]) -> None:
        version = str(payload.get("version", ""))
        prefix = "mesh.cos."
        if not version.startswith(prefix):
            raise ValueError("Missing or invalid Mesh contract version")
        schema_name = version[len(prefix):]
        self.validate(schema_name, payload)

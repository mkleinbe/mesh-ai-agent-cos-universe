#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from mesh_cos.mcp_validation import load_input_schemas

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"
SNAPSHOT_VERSION = "mesh.cos.published-action-snapshot.v1"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_expected() -> tuple[dict[str, dict[str, Any]], set[str], dict[str, list[str]]]:
    payload = json.loads(CONTRACT.read_text())
    catalog = {str(tool["name"]) for tool in payload["tools"]}
    human = set(payload.get("human_tool_allowlist", []))
    allowlists = payload["agent_tool_allowlists"]
    expected_names = set(allowlists["cos"]) - human
    all_schemas = load_input_schemas()
    expected = {name: all_schemas[name] for name in sorted(expected_names)}
    return expected, catalog, allowlists


def load_actual(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict) or payload.get("schema_version") != SNAPSHOT_VERSION:
        raise SystemExit(f"actual surface must use schema_version={SNAPSHOT_VERSION}")
    values = payload.get("tools")
    if not isinstance(values, list):
        raise SystemExit("actual surface tools must be a list of name/input-schema objects")
    result: dict[str, dict[str, Any]] = {}
    for item in values:
        if not isinstance(item, dict):
            raise SystemExit("actual surface tool entries must be objects")
        name = str(item.get("name") or "").strip()
        schema = item.get("input_schema", item.get("inputSchema"))
        if not name or not isinstance(schema, dict):
            raise SystemExit("each actual tool requires name and input_schema")
        if name in result:
            raise SystemExit(f"duplicate actual tool: {name}")
        result[name] = dict(schema)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual-file", type=Path)
    parser.add_argument("--require-actual", action="store_true")
    args = parser.parse_args()

    expected, catalog, allowlists = load_expected()
    failures: list[str] = []
    expected_names = set(expected)

    for agent_id, tools in allowlists.items():
        missing = set(tools) - catalog
        if missing:
            failures.append(f"{agent_id}: allowlist references unknown tools {sorted(missing)}")
    if not expected_names.issubset(catalog):
        failures.append("CoS machine allowlist is not a subset of the canonical catalog")
    if "delegation.execute_owner" not in expected:
        failures.append("cos published surface must include delegation.execute_owner")

    expected_digest = digest(expected)
    if not args.actual_file:
        if args.require_actual:
            failures.append("actual ChatGPT published/draft action snapshot is required")
        if failures:
            print("PUBLISHED_ACTION_SURFACE=FAIL")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print(
            "PUBLISHED_ACTION_SURFACE=SOURCE_CONTRACT_ONLY "
            f"expected={len(expected)} catalog={len(catalog)} schema_digest={expected_digest}"
        )
        return 0

    actual = load_actual(args.actual_file)
    actual_names = set(actual)
    missing = expected_names - actual_names
    unexpected = actual_names - expected_names
    if missing:
        failures.append(f"published action snapshot missing {sorted(missing)}")
    if unexpected:
        failures.append(f"published action snapshot has unexpected {sorted(unexpected)}")
    for name in sorted(expected_names & actual_names):
        if digest(actual[name]) != digest(expected[name]):
            failures.append(f"published action schema mismatch: {name}")

    actual_digest = digest({name: actual[name] for name in sorted(actual)})
    if failures:
        print("PUBLISHED_ACTION_SURFACE=FAIL")
        print(f"expected_schema_digest={expected_digest}")
        print(f"actual_schema_digest={actual_digest}")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "PUBLISHED_ACTION_SURFACE=PASS "
        f"expected={len(expected)} catalog={len(catalog)} schema_digest={expected_digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"


def load_expected() -> tuple[set[str], set[str], dict[str, list[str]]]:
    payload = json.loads(CONTRACT.read_text())
    catalog = {tool["name"] for tool in payload["tools"]}
    human = set(payload.get("human_tool_allowlist", []))
    allowlists = payload["agent_tool_allowlists"]
    expected = set(allowlists["cos"]) - human
    return expected, catalog, allowlists


def load_actual(path: Path) -> set[str]:
    payload = json.loads(path.read_text())
    if isinstance(payload, list):
        values = payload
    elif isinstance(payload, dict) and isinstance(payload.get("tools"), list):
        values = payload["tools"]
    else:
        raise SystemExit("actual surface must be a JSON list or {\"tools\": [...]} object")
    return {str(value) for value in values}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual-file", type=Path)
    args = parser.parse_args()

    expected, catalog, allowlists = load_expected()
    failures: list[str] = []

    if len(catalog) != 30:
        failures.append(f"catalog expected 30 tools including 2 human-only, got {len(catalog)}")
    if len(expected) != 28:
        failures.append(f"cos published machine surface expected 28 tools, got {len(expected)}")
    if "delegation.execute_owner" not in expected:
        failures.append("cos published surface must include delegation.execute_owner")

    for agent_id, tools in allowlists.items():
        missing = set(tools) - catalog
        if missing:
            failures.append(f"{agent_id}: allowlist references unknown tools {sorted(missing)}")

    if args.actual_file:
        actual = load_actual(args.actual_file)
        missing = expected - actual
        unexpected = actual - expected
        if missing:
            failures.append(f"published action snapshot missing {sorted(missing)}")
        if unexpected:
            failures.append(f"published action snapshot has unexpected {sorted(unexpected)}")

    if failures:
        print("PUBLISHED_ACTION_SURFACE=FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PUBLISHED_ACTION_SURFACE=PASS expected={len(expected)} catalog={len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

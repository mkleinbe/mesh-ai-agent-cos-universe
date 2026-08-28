from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mesh_cos.mcp_validation import load_input_schemas

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"
SCRIPT = ROOT / "scripts" / "check-published-action-surface.py"
SNAPSHOT_VERSION = "mesh.cos.published-action-snapshot.v1"


def expected_actions() -> list[str]:
    payload = json.loads(CONTRACT.read_text())
    human = set(payload.get("human_tool_allowlist", []))
    return sorted(set(payload["agent_tool_allowlists"]["cos"]) - human)


def exact_snapshot() -> dict:
    schemas = load_input_schemas()
    return {
        "schema_version": SNAPSHOT_VERSION,
        "tools": [
            {"name": name, "input_schema": schemas[name]}
            for name in expected_actions()
        ],
    }


def run_check(path: Path | None = None, *, require_actual: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT)]
    if path is not None:
        command.extend(["--actual-file", str(path)])
    if require_actual:
        command.append("--require-actual")
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_exact_published_surface_and_schemas_pass(tmp_path: Path) -> None:
    actual = tmp_path / "actual.json"
    actual.write_text(json.dumps(exact_snapshot()))
    result = run_check(actual)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PUBLISHED_ACTION_SURFACE=PASS" in result.stdout
    assert f"expected={len(expected_actions())}" in result.stdout


def test_missing_owner_executor_fails(tmp_path: Path) -> None:
    actual = tmp_path / "actual.json"
    snapshot = exact_snapshot()
    snapshot["tools"] = [
        item for item in snapshot["tools"] if item["name"] != "delegation.execute_owner"
    ]
    actual.write_text(json.dumps(snapshot))
    result = run_check(actual)
    assert result.returncode == 1
    assert "delegation.execute_owner" in result.stdout
    assert "PUBLISHED_ACTION_SURFACE=FAIL" in result.stdout


def test_schema_drift_fails_even_when_action_names_match(tmp_path: Path) -> None:
    actual = tmp_path / "actual.json"
    snapshot = exact_snapshot()
    owner = next(
        item for item in snapshot["tools"] if item["name"] == "delegation.execute_owner"
    )
    owner["input_schema"]["required"] = [
        field for field in owner["input_schema"]["required"] if field != "protocol_version"
    ]
    actual.write_text(json.dumps(snapshot))
    result = run_check(actual)
    assert result.returncode == 1
    assert "published action schema mismatch: delegation.execute_owner" in result.stdout


def test_source_only_check_never_claims_publication_pass() -> None:
    result = run_check()
    assert result.returncode == 0
    assert "PUBLISHED_ACTION_SURFACE=SOURCE_CONTRACT_ONLY" in result.stdout
    assert "PUBLISHED_ACTION_SURFACE=PASS" not in result.stdout


def test_require_actual_fails_without_workspace_snapshot() -> None:
    result = run_check(require_actual=True)
    assert result.returncode == 1
    assert "actual ChatGPT published/draft action snapshot is required" in result.stdout

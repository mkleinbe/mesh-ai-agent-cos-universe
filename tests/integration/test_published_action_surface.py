from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"
SCRIPT = ROOT / "scripts" / "check-published-action-surface.py"


def expected_actions() -> list[str]:
    payload = json.loads(CONTRACT.read_text())
    human = set(payload.get("human_tool_allowlist", []))
    return sorted(set(payload["agent_tool_allowlists"]["cos"]) - human)


def run_check(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--actual-file", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_exact_published_surface_passes(tmp_path: Path) -> None:
    actual = tmp_path / "actual.json"
    actual.write_text(json.dumps({"tools": expected_actions()}))
    result = run_check(actual)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PUBLISHED_ACTION_SURFACE=PASS expected=28 catalog=30" in result.stdout


def test_missing_owner_executor_fails(tmp_path: Path) -> None:
    actual = tmp_path / "actual.json"
    tools = [name for name in expected_actions() if name != "delegation.execute_owner"]
    actual.write_text(json.dumps({"tools": tools}))
    result = run_check(actual)
    assert result.returncode == 1
    assert "delegation.execute_owner" in result.stdout
    assert "PUBLISHED_ACTION_SURFACE=FAIL" in result.stdout

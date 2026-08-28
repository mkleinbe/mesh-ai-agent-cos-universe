from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check-capability-closure.py"


def test_capability_execution_universe_is_closed() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "CAPABILITY_CLOSURE=PASS agents=10" in result.stdout
    assert "skills=" in result.stdout
    assert "declared_tools=" in result.stdout

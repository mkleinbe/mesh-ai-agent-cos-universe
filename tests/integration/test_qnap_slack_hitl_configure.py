from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_qnap_slack_hitl_protected_provisioning_script() -> None:
    result = subprocess.run(
        ["sh", "deployment/qnap/tests/test-slack-hitl-configure.sh"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (
        "PASS Slack HITL deploy path requires only governed approver identity and Socket Mode credential and does not log protected values"
        in result.stdout
    )

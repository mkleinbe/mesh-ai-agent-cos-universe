#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_required(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text()
    if old not in text:
        raise SystemExit(f"required token missing in {path}: {old!r}")
    target.write_text(text.replace(old, new))


replace_required(
    "tests/integration/test_governance.py",
    '    assert len(registry) == 9\n    assert "devils-advocate" not in registry\n    assert "message-ops" not in registry\n',
    '    assert len(registry) == 10\n    assert "devils-advocate" not in registry\n    assert "message-ops" in registry\n',
)

replace_required(
    "tests/unit/test_mcp_runtime_handlers.py",
    '    assert len(agents) == 9\n    assert all(record["agent_id"] != "devils-advocate" for record in agents)\n    assert all(record["agent_id"] != "message-ops" for record in agents)\n',
    '    assert len(agents) == 10\n    assert all(record["agent_id"] != "devils-advocate" for record in agents)\n    assert any(record["agent_id"] == "message-ops" for record in agents)\n',
)

replace_required(
    "tests/unit/test_mcp_stdio_bridge.py",
    '    assert len(result["result"]) == 9\n    assert all(record["agent_id"] != "devils-advocate" for record in result["result"])\n    assert all(record["agent_id"] != "message-ops" for record in result["result"])\n\n\n@pytest.mark.parametrize("removed_agent", ["devils-advocate", "message-ops"])\ndef test_bridge_rejects_removed_shared_capability_agent_identities(tmp_path: Path, removed_agent: str) -> None:\n',
    '    assert len(result["result"]) == 10\n    assert all(record["agent_id"] != "devils-advocate" for record in result["result"])\n    assert any(record["agent_id"] == "message-ops" for record in result["result"])\n\n\n@pytest.mark.parametrize("removed_agent", ["devils-advocate"])\ndef test_bridge_rejects_removed_shared_capability_agent_identities(tmp_path: Path, removed_agent: str) -> None:\n',
)

replace_required(
    "tests/evaluations/test_phase1_scenarios.py",
    "    t=TaskRecord(task_id='T',objective='o',expected_outcome='e',requested_by='m',executive_sponsor='m',accountable_agent='cro',decision_owner='m',acceptance_test='verify')\n    for s in [TaskStatus.TRIAGED,TaskStatus.PLANNED,TaskStatus.ASSIGNED,TaskStatus.IN_PROGRESS,TaskStatus.QA,TaskStatus.COMPLETED]:transition(t,s)\n",
    "    t=TaskRecord(task_id='T',objective='o',expected_outcome='e',requested_by='m',executive_sponsor='m',accountable_agent='cro',decision_owner='m',acceptance_test='verify')\n    t.outcome='done';t.outcome_evidence=['evidence://completion']\n    for s in [TaskStatus.TRIAGED,TaskStatus.PLANNED,TaskStatus.ASSIGNED,TaskStatus.IN_PROGRESS,TaskStatus.QA,TaskStatus.COMPLETED]:transition(t,s)\n",
)

replace_required(
    "tests/unit/test_control_plane.py",
    "    with pytest.raises(ValueError):transition(t,TaskStatus.COMPLETED)\n    for s in [TaskStatus.TRIAGED,TaskStatus.PLANNED,TaskStatus.ASSIGNED,TaskStatus.IN_PROGRESS,TaskStatus.QA,TaskStatus.COMPLETED]:transition(t,s)\n    with pytest.raises(ValueError):transition(t,TaskStatus.VERIFIED)\n    t.outcome_evidence=['evidence://1'];transition(t,TaskStatus.VERIFIED);transition(t,TaskStatus.CLOSED);assert t.status==TaskStatus.CLOSED\n",
    "    with pytest.raises(ValueError):transition(t,TaskStatus.COMPLETED)\n    t.outcome='done';t.outcome_evidence=['evidence://completion']\n    for s in [TaskStatus.TRIAGED,TaskStatus.PLANNED,TaskStatus.ASSIGNED,TaskStatus.IN_PROGRESS,TaskStatus.QA,TaskStatus.COMPLETED]:transition(t,s)\n    t.outcome_evidence=[]\n    with pytest.raises(ValueError):transition(t,TaskStatus.VERIFIED)\n    t.outcome_evidence=['evidence://1'];transition(t,TaskStatus.VERIFIED);transition(t,TaskStatus.CLOSED);assert t.status==TaskStatus.CLOSED\n",
)

replace_required(
    "tests/unit/test_production_hardening.py",
    "    transition(task, TaskStatus.QA)\n    transition(task, TaskStatus.COMPLETED)\n    assert task.completed_at is not None\n    with pytest.raises(ValueError, match=\"outcome evidence\"):\n        transition(task, TaskStatus.VERIFIED)\n    transition(task, TaskStatus.REWORK)\n    assert task.rework_count == 1\n    transition(task, TaskStatus.IN_PROGRESS)\n    transition(task, TaskStatus.QA)\n    transition(task, TaskStatus.COMPLETED)\n    task.outcome_evidence = [\"evidence://1\"]\n",
    "    transition(task, TaskStatus.QA)\n    task.outcome = \"done\"\n    task.outcome_evidence = [\"evidence://completion\"]\n    transition(task, TaskStatus.COMPLETED)\n    assert task.completed_at is not None\n    task.outcome_evidence = []\n    with pytest.raises(ValueError, match=\"outcome evidence\"):\n        transition(task, TaskStatus.VERIFIED)\n    transition(task, TaskStatus.REWORK)\n    assert task.rework_count == 1\n    transition(task, TaskStatus.IN_PROGRESS)\n    transition(task, TaskStatus.QA)\n    task.outcome_evidence = [\"evidence://second-completion\"]\n    transition(task, TaskStatus.COMPLETED)\n    task.outcome_evidence = [\"evidence://1\"]\n",
)

print("v4 stale-test remediation applied")

from __future__ import annotations

import pytest

from mesh_cos.lifecycle import transition
from mesh_cos.models import TaskRecord, TaskStatus


def test_completion_requires_non_empty_outcome_even_with_evidence() -> None:
    task = TaskRecord(
        task_id="T-v4-outcome",
        objective="exercise completion contract",
        expected_outcome="completed work with evidence",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cro",
        decision_owner="michael",
        acceptance_test="completion evidence is present",
    )
    for state in (
        TaskStatus.TRIAGED,
        TaskStatus.PLANNED,
        TaskStatus.ASSIGNED,
        TaskStatus.IN_PROGRESS,
        TaskStatus.QA,
    ):
        transition(task, state)

    task.outcome_evidence = ["synthetic://completion-evidence"]
    with pytest.raises(ValueError, match="non-empty outcome"):
        transition(task, TaskStatus.COMPLETED)

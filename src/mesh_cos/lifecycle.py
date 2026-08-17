from __future__ import annotations

from .models import TaskRecord, TaskStatus, utcnow

ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.INTAKE: {TaskStatus.TRIAGED, TaskStatus.CANCELLED},
    TaskStatus.TRIAGED: {TaskStatus.PLANNED, TaskStatus.CANCELLED},
    TaskStatus.PLANNED: {TaskStatus.ASSIGNED, TaskStatus.CANCELLED},
    TaskStatus.ASSIGNED: {TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.BLOCKED, TaskStatus.AWAITING_INPUT, TaskStatus.AWAITING_APPROVAL, TaskStatus.QA, TaskStatus.CANCELLED},
    TaskStatus.BLOCKED: {TaskStatus.IN_PROGRESS, TaskStatus.AWAITING_INPUT, TaskStatus.CANCELLED},
    TaskStatus.AWAITING_INPUT: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.AWAITING_APPROVAL: {TaskStatus.READY_FOR_ACTION, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.QA: {TaskStatus.REWORK, TaskStatus.READY_FOR_DECISION, TaskStatus.READY_FOR_ACTION, TaskStatus.COMPLETED},
    TaskStatus.REWORK: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.READY_FOR_DECISION: {TaskStatus.AWAITING_APPROVAL, TaskStatus.READY_FOR_ACTION, TaskStatus.CANCELLED},
    TaskStatus.READY_FOR_ACTION: {TaskStatus.COMPLETED, TaskStatus.CANCELLED},
    TaskStatus.COMPLETED: {TaskStatus.VERIFIED, TaskStatus.REWORK, TaskStatus.IN_PROGRESS},
    TaskStatus.VERIFIED: {TaskStatus.CLOSED, TaskStatus.REWORK},
    TaskStatus.CLOSED: set(),
    TaskStatus.CANCELLED: set(),
}


def transition(task: TaskRecord, target: TaskStatus) -> TaskRecord:
    if target not in ALLOWED_TRANSITIONS[task.status]:
        raise ValueError(f"Invalid transition: {task.status} -> {target}")
    if target == TaskStatus.COMPLETED and not task.acceptance_test:
        raise ValueError("Cannot complete a task without an acceptance test")
    if target == TaskStatus.VERIFIED and not task.outcome_evidence:
        raise ValueError("Verification requires outcome evidence")
    task.status = target
    now = utcnow()
    if target == TaskStatus.IN_PROGRESS and task.started_at is None:
        task.started_at = now
    elif target == TaskStatus.COMPLETED:
        task.completed_at = now
    elif target == TaskStatus.VERIFIED:
        task.verified_at = now
    elif target == TaskStatus.CLOSED:
        task.closed_at = now
    elif target == TaskStatus.REWORK:
        task.rework_count += 1
    return task

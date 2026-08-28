from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import IntEnum, StrEnum
from typing import Any


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


class AuthorityLevel(IntEnum):
    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5


class TaskStatus(StrEnum):
    INTAKE = "INTAKE"
    TRIAGED = "TRIAGED"
    PLANNED = "PLANNED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    AWAITING_INPUT = "AWAITING_INPUT"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    QA = "QA"
    REWORK = "REWORK"
    READY_FOR_DECISION = "READY_FOR_DECISION"
    READY_FOR_ACTION = "READY_FOR_ACTION"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class AgentHealth(StrEnum):
    SHADOW = "SHADOW"
    ACTIVE = "ACTIVE"
    WATCH = "WATCH"
    RESTRICTED = "RESTRICTED"
    QUARANTINED = "QUARANTINED"
    RETIRED = "RETIRED"


@dataclass(slots=True)
class TaskRecord:
    task_id: str
    objective: str
    expected_outcome: str
    requested_by: str
    executive_sponsor: str
    accountable_agent: str
    decision_owner: str
    priority: str = "P2"
    status: TaskStatus = TaskStatus.INTAKE
    authority_level: AuthorityLevel = AuthorityLevel.L0
    parent_task_id: str | None = None
    correlation_id: str = field(default_factory=lambda: new_id("corr"))
    contributors: list[str] = field(default_factory=list)
    source_references: list[str] = field(default_factory=list)
    evidence_status: str = "OPEN"
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    deliverable_contract: str = ""
    due_at: str | None = None
    next_check_at: str | None = None
    success_metrics: list[str] = field(default_factory=list)
    acceptance_test: str = ""
    blockers: list[str] = field(default_factory=list)
    approval_status: str = "NOT_REQUIRED"
    approval_owner: str | None = None
    slack_channel_id: str | None = None
    slack_thread_ts: str | None = None
    created_at: str = field(default_factory=utcnow)
    started_at: str | None = None
    completed_at: str | None = None
    verified_at: str | None = None
    closed_at: str | None = None
    outcome: str | None = None
    outcome_evidence: list[str] = field(default_factory=list)
    rework_count: int = 0
    escalation_count: int = 0
    human_touches: int = 0
    CEO_touches: int = 0
    ceo_time_avoided_estimate_minutes: int | None = None
    ceo_time_avoided_methodology: str | None = None
    audit_events: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["version"] = "mesh.cos.task.v1"
        data["status"] = self.status.value
        data["authority_level"] = int(self.authority_level)
        return data


@dataclass(slots=True)
class Delegation:
    delegation_id: str
    task_id: str
    delegating_agent: str
    accountable_agent: str
    business_objective: str
    expected_outcome: str
    deliverable: str
    success_criteria: list[str]
    priority: str
    authority_level: AuthorityLevel
    acceptance_test: str
    parent_task_id: str | None = None
    contributing_agents: list[str] = field(default_factory=list)
    deadline: str | None = None
    evidence_supplied: list[str] = field(default_factory=list)
    unresolved_evidence: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    permitted_actions: list[str] = field(default_factory=list)
    permitted_capabilities: list[str] = field(default_factory=list)
    prohibited_actions: list[str] = field(default_factory=list)
    approval_gates: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    next_check_at: str | None = None
    escalation_condition: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["version"] = "mesh.cos.delegation.v1"
        data["authority_level"] = int(self.authority_level)
        return data

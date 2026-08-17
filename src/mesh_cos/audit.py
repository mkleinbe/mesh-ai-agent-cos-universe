from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
from .models import new_id, utcnow

@dataclass(slots=True)
class AuditEvent:
    event_type: str
    actor_agent: str
    task_id: str
    correlation_id: str
    authority_level: int
    result: str
    event_id: str = ""
    event_version: str = "mesh.cos.agent-event.v1"
    timestamp: str = ""
    source: str = "mesh-cos"
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    approval_reference: str | None = None
    evidence_references: list[str] | None = None
    error: str | None = None
    idempotency_key: str = ""

    def __post_init__(self) -> None:
        self.event_id = self.event_id or new_id("event")
        self.timestamp = self.timestamp or utcnow()
        self.idempotency_key = self.idempotency_key or self.event_id

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

from __future__ import annotations

from typing import Any

from .audit import AuditEvent
from .functional_runtime import FunctionalRuntime
from .ledger import TaskLedger
from .orchestration import CoSService
from .reliability import ExecutionPolicy, execute_with_policy


class AgentExecutionService:
    """Executes bounded agent work without making chat or the tool response canonical."""

    def __init__(
        self,
        *,
        cos: CoSService,
        runtime: FunctionalRuntime,
        ledger: TaskLedger,
        policy: ExecutionPolicy | None = None,
    ) -> None:
        self.cos = cos
        self.runtime = runtime
        self.ledger = ledger
        self.policy = policy or ExecutionPolicy()

    def execute(
        self,
        *,
        task_id: str,
        agent_id: str,
        tool: str,
        source: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        task = self.ledger.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        if agent_id != task.accountable_agent and agent_id not in task.contributors:
            raise PermissionError("Agent is neither accountable owner nor registered contributor for this task")
        try:
            result = execute_with_policy(
                lambda: self.runtime.execute(agent_id, tool=tool, source=source, payload=payload or {}),
                self.policy,
            )
        except Exception as exc:
            event = AuditEvent(
                event_type="agent_execution_failed",
                actor_agent=agent_id,
                task_id=task.task_id,
                correlation_id=task.correlation_id,
                authority_level=int(task.authority_level),
                result="failed",
                evidence_references=[f"tool://{tool}"] + ([f"source://{source}"] if source else []),
                error=type(exc).__name__,
            )
            self.ledger.record_event(event.to_dict())
            raise
        event = AuditEvent(
            event_type="agent_execution_succeeded",
            actor_agent=agent_id,
            task_id=task.task_id,
            correlation_id=task.correlation_id,
            authority_level=int(task.authority_level),
            result="ok",
            evidence_references=[f"tool://{tool}"] + ([f"source://{source}"] if source else []),
        )
        self.ledger.record_event(event.to_dict())
        return result

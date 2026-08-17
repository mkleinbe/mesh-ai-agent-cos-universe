from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .adapters import GovernedAdapterRegistry
from .agentops import AgentOpsEvaluator
from .answer_desk import AnswerDeskService
from .approval import ApprovalService
from .conflict import ConflictService
from .governance import GovernanceJournal, verify_audit_chain
from .ledger import TaskLedger
from .mcp_policy import WorkspaceAgentMCPPolicy
from .metrics import MetricsService
from .models import AuthorityLevel, Delegation, TaskRecord, TaskStatus
from .orchestration import ChiefOfStaffService
from .registry import load_registry
from .reliability import ReplayManager
from .workforce import ChiefOfStaffWorkforceManager

ROOT = Path(__file__).resolve().parents[2]
HUMAN_ONLY_TOOLS = {"approval.record_decision", "reliability.human_override"}
ReplayExecutor = Callable[[dict[str, Any]], Any]
ToolHandler = Callable[[str, dict[str, Any]], Any]


@dataclass(slots=True)
class ReplayExecutorRegistry:
    """Server-owned replay executors keyed by stable identifiers, never client code."""

    executors: dict[str, ReplayExecutor] = field(default_factory=dict)

    def register(self, replay_key: str, executor: ReplayExecutor) -> None:
        if not replay_key.strip():
            raise ValueError("replay_key is required")
        self.executors[replay_key] = executor

    def resolve(self, replay_key: str) -> ReplayExecutor:
        executor = self.executors.get(replay_key)
        if executor is None:
            raise PermissionError(f"No server-registered replay executor for {replay_key!r}")
        return executor


class MCPRuntime:
    """Serialized execution boundary behind the remote Mesh CoS MCP transport.

    The transport authenticates the caller and passes only a trusted principal ID,
    tool name, and JSON arguments. This facade performs server-side allowlist checks,
    derives agent identity/provenance from the canonical registry, and dispatches to
    fixed handlers. It never imports or executes a client-supplied callable/path.
    """

    def __init__(
        self,
        ledger: TaskLedger,
        *,
        policy: WorkspaceAgentMCPPolicy | None = None,
        adapters: GovernedAdapterRegistry | None = None,
        agentops: AgentOpsEvaluator | None = None,
        replay_executors: ReplayExecutorRegistry | None = None,
    ) -> None:
        self.ledger = ledger
        self.policy = policy or WorkspaceAgentMCPPolicy.from_file()
        self.registry = load_registry()
        self.governance = GovernanceJournal(ledger)
        self.cos = ChiefOfStaffService(ledger)
        self.approvals = ApprovalService(ledger)
        self.conflicts = ConflictService(ledger)
        self.answer_desk = AnswerDeskService(ledger)
        self.metrics = MetricsService(ledger)
        self.replay = ReplayManager(ledger)
        self.replay_executors = replay_executors or ReplayExecutorRegistry()
        if agentops is None:
            agentops = AgentOpsEvaluator.from_file(
                ROOT / "config" / "performance-policy.v1.json",
                ledger=ledger,
            )
        self.agentops = agentops
        self.workforce = ChiefOfStaffWorkforceManager(ledger, agentops=agentops)
        self.adapters = adapters or GovernedAdapterRegistry(self.registry, self.governance)
        self._handlers: dict[str, ToolHandler] = {
            "registry.get_agent": self._registry_get_agent,
            "registry.list_agents": self._registry_list_agents,
            "task.intake": self._task_intake,
            "task.get": self._task_get,
            "task.list": self._task_list,
            "task.decompose": self._task_decompose,
            "task.transition": self._task_transition,
            "task.check_in": self._task_check_in,
            "task.complete": self._task_complete,
            "task.reassign": self._task_reassign,
            "task.remediate_stall": self._task_remediate_stall,
            "task.verify": self._task_verify,
            "delegation.create": self._delegation_create,
            "approval.request": self._approval_request,
            "approval.get": self._approval_get,
            "approval.record_decision": self._human_only,
            "conflict.open": self._conflict_open,
            "conflict.decide": self._conflict_decide,
            "governance.record_decision": self._governance_record_decision,
            "governance.record_event": self._governance_record_event,
            "governance.verify_audit_chain": self._governance_verify_audit_chain,
            "agentops.record_event": self._agentops_record_event,
            "agentops.score": self._agentops_score,
            "agentops.recommend": self._agentops_recommend,
            "answer_desk.resolve": self._answer_desk_resolve,
            "skills.invoke_governed": self._skill_invoke,
            "metrics.snapshot": self._metrics_snapshot,
            "reliability.replay": self._reliability_replay,
            "reliability.human_override": self._human_only,
        }
        contract_tools = {str(tool["name"]) for tool in self.policy.contract["tools"]}
        if set(self._handlers) != contract_tools:
            missing = sorted(contract_tools - set(self._handlers))
            extra = sorted(set(self._handlers) - contract_tools)
            raise ValueError(f"MCP runtime/contract handler drift: missing={missing}, extra={extra}")

    def tool_names(self) -> set[str]:
        return set(self._handlers)

    def call_agent(self, agent_id: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        if tool_name in HUMAN_ONLY_TOOLS:
            raise PermissionError(f"{tool_name} requires an authenticated human principal")
        self.policy.authorize(agent_id, tool_name)
        handler = self._handlers.get(tool_name)
        if handler is None:
            raise PermissionError(f"Unknown MCP tool: {tool_name}")
        return handler(agent_id, dict(arguments))

    def call_human(self, principal_id: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        if not principal_id.strip():
            raise PermissionError("Authenticated human principal is required")
        self.policy.authorize_human(tool_name)
        if tool_name == "approval.record_decision":
            args = dict(arguments)
            return self.approvals.decide(
                str(args["approval_id"]),
                actor=principal_id,
                approved=bool(args["approved"]),
                reason=str(args["reason"]),
            ).to_dict()
        if tool_name == "reliability.human_override":
            args = dict(arguments)
            return self.replay.override(
                str(args["effect_id"]),
                actor=principal_id,
                disposition=str(args["disposition"]),
                reason=str(args["reason"]),
            )
        raise PermissionError(f"Human principal is not authorized for MCP tool: {tool_name}")

    def _agent_record(self, agent_id: str) -> dict[str, Any]:
        record = self.registry.get(agent_id)
        if record is None:
            raise PermissionError(f"Unknown agent principal: {agent_id}")
        if record.get("runtime_health") in {"QUARANTINED", "RETIRED"}:
            raise PermissionError(f"Agent is not routable: {agent_id}")
        return record

    def _require_task_write_access(self, agent_id: str, task_id: str) -> TaskRecord:
        task = self.ledger.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        if agent_id != "cos" and task.accountable_agent != agent_id:
            raise PermissionError("Task write requires the accountable owner or Chief of Staff")
        return task

    def _registry_get_agent(self, _: str, args: dict[str, Any]) -> dict[str, Any]:
        target = str(args["agent_id"])
        record = self.registry.get(target)
        if record is None:
            raise KeyError(target)
        return dict(record)

    def _registry_list_agents(self, _: str, __: dict[str, Any]) -> list[dict[str, Any]]:
        return [dict(record) for record in self.registry.values()]

    def _task_intake(self, _: str, args: dict[str, Any]) -> dict[str, Any]:
        args = dict(args)
        args["authority_level"] = AuthorityLevel(int(args.get("authority_level", 0)))
        return self.cos.intake(**args).to_dict()

    def _task_get(self, _: str, args: dict[str, Any]) -> dict[str, Any] | None:
        task = self.ledger.get_task(str(args["task_id"]))
        return task.to_dict() if task else None

    def _task_list(self, _: str, __: dict[str, Any]) -> list[dict[str, Any]]:
        return [task.to_dict() for task in self.ledger.list_tasks()]

    def _task_decompose(self, _: str, args: dict[str, Any]) -> list[dict[str, Any]]:
        children = self.cos.decompose(str(args["parent_task_id"]), list(args["work_packages"]))
        return [child.to_dict() for child in children]

    def _task_transition(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        task_id = str(args["task_id"])
        self._require_task_write_access(agent_id, task_id)
        return self.cos.advance(task_id, TaskStatus(str(args["target"]))).to_dict()

    def _task_check_in(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        task_id = str(args["task_id"])
        self._require_task_write_access(agent_id, task_id)
        return self.cos.record_checkin(
            task_id,
            agent_id=agent_id,
            note=str(args["note"]),
            evidence=list(args.get("evidence", [])),
        )

    def _task_complete(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        task_id = str(args["task_id"])
        self._require_task_write_access(agent_id, task_id)
        return self.cos.complete(
            task_id,
            outcome=str(args["outcome"]),
            evidence=list(args.get("evidence", [])),
        ).to_dict()

    def _task_reassign(self, _: str, args: dict[str, Any]) -> dict[str, Any]:
        return self.cos.reassign(
            str(args["task_id"]),
            str(args["expected_owner"]),
            str(args["new_owner"]),
            reason=str(args["reason"]),
        ).to_dict()

    def _task_remediate_stall(self, _: str, args: dict[str, Any]) -> dict[str, Any]:
        return self.cos.remediate_stalled(
            str(args["task_id"]),
            new_owner=args.get("new_owner"),
            reason=str(args.get("reason", "stalled")),
        ).to_dict()

    def _task_verify(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        task_id = str(args["task_id"])
        self._require_task_write_access(agent_id, task_id)
        return self.cos.record_verification_result(
            task_id,
            passed=bool(args["passed"]),
            reason=str(args["reason"]),
            verifier_id=agent_id,
            evidence_references=list(args.get("evidence_references", [])),
        ).to_dict()

    def _delegation_create(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        delegation_payload = dict(args["delegation"])
        delegation_payload["delegating_agent"] = agent_id
        delegation_payload["authority_level"] = AuthorityLevel(int(delegation_payload["authority_level"]))
        delegation = Delegation(**delegation_payload)
        target = self.registry.get(delegation.accountable_agent)
        if target is None or target.get("parent_agent_id") != agent_id:
            raise PermissionError("Delegation target must be a registered direct child of the delegating agent")
        return self.workforce.delegate(
            delegation,
            parent_authority=int(args["parent_authority"]),
            depth=int(args["depth"]),
            active_owner=args.get("active_owner"),
            ancestry=list(args.get("ancestry", [])),
            parent_approval_gates=list(args.get("parent_approval_gates", [])),
        )

    def _approval_request(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        return self.approvals.request(
            str(args["task_id"]),
            agent_id,
            str(args["approval_owner"]),
            AuthorityLevel(int(args["authority_level"])),
            str(args["action"]),
        ).to_dict()

    def _approval_get(self, _: str, args: dict[str, Any]) -> dict[str, Any] | None:
        return self.ledger.get_record("approval", str(args["approval_id"]))

    def _human_only(self, _: str, __: dict[str, Any]) -> Any:
        raise PermissionError("Tool requires an authenticated human principal")

    def _conflict_open(self, _: str, args: dict[str, Any]) -> dict[str, Any]:
        payload = dict(args)
        task_id = str(payload.pop("task_id"))
        summary = str(payload.pop("summary"))
        disputed_points = list(payload.pop("disputed_points"))
        return self.conflicts.open(task_id, summary, disputed_points, **payload)

    def _conflict_decide(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        payload = dict(args)
        conflict_id = str(payload.pop("conflict_id"))
        payload.pop("owner", None)
        return self.conflicts.decide(conflict_id, owner=agent_id, **payload)

    def _governance_record_decision(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        record = self._agent_record(agent_id)
        payload = dict(args)
        payload["agent_id"] = agent_id
        payload["agent_role"] = record["display_name"]
        payload["skill_agent_version"] = str(record["version"])
        return self.governance.record_decision(**payload)

    def _governance_record_event(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        record = self._agent_record(agent_id)
        payload = dict(args)
        payload["actor_type"] = "AGENT"
        payload["actor_id"] = agent_id
        payload["actor_role"] = record["display_name"]
        payload["skill_agent_version"] = str(record["version"])
        return self.governance.record_event(**payload)

    def _governance_verify_audit_chain(self, _: str, __: dict[str, Any]) -> dict[str, Any]:
        records = self.ledger.list_records("audit_event_v2")
        return {"valid": verify_audit_chain(records), "event_count": len(records)}

    def _agentops_record_event(self, _: str, args: dict[str, Any]) -> dict[str, Any]:
        self.agentops.record(
            str(args["agent_id"]),
            str(args["task_id"]),
            str(args["category"]),
            float(args["value"]),
            str(args.get("severity", "LOW")),
            str(args.get("reason", "")),
        )
        return {"recorded": True}

    def _agentops_score(self, _: str, args: dict[str, Any]) -> dict[str, Any]:
        return self.agentops.scorecard(str(args["agent_id"]))

    def _agentops_recommend(self, _: str, args: dict[str, Any]) -> dict[str, Any]:
        payload = dict(args)
        agent_id = str(payload.pop("agent_id"))
        recommendation = self.agentops.recommend_for_signals(agent_id, **payload)
        return {"agent_id": agent_id, "recommendation": recommendation}

    def _answer_desk_resolve(self, _: str, args: dict[str, Any]) -> dict[str, Any]:
        result = self.answer_desk.handle(**args)
        return {"disposition": result.disposition, "reason": result.reason, "routed_to": result.routed_to}

    def _skill_invoke(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        return self.adapters.execute(agent_id, str(args["capability"]), dict(args.get("payload", {})))

    def _metrics_snapshot(self, _: str, __: dict[str, Any]) -> dict[str, Any]:
        return self.metrics.summary()

    def _reliability_replay(self, _: str, args: dict[str, Any]) -> Any:
        effect_id = str(args["effect_id"])
        failure = self.ledger.get_record("execution_failure", effect_id)
        if failure is None:
            raise KeyError(effect_id)
        replay_key = failure.get("replay_key")
        if not isinstance(replay_key, str) or not replay_key:
            raise PermissionError("Failed effect does not name a server-registered replay executor")
        executor = self.replay_executors.resolve(replay_key)
        payload = dict(failure.get("payload", {}))
        return self.replay.replay(effect_id, lambda: executor(payload), actor="cos")

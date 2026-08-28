from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from .adapters import GovernedAdapterRegistry
from .agentops import AgentOpsEvaluator
from .answer_desk import AnswerDeskService
from .approval import ApprovalService
from .conflict import ConflictService
from .governance import GovernanceJournal, verify_audit_chain
from .ledger import TaskLedger
from .mcp_policy import WorkspaceAgentMCPPolicy
from .mcp_validation import validate_tool_arguments
from .metrics import MetricsService
from .models import AuthorityLevel, Delegation, TaskRecord, TaskStatus, new_id, utcnow
from .orchestration import ChiefOfStaffService
from .registry import load_registry
from .reliability import ReplayManager
from .workforce import ChiefOfStaffWorkforceManager

ROOT = Path(__file__).resolve().parents[2]
HUMAN_ONLY_TOOLS = {"approval.record_decision", "reliability.human_override"}
OWNER_LIFECYCLE_TOOLS = {"task.get", "task.transition", "task.check_in", "task.complete"}
OWNER_EXECUTION_PROTOCOL = "mesh.cos.owner-execution.v2"
OWNER_EXECUTABLE_TOOLS = {
    "registry.get_agent",
    "task.get",
    "task.transition",
    "task.check_in",
    "task.complete",
    "task.decompose",
    "delegation.create",
    "delegation.execute_owner",
    "approval.request",
    "approval.get",
    "conflict.open",
    "governance.record_decision",
    "governance.record_event",
    "skills.invoke_governed",
}
OWNER_NESTED_DELEGATION_TOOLS = {
    "task.decompose",
    "delegation.create",
    "delegation.execute_owner",
}
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

    The external transport is immutably bound to one authenticated principal. Cross-agent
    execution is permitted only through the server-owned delegation executor, which derives
    the acting owner from canonical TaskLedger and Agent Registry state. Caller payloads can
    select an operation, but can never select or spoof the execution principal.
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
            "delegation.execute_owner": self._delegation_execute_owner,
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

    def _active_owner_record(self, agent_id: str) -> dict[str, Any]:
        record = self._agent_record(agent_id)
        if record.get("status") != "ACTIVE" or record.get("runtime_health") != "ACTIVE":
            raise RuntimeError(f"OWNER_RUNTIME_UNAVAILABLE: {agent_id}")
        allowed = set(self.policy.allowed_tools(agent_id))
        missing = sorted(OWNER_LIFECYCLE_TOOLS - allowed)
        if missing:
            raise RuntimeError(
                f"OWNER_EXECUTION_TRANSPORT_UNAVAILABLE: {agent_id}: missing={','.join(missing)}"
            )
        return record

    def _validate_owner_candidate(
        self,
        owner_id: str,
        *,
        parent_agent_id: str | None = None,
        allow_self: bool = True,
    ) -> dict[str, Any]:
        record = self._active_owner_record(owner_id)
        if (
            parent_agent_id is not None
            and owner_id != parent_agent_id
            and record.get("parent_agent_id") != parent_agent_id
        ):
            raise PermissionError(
                "Decomposed work must remain with the current owner or a registered direct child"
            )
        if not allow_self and parent_agent_id is not None and owner_id == parent_agent_id:
            raise PermissionError("Self assignment is not permitted for this ownership mutation")
        return record

    def _approval_records_for_task(self, task_id: str) -> list[dict[str, Any]]:
        return [
            dict(record)
            for record in self.ledger.list_records("approval")
            if str(record.get("task_id") or "") == task_id
        ]

    def _validate_approval_reference(
        self,
        approval_reference: str,
        *,
        task_id: str,
        minimum_authority: int,
        required_action: str | None = None,
        human_approver: str | None = None,
    ) -> dict[str, Any]:
        approval = self.ledger.get_record("approval", approval_reference)
        if approval is None:
            raise PermissionError("Canonical approval record was not found")
        if str(approval.get("task_id") or "") != task_id:
            raise PermissionError("Approval does not belong to the canonical task")
        if str(approval.get("status") or "") != "APPROVED":
            raise PermissionError("Canonical approval is not approved")
        authority = int(approval.get("authority_level", -1))
        if authority < minimum_authority:
            raise PermissionError("Approval authority is below the requested authority")
        approval_owner = str(approval.get("approval_owner") or "").strip()
        decided_by = str(approval.get("decided_by") or "").strip()
        if not approval_owner or not decided_by or decided_by != approval_owner:
            raise PermissionError("Approval decision actor does not match the canonical approval owner")
        if required_action is not None and str(approval.get("action") or "") != required_action:
            raise PermissionError("Approval action does not match the requested action")
        if human_approver is not None and human_approver.strip() and human_approver.strip() != decided_by:
            raise PermissionError("Caller-supplied human approver does not match canonical approval evidence")
        if minimum_authority >= 5 and decided_by.lower() != "michael":
            raise PermissionError("L5 authority requires Michael as the canonical approval actor")
        return dict(approval)

    def _find_approved_task_authority(
        self,
        task: TaskRecord,
        *,
        minimum_authority: int,
        approval_references: list[str] | None = None,
    ) -> dict[str, Any]:
        refs = [str(item).strip() for item in (approval_references or []) if str(item).strip()]
        if refs:
            last_error: PermissionError | None = None
            for approval_reference in refs:
                try:
                    return self._validate_approval_reference(
                        approval_reference,
                        task_id=task.task_id,
                        minimum_authority=minimum_authority,
                    )
                except PermissionError as exc:
                    last_error = exc
            raise cast(PermissionError, last_error)
        for approval in reversed(self._approval_records_for_task(task.task_id)):
            try:
                return self._validate_approval_reference(
                    str(approval["approval_id"]),
                    task_id=task.task_id,
                    minimum_authority=minimum_authority,
                )
            except PermissionError:
                continue
        raise PermissionError("No canonical approved authority exists for the task")

    def _authorize_governance_authority(
        self,
        agent_id: str,
        payload: dict[str, Any],
        *,
        decision: bool,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        record = self._agent_record(agent_id)
        authority_level = int(payload.get("authority_level", 0))
        if not 0 <= authority_level <= 5:
            raise ValueError("authority_level must be between L0 and L5")

        approval: dict[str, Any] | None = None
        if authority_level >= 4:
            approval_reference = str(payload.get("approval_reference") or "").strip()
            if decision and payload.get("human_approval_required") is not True:
                raise PermissionError("L4/L5 decisions require explicit human approval")
            if not approval_reference:
                raise PermissionError("L4/L5 authority requires a canonical approval reference")
            if (
                authority_level == 5
                and decision
                and str(payload.get("decision_owner") or "").strip().lower() != "michael"
            ):
                raise PermissionError("L5 authority requires Michael as decision owner")
            task_id = str(payload.get("task_id") or "").strip()
            if not task_id:
                raise PermissionError("L4/L5 authority requires a canonical task")
            required_action = str(
                payload.get("decision_type") if decision else payload.get("action")
            ).strip()
            approval = self._validate_approval_reference(
                approval_reference,
                task_id=task_id,
                minimum_authority=authority_level,
                required_action=required_action,
                human_approver=str(payload.get("human_approver") or ""),
            )
            return record, approval

        ceiling = int(record["decision_authority"])
        if authority_level > ceiling:
            raise PermissionError(
                f"Requested authority L{authority_level} exceeds agent authority L{ceiling}"
            )
        return record, approval

    def _require_task_owner_access(self, agent_id: str, task_id: str) -> TaskRecord:
        task = self.ledger.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        if task.accountable_agent != agent_id:
            raise PermissionError("Task write requires the canonical accountable owner")
        return task

    def _require_task_write_access(self, agent_id: str, task_id: str) -> TaskRecord:
        task = self.ledger.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        if agent_id != "cos" and task.accountable_agent != agent_id:
            raise PermissionError("Task write requires the accountable owner or Chief of Staff")
        return task

    def _agent_lineage(self, agent_id: str) -> list[str]:
        lineage: list[str] = []
        current: str | None = agent_id
        while current is not None:
            lineage.append(current)
            current = self.registry[current].get("parent_agent_id")
        return list(reversed(lineage))

    def _parent_approval_gates(self, parent_task_id: str) -> list[str]:
        inherited: list[str] = []
        for record in self.ledger.list_records("delegation"):
            if record.get("task_id") == parent_task_id:
                inherited = list(record.get("approval_gates", []))
        return inherited

    @staticmethod
    def _routing_failure_classification(exc: Exception) -> str:
        message = str(exc)
        for classification in (
            "OWNER_RUNTIME_UNAVAILABLE",
            "OWNER_EXECUTION_TRANSPORT_UNAVAILABLE",
        ):
            if classification in message:
                return classification
        if isinstance(exc, PermissionError) and "not routable" in message:
            return "OWNER_DISABLED_OR_QUARANTINED"
        return type(exc).__name__

    def _record_owner_routing_failure(
        self,
        *,
        task: TaskRecord,
        delegation_id: str,
        parent_task_id: str | None,
        orchestrating_agent: str,
        accountable_owner: str,
        attempted_operation: str,
        exc: Exception,
    ) -> dict[str, Any]:
        classification = self._routing_failure_classification(exc)
        retry_eligible = classification in {
            "OWNER_RUNTIME_UNAVAILABLE",
            "OWNER_EXECUTION_TRANSPORT_UNAVAILABLE",
        }
        record: dict[str, Any] = {
            "version": "mesh.cos.owner-routing-failure.v1",
            "record_id": new_id("owner-routing-failure"),
            "canonical_task": task.task_id,
            "parent_task": parent_task_id,
            "delegation": delegation_id,
            "orchestrator": orchestrating_agent,
            "accountable_owner": accountable_owner,
            "executing_principal": None,
            "expected_execution_principal": accountable_owner,
            "task_state": task.status.value,
            "attempted_operation": attempted_operation,
            "authorization_result": "DENY",
            "failure_classification": classification,
            "retry_eligibility": retry_eligible,
            "remediation_path": (
                "restore validated owner runtime/transport and resume existing canonical state"
                if retry_eligible
                else "apply governed owner remediation or reassignment; do not impersonate another agent"
            ),
            "timestamp": utcnow(),
        }
        self.ledger.save_record("owner_routing_failure", record["record_id"], record)
        return record

    def _ensure_owner_route(self, delegation: dict[str, Any]) -> dict[str, Any]:
        owner_id = str(delegation["accountable_agent"])
        self._active_owner_record(owner_id)
        route_id = str(delegation["delegation_id"])
        existing = self.ledger.get_record("owner_execution_route", route_id)
        if existing is not None:
            if existing.get("task_id") != delegation.get("task_id") or existing.get("accountable_owner") != owner_id:
                raise PermissionError("Owner execution route does not match canonical delegation")
            return existing
        route = {
            "version": "mesh.cos.owner-execution-route.v2",
            "protocol_version": OWNER_EXECUTION_PROTOCOL,
            "delegation_id": route_id,
            "task_id": str(delegation["task_id"]),
            "orchestrating_agent": str(delegation["delegating_agent"]),
            "accountable_owner": owner_id,
            "expected_execution_principal": owner_id,
            "status": "OWNER_ROUTABLE",
            "approval_gates": list(delegation.get("approval_gates", [])),
            "permitted_actions": list(delegation.get("permitted_actions", [])),
            "permitted_capabilities": list(delegation.get("permitted_capabilities", [])),
            "created_at": utcnow(),
        }
        self.ledger.save_record("owner_execution_route", route_id, route)
        return route

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
        self._validate_owner_candidate(str(args["accountable_agent"]))
        args["authority_level"] = AuthorityLevel(int(args.get("authority_level", 0)))
        return self.cos.intake(**args).to_dict()

    def _task_get(self, _: str, args: dict[str, Any]) -> dict[str, Any] | None:
        task = self.ledger.get_task(str(args["task_id"]))
        return task.to_dict() if task else None

    def _task_list(self, _: str, __: dict[str, Any]) -> list[dict[str, Any]]:
        return [task.to_dict() for task in self.ledger.list_tasks()]

    def _task_decompose(self, agent_id: str, args: dict[str, Any]) -> list[dict[str, Any]]:
        parent_task_id = str(args["parent_task_id"])
        self._require_task_owner_access(agent_id, parent_task_id)
        work_packages = list(args["work_packages"])
        for package in work_packages:
            self._validate_owner_candidate(
                str(package["accountable_agent"]),
                parent_agent_id=agent_id,
            )
        children = self.cos.decompose(
            parent_task_id,
            work_packages,
            actor_id=agent_id,
        )
        return [child.to_dict() for child in children]

    def _task_transition(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        task_id = str(args["task_id"])
        self._require_task_owner_access(agent_id, task_id)
        return self.cos.advance(
            task_id,
            TaskStatus(str(args["target"])),
            actor_id=agent_id,
        ).to_dict()

    def _task_check_in(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        task_id = str(args["task_id"])
        self._require_task_owner_access(agent_id, task_id)
        return self.cos.record_checkin(
            task_id,
            agent_id=agent_id,
            note=str(args["note"]),
            evidence=list(args.get("evidence", [])),
        )

    def _task_complete(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        task_id = str(args["task_id"])
        task = self._require_task_owner_access(agent_id, task_id)
        if int(task.authority_level) >= 4 or task.approval_status != "NOT_REQUIRED":
            self._find_approved_task_authority(
                task,
                minimum_authority=max(4, int(task.authority_level)),
            )
        return self.cos.complete(
            task_id,
            outcome=str(args["outcome"]),
            evidence=list(args.get("evidence", [])),
            actor_id=agent_id,
        ).to_dict()

    def _task_reassign(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        new_owner = str(args["new_owner"])
        self._validate_owner_candidate(new_owner)
        return self.cos.reassign(
            str(args["task_id"]),
            str(args["expected_owner"]),
            new_owner,
            reason=str(args["reason"]),
            actor_id=agent_id,
        ).to_dict()

    def _task_remediate_stall(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        new_owner = args.get("new_owner")
        if new_owner:
            self._validate_owner_candidate(str(new_owner))
        return self.cos.remediate_stalled(
            str(args["task_id"]),
            new_owner=new_owner,
            reason=str(args.get("reason", "stalled")),
            actor_id=agent_id,
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
        delegator = self._agent_record(agent_id)
        if int(delegator.get("max_delegation_depth", 0)) <= 0:
            raise PermissionError(f"Delegation is not permitted for {agent_id}")

        delegation_payload = dict(args["delegation"])
        delegation_payload["delegating_agent"] = agent_id
        delegation_payload["authority_level"] = AuthorityLevel(int(delegation_payload["authority_level"]))
        delegation = Delegation(**delegation_payload)
        target = self.registry.get(delegation.accountable_agent)
        if target is None or target.get("parent_agent_id") != agent_id:
            raise PermissionError("Delegation target must be a registered direct child of the delegating agent")

        child_task = self.ledger.get_task(delegation.task_id)
        if child_task is None:
            raise KeyError(delegation.task_id)
        if child_task.accountable_agent != delegation.accountable_agent:
            raise PermissionError("Delegation owner must match the canonical child task owner")
        if child_task.parent_task_id is None:
            raise ValueError("Delegated child task requires a canonical parent task")
        parent_task = self.ledger.get_task(child_task.parent_task_id)
        if parent_task is None:
            raise KeyError(child_task.parent_task_id)
        if parent_task.accountable_agent != agent_id:
            raise PermissionError("Delegating agent must own the canonical parent task")
        if delegation.parent_task_id not in {None, child_task.parent_task_id}:
            raise PermissionError("Delegation parent task does not match canonical work graph")
        delegation.parent_task_id = child_task.parent_task_id
        if int(delegation.authority_level) != int(child_task.authority_level):
            raise PermissionError("Delegation authority must match canonical child task authority")

        parent_lineage = self._agent_lineage(agent_id)
        target_lineage = self._agent_lineage(delegation.accountable_agent)
        canonical_depth = len(target_lineage) - 1
        max_canonical_depth = len(parent_lineage) - 1 + int(delegator["max_delegation_depth"])
        if canonical_depth > max_canonical_depth:
            raise PermissionError("Canonical delegation depth exceeds delegating agent authority")
        if "depth" in args and int(args["depth"]) != canonical_depth:
            raise PermissionError("Caller-supplied delegation depth does not match canonical registry")
        if "parent_authority" in args and int(args["parent_authority"]) != int(parent_task.authority_level):
            raise PermissionError("Caller-supplied parent authority does not match canonical parent task")
        if args.get("ancestry") and list(args["ancestry"]) != parent_lineage:
            raise PermissionError("Caller-supplied ancestry does not match canonical registry")
        if args.get("active_owner") not in {None, delegation.accountable_agent}:
            raise PermissionError("Caller-supplied active owner does not match canonical owner")

        requested_permitted = set(delegation.permitted_actions)
        canonical_permitted = set(target.get("permitted_actions", []))
        if requested_permitted and not requested_permitted.issubset(canonical_permitted):
            raise PermissionError("Delegation cannot grant actions outside owner authority")
        delegation.permitted_actions = sorted(requested_permitted or canonical_permitted)

        requested_capabilities = set(delegation.permitted_capabilities)
        canonical_capabilities = set(target.get("skills", []))
        if requested_capabilities and not requested_capabilities.issubset(canonical_capabilities):
            raise PermissionError("Delegation cannot grant capabilities outside owner authority")
        delegation.permitted_capabilities = sorted(requested_capabilities)

        delegation.prohibited_actions = sorted(
            set(delegation.prohibited_actions) | set(target.get("prohibited_actions", []))
        )
        inherited_gates = self._parent_approval_gates(parent_task.task_id)
        delegation.approval_gates = sorted(
            set(delegation.approval_gates)
            | set(inherited_gates)
            | set(target.get("required_approvals", []))
        )

        existing = self.ledger.get_record("delegation", delegation.delegation_id)
        if existing is not None:
            if (
                existing.get("task_id") != delegation.task_id
                or existing.get("delegating_agent") != agent_id
                or existing.get("accountable_agent") != delegation.accountable_agent
            ):
                raise ValueError("Delegation ID is already bound to different canonical work")
            self._ensure_owner_route(existing)
            return existing

        try:
            self._active_owner_record(delegation.accountable_agent)
        except Exception as exc:
            self._record_owner_routing_failure(
                task=child_task,
                delegation_id=delegation.delegation_id,
                parent_task_id=parent_task.task_id,
                orchestrating_agent=agent_id,
                accountable_owner=delegation.accountable_agent,
                attempted_operation="delegation.create",
                exc=exc,
            )
            raise

        created = self.workforce.delegate(
            delegation,
            parent_authority=int(parent_task.authority_level),
            depth=canonical_depth,
            max_depth=max_canonical_depth,
            active_owner=delegation.accountable_agent,
            ancestry=parent_lineage,
            parent_approval_gates=inherited_gates,
        )
        self._ensure_owner_route(created)
        return created

    @staticmethod
    def _delegation_allows_nested_work(delegation: dict[str, Any]) -> bool:
        return any(
            str(action).startswith("delegate_")
            for action in delegation.get("permitted_actions", [])
        )

    def _owner_scoped_arguments(
        self,
        task: TaskRecord,
        owner_id: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        payload = dict(arguments)
        if tool_name == "delegation.execute_owner":
            payload.setdefault("protocol_version", OWNER_EXECUTION_PROTOCOL)
            nested_id = str(payload.get("delegation_id") or "")
            nested = self.ledger.get_record("delegation", nested_id)
            if nested is None:
                raise KeyError(nested_id)
            if nested.get("delegating_agent") != owner_id:
                raise PermissionError("Nested owner execution requires the current owner to be the canonical delegator")
            if nested.get("parent_task_id") != task.task_id:
                raise PermissionError("Nested delegation must descend from the current delegated task")
            if str(payload.get("task_id")) != str(nested.get("task_id")):
                raise PermissionError("Nested owner execution task must match the canonical child delegation")
        elif "task_id" in payload and str(payload["task_id"]) != task.task_id:
            raise PermissionError("Owner execution cannot cross canonical task boundaries")

        if tool_name == "task.decompose" and str(payload.get("parent_task_id")) != task.task_id:
            raise PermissionError("Owner decomposition must remain within the delegated task")
        if tool_name == "approval.get":
            approval = self.ledger.get_record("approval", str(payload.get("approval_id") or ""))
            if approval is None:
                raise KeyError(str(payload.get("approval_id") or ""))
            if str(approval.get("task_id") or "") != task.task_id:
                raise PermissionError("Delegated owner cannot read approval state for another task")
        if tool_name == "registry.get_agent":
            target = str(payload.get("agent_id") or "")
            record = self.registry.get(target)
            if record is None:
                raise KeyError(target)
            if target != owner_id and record.get("parent_agent_id") != owner_id:
                raise PermissionError("Delegated owner registry reads are limited to self or direct children")
        if tool_name == "skills.invoke_governed":
            skill_payload = dict(payload.get("payload", {}))
            if "task_id" in skill_payload and str(skill_payload["task_id"]) != task.task_id:
                raise PermissionError("Governed Skill invocation cannot cross canonical task boundaries")
            skill_payload["task_id"] = task.task_id
            skill_payload["correlation_id"] = task.correlation_id
            skill_payload["authority_level"] = int(task.authority_level)
            skill_payload["execution_mode"] = "LOGICAL_SKILL_AGENT"
            payload["payload"] = skill_payload
        return validate_tool_arguments(tool_name, payload)

    def _delegation_execute_owner(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        protocol_version = str(args.get("protocol_version") or OWNER_EXECUTION_PROTOCOL)
        if protocol_version != OWNER_EXECUTION_PROTOCOL:
            raise PermissionError("Unsupported owner-execution protocol version")
        delegation_id = str(args["delegation_id"])
        delegation = self.ledger.get_record("delegation", delegation_id)
        if delegation is None:
            raise KeyError(delegation_id)
        if delegation.get("delegating_agent") != agent_id:
            raise PermissionError("Only the canonical delegating agent may invoke the owner execution route")
        task_id = str(args["task_id"])
        if task_id != str(delegation.get("task_id")):
            raise PermissionError("Owner execution task does not match canonical delegation")
        task = self.ledger.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        owner_id = str(delegation["accountable_agent"])
        if task.accountable_agent != owner_id:
            raise PermissionError("Canonical task owner no longer matches delegation owner")

        tool_name = str(args["tool_name"])
        if tool_name in HUMAN_ONLY_TOOLS or tool_name == "task.verify":
            raise PermissionError("Owner execution cannot invoke human-only or verifier MCP tools")
        if tool_name not in OWNER_EXECUTABLE_TOOLS:
            raise PermissionError("Tool is not available through delegated owner execution")
        if tool_name in OWNER_NESTED_DELEGATION_TOOLS and not self._delegation_allows_nested_work(delegation):
            raise PermissionError("Delegation does not authorize nested delegation work")

        try:
            owner_record = self._active_owner_record(owner_id)
            self._ensure_owner_route(delegation)
        except Exception as exc:
            self._record_owner_routing_failure(
                task=task,
                delegation_id=delegation_id,
                parent_task_id=delegation.get("parent_task_id"),
                orchestrating_agent=agent_id,
                accountable_owner=owner_id,
                attempted_operation=tool_name,
                exc=exc,
            )
            route = self.ledger.get_record("owner_execution_route", delegation_id)
            if route is not None:
                route["status"] = "OWNER_ROUTING_FAILED"
                route["failure_classification"] = self._routing_failure_classification(exc)
                route["updated_at"] = utcnow()
                self.ledger.save_record("owner_execution_route", delegation_id, route)
            raise

        self.policy.authorize(owner_id, tool_name)

        raw_arguments = dict(args.get("arguments", {}))
        owner_args = self._owner_scoped_arguments(
            task,
            owner_id,
            tool_name,
            raw_arguments,
        )

        approval_references = [
            str(item).strip()
            for item in args.get("approval_references", [])
            if str(item).strip()
        ]
        approval: dict[str, Any] | None = None
        if task.approval_status in {"PENDING", "REJECTED"} and tool_name not in {
            "task.get",
            "task.check_in",
            "approval.request",
            "approval.get",
            "governance.record_event",
        }:
            raise PermissionError("Canonical task approval state blocks delegated execution")
        approval_required = tool_name == "task.complete" and (
            int(task.authority_level) >= 4 or task.approval_status != "NOT_REQUIRED"
        )
        if tool_name == "skills.invoke_governed":
            capability = str(owner_args.get("capability") or "")
            approval_required = approval_required or owner_id == "message-ops" or capability == "mesh-message-operations"
        if approval_required:
            approval = self._find_approved_task_authority(
                task,
                minimum_authority=max(4, int(task.authority_level)),
                approval_references=approval_references,
            )
        elif approval_references:
            approval = self._validate_approval_reference(
                approval_references[0],
                task_id=task.task_id,
                minimum_authority=4,
            )

        idempotency_key = str(args["idempotency_key"]).strip()
        if not idempotency_key:
            raise ValueError("Owner execution idempotency_key is required")
        request_fingerprint = hashlib.sha256(
            json.dumps(
                {
                    "protocol_version": protocol_version,
                    "delegation_id": delegation_id,
                    "task_id": task_id,
                    "tool_name": tool_name,
                    "arguments": owner_args,
                    "approval_references": approval_references,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        accepted_request_fingerprints = {request_fingerprint}
        if not approval_references:
            legacy_request_fingerprint = hashlib.sha256(
                json.dumps(
                    {
                        "delegation_id": delegation_id,
                        "task_id": task_id,
                        "tool_name": tool_name,
                        "arguments": owner_args,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            accepted_request_fingerprints.add(legacy_request_fingerprint)
        record_id = f"{delegation_id}:{idempotency_key}"
        existing = self.ledger.get_record("owner_execution", record_id)
        if existing is not None:
            if existing.get("request_fingerprint") not in accepted_request_fingerprints:
                raise PermissionError("Owner execution idempotency key cannot be reused for another request")
            if existing.get("status") == "OWNER_RESULT_RECORDED":
                return dict(existing["response"])
            raise RuntimeError(f"OWNER_EXECUTION_NOT_RETRYABLE: {existing.get('status', 'UNKNOWN')}")

        execution_record: dict[str, Any] = {
            "version": "mesh.cos.owner-execution.v2",
            "protocol_version": protocol_version,
            "record_id": record_id,
            "delegation_id": delegation_id,
            "task_id": task_id,
            "orchestrating_agent": agent_id,
            "accountable_owner": owner_id,
            "expected_execution_principal": owner_id,
            "executing_principal": owner_id,
            "tool_name": tool_name,
            "authorization_result": "ALLOW",
            "request_fingerprint": request_fingerprint,
            "approval_reference": approval.get("approval_id") if approval else None,
            "status": "OWNER_EXECUTING",
            "started_at": utcnow(),
        }
        claimed = self.ledger.save_idempotent_record(
            f"owner-execution:{record_id}",
            "owner_execution",
            record_id,
            execution_record,
        )
        if not claimed:
            prior = self.ledger.get_record("owner_execution", record_id)
            if (
                prior
                and prior.get("request_fingerprint") in accepted_request_fingerprints
                and prior.get("status") == "OWNER_RESULT_RECORDED"
            ):
                return dict(prior["response"])
            raise RuntimeError("OWNER_EXECUTION_ALREADY_CLAIMED")

        try:
            if tool_name == "skills.invoke_governed":
                capability = str(owner_args.get("capability") or "")
                permitted_capabilities = set(delegation.get("permitted_capabilities", []))
                if capability not in permitted_capabilities:
                    raise PermissionError(
                        "Capability not allowed: capability is not explicitly permitted by the canonical delegation"
                    )
            result = self.call_agent(owner_id, tool_name, owner_args)
        except Exception as exc:
            execution_record["status"] = "OWNER_EXECUTION_FAILED"
            execution_record["failure_classification"] = type(exc).__name__
            execution_record["retry_eligible"] = False
            execution_record["completed_at"] = utcnow()
            self.ledger.save_record("owner_execution", record_id, execution_record)
            route = self.ledger.get_record("owner_execution_route", delegation_id) or {}
            route["status"] = "OWNER_EXECUTION_FAILED"
            route["failure_classification"] = type(exc).__name__
            route["updated_at"] = utcnow()
            self.ledger.save_record("owner_execution_route", delegation_id, route)
            raise

        response = {
            "status": "OWNER_RESULT_RECORDED",
            "protocol_version": protocol_version,
            "delegation_id": delegation_id,
            "task_id": task_id,
            "orchestrating_agent": agent_id,
            "accountable_owner": owner_id,
            "executing_principal": owner_id,
            "expected_execution_principal": owner_id,
            "tool_name": tool_name,
            "authorization_result": "ALLOW",
            "approval_reference": approval.get("approval_id") if approval else None,
            "result": result,
        }
        execution_record["status"] = "OWNER_RESULT_RECORDED"
        execution_record["response"] = response
        execution_record["completed_at"] = utcnow()
        execution_record["retry_eligible"] = True
        self.ledger.save_record("owner_execution", record_id, execution_record)
        route = self.ledger.get_record("owner_execution_route", delegation_id) or {}
        route["status"] = (
            "OWNER_COMPLETED"
            if tool_name == "task.complete" and isinstance(result, dict) and result.get("status") == "COMPLETED"
            else "OWNER_RESULT_RECORDED"
        )
        route["last_tool_name"] = tool_name
        route["last_execution_record_id"] = record_id
        route["last_approval_reference"] = approval.get("approval_id") if approval else None
        route["parent_result_available_at"] = utcnow()
        route["updated_at"] = utcnow()
        self.ledger.save_record("owner_execution_route", delegation_id, route)
        self.governance.record_event(
            event_type="delegation.owner_execution",
            event_category="EXECUTION",
            action=tool_name,
            actor_type="AGENT",
            actor_id=owner_id,
            actor_role=str(owner_record["display_name"]),
            skill_agent_version=str(owner_record["version"]),
            task_id=task_id,
            correlation_id=task.correlation_id,
            authority_level=int(task.authority_level),
            policy_rule_ids=[
                "canonical-owner-derived-server-side",
                "delegation-bound-execution",
                "delegation-capability-scope",
                "canonical-approval-when-required",
            ],
            capability_tool="delegation.execute_owner",
            target_resource=task_id,
            source_system="Mesh server-owned owner executor",
            input_summary=f"Owner execution orchestrated by {agent_id}; principal and authority derived from canonical state.",
            result_status="SUCCESS",
            output_summary=f"{owner_id} executed {tool_name} under bounded delegated authority.",
            evidence_references=list(task.outcome_evidence),
            approval_reference=approval.get("approval_id") if approval else None,
            human_approver=str(approval.get("decided_by") or "") if approval else None,
            risk_severity="MEDIUM",
            data_classification="INTERNAL",
            error_code=None,
            error_summary=None,
            model_provider=None,
            model_id_version=None,
            environment="RUNTIME",
            retention_class="GOVERNANCE_LONG_TERM",
            idempotency_key=f"owner-execution-audit:{record_id}",
        )
        return response

    def _approval_request(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        task_id = str(args["task_id"])
        self._require_task_write_access(agent_id, task_id)
        authority = AuthorityLevel(int(args["authority_level"]))
        approval_owner = str(args["approval_owner"]).strip()
        if approval_owner in self.registry:
            raise PermissionError("Approval owner must be a qualified human principal, not an agent")
        if authority == AuthorityLevel.L5 and approval_owner.lower() != "michael":
            raise PermissionError("L5 approval requests must be owned by Michael")
        return self.approvals.request(
            task_id,
            agent_id,
            approval_owner,
            authority,
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
        authority_level = int(payload.get("authority_level", 3))
        if authority_level >= 4:
            conflict = self.ledger.get_record("conflict", conflict_id)
            if conflict is None:
                raise KeyError(conflict_id)
            approval = self._validate_approval_reference(
                str(payload.get("approval_reference") or ""),
                task_id=str(conflict["task_id"]),
                minimum_authority=authority_level,
                required_action="CONFLICT_RESOLUTION",
                human_approver=str(payload.get("human_approver") or ""),
            )
            payload["human_approver"] = str(approval["decided_by"])
        return self.conflicts.decide(conflict_id, owner=agent_id, **payload)

    def _governance_record_decision(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        payload = dict(args)
        record, approval = self._authorize_governance_authority(agent_id, payload, decision=True)
        payload["agent_id"] = agent_id
        payload["agent_role"] = record["display_name"]
        payload["skill_agent_version"] = str(record["version"])
        if approval is not None:
            payload["human_approver"] = str(approval["decided_by"])
        return self.governance.record_decision(**payload)

    def _governance_record_event(self, agent_id: str, args: dict[str, Any]) -> dict[str, Any]:
        payload = dict(args)
        record, approval = self._authorize_governance_authority(agent_id, payload, decision=False)
        payload["actor_type"] = "AGENT"
        payload["actor_id"] = agent_id
        payload["actor_role"] = record["display_name"]
        payload["skill_agent_version"] = str(record["version"])
        if approval is not None:
            payload["human_approver"] = str(approval["decided_by"])
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

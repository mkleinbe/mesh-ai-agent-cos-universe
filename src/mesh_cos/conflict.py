from __future__ import annotations

from .audit import AuditEvent
from .ledger import TaskLedger
from .models import new_id, utcnow

DOMAIN_AUTHORITY = {
    "financial_calculation": "cfo",
    "commercial_evidence": "mesh-revenue-intelligence",
    "account_qualification": "mesh-revenue-intelligence",
    "staffing_feasibility": "coo",
    "marketing_strategy": "cmo",
}


def authoritative_owner(fact_type: str) -> str | None:
    return DOMAIN_AUTHORITY.get(fact_type)


def decision_brief(**values) -> dict:
    return {
        "decision_required": values["decision_required"],
        "why_now": values["why_now"],
        "known_facts": values["known_facts"],
        "material_disagreement": values["material_disagreement"],
        "options": values["options"],
        "cos_recommendation": values["cos_recommendation"],
        "primary_risk": values["primary_risk"],
        "what_would_reverse": values["reversal_condition"],
        "approval_action_requested": values["approval_requested"],
    }


class ConflictService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def open(
        self,
        task_id: str,
        summary: str,
        disputed_points: list[str],
        *,
        participants: list[str] | None = None,
        business_consequence: str = "material cross-functional tradeoff",
        decision_owner: str = "cos",
    ) -> dict:
        conflict_id = new_id("conflict")
        record = {
            "version": "mesh.cos.conflict.v1",
            "conflict_id": conflict_id,
            "task_id": task_id,
            "participants": list(participants or ["functional-owner-1", "functional-owner-2"]),
            "summary": summary,
            "disputed_points": list(disputed_points),
            "business_consequence": business_consequence,
            "decision_owner": decision_owner,
            "disposition": "PENDING",
            "status": "OPEN",
            "created_at": utcnow(),
            "decided_at": None,
        }
        self.ledger.save_record("conflict", conflict_id, record)
        self._audit(task_id, "conflict_opened", decision_owner, conflict_id)
        return record

    def decide(
        self,
        conflict_id: str,
        *,
        owner: str,
        disposition: str,
        reversal_condition: str,
        rationale: str = "CoS arbitration based on authoritative functional evidence",
        authority_level: int = 3,
        approval_reference: str | None = None,
    ) -> dict:
        conflict = self.ledger.get_record("conflict", conflict_id)
        if not conflict:
            raise KeyError(conflict_id)
        if owner != conflict.get("decision_owner"):
            raise PermissionError("Only the assigned decision owner may decide the conflict")
        conflict["status"] = "DECIDED"
        conflict["disposition"] = disposition
        conflict["decided_at"] = utcnow()
        self.ledger.save_record("conflict", conflict_id, conflict)
        decision_id = new_id("decision")
        decision = {
            "version": "mesh.cos.decision.v1",
            "decision_id": decision_id,
            "task_id": conflict["task_id"],
            "conflict_id": conflict_id,
            "decision_owner": owner,
            "authority_level": authority_level,
            "decision": disposition,
            "rationale": rationale,
            "disposition": disposition,
            "reversal_condition": reversal_condition,
            "approval_reference": approval_reference,
            "decided_at": utcnow(),
        }
        self.ledger.save_record("decision", decision_id, decision)
        self._audit(conflict["task_id"], "conflict_decided", owner, decision_id)
        return decision

    def _audit(self, task_id: str, event_type: str, actor: str, result: str) -> None:
        task = self.ledger.get_task(task_id)
        correlation_id = task.correlation_id if task else new_id("corr")
        authority_level = int(task.authority_level) if task else 3
        self.ledger.record_event(AuditEvent(event_type, actor, task_id, correlation_id, authority_level, result).to_dict())

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
        uncontested_facts: list[str] | None = None,
        disputed_facts: list[str] | None = None,
        source_authority: dict[str, str] | None = None,
        business_consequence: str = "material cross-functional tradeoff",
        option_a: dict | None = None,
        option_b: dict | None = None,
        other_options: list[dict] | None = None,
        agent_positions: dict[str, str] | None = None,
        confidence: str = "MEDIUM",
        reversibility: str = "REVERSIBLE",
        devils_advocate_review: str | None = None,
        cos_recommendation: str = "",
        reversal_condition: str = "",
        decision_owner: str = "cos",
    ) -> dict:
        if confidence not in {"HIGH", "MEDIUM", "LOW"}:
            raise ValueError("Invalid confidence")
        if reversibility not in {"REVERSIBLE", "PARTIALLY_REVERSIBLE", "IRREVERSIBLE"}:
            raise ValueError("Invalid reversibility")
        conflict_id = new_id("conflict")
        record = {
            "version": "mesh.cos.conflict.v1",
            "conflict_id": conflict_id,
            "task_id": task_id,
            "participants": list(participants or ["unspecified-functional-owner-1", "unspecified-functional-owner-2"]),
            "uncontested_facts": list(uncontested_facts or []),
            "disputed_facts": list(disputed_facts or []),
            "disputed_recommendations": list(disputed_points),
            "source_authority": dict(source_authority or {}),
            "business_consequence": business_consequence,
            "option_a": dict(option_a or {}),
            "option_b": dict(option_b or {}),
            "other_options": list(other_options or []),
            "agent_positions": dict(agent_positions or {}),
            "confidence": confidence,
            "reversibility": reversibility,
            "devils_advocate_review": devils_advocate_review,
            "cos_recommendation": cos_recommendation,
            "reversal_condition": reversal_condition,
            "decision_owner": decision_owner,
            "disposition": "PENDING",
            "status": "OPEN",
            "created_at": utcnow(),
            "decided_at": None,
            "summary": summary,
        }
        # Summary is retained as a convenience record but excluded from the contract view.
        self.ledger.save_record("conflict", conflict_id, record)
        self._audit(task_id, "conflict_opened", decision_owner, conflict_id)
        return record

    @staticmethod
    def contract_view(record: dict) -> dict:
        return {key: value for key, value in record.items() if key != "summary"}

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
        conflict["cos_recommendation"] = conflict.get("cos_recommendation") or disposition
        conflict["reversal_condition"] = reversal_condition
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

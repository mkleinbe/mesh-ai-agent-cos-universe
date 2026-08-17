from __future__ import annotations

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


def decision_brief(**k) -> dict:
    return {
        "decision_required": k["decision_required"], "why_now": k["why_now"],
        "known_facts": k["known_facts"], "material_disagreement": k["material_disagreement"],
        "options": k["options"], "cos_recommendation": k["cos_recommendation"],
        "primary_risk": k["primary_risk"], "what_would_reverse": k["reversal_condition"],
        "approval_action_requested": k["approval_requested"],
    }


class ConflictService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def open(self, task_id: str, summary: str, disputed_points: list[str]) -> dict:
        conflict_id = new_id("conflict")
        record = {
            "version": "mesh.cos.conflict.v1", "conflict_id": conflict_id, "task_id": task_id,
            "summary": summary, "disputed_points": disputed_points, "status": "OPEN", "created_at": utcnow(),
        }
        self.ledger.save_record("conflict", conflict_id, record)
        return record

    def decide(self, conflict_id: str, *, owner: str, disposition: str, reversal_condition: str) -> dict:
        conflict = self.ledger.get_record("conflict", conflict_id)
        if not conflict:
            raise KeyError(conflict_id)
        conflict["status"] = "DECIDED"
        conflict["decided_at"] = utcnow()
        self.ledger.save_record("conflict", conflict_id, conflict)
        decision_id = new_id("decision")
        decision = {
            "version": "mesh.cos.decision.v1", "decision_id": decision_id,
            "task_id": conflict["task_id"], "conflict_id": conflict_id, "decision_owner": owner,
            "disposition": disposition, "reversal_condition": reversal_condition, "decided_at": utcnow(),
        }
        self.ledger.save_record("decision", decision_id, decision)
        return decision

from __future__ import annotations

from .audit import AuditEvent
from .governance import GovernanceJournal
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
        self.governance = GovernanceJournal(ledger)

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
        human_approver: str | None = None,
        risk_level: str = "MEDIUM",
    ) -> dict:
        conflict = self.ledger.get_record("conflict", conflict_id)
        if not conflict:
            raise KeyError(conflict_id)
        if owner != conflict.get("decision_owner"):
            raise PermissionError("Only the assigned decision owner may decide the conflict")
        if authority_level >= 4 and not (approval_reference and human_approver):
            raise PermissionError("L4/L5 conflict decisions require explicit human approval evidence")
        conflict["status"] = "DECIDED"
        conflict["disposition"] = disposition
        conflict["cos_recommendation"] = conflict.get("cos_recommendation") or disposition
        conflict["reversal_condition"] = reversal_condition
        conflict["decided_at"] = utcnow()
        self.ledger.save_record("conflict", conflict_id, conflict)
        decision_id = new_id("decision")
        legacy_decision = {
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
        self.ledger.save_record("decision", decision_id, legacy_decision)
        task = self.ledger.get_task(conflict["task_id"])
        correlation_id = task.correlation_id if task else new_id("corr")
        option_labels = [label for label, value in (("option_a", conflict.get("option_a")), ("option_b", conflict.get("option_b"))) if value]
        option_labels.extend(f"other_option_{index + 1}" for index, _ in enumerate(conflict.get("other_options", [])))
        source_systems = sorted(set(conflict.get("source_authority", {}).values())) or ["TaskLedger"]
        self.governance.record_decision(
            decision_id=decision_id,
            decision_type="CONFLICT_RESOLUTION",
            decision_title=f"Resolve conflict {conflict_id}",
            task_id=conflict["task_id"],
            correlation_id=correlation_id,
            agent_id=owner,
            agent_role="Assigned conflict decision owner",
            decision_owner=owner,
            authority_level=authority_level,
            human_approval_required=authority_level >= 4,
            approval_reference=approval_reference,
            human_approver=human_approver,
            decision=disposition,
            disposition=disposition,
            decision_basis_summary=rationale,
            evidence_references=[f"conflict:{conflict_id}"],
            source_systems=source_systems,
            alternatives_considered=option_labels,
            selection_criteria=["authoritative functional evidence", "business consequence", "reversibility"],
            confidence=conflict.get("confidence", "MEDIUM"),
            risk_level=risk_level,
            affected_entities=list(conflict.get("participants", [])),
            reversibility=conflict.get("reversibility", "REVERSIBLE"),
            reversal_condition=reversal_condition,
            policy_rule_ids=["functional-truth-boundary", "mesh-decision-rights"],
            model_provider=None,
            model_id_version=None,
            prompt_template_version=None,
            skill_agent_version="conflict-service-v1",
            data_classification="INTERNAL",
            outcome_validation=reversal_condition,
            outcome_status="IN_PROGRESS",
            retention_class="GOVERNANCE_LONG_TERM",
        )
        self._audit(conflict["task_id"], "conflict_decided", owner, decision_id)
        return legacy_decision

    def _audit(self, task_id: str, event_type: str, actor: str, result: str) -> None:
        task = self.ledger.get_task(task_id)
        correlation_id = task.correlation_id if task else new_id("corr")
        authority_level = int(task.authority_level) if task else 3
        self.ledger.record_event(AuditEvent(event_type, actor, task_id, correlation_id, authority_level, result).to_dict())

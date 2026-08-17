from __future__ import annotations

from .ledger import TaskLedger
from .models import AuthorityLevel, ConflictRecord, DecisionRecord, new_id


class GovernanceService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def create_conflict(
        self,
        *,
        task_id: str,
        created_by: str,
        uncontested_facts: list[str],
        disputed_facts: list[str],
        source_authority: dict[str, str],
        options: list[str],
        positions: dict[str, str],
        confidence: dict[str, float],
        reversibility: str,
        decision_owner: str,
        consequences: list[str] | None = None,
        devils_advocate_review: str | None = None,
    ) -> dict:
        record = ConflictRecord(
            conflict_id=new_id("conflict"),
            task_id=task_id,
            created_by=created_by,
            uncontested_facts=uncontested_facts,
            disputed_facts=disputed_facts,
            source_authority=source_authority,
            options=options,
            positions=positions,
            confidence=confidence,
            reversibility=reversibility,
            decision_owner=decision_owner,
            consequences=consequences or [],
            devils_advocate_review=devils_advocate_review,
        )
        payload = record.to_dict()
        self.ledger.save_conflict(payload)
        return payload

    def dispose_conflict(self, conflict_id: str, *, disposition: str, cos_recommendation: str, reversal_condition: str | None = None) -> dict:
        payload = self.ledger.get_conflict(conflict_id)
        if payload is None:
            raise KeyError(conflict_id)
        payload["disposition"] = disposition
        payload["cos_recommendation"] = cos_recommendation
        payload["reversal_condition"] = reversal_condition
        self.ledger.save_conflict(payload)
        return payload

    def record_decision(
        self,
        *,
        task_id: str,
        decision_owner: str,
        decision: str,
        rationale: str,
        authority_level: AuthorityLevel,
        approval_reference: str | None = None,
        options_considered: list[str] | None = None,
        source_references: list[str] | None = None,
        reversal_condition: str | None = None,
    ) -> dict:
        if authority_level >= AuthorityLevel.L4 and not approval_reference:
            raise PermissionError("L4/L5 decision records require an approval reference")
        record = DecisionRecord(
            decision_id=new_id("decision"),
            task_id=task_id,
            decision_owner=decision_owner,
            decision=decision,
            rationale=rationale,
            authority_level=authority_level,
            approval_reference=approval_reference,
            options_considered=options_considered or [],
            source_references=source_references or [],
            reversal_condition=reversal_condition,
        )
        payload = record.to_dict()
        self.ledger.save_decision(payload)
        return payload

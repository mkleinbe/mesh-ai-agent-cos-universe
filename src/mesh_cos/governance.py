from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .ledger import TaskLedger
from .models import new_id, utcnow

GENESIS_HASH = "GENESIS"
FORBIDDEN_REASONING_FIELDS = {
    "chain_of_thought", "reasoning_trace", "hidden_reasoning", "raw_prompt",
    "raw_secret", "credential", "token",
}


def _canonical_json(payload: dict[str, Any], *, exclude: set[str] | None = None) -> str:
    excluded = exclude or set()
    clean = {key: value for key, value in payload.items() if key not in excluded}
    return json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(payload: dict[str, Any], *, exclude: set[str] | None = None) -> str:
    return hashlib.sha256(_canonical_json(payload, exclude=exclude).encode("utf-8")).hexdigest()


def _assert_safe_fields(payload: dict[str, Any]) -> None:
    forbidden = FORBIDDEN_REASONING_FIELDS.intersection(payload)
    if forbidden:
        raise ValueError(
            "Private reasoning or secret-bearing fields cannot be persisted: "
            + ", ".join(sorted(forbidden))
        )


class GovernanceMirror:
    """Optional human-readable mirror. Canonical state remains in TaskLedger."""

    def mirror_decision(self, record: dict[str, Any]) -> None:
        return None

    def mirror_event(self, record: dict[str, Any]) -> None:
        return None


@dataclass(slots=True)
class GovernanceJournal:
    ledger: TaskLedger
    mirror: GovernanceMirror | None = None

    def record_decision(
        self,
        *,
        decision_type: str,
        decision_title: str,
        task_id: str,
        correlation_id: str,
        agent_id: str,
        agent_role: str,
        decision_owner: str,
        authority_level: int,
        human_approval_required: bool,
        decision: str,
        disposition: str,
        decision_basis_summary: str,
        evidence_references: list[str],
        source_systems: list[str],
        alternatives_considered: list[str],
        selection_criteria: list[str],
        confidence: float | str,
        risk_level: str,
        affected_entities: list[str],
        reversibility: str,
        reversal_condition: str,
        policy_rule_ids: list[str],
        model_provider: str | None,
        model_id_version: str | None,
        prompt_template_version: str | None,
        skill_agent_version: str,
        data_classification: str,
        outcome_validation: str,
        outcome_status: str,
        retention_class: str,
        approval_reference: str | None = None,
        human_approver: str | None = None,
        decision_id: str | None = None,
        decision_status: str = "DECIDED",
        supersedes_decision_id: str | None = None,
        superseded_by_decision_id: str | None = None,
        review_due_at_utc: str | None = None,
        decided_at_utc: str | None = None,
    ) -> dict[str, Any]:
        if not 0 <= authority_level <= 5:
            raise ValueError("authority_level must be between L0 and L5")
        if human_approval_required and not (approval_reference and human_approver):
            raise PermissionError("Human-approval-required decisions need approval reference and approver")
        if not decision_basis_summary.strip() or not evidence_references:
            raise ValueError("Explainable decision basis and evidence references are required")
        if isinstance(confidence, str) and confidence not in {"HIGH", "MEDIUM", "LOW", "UNKNOWN"}:
            raise ValueError("Unsupported qualitative confidence")
        if isinstance(confidence, (int, float)) and not 0 <= float(confidence) <= 1:
            raise ValueError("Numeric confidence must be between 0 and 1")

        decision_id = decision_id or new_id("decision")
        record: dict[str, Any] = {
            "version": "mesh.cos.decision.v2",
            "decision_id": decision_id,
            "decided_at_utc": decided_at_utc or utcnow(),
            "decision_status": decision_status,
            "decision_type": decision_type,
            "decision_title": decision_title,
            "task_id": task_id,
            "correlation_id": correlation_id,
            "agent_id": agent_id,
            "agent_role": agent_role,
            "decision_owner": decision_owner,
            "authority_level": authority_level,
            "human_approval_required": human_approval_required,
            "approval_reference": approval_reference,
            "human_approver": human_approver,
            "decision": decision,
            "disposition": disposition,
            "decision_basis_summary": decision_basis_summary,
            "evidence_references": list(evidence_references),
            "source_systems": list(source_systems),
            "alternatives_considered": list(alternatives_considered),
            "selection_criteria": list(selection_criteria),
            "confidence": confidence,
            "risk_level": risk_level,
            "affected_entities": list(affected_entities),
            "reversibility": reversibility,
            "reversal_condition": reversal_condition,
            "policy_rule_ids": list(policy_rule_ids),
            "model_provider": model_provider,
            "model_id_version": model_id_version,
            "prompt_template_version": prompt_template_version,
            "skill_agent_version": skill_agent_version,
            "data_classification": data_classification,
            "outcome_validation": outcome_validation,
            "outcome_status": outcome_status,
            "supersedes_decision_id": supersedes_decision_id,
            "superseded_by_decision_id": superseded_by_decision_id,
            "review_due_at_utc": review_due_at_utc,
            "retention_class": retention_class,
            "canonical_record_ref": f"TaskLedger:decision_v2:{decision_id}",
            "record_hash": "",
            "recorded_at_utc": utcnow(),
        }
        _assert_safe_fields(record)
        record["record_hash"] = _sha256(record, exclude={"record_hash"})
        self.ledger.save_record("decision_v2", decision_id, record)
        self._mirror("decision", record)
        return record

    def record_event(
        self,
        *,
        event_type: str,
        event_category: str,
        action: str,
        actor_type: str,
        actor_id: str,
        actor_role: str,
        task_id: str | None,
        correlation_id: str,
        authority_level: int,
        policy_rule_ids: list[str],
        capability_tool: str,
        target_resource: str,
        source_system: str,
        input_summary: str,
        result_status: str,
        output_summary: str,
        evidence_references: list[str],
        risk_severity: str,
        data_classification: str,
        model_provider: str | None,
        model_id_version: str | None,
        skill_agent_version: str,
        environment: str,
        retention_class: str,
        decision_id: str | None = None,
        parent_event_id: str | None = None,
        run_id: str | None = None,
        approval_reference: str | None = None,
        human_approver: str | None = None,
        before_state_ref: str | None = None,
        after_state_ref: str | None = None,
        error_code: str | None = None,
        error_summary: str | None = None,
        idempotency_key: str | None = None,
        event_id: str | None = None,
        event_timestamp_utc: str | None = None,
    ) -> dict[str, Any]:
        if not 0 <= authority_level <= 5:
            raise ValueError("authority_level must be between L0 and L5")
        existing = sorted(
            self.ledger.list_records("audit_event_v2"),
            key=lambda item: item["event_sequence"],
        )
        previous_hash = existing[-1]["event_hash"] if existing else GENESIS_HASH
        event_id = event_id or new_id("event")
        record: dict[str, Any] = {
            "version": "mesh.cos.agent-event.v2",
            "event_id": event_id,
            "event_sequence": len(existing) + 1,
            "event_timestamp_utc": event_timestamp_utc or utcnow(),
            "event_type": event_type,
            "event_category": event_category,
            "action": action,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "task_id": task_id,
            "correlation_id": correlation_id,
            "decision_id": decision_id,
            "parent_event_id": parent_event_id,
            "run_id": run_id,
            "authority_level": authority_level,
            "policy_rule_ids": list(policy_rule_ids),
            "capability_tool": capability_tool,
            "target_resource": target_resource,
            "source_system": source_system,
            "input_summary": input_summary,
            "result_status": result_status,
            "output_summary": output_summary,
            "before_state_ref": before_state_ref,
            "after_state_ref": after_state_ref,
            "evidence_references": list(evidence_references),
            "approval_reference": approval_reference,
            "human_approver": human_approver,
            "risk_severity": risk_severity,
            "data_classification": data_classification,
            "error_code": error_code,
            "error_summary": error_summary,
            "idempotency_key": idempotency_key or event_id,
            "model_provider": model_provider,
            "model_id_version": model_id_version,
            "skill_agent_version": skill_agent_version,
            "environment": environment,
            "retention_class": retention_class,
            "previous_event_hash": previous_hash,
            "event_hash": "",
            "recorded_at_utc": utcnow(),
            "canonical_record_ref": f"TaskLedger:audit_event_v2:{event_id}",
        }
        _assert_safe_fields(record)
        record["event_hash"] = _sha256(record, exclude={"event_hash"})
        governance_key = f"governance:{record['idempotency_key']}"
        if not self.ledger.claim_idempotency_key(governance_key):
            current = self.ledger.get_record("audit_event_v2", event_id)
            if current is not None:
                return current
            raise ValueError("Duplicate governance idempotency key")
        self.ledger.save_record("audit_event_v2", event_id, record)
        if task_id is not None:
            self.ledger.conn.execute(
                "INSERT OR IGNORE INTO events(event_id,task_id,payload) VALUES(?,?,?)",
                (event_id, task_id, json.dumps(record, sort_keys=True)),
            )
            self.ledger.conn.commit()
        self._mirror("event", record)
        return record

    def update_decision_outcome(
        self,
        decision_id: str,
        *,
        outcome_status: str,
        outcome_validation: str,
        actor_id: str,
        actor_role: str,
    ) -> dict[str, Any]:
        record = self.ledger.get_record("decision_v2", decision_id)
        if record is None:
            raise KeyError(decision_id)
        before_hash = record["record_hash"]
        record["outcome_status"] = outcome_status
        record["outcome_validation"] = outcome_validation
        record["recorded_at_utc"] = utcnow()
        record["record_hash"] = _sha256(record, exclude={"record_hash"})
        self.ledger.save_record("decision_v2", decision_id, record)
        self.record_event(
            event_type="decision.outcome_reviewed",
            event_category="GOVERNANCE",
            action="REVIEW",
            actor_type="AGENT",
            actor_id=actor_id,
            actor_role=actor_role,
            task_id=record["task_id"],
            correlation_id=record["correlation_id"],
            decision_id=decision_id,
            authority_level=record["authority_level"],
            policy_rule_ids=record["policy_rule_ids"],
            capability_tool="governance-journal",
            target_resource=decision_id,
            source_system="TaskLedger",
            input_summary=f"Review prior decision outcome; prior hash {before_hash}.",
            result_status="SUCCESS",
            output_summary=f"Outcome status set to {outcome_status}.",
            evidence_references=record["evidence_references"],
            risk_severity=record["risk_level"],
            data_classification=record["data_classification"],
            model_provider=record["model_provider"],
            model_id_version=record["model_id_version"],
            skill_agent_version=record["skill_agent_version"],
            environment="RUNTIME",
            retention_class=record["retention_class"],
            before_state_ref=before_hash,
            after_state_ref=record["record_hash"],
        )
        self._mirror("decision", record)
        return record

    def _mirror(self, kind: str, record: dict[str, Any]) -> None:
        if self.mirror is None:
            return
        try:
            if kind == "decision":
                self.mirror.mirror_decision(dict(record))
            else:
                self.mirror.mirror_event(dict(record))
        except Exception as exc:
            failure_id = new_id("mirror-failure")
            self.ledger.save_record(
                "governance_mirror_failure",
                failure_id,
                {
                    "record_id": failure_id,
                    "kind": kind,
                    "canonical_record_ref": record["canonical_record_ref"],
                    "error_type": type(exc).__name__,
                    "timestamp": utcnow(),
                },
            )


def verify_audit_chain(records: list[dict[str, Any]]) -> bool:
    expected_previous = GENESIS_HASH
    for record in sorted(records, key=lambda item: item["event_sequence"]):
        if record.get("previous_event_hash") != expected_previous:
            return False
        if record.get("event_hash") != _sha256(record, exclude={"event_hash"}):
            return False
        expected_previous = record["event_hash"]
    return True

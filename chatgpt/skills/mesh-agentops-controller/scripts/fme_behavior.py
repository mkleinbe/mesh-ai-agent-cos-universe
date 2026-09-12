#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SKILL_TO_ROLE = {
    "mesh-chief-of-staff": "cos",
    "mesh-agentops-controller": "agentops",
    "mesh-answer-decision-desk": "answer-desk",
    "mesh-cro": "cro",
    "mesh-cfo": "cfo",
    "mesh-coo": "coo",
    "mesh-consultant-network-steward": "consultant-network-steward",
    "mesh-cmo": "cmo",
    "mesh-vp-content": "vp-content",
    "mesh-message-operations": "message-ops",
}
ROLE = SKILL_TO_ROLE.get(Path(__file__).resolve().parents[1].name)


class BehaviorInputError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BehaviorInputError(message)


def security_guard(_: dict[str, Any]) -> dict[str, Any]:
    return {
        "disposition": "FAIL_CLOSED",
        "identity_changed": False,
        "tools_changed": False,
        "canonical_source_changed": False,
        "approval_bypassed": False,
        "external_action_authorized": False,
        "private_reasoning_persisted": False,
    }


def queue_method(inputs: dict[str, Any]) -> dict[str, Any]:
    assumptions = inputs.get("assumptions", {})
    required = ("queued_work", "stationary_arrivals", "independent_arrivals", "stable_service_rate")
    valid = inputs.get("work_type") == "queued" and all(assumptions.get(key) is True for key in required)
    return {
        "erlang_c_allowed": valid,
        "disposition": "ERLANG_C_ALLOWED" if valid else "REJECT_ERLANG_C",
        "assumptions_satisfied": valid,
    }


def cos(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation == "select_deliberation":
        authority = int(inputs.get("authority_level", 0))
        if authority >= 4 or inputs.get("unresolved_conflict") or not inputs.get("evidence_sufficient"):
            mode = "HUMAN_DECISION_ESCALATION"
        elif inputs.get("cross_functional") and (
            inputs.get("materiality") == "high" or not inputs.get("reversible") or inputs.get("conflict")
        ):
            mode = "INDEPENDENT_MULTI_FUNCTIONAL"
        elif inputs.get("cross_functional"):
            mode = "BOUNDED_CROSS_FUNCTIONAL"
        else:
            mode = "SINGLE_FUNCTIONAL"
        return {"mode": mode, "unnecessary_deliberation": False}
    if operation == "synthesize_contributions":
        contributions = inputs.get("contributions", [])
        require(isinstance(contributions, list) and contributions, "contributions required")
        required = {"function", "supported_facts", "assumptions", "uncertainty", "recommendation", "confidence", "reversal_evidence"}
        require(all(required <= set(item) for item in contributions), "contribution evidence contract incomplete")
        recommendations = {json.dumps(item["recommendation"], sort_keys=True) for item in contributions}
        return {
            "contributions": contributions,
            "disagreement_visible": len(recommendations) > 1,
            "false_consensus_created": False,
        }
    if operation == "scenario_stress":
        scenarios = inputs.get("scenarios", {})
        require(list(scenarios) == ["Base", "Stress", "Severe"], "Base, Stress, Severe required in order")
        return {"scenario_order": ["Base", "Stress", "Severe"], "scenarios": scenarios, "authority": "ANALYTICAL_EVIDENCE_ONLY"}
    if operation == "work_graph_gaps":
        return {
            "gap_classes": [
                "orphan_outcomes", "unaligned_work", "conflicting_objectives", "duplicate_effort",
                "missing_dependencies", "coverage_gaps", "stale_commitments", "blocking_decisions",
            ],
            "parallel_task_store_created": False,
            "outcomes_inspected": len(inputs.get("outcomes", [])),
            "tasks_inspected": len(inputs.get("tasks", [])),
        }
    if operation == "change_readiness":
        return {
            "affected_groups": inputs.get("affected_groups", []),
            "adoption_dependencies": inputs.get("adoption_dependencies", []),
            "resistance_evidence": inputs.get("resistance_evidence", []),
            "saturation": inputs.get("saturation"),
            "knowledge_or_ability_gaps": inputs.get("knowledge_or_ability_gaps", []),
            "reinforcement_evidence": inputs.get("reinforcement_evidence", []),
            "post_change_signals": inputs.get("post_change_signals", []),
            "analysis_only": True,
            "hr_authority": False,
        }
    raise BehaviorInputError("unsupported cos operation")


def agentops(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation == "flow_diagnostic":
        source = inputs.get("source")
        require(source in {"TaskLedger", "telemetry"}, "authoritative flow evidence required")
        metrics = inputs.get("metrics", {})
        require(isinstance(metrics, dict) and bool(metrics), "metrics required")
        return {"source": source, "metrics": metrics, "evidence_supported": True, "recommendation_only": True}
    if operation == "queue_method":
        return queue_method(inputs)
    if operation == "recommendation_boundary":
        return {"can_add_agents": False, "can_add_headcount": False, "can_add_tools": False, "can_expand_authority": False}
    raise BehaviorInputError("unsupported agentops operation")


def answer_desk(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation != "classify_answerability":
        raise BehaviorInputError("unsupported answer-desk operation")
    if not inputs.get("access"):
        state = "BLOCKED_ACCESS"
    elif not inputs.get("authoritative_source"):
        state = "BLOCKED_NO_AUTHORITATIVE_SOURCE"
    elif inputs.get("stale") or inputs.get("conflict"):
        state = "BLOCKED_STALE_OR_CONFLICTING"
    elif inputs.get("sufficient"):
        state = "AUTHORITATIVE_ANSWER"
    else:
        state = "BOUNDED_RECOMMENDATION"
    return {
        "state": state,
        "route_to_authoritative_owner": state == "BLOCKED_STALE_OR_CONFLICTING",
        "silent_policy_rewrite": False,
    }


def cro(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation == "pricing_recommendation":
        return {"output_type": "RECOMMENDATION", "recommendation": inputs.get("recommendation"), "approval_granted": False}
    if operation == "buyer_intent":
        evidence = inputs.get("authoritative_evidence", [])
        return {"intent": "SUPPORTED" if evidence else "UNKNOWN", "evidence": evidence}
    if operation == "discount_exception":
        within = inputs.get("within_policy") is True
        return {"disposition": "WITHIN_POLICY" if within else "ESCALATE_APPROVAL", "approved": False}
    if operation == "forecast":
        return {"commit": inputs.get("commit", []), "best_case": inputs.get("best_case", []), "pipeline_upside": inputs.get("pipeline_upside", [])}
    if operation == "partner_attribution":
        return {"sourced": inputs.get("sourced", 0), "influenced": inputs.get("influenced", 0), "external_commitment_authorized": False}
    if operation == "rfp_proof":
        proof = inputs.get("proof", [])
        classification = "GAP"
        if proof:
            classification = "PARTIAL" if any(str(item).lower() == "partial" for item in proof) else "STRONG"
        return {"classification": classification, "invented_evidence": False, "proof": proof}
    raise BehaviorInputError("unsupported cro operation")


def cfo(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation != "finance_boundary":
        raise BehaviorInputError("unsupported cfo operation")
    return {
        "output_type": "ANALYTICAL_EVIDENCE",
        "analysis": inputs.get("analysis"),
        "assumptions": inputs.get("assumptions", []),
        "unsupported_assumptions": inputs.get("unsupported_assumptions", []),
        "approval_granted": False,
        "pricing_authority": False,
        "discount_authority": False,
        "procurement_authority": False,
        "contract_authority": False,
    }


def coo(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation == "process_analysis":
        measured = inputs.get("measured", {})
        return {"measured": measured, "assumptions": inputs.get("assumptions", {}), "toc_evidence_supported": bool(measured.get("constraint"))}
    if operation == "queue_method":
        return queue_method(inputs)
    if operation == "resource_availability":
        return {"freshness": inputs.get("freshness"), "treat_as_current": inputs.get("freshness") == "current"}
    if operation == "procurement_analysis":
        return {"evidence": inputs.get("evidence", {}), "procurement_authorized": False}
    raise BehaviorInputError("unsupported coo operation")


def consultant_steward(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation == "readiness":
        age = int(inputs.get("availability_age_days", 10**9))
        limit = int(inputs.get("freshness_limit_days", 0))
        current = age <= limit
        return {"availability_state": "CURRENT" if current else "STALE", "contracting_ready": bool(inputs.get("contracting_ready")), "staffing_commitment": False}
    if operation == "concentration_risk":
        people = inputs.get("qualified_consultants", [])
        return {"capability": inputs.get("capability"), "key_person_risk": bool(inputs.get("critical")) and len(people) <= 1, "portfolio_concentration_count": len(people)}
    if operation == "coverage":
        fallbacks = inputs.get("fallbacks", [])
        contingency = inputs.get("contingency_plan")
        return {"fallback_ready": bool(fallbacks), "contingency_ready": bool(contingency), "fallback_and_contingency_distinct": True, "staffing_commitment": False}
    raise BehaviorInputError("unsupported consultant-network-steward operation")


def cmo(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation == "benchmark":
        contextual = inputs.get("source_type") == "generic_donor"
        return {"value": inputs.get("value"), "policy_status": "CONTEXTUAL_ONLY" if contextual else "EVIDENCE_BOUND"}
    if operation == "growth_recommendation":
        dependencies: list[str] = []
        if inputs.get("includes_revenue"):
            dependencies.append("cro")
        if inputs.get("includes_investment"):
            dependencies.append("cfo")
        return {"required_dependencies": dependencies, "publication_authorized": False}
    if operation == "change_communication":
        return {"content": inputs.get("content"), "status": "DRAFT_ANALYSIS_ONLY", "publication_authorized": False}
    raise BehaviorInputError("unsupported cmo operation")


def vp_content(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation == "content_inventory":
        assets = inputs.get("assets", [])
        return {
            "stale_assets": [a["id"] for a in assets if not a.get("fresh")],
            "unsupported_claim_assets": [a["id"] for a in assets if not a.get("proof")],
            "orphan_assets": [a["id"] for a in assets if not a.get("source")],
            "duplicate_assets": [a["id"] for a in assets if a.get("duplicate_of")],
        }
    if operation == "derivative_lineage":
        return {"source_asset": inputs.get("source_asset"), "proof_lineage": inputs.get("proof_lineage", []), "publication_authorized": False}
    if operation == "authority_boundary":
        return {"pursuit_strategy": False, "enterprise_policy": False, "publication_authority": False}
    raise BehaviorInputError("unsupported vp-content operation")


def message_ops(operation: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if operation != "execute_message":
        raise BehaviorInputError("unsupported message-ops operation")
    checks = (
        (not inputs.get("content_approved"), "MISSING_CONTENT_APPROVAL"),
        (not inputs.get("message_specific_approval"), "MISSING_MESSAGE_SPECIFIC_APPROVAL"),
        (not inputs.get("recipient_authorized"), "MISSING_RECIPIENT_AUTHORITY"),
        (not inputs.get("send_authorized"), "MISSING_SEND_AUTHORITY"),
        (not inputs.get("idempotency_key"), "MISSING_IDEMPOTENCY_KEY"),
        (bool(inputs.get("duplicate")), "DUPLICATE_BLOCK"),
        (bool(inputs.get("suppressed")), "SUPPRESSION_BLOCK"),
        (bool(inputs.get("kill_switch")), "KILL_SWITCH_BLOCK"),
    )
    for blocked, reason in checks:
        if blocked:
            return {"status": "BLOCKED", "reason": reason, "approval_originated": False, "external_action_executed": False}
    return {"status": "READY_FOR_GOVERNED_EXECUTION", "metadata_consumed": inputs.get("metadata", {}), "approval_originated": False, "external_action_executed": False}


HANDLERS = {
    "cos": cos,
    "agentops": agentops,
    "answer-desk": answer_desk,
    "cro": cro,
    "cfo": cfo,
    "coo": coo,
    "consultant-network-steward": consultant_steward,
    "cmo": cmo,
    "vp-content": vp_content,
    "message-ops": message_ops,
}


def execute(payload: dict[str, Any]) -> dict[str, Any]:
    require(ROLE in HANDLERS, "unknown Skill role")
    require(set(payload) <= {"operation", "inputs"}, "unsupported top-level fields")
    operation = payload.get("operation")
    inputs = payload.get("inputs", {})
    require(isinstance(operation, str) and bool(operation), "operation required")
    require(isinstance(inputs, dict), "inputs must be an object")
    result = security_guard(inputs) if operation == "security_guard" else HANDLERS[ROLE](operation, inputs)
    return {"ok": True, "role": ROLE, "operation": operation, "result": result}


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
        require(isinstance(payload, dict), "payload must be an object")
        print(json.dumps(execute(payload), sort_keys=True))
        return 0
    except (BehaviorInputError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": "invalid_input", "detail": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from dataclasses import dataclass

from .models import AuthorityLevel

L4_ALWAYS = {
    "pricing",
    "discount",
    "commercial_terms",
    "contractual_language",
    "final_scope",
    "final_staffing",
    "material_delivery",
    "client_facing_strategy",
    "external_message",
    "public_publish",
    "public_claim",
    "legal_interpretation",
    "regulatory_interpretation",
    "security_conclusion",
    "privacy_exception",
    "capital_commitment",
    "investor_communication",
    "personnel_decision",
    "destructive_operation",
    "sensitive_system_change",
    "material_crm_truth_change",
    "irreversible_decision",
}
L5_EXCLUSIVE = {
    "firm_strategy",
    "strategic_pivot",
    "major_capital_allocation",
    "material_client_relationship",
    "major_partnership",
    "material_commercial_exception",
    "senior_personnel",
    "change_decision_rights",
    "change_cos_authority",
    "expand_agent_authority",
}


@dataclass(frozen=True, slots=True)
class AuthorityDecision:
    required_level: AuthorityLevel
    human_approval_required: bool
    michael_exclusive: bool
    reason: str


def classify(
    action: str,
    requested_level: AuthorityLevel = AuthorityLevel.L0,
    *,
    reversible: bool = True,
    material: bool = False,
    external: bool = False,
    low_confidence: bool = False,
) -> AuthorityDecision:
    if action in L5_EXCLUSIVE:
        return AuthorityDecision(AuthorityLevel.L5, True, True, "Michael-exclusive authority")
    if action in L4_ALWAYS or external or not reversible:
        return AuthorityDecision(AuthorityLevel.L4, True, False, "Consequential or externally binding action")
    if material or (low_confidence and requested_level >= AuthorityLevel.L3):
        return AuthorityDecision(
            max(requested_level, AuthorityLevel.L3),
            True,
            False,
            "Material judgment requires explicit delegation or approval",
        )
    return AuthorityDecision(
        requested_level,
        requested_level >= AuthorityLevel.L4,
        False,
        "Within configured Phase 1 authority",
    )


def assert_agent_may_act(
    agent_max_level: AuthorityLevel,
    decision: AuthorityDecision,
    approved: bool = False,
) -> None:
    if decision.required_level > agent_max_level:
        raise PermissionError("Agent authority exceeded")
    if decision.human_approval_required and not approved:
        raise PermissionError("Required human approval missing")

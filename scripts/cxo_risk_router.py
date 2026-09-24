#!/usr/bin/env python3
"""Deterministic cross-functional executive-risk routing for Mesh CxO Skills."""
from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping

CATEGORY_TO_REMIT={
    "opportunity_quality":"CRO","pricing_precedent":"CRO","commercial_exposure":"CRO",
    "forecast":"CRO","channel_conflict":"CRO","partner_concentration":"CRO",
    "partner_dependency":"CRO","revenue_concentration":"CRO","deal_quality":"CRO",
    "product_resale_conflict":"CRO","buyer_assumption":"CRO","procurement":"CRO",
    "bid_rfp":"CRO","no_decision":"CRO","consulting_resale_independence":"CRO",
    "margin":"CFO","gross_to_net":"CFO","discount_exposure":"CFO","cost_to_serve":"CFO",
    "working_capital":"CFO","payment_terms":"CFO","forecast_sensitivity":"CFO",
    "economic_concentration":"CFO","partner_rebate_economics":"CFO","pricing_model":"CFO",
    "model_assumption":"CFO","cost_uncertainty":"CFO","scenario_downside":"CFO",
    "commercial_investment":"CFO","switching_consolidation_economics":"CFO",
    "delivery_feasibility":"COO","capacity":"COO","staffing_dependency":"COO",
    "schedule":"COO","handoff_failure":"COO","implementation_dependency":"COO",
    "vendor_partner_operational":"COO","operational_concentration":"COO","resilience":"COO",
    "process_bottleneck":"COO","service_quality":"COO","operational_readiness":"COO",
    "integration":"COO","support_obligation":"COO","change_adoption_execution":"COO",
    "recovery_contingency":"COO",
    "brand":"CMO","reputation":"CMO","unsupported_claim":"CMO","audience_trust":"CMO",
    "partner_representation":"CMO","channel_dependency":"CMO","demand_quality":"CMO",
    "market_positioning":"CMO","campaign_economics":"CMO","messaging_consistency":"CMO",
    "audience_fatigue":"CMO","public_narrative":"CMO","change_communication":"CMO",
    "content_evidence":"CMO","distribution_concentration":"CMO","brand_partner_conflict":"CMO",
}

def route_category(category:str)->str:
    try:
        return CATEGORY_TO_REMIT[category]
    except KeyError as exc:
        raise ValueError(f"unrecognized risk category: {category}") from exc

def build_executive_risk(
    *,
    risk_id:str,
    governing_decision:str,
    category:str,
    cause:str,
    uncertain_event_or_condition:str,
    potential_business_consequence:str,
    evidence:list[dict[str,Any]],
    assumptions:list[str],
    material_unknowns:list[str],
    qualitative_likelihood:str,
    qualitative_impact:str,
    exposure_rationale:str,
    current_controls:list[str],
    treatment:str,
    treatment_owner:str,
    monitoring_indicator:str,
    trigger_or_escalation_condition:str,
    reversibility:str,
    residual_risk:str,
    review_horizon:str,
    source_lineage:list[dict[str,Any]],
)->dict[str,Any]:
    remit=route_category(category)
    if not source_lineage:
        raise ValueError("source_lineage is required")
    return {
        "contract_version":"mesh.executive-risk.v2",
        "version":"2.0.0",
        "risk_id":risk_id,
        "governing_decision":governing_decision,
        "risk_category":category,
        "functional_remit":remit,
        "cause":cause,
        "uncertain_event_or_condition":uncertain_event_or_condition,
        "potential_business_consequence":potential_business_consequence,
        "evidence":deepcopy(evidence),
        "assumptions":list(assumptions),
        "material_unknowns":list(material_unknowns),
        "qualitative_likelihood":qualitative_likelihood,
        "qualitative_impact":qualitative_impact,
        "exposure_rationale":exposure_rationale,
        "current_controls":list(current_controls),
        "treatment":treatment,
        "treatment_owner":treatment_owner,
        "monitoring_indicator":monitoring_indicator,
        "trigger_or_escalation_condition":trigger_or_escalation_condition,
        "reversibility":reversibility,
        "residual_risk":residual_risk,
        "review_horizon":review_horizon,
        "approval_or_risk_acceptance_owner":"QUALIFIED_HUMAN",
        "acceptance_role":f"{remit}_HUMAN_OWNER",
        "source_lineage":deepcopy(source_lineage),
    }

def route_risk(risk:Mapping[str,Any],current_remit:str)->dict[str,Any]:
    owner=route_category(str(risk.get("risk_category") or ""))
    return {
        "risk_id":risk.get("risk_id"),
        "from_remit":current_remit,
        "to_remit":owner,
        "handoff_required":owner!=current_remit,
        "contract_version":"mesh.executive-risk.v2",
        "risk_acceptance_owner":"QUALIFIED_HUMAN",
        "skill_acceptance_authority":False,
    }

def capacity_gate(*,actual_delivery_need_evidence:bool,staffing_or_timeline_commitment:bool)->dict[str,Any]:
    relevant=bool(actual_delivery_need_evidence and staffing_or_timeline_commitment)
    return {
        "capacity_decision_relevant":relevant,
        "early_pursuit_blocked":False,
        "decision_owner":"QUALIFIED_HUMAN" if relevant else None,
    }

def no_veto(*,risk_affects_action:bool,action_reversible:bool,dependent:bool)->dict[str,bool]:
    return {
        "continue_unaffected_work":bool(action_reversible and (not risk_affects_action or not dependent)),
        "stage_dependent_action":bool(risk_affects_action and dependent),
        "generic_workflow_blocker":False,
    }

from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("router",ROOT/"scripts/cxo_risk_router.py")
MOD=importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(MOD)

def build(category):
    return MOD.build_executive_risk(
        risk_id="R1",governing_decision="Pursue",category=category,cause="Cause",
        uncertain_event_or_condition="Future condition",potential_business_consequence="Consequence",
        evidence=[{"source":"e"}],assumptions=[],material_unknowns=[],
        qualitative_likelihood="UNKNOWN",qualitative_impact="HIGH",exposure_rationale="Material",
        current_controls=["control"],treatment="TEST_BEFORE_COMMITMENT",treatment_owner="owner",
        monitoring_indicator="indicator",trigger_or_escalation_condition="before commitment",
        reversibility="MODERATE",residual_risk="bounded",review_horizon="before commitment",
        source_lineage=[{"source":"e","observed_at":"2026-09-24"}],
    )

def test_cro_routes_margin_to_cfo():
    risk=build("margin")
    result=MOD.route_risk(risk,"CRO")
    assert result["to_remit"]=="CFO"
    assert result["handoff_required"] is True

def test_cfo_routes_staffing_to_coo():
    risk=build("staffing_dependency")
    assert MOD.route_risk(risk,"CFO")["to_remit"]=="COO"

def test_coo_routes_public_claim_to_cmo():
    risk=build("unsupported_claim")
    assert MOD.route_risk(risk,"COO")["to_remit"]=="CMO"

def test_cmo_routes_pricing_to_cro():
    risk=build("pricing_precedent")
    assert MOD.route_risk(risk,"CMO")["to_remit"]=="CRO"

def test_risk_acceptance_is_always_human():
    for category in ("margin","staffing_dependency","unsupported_claim","pricing_precedent"):
        risk=build(category)
        assert risk["approval_or_risk_acceptance_owner"]=="QUALIFIED_HUMAN"
        assert risk["acceptance_role"].endswith("_HUMAN_OWNER")

def test_unknown_capacity_does_not_block_early_pursuit():
    gate=MOD.capacity_gate(actual_delivery_need_evidence=False,staffing_or_timeline_commitment=False)
    assert gate["early_pursuit_blocked"] is False
    assert gate["capacity_decision_relevant"] is False

def test_capacity_decision_becomes_human_when_concrete():
    gate=MOD.capacity_gate(actual_delivery_need_evidence=True,staffing_or_timeline_commitment=True)
    assert gate["capacity_decision_relevant"] is True
    assert gate["decision_owner"]=="QUALIFIED_HUMAN"

def test_manageable_risk_not_generic_blocker():
    result=MOD.no_veto(risk_affects_action=True,action_reversible=True,dependent=False)
    assert result["continue_unaffected_work"] is True
    assert result["generic_workflow_blocker"] is False

def test_v2_contract_validates_router_output():
    schema=json.loads((ROOT/"contracts/executive-risk.v2.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(build("margin"))

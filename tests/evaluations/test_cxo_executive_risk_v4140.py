from __future__ import annotations
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
SKILLS=ROOT/"chatgpt"/"skills"

def read_skill(name:str)->str:
    return (SKILLS/name/"SKILL.md").read_text()

def test_ready_scenarios_are_complete():
    text=(ROOT/"specs/cxo-executive-risk-v4.14.0.feature").read_text()
    ids=set(re.findall(r"Scenario:\s+(CXR-\d{3})",text))
    assert ids=={f"CXR-{i:03d}" for i in range(1,11)}

def test_shared_executive_risk_contract_validates():
    schema=json.loads((ROOT/"contracts/executive-risk.v1.schema.json").read_text())
    example=json.loads((ROOT/"contracts/examples/executive-risk.v1.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(example)
    assert example["contract_version"]=="mesh.executive-risk.v1"
    assert example["approval_or_risk_acceptance_owner"]

def test_all_cxo_skills_use_shared_contract_and_human_acceptance():
    for name in ("mesh-cro","mesh-cfo","mesh-coo","mesh-cmo"):
        text=read_skill(name)
        assert "mesh.executive-risk.v1" in text
        assert "qualified human" in text.lower()
        assert "generic workflow blocker" in text.lower()

def test_cro_risk_remit():
    text=read_skill("mesh-cro").lower()
    for token in (
        "opportunity-quality risk","pricing/discount precedent","commercial exposure",
        "forecast risk","channel conflict","partner concentration","partner dependency",
        "revenue concentration","deal-quality deterioration","product/resale conflict",
        "unsupported buyer assumptions","procurement exposure","bid/rfp risk",
        "no-decision risk","consulting/resale independence risk"
    ):
        assert token in text
    assert "margin uncertainty -> cfo" in text

def test_cfo_risk_remit():
    text=read_skill("mesh-cfo").lower()
    for token in (
        "margin risk","gross-to-net economics","discount exposure","fixed cost-to-serve",
        "working-capital effects","payment-term economics","forecast sensitivity",
        "economic concentration","partner/rebate economics","pricing-model risk",
        "model and assumption risk","cost uncertainty","scenario downside",
        "commercial investment economics","switching/consolidation economics"
    ):
        assert token in text
    assert "staffing constraint -> coo" in text

def test_coo_risk_remit_and_capacity_boundary():
    text=read_skill("mesh-coo").lower()
    for token in (
        "delivery feasibility","capacity when capacity has actually become decision relevant",
        "staffing dependencies","schedule risk","handoff failure","implementation dependencies",
        "vendor/partner operational dependency","concentration","resilience","process bottlenecks",
        "service quality","operational readiness","integration risk","support obligations",
        "change/adoption execution","recovery and contingency"
    ):
        assert token in text
    assert "do not make unknown capacity an early sales blocker" in text
    assert "reputational/public claim issue -> cmo" in text

def test_cmo_risk_remit_and_publication_boundary():
    text=read_skill("mesh-cmo").lower()
    for token in (
        "brand risk","reputation","unsupported claims","audience trust",
        "partner representation","channel dependency","demand-quality degradation",
        "market-positioning conflict","campaign economics","messaging inconsistency",
        "audience fatigue","public narrative","change communication","content evidence",
        "distribution concentration","brand/partner conflict"
    ):
        assert token in text
    assert "commercial pricing exposure -> cro/cfo" in text
    assert "does not create publication authority" in text

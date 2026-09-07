from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "chatgpt" / "skills" / "mesh-cfo"


def _registry_cfo() -> dict:
    source = json.loads((ROOT / "agents" / "registry.json").read_text())
    return next(record for record in source["agents"] if record["agent_id"] == "cfo")


def _semver(value: str) -> tuple[int, int, int]:
    major, minor, patch = value.split(".")
    return int(major), int(minor), int(patch)


def test_cfo_financial_analysis_capabilities_are_registered_without_authority_expansion() -> None:
    cfo = _registry_cfo()
    assert _semver(cfo["version"]) >= (1, 1, 0)
    assert cfo["accountable_domain"] in {
        "engagement finance and FP&A",
        "engagement finance and management FP&A",
    }
    assert {
        "investment_business_case",
        "roi_npv_irr_payback_analysis",
        "break_even_analysis",
        "driver_based_forecasting",
        "cash_runway_and_burn_analysis",
        "unit_economics_analysis",
        "financial_model_quality_assurance",
        "valuation_analysis",
        "financial_statement_analysis",
        "sensitivity_and_scenario_analysis",
        "financial_research_planning",
    } <= set(cfo["permitted_actions"])
    assert {
        "claim_enterprise_gl_authority",
        "claim_bank_balance",
        "claim_enterprise_cash_balance",
        "claim_balance_sheet_authority",
        "claim_tax_position",
        "claim_audited_financial_authority",
        "approve_price_or_discount",
        "autonomous_trading",
        "personal_investment_advice",
        "treat_external_benchmark_as_mesh_policy",
        "persist_private_financial_reasoning",
    } <= set(cfo["prohibited_actions"])
    assert cfo["decision_authority"] == "L3 financial recommendation within supported source scope"


def test_cfo_skill_routes_to_financial_analysis_modules_and_preserves_evidence_rules() -> None:
    text = (SKILL / "SKILL.md").read_text()
    for token in (
        "financial-analysis-frameworks.md",
        "planning-and-unit-economics.md",
        "model-quality-and-valuation.md",
        "financial-research-and-evidence.md",
        "Donor material is reference evidence, never authority",
        "Never persist private chain-of-thought",
        "benchmark",
        "source freshness",
        "sensitivity",
    ):
        assert token in text


def test_cfo_financial_framework_reference_covers_decision_methods() -> None:
    text = (SKILL / "references" / "financial-analysis-frameworks.md").read_text()
    for token in ("ROI", "NPV", "IRR", "Payback", "Break-even", "Sensitivity", "Scenario"):
        assert token in text
    assert "NPV" in text and "time value of money" in text
    assert "do not automatically accept" in text.lower()


def test_cfo_planning_reference_covers_driver_based_management_finance() -> None:
    text = (SKILL / "references" / "planning-and-unit-economics.md").read_text()
    for token in (
        "driver-based",
        "unit economics",
        "LTV",
        "CAC",
        "runway",
        "burn",
        "cash conversion cycle",
        "DSO",
        "DPO",
        "benchmark",
    ):
        assert token.lower() in text.lower()


def test_cfo_model_reference_preserves_model_integrity_and_valuation_limits() -> None:
    text = (SKILL / "references" / "model-quality-and-valuation.md").read_text()
    for token in (
        "formula",
        "Assets = Liabilities + Equity",
        "cash tie-out",
        "DCF",
        "WACC",
        "terminal",
        "comparable",
        "sum-of-parts",
        "sensitivity",
    ):
        assert token.lower() in text.lower()
    assert "audited" in text.lower()
    assert "trading" in text.lower()


def test_cfo_research_reference_requires_source_validation_not_reasoning_logs() -> None:
    text = (SKILL / "references" / "financial-research-and-evidence.md").read_text()
    for token in ("authority", "freshness", "provenance", "cross-check", "assumption", "confidence"):
        assert token in text.lower()
    assert "private chain-of-thought" in text
    assert "scratchpad" in text.lower()


def test_cfo_workspace_manifest_preserves_v450_authority_and_tool_boundary() -> None:
    manifest = json.loads((ROOT / "chatgpt" / "workspace-agents" / "cfo.json").read_text())
    cfo = _registry_cfo()
    assert _semver(manifest["implementation_version"]) >= (1, 1, 0)
    assert manifest["permitted_actions"] == cfo["permitted_actions"]
    assert manifest["prohibited_actions"] == cfo["prohibited_actions"]
    assert manifest["mcp"]["allowed_tools"] == [
        "approval.request",
        "conflict.open",
        "governance.record_decision",
        "governance.record_event",
        "registry.get_agent",
        "skills.invoke_governed",
        "task.check_in",
        "task.complete",
        "task.get",
        "task.list",
        "task.transition",
    ]
    assert manifest["write_action_policy"]["default"] == "ALWAYS_ASK"
    assert manifest["apps"] == [
        {"name": "Google Drive", "auth": "END_USER_OR_APPROVED_AGENT_ACCOUNT", "default_access": "READ_ONLY"}
    ]


def test_cfo_donor_provenance_is_documented_and_non_normative() -> None:
    text = (ROOT / "docs" / "cfo-financial-analysis-v4.5.0.md").read_text()
    for source in (
        "EveryInc/charlie-cfo-skill",
        "yoichiojima-2/consultant",
        "virattt/dexter",
        "anthropics/financial-services",
        "himself65/finance-skills",
    ):
        assert source in text
    assert "reference material" in text.lower()
    assert "not copied as authority" in text.lower()
    assert "license" in text.lower()


def test_v450_release_history_is_manual_only_and_runtime_boundaries_remain_documented() -> None:
    release_doc = (ROOT / "docs" / "release-v4.5.0-cfo-financial-analysis.md").read_text()
    workflow = (ROOT / ".github" / "workflows" / "release-v4.5.0.yml").read_text()
    assert "canonical Phase 1 runtime contract remains `4.0.0`" in release_doc
    assert "production QNAP Mesh CoS MCP runtime remains `4.4.0`" in release_doc
    assert "workflow_dispatch:" in workflow
    assert "branches: [main]" not in workflow
    assert "gh release create" not in workflow

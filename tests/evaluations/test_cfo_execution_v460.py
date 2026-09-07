from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "chatgpt" / "skills" / "mesh-cfo"


def _finance_math() -> ModuleType:
    path = SKILL / "scripts" / "financial_math.py"
    spec = importlib.util.spec_from_file_location("mesh_cfo_financial_math", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cfz001_known_answer_finance_math_is_reproducible() -> None:
    finance = _finance_math()
    assert finance.npv(0.10, [-100000, 30000, 35000, 40000, 45000]) == pytest.approx(
        16986.544634929287
    )
    assert finance.irr([-100, 60, 60]) == pytest.approx(0.1306623863, abs=1e-9)
    assert finance.payback_period([-100000, 20000, 30000, 40000, 50000]) == pytest.approx(3.2)
    assert finance.payback_period(
        [-100, 60, 60], discount_rate=0.10
    ) == pytest.approx(1.9166666667, abs=1e-9)
    assert finance.break_even_units(50000, 100, 60) == pytest.approx(1250)
    assert finance.runway(100000, 10000) == {
        "cash_generative": False,
        "runway_periods": 10.0,
    }
    assert finance.runway(100000, -1000) == {
        "cash_generative": True,
        "runway_periods": None,
    }
    assert finance.contribution_margin(1000, 600) == {
        "contribution": 400.0,
        "contribution_margin_ratio": 0.4,
    }
    assert finance.ltv_cac(1200, 300) == pytest.approx(4.0)


def test_cfz001_finance_math_fails_closed_on_invalid_or_unsupported_input() -> None:
    finance = _finance_math()
    with pytest.raises(finance.FinanceInputError):
        finance.npv(-1, [-1, 2])
    with pytest.raises(finance.FinanceInputError):
        finance.irr([1, 2, 3])
    with pytest.raises(finance.FinanceInputError):
        finance.break_even_units(100, 50, 50)
    with pytest.raises(finance.FinanceInputError):
        finance.ltv_cac(1000, 0)
    with pytest.raises(finance.FinanceInputError, match="unsupported operation"):
        finance.execute({"operation": "trade", "inputs": {}})
    with pytest.raises(finance.FinanceInputError, match="unsupported fields"):
        finance.execute({"operation": "npv", "inputs": {}, "command": "shell"})


def test_cfz002_cfz003_cfo_only_governed_analytics_handoff_is_bounded() -> None:
    registry = load_registry()
    assert registry["cfo"]["skills"] == ["mesh-data-analytics"]
    adapters = GovernedAdapterRegistry(registry)
    result = adapters.execute(
        "cfo",
        "mesh-data-analytics",
        {
            "task_id": "CFZ-002",
            "authority_level": 3,
            "evidence_references": ["synthetic://approved-finance-input"],
        },
    )
    assert result["status"] == "AUTHORIZED"
    assert result["execution_mode"] == "CHATGPT_SKILL_HANDOFF"
    assert result["execution_claim"] == "AUTHORIZATION_HANDOFF_ONLY"
    assert result["synchronous_workspace_agent_execution"] is False
    assert result["result_provenance_required"] is True
    assert result["agent_id"] == "cfo"
    assert result["capability"] == "mesh-data-analytics"

    for agent_id in ("coo", "cmo", "message-ops"):
        with pytest.raises(PermissionError, match="Capability not allowed"):
            adapters.execute(agent_id, "mesh-data-analytics", {})


def test_cfz003_shared_analytics_contract_cannot_modify_authority_or_canonical_facts() -> None:
    raw = json.loads((ROOT / "agents" / "registry.json").read_text())
    capabilities = {item["capability"]: item for item in raw["shared_capabilities"]}
    analytics = capabilities["mesh-data-analytics"]
    assert analytics["deployment"] == "EXTERNAL_SHARED_SKILL"
    assert analytics["consumers"] == ["cfo"]
    assert analytics["authority"] == "ANALYTICAL_EXECUTION_ONLY"
    assert analytics["canonical_facts_modified"] is False
    assert analytics["external_action_included"] is False
    assert analytics["request_contract"] == "mesh.data.analytics.handoff.v1.2"


def test_cfz004_management_fpa_source_scope_expands_analysis_not_enterprise_authority() -> None:
    raw = json.loads((ROOT / "agents" / "registry.json").read_text())
    cfo = next(item for item in raw["agents"] if item["agent_id"] == "cfo")
    assert cfo["version"] == "1.2.0"
    assert cfo["accountable_domain"] == "engagement finance and management FP&A"
    assert "approved Mesh management FP&A artifacts" in cfo["allowed_sources"]
    assert "approved primary or public financial evidence for an authorized analysis" in cfo[
        "allowed_sources"
    ]
    assert {
        "management_fpa_analysis",
        "reproducible_financial_calculation",
        "financial_research_execution",
        "financial_artifact_production",
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
    } <= set(cfo["prohibited_actions"])
    assert cfo["decision_authority"] == "L3 financial recommendation within supported source scope"


def test_cfz006_operating_cadence_and_artifact_contract_is_routed() -> None:
    skill = (SKILL / "SKILL.md").read_text()
    cadence = (SKILL / "references" / "operating-cadence-and-executive-artifacts.md").read_text()
    for token in (
        "scripts/financial_math.py",
        "mesh-data-analytics",
        "skills.invoke_governed",
        "operating-cadence-and-executive-artifacts.md",
    ):
        assert token in skill
    for token in (
        "Weekly exception cadence",
        "Monthly management FP&A cadence",
        "Quarterly decision cadence",
        "CFO scorecard",
        "Rolling forecast",
        "13-week cash view",
        "CEO or board finance brief",
    ):
        assert token in cadence


def test_cfz007_cfo_mcp_allowlist_remains_exact_and_human_only_tools_stay_absent() -> None:
    manifest = json.loads((ROOT / "chatgpt" / "workspace-agents" / "cfo.json").read_text())
    expected = [
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
    assert manifest["mcp"]["allowed_tools"] == expected
    assert manifest["builder_configuration"]["mcp_allowed_tools"] == expected
    assert manifest["apps"] == [
        {
            "name": "Google Drive",
            "auth": "END_USER_OR_APPROVED_AGENT_ACCOUNT",
            "default_access": "READ_ONLY",
        }
    ]
    assert "approval.record_decision" not in expected
    assert "reliability.human_override" not in expected


def test_cfz008_historical_cfo_release_workflows_are_manual_only() -> None:
    for version in ("4.5.0", "4.5.1", "4.5.2"):
        text = (ROOT / ".github" / "workflows" / f"release-v{version}.yml").read_text()
        assert "workflow_dispatch:" in text
        assert "branches: [main]" not in text
        assert "gh release create" not in text


def test_cfz009_version_identity_is_explicit_and_non_ambiguous() -> None:
    manifest = json.loads((ROOT / "chatgpt" / "workspace-agents" / "cfo.json").read_text())
    identity = manifest["version_identity"]
    assert identity == {
        "agent_implementation": "1.2.0",
        "repository_capability_release": "4.6.0",
        "canonical_runtime_contract": "4.0.0",
        "production_qnap_deployment": "4.4.0",
        "legacy_repository_release_field_semantics": "canonical_runtime_contract",
    }
    assert manifest["repository_release"] == "4.0.0"

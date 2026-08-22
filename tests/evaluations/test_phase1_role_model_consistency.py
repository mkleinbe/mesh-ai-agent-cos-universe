from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from mesh_cos import __version__
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".toml", ".txt"}
LEGACY_ROLE_NAMES = ("CFO" + " v1", "COO" + " v1")


def test_canonical_role_names_are_stable_and_version_is_metadata() -> None:
    registry = load_registry()
    assert registry["cro"]["display_name"] == "CRO"
    assert registry["cfo"]["display_name"] == "CFO"
    assert registry["coo"]["display_name"] == "COO"
    assert registry["consultant-network-steward"]["display_name"] == "Consultant Network Steward"
    assert registry["cmo"]["display_name"] == "CMO"
    assert registry["vp-content"]["display_name"] == "VP Content"
    assert registry["message-ops"]["display_name"] == "Message Operations"

    for agent_id in ("cro", "cfo", "coo", "consultant-network-steward", "cmo", "vp-content", "message-ops"):
        record = registry[agent_id]
        assert re.fullmatch(r"\d+\.\d+\.\d+", record["version"])
        assert not re.search(r"\bv\d+(?:\.\d+)*\b", record["display_name"], re.IGNORECASE)


def test_runtime_rejects_role_names_that_embed_implementation_version(tmp_path: Path) -> None:
    raw = json.loads((ROOT / "agents" / "registry.json").read_text())
    raw["agents"][0]["display_name"] = "Chief of Staff" + " v9"
    path = tmp_path / "agents" / "registry.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(raw))

    with pytest.raises(ValueError, match="display_name must not embed implementation version"):
        load_registry(path)


def test_runtime_and_package_release_versions_are_aligned() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text()
    assert __version__ == "4.0.0"
    assert f'version = "{__version__}"' in pyproject


def test_legacy_role_names_are_removed_repo_wide() -> None:
    offenders: dict[str, list[str]] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        matches = [legacy for legacy in LEGACY_ROLE_NAMES if legacy in text]
        if matches:
            offenders[str(path.relative_to(ROOT))] = matches
    assert offenders == {}, offenders


def test_phase1_role_capabilities_cover_canonical_accountabilities() -> None:
    registry = load_registry()
    required = {
        "cro": {
            "commercial_analysis",
            "opportunity_qualification",
            "pipeline_health_analysis",
            "pursuit_prioritization",
            "proposal_strategy",
            "next_best_commercial_action",
            "expansion_strategy",
            "commercial_risk_framing",
            "request_cfo_economics",
            "request_coo_feasibility",
            "request_devils_advocate_review",
        },
        "cfo": {
            "engagement_economics",
            "pricing_scenarios",
            "cost_to_serve_analysis",
            "contribution_economics",
            "margin_analysis",
            "margin_leakage_detection",
            "working_capital_implications",
            "economic_scenario_comparison",
            "assumption_management",
            "financial_risk_analysis",
            "forecast_vs_actual",
        },
        "coo": {
            "delivery_feasibility",
            "delivery_configuration",
            "capacity_analysis",
            "pod_resource_composition",
            "dependency_readiness_analysis",
            "delivery_risk_sensing",
            "partner_capacity_analysis",
            "operational_constraint_management",
            "staffing_recommendation",
            "delegate_network_steward",
        },
        "consultant-network-steward": {
            "candidate_identification",
            "candidate_matching",
            "candidate_fit_check",
            "availability_freshness_check",
            "validation_timestamp_check",
            "rate_validity_check",
            "contracting_readiness_check",
            "readiness_gap_analysis",
            "refresh_workflow",
            "mark_requires_refresh",
            "establish_staffing_ready_status",
        },
        "cmo": {
            "marketing_strategy",
            "audience_icp_strategy",
            "category_positioning",
            "campaign_strategy",
            "demand_campaign_architecture",
            "distribution_strategy",
            "campaign_performance_optimization",
            "marketing_commercial_feedback",
            "brand_governance",
            "editorial_priority",
            "content_review",
            "delegate_vp_content",
        },
        "vp-content": {
            "editorial_planning",
            "editorial_calendar_management",
            "source_evidence_assembly",
            "draft_content",
            "channel_adaptation",
            "derivative_content_production",
            "repurpose_content",
            "ip_reuse",
            "content_inventory_management",
            "editorial_qa",
            "performance_feedback",
            "prepare_for_cmo_review",
        },
        "message-ops": {
            "prepare_execution",
            "execute_approved_message",
        },
    }
    for agent_id, required_actions in required.items():
        assert required_actions <= set(registry[agent_id]["permitted_actions"]), agent_id


def test_registry_source_preserves_role_boundaries() -> None:
    raw = json.loads((ROOT / "agents" / "registry.json").read_text())
    records = {record["agent_id"]: record for record in raw["agents"]}

    assert records["cfo"]["accountable_domain"] == "engagement finance and FP&A"
    assert "claim_enterprise_gl_authority" in records["cfo"]["prohibited_actions"]
    assert "approve_price_or_discount" in records["cfo"]["prohibited_actions"]

    assert records["coo"]["accountable_domain"] == "delivery feasibility, capacity, and resource readiness"
    assert "final_staffing_commitment_without_approval" in records["coo"]["prohibited_actions"]

    assert records["consultant-network-steward"]["parent_agent_id"] == "coo"
    assert "make_final_staffing_commitment" in records["consultant-network-steward"]["prohibited_actions"]

    assert "public_publish_without_approval" in records["cmo"]["prohibited_actions"]
    assert "public_publish" in records["vp-content"]["prohibited_actions"]

    assert "devils-advocate" not in records
    assert "message-ops" in records
    assert records["message-ops"]["parent_agent_id"] == "cos"
    assert records["message-ops"]["decision_authority"] == "L1 execution of explicitly approved communication"
    assert "mesh-message-operations" in records["message-ops"]["skills"]
    assert "consequential_external_send_without_approval" in records["message-ops"]["prohibited_actions"]

    shared = {item["capability"]: item for item in raw["shared_capabilities"]}
    assert set(shared) == {"mesh-devils-advocate"}
    assert shared["mesh-devils-advocate"]["authority"] == "ADVISORY_ONLY"

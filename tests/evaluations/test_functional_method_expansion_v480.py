from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "chatgpt" / "skills"


def _registry() -> dict:
    return json.loads((ROOT / "agents" / "registry.json").read_text(encoding="utf-8"))


def _skill(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


def _agent(name: str) -> str:
    return (ROOT / "agents" / f"{name}.md").read_text(encoding="utf-8")


def _finance_math() -> ModuleType:
    path = SKILLS / "mesh-cfo" / "scripts" / "financial_math.py"
    spec = importlib.util.spec_from_file_location("mesh_cfo_financial_math_v480", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fme_001_002_003_governance_invariants() -> None:
    raw = _registry()
    agents = {item["agent_id"]: item for item in raw["agents"]}
    assert len(agents) == 10
    assert set(agents) == {
        "cos", "agentops", "answer-desk", "cro", "cfo", "coo",
        "consultant-network-steward", "cmo", "vp-content", "message-ops",
    }
    assert agents["consultant-network-steward"]["parent_agent_id"] == "coo"
    assert agents["vp-content"]["parent_agent_id"] == "cmo"
    shared = {item["capability"]: item for item in raw["shared_capabilities"]}
    assert set(shared) == {"mesh-devils-advocate", "mesh-data-analytics"}
    assert shared["mesh-devils-advocate"]["type"] == "shared_skill"
    assert "L4/L5 require human authority" in agents["cos"]["decision_authority"]
    assert "COMPLETED != VERIFIED" in _skill("mesh-chief-of-staff")
    combined = "\n".join(_skill(name) for name in (
        "mesh-chief-of-staff", "mesh-agentops-controller", "mesh-answer-decision-desk",
        "mesh-cro", "mesh-cfo", "mesh-coo", "mesh-consultant-network-steward",
        "mesh-cmo", "mesh-vp-content", "mesh-message-operations",
    ))
    for rejected in ("~/.claude/decisions/", "[INVOKE:", "company-context.md"):
        assert rejected not in combined


def test_fme_004_through_009_cos_methods_are_explicit_and_bounded() -> None:
    text = _skill("mesh-chief-of-staff") + "\n" + _agent("cos")
    for marker in (
        "SINGLE_FUNCTIONAL",
        "BOUNDED_CROSS_FUNCTIONAL",
        "INDEPENDENT_MULTI_FUNCTIONAL",
        "DEVILS_ADVOCATE_CHALLENGE",
        "HUMAN_DECISION_ESCALATION",
        "supported fact",
        "what evidence would reverse",
        "Base / Stress / Severe",
        "orphan outcomes",
        "stale commitments",
        "change saturation",
        "post-change adoption signals",
    ):
        assert marker in text
    assert "parallel OKR" not in text


def test_fme_010_011_agentops_flow_intelligence_is_assumption_bound() -> None:
    text = _skill("mesh-agentops-controller") + "\n" + _agent("agentops")
    for marker in (
        "P50/P90",
        "active-work versus wait time",
        "approval/queue delay",
        "rework frequency",
        "work-in-progress concentration",
        "Erlang-C",
        "queued work",
        "P50/P90/P99",
        "cannot add agents, headcount, tools, or authority",
    ):
        assert marker in text


def test_fme_012_answer_desk_answerability_states_and_owner_routing() -> None:
    text = _skill("mesh-answer-decision-desk") + "\n" + _agent("answer-desk")
    for marker in (
        "AUTHORITATIVE_ANSWER",
        "BOUNDED_RECOMMENDATION",
        "BLOCKED_ACCESS",
        "BLOCKED_STALE_OR_CONFLICTING",
        "BLOCKED_NO_AUTHORITATIVE_SOURCE",
        "canonical source owner",
        "terminology drift",
        "rollback/escalation",
        "authoritative owner",
    ):
        assert marker in text


def test_fme_013_015_016_017_cro_method_depth_preserves_commercial_bounds() -> None:
    text = _skill("mesh-cro") + "\n" + _agent("cro")
    for marker in (
        "model + range",
        "discount matrix",
        "precedent risk",
        "commit / best case / pipeline-upside",
        "confidence bands",
        "sourced versus influenced",
        "kill/unwind criteria",
        "STRONG / PARTIAL / GAP",
        "A GAP remains a GAP",
        "bid/no-bid",
        "cannot execute external commitments",
    ):
        assert marker in text
    assert "unsupported buyer intent remains unknown" in text


def test_fme_014_deal_discount_math_uses_fixed_cost_to_serve() -> None:
    finance = _finance_math()
    result = finance.deal_discount_economics(list_price=100, fixed_cost_to_serve=20, discount_rate=0.30)
    assert result == {
        "pre_discount_revenue": 100.0,
        "post_discount_revenue": 70.0,
        "pre_discount_margin_dollars": 80.0,
        "post_discount_margin_dollars": 50.0,
        "pre_discount_margin_ratio": 0.8,
        "post_discount_margin_ratio": 50.0 / 70.0,
        "margin_dollar_loss_ratio": 0.375,
    }
    response = finance.execute({
        "operation": "deal_discount_economics",
        "inputs": {"list_price": 100, "fixed_cost_to_serve": 20, "discount_rate": 0.30},
    })
    assert response["ok"] is True
    assert response["result"]["margin_dollar_loss_ratio"] == 0.375


def test_fme_018_cfo_commercial_economics_are_evidence_only() -> None:
    text = _skill("mesh-cfo") + "\n" + _agent("cfo")
    for marker in (
        "channel cost-to-serve",
        "discount economics",
        "partner economics",
        "supplier concentration economics",
        "switching-cost",
        "commercial forecast cross-check",
        "analytical evidence, not approval",
    ):
        assert marker in text


def test_fme_019_coo_process_capacity_vendor_and_procurement_methods_are_bounded() -> None:
    text = _skill("mesh-coo") + "\n" + _agent("coo")
    for marker in (
        "current-state-first",
        "elapsed time",
        "active time",
        "wait time",
        "Theory of Constraints",
        "queueing methods only",
        "break-glass readiness",
        "supplier concentration",
        "cannot authorize procurement",
    ):
        assert marker in text


def test_fme_020_consultant_steward_concentration_freshness_and_contingency() -> None:
    text = _skill("mesh-consultant-network-steward")
    for marker in (
        "capability criticality",
        "portfolio concentration",
        "key-person concentration",
        "rate freshness",
        "availability freshness",
        "fallback coverage",
        "contingency readiness",
        "final staffing commitment",
    ):
        assert marker in text


def test_fme_021_cmo_growth_and_change_readiness_remain_human_gated() -> None:
    text = _skill("mesh-cmo")
    for marker in (
        "growth-model comparison",
        "channel-allocation evidence",
        "marketing investment scenarios",
        "acquisition economics",
        "organization/capacity implications",
        "change-readiness",
        "generic benchmarks",
        "human-gated",
    ):
        assert marker in text


def test_fme_022_vp_content_proof_inventory_is_narrow() -> None:
    text = _skill("mesh-vp-content")
    for marker in (
        "inventory freshness",
        "orphaned assets",
        "terminology drift",
        "duplicate/stale IP",
        "source/proof lineage",
        "reusable proof-point inventory",
        "derivative-content traceability",
        "does not own RFP pursuit strategy",
    ):
        assert marker in text


def test_fme_023_message_ops_consumes_metadata_without_originating_approval() -> None:
    text = _skill("mesh-message-operations")
    for marker in (
        "campaign/change sequence",
        "scheduled window",
        "audience/recipient class",
        "message-specific approval",
        "cannot originate approval",
        "idempotency",
        "kill switch",
    ):
        assert marker in text


def test_fme_024_shared_skills_do_not_become_principals() -> None:
    combined = "\n".join(_skill(name) for name in (
        "mesh-chief-of-staff", "mesh-cfo", "mesh-cro", "mesh-cmo",
    ))
    assert "Skill is a capability, not an agent principal" in combined
    assert "private chain-of-thought" in combined

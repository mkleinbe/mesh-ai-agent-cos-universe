from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _registry() -> dict:
    raw = json.loads((ROOT / "agents" / "registry.json").read_text(encoding="utf-8"))
    return {record["agent_id"]: record for record in raw["agents"]}, raw


def _agent(name: str) -> str:
    return (ROOT / "agents" / name).read_text(encoding="utf-8")


def test_registry_authority_and_roster_are_unchanged() -> None:
    records, raw = _registry()
    assert len(records) == 10
    assert set(records) == {
        "cos",
        "agentops",
        "answer-desk",
        "cro",
        "cfo",
        "coo",
        "consultant-network-steward",
        "cmo",
        "vp-content",
        "message-ops",
    }
    shared = {item["capability"]: item for item in raw["shared_capabilities"]}
    assert set(shared) == {"mesh-devils-advocate", "mesh-data-analytics"}
    assert records["cos"]["decision_authority"] == "L3 only where explicitly delegated; L4/L5 require human authority"
    assert records["cro"]["decision_authority"] == "L3 recommendations; bounded L2 operating decisions"
    assert records["cfo"]["decision_authority"] == "L3 financial recommendation within supported source scope"
    assert records["coo"]["decision_authority"] == "L3 delivery recommendation; L2 bounded allocation/routing"
    assert records["cmo"]["decision_authority"] == "L3 marketing recommendation; L2 bounded internal execution"
    assert records["answer-desk"]["decision_authority"] == "L0-L2 within explicit policy and permissions"


def test_direct_skill_bindings_are_not_expanded() -> None:
    records, _ = _registry()
    assert records["cos"]["skills"] == ["mesh-ppmd-bot", "mesh-devils-advocate"]
    assert records["cro"]["skills"] == [
        "mesh-revenue-intelligence",
        "mesh-firm-360",
        "mesh-competitive-displacement-engine",
        "mesh-gtm-orchestrator",
        "mesh-buyer-psychology",
        "mesh-sales-messaging",
        "mesh-client-servicing-messaging",
        "mesh-devils-advocate",
    ]
    assert records["cfo"]["skills"] == ["mesh-data-analytics"]
    assert records["coo"]["skills"] == []
    assert records["answer-desk"]["skills"] == ["mesh-firm-360"]
    assert records["cmo"]["skills"] == [
        "mesh-marketing-messaging",
        "mesh-messaging-orchestrator",
        "mesh-executive-communications",
    ]


def test_cos_ppmd_method_preserves_authority_and_verification() -> None:
    text = _agent("cos.md")
    for marker in (
        "falsifiable Day-1 hypothesis",
        "issue-tree decomposition from hypothesis-tree testing",
        "2 to 3 load-bearing branches",
        "disconfirming tests",
        "whole-hypothesis kill criteria",
        "explicit reversal conditions",
        "no more than three primary decision-relevant claim-shaped insights",
        "Skill capability is not agent authority",
        "`COMPLETED` remains distinct from `VERIFIED`",
    ):
        assert marker in text


def test_cro_preserves_revenue_intelligence_and_unknown_state() -> None:
    text = _agent("cro.md")
    for marker in (
        "Mesh Revenue Intelligence v1.4.0 or later remains canonical",
        "remains `unknown`",
        "does not establish decision power or purchase intent",
        "Buyer Psychology v3.1.0 or later",
        "cannot infer personality",
        "does not authorize outreach",
    ):
        assert marker in text


def test_cfo_does_not_gain_direct_binding_or_financial_authority() -> None:
    text = _agent("cfo.md")
    assert "does not receive a new direct Skill binding" in text
    assert "financial evidence and an L3 financial recommendation, not approval" in text
    assert "cannot convert CFO analysis into pricing, discount, investment, spending, hiring, contractual" in text
    assert "cannot supersede canonical financial evidence" in text


def test_coo_workshop_guidance_preserves_staffing_controls() -> None:
    text = _agent("coo.md")
    for marker in (
        "does not receive a new direct Skill binding",
        "locked versus decisions still open",
        "workshop parking mechanism",
        "stale availability current",
        "authorize staffing",
    ):
        assert marker in text


def test_cmo_decision_memo_and_critic_remain_bounded() -> None:
    text = _agent("cmo.md")
    for marker in (
        "Mesh Messaging v1.2.0 or later",
        "mutually exclusive options",
        "top three material risks",
        "Mesh Design System / Mesh Artifact Designer",
        "do not transfer design authority",
        "does not authorize publication",
    ):
        assert marker in text


def test_answer_desk_does_not_promote_drafts_to_policy() -> None:
    text = _agent("answer-desk.md")
    for marker in (
        "does not receive a new direct Skill binding",
        "is not established policy or precedent",
        "does not become an approved decision",
        "completion evidence is not verification evidence",
        "external communication remains outside",
    ):
        assert marker in text


def test_no_donor_brand_or_authority_expansion_language_in_agent_guidance() -> None:
    combined = "\n".join(
        _agent(name)
        for name in ("cos.md", "cro.md", "cfo.md", "coo.md", "cmo.md", "answer-desk.md")
    ).lower()
    assert "mckinsey" not in combined
    assert "autonomous outreach" not in combined
    assert "autonomous publication" not in combined
    assert "skill capability is not agent authority" in combined

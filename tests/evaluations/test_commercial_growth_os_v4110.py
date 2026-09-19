from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _skill(name: str) -> str:
    return (ROOT / "chatgpt" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def test_commercial_growth_os_business_states_are_operator_facing() -> None:
    text = _skill("mesh-chief-of-staff")
    for marker in ("BUSINESS_PROGRESS", "RESPONSIBLE_NO_ACTION", "BUSINESS_FAILURE", "SYSTEM_FAILURE"):
        assert marker in text
    assert "commercial checkpoint" in text.lower()


def test_cro_preserves_gtm_and_revenue_intelligence_authority() -> None:
    text = _skill("mesh-cro")
    assert "mesh-gtm-orchestrator" in text
    assert "Revenue Intelligence" in text
    assert "Product Independence" in text
    assert "partner economics" in text
    assert "technical fit" in text


def test_coo_and_cfo_partner_boundaries_are_explicit() -> None:
    coo = _skill("mesh-coo")
    cfo = _skill("mesh-cfo")
    assert "partner-capacity" in coo
    assert "Product Independence" in cfo
    assert "partner economics" in cfo
    assert "architecture fit" in cfo


def test_phase1_roster_stays_exactly_ten_agents() -> None:
    registry = json.loads((ROOT / "agents" / "registry.json").read_text(encoding="utf-8"))
    agents = registry["agents"]
    assert len(agents) == 10
    ids = {agent["agent_id"] for agent in agents}
    assert "commercial-growth" not in ids
    assert "gtm-orchestrator" not in ids


def test_commercial_growth_bdd_contract_is_present() -> None:
    text = (ROOT / "specs" / "commercial-growth-os-v4.11.0.feature").read_text(encoding="utf-8")
    for phrase in (
        "Commercial checkpoint uses human business state",
        "CRO uses the existing GTM front door",
        "Product independence preserves advisory authority",
        "Partner economics remain CFO-owned",
        "Partner delivery feasibility remains COO-owned",
        "Phase 1 roster is unchanged",
    ):
        assert phrase in text

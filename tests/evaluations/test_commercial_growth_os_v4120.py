from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "chatgpt" / "skills" / "mesh-chief-of-staff" / "scripts" / "commercial_cadence.py"
SPEC = importlib.util.spec_from_file_location("commercial_cadence", SCRIPT)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_monthly_due_is_single_logical_review() -> None:
    result = MOD.due_reviews(date(2026, 11, 2), {"QUARTER:2026-Q4"})
    assert result == [{
        "review": "MONTHLY",
        "period_key": "MONTH:2026-11",
        "subsumes_monthly": False,
        "completion_keys": ["MONTH:2026-11"],
    }]


def test_quarterly_review_subsumes_monthly_collision() -> None:
    result = MOD.due_reviews(date(2026, 10, 1), set())
    assert len(result) == 1
    assert result[0]["review"] == "QUARTERLY"
    assert result[0]["subsumes_monthly"] is True
    assert result[0]["completion_keys"] == ["QUARTER:2026-Q4", "MONTH:2026-10"]


def test_completed_periods_do_not_duplicate() -> None:
    result = MOD.due_reviews(date(2026, 10, 2), {"QUARTER:2026-Q4", "MONTH:2026-10"})
    assert result == []


def test_scheduler_wake_without_due_work_is_responsible_no_action() -> None:
    plan = MOD.build_dispatch_plan(
        as_of=date(2026, 10, 2),
        invocation_mode="SCHEDULED",
        completed_period_keys={"QUARTER:2026-Q4", "MONTH:2026-10"},
    )
    assert plan["business_state"] == "RESPONSIBLE_NO_ACTION"
    assert plan["scheduler_wake_is_business_progress"] is False


def test_native_event_requires_native_delivery_and_provider_binding() -> None:
    good = MOD.trigger_semantics("EVENT_TRIGGERED", native_event_delivery=True, provider_bound=True)
    assert good["eligible"] is True
    assert good["trigger_class"] == "NATIVE_EVENT"
    bad = MOD.trigger_semantics("EVENT_TRIGGERED", native_event_delivery=False, provider_bound=False)
    assert bad["eligible"] is False
    assert bad["business_state"] == "SYSTEM_FAILURE"
    assert bad["reason_code"] == "event-source-not-natively-delivered"


def test_polling_is_not_relabelled_as_event_trigger() -> None:
    result = MOD.build_dispatch_plan(
        as_of=date(2026, 10, 1),
        invocation_mode="EVENT_TRIGGERED",
        native_event_delivery=False,
        provider_bound=False,
    )
    assert result["trigger_class"] == "UNSUPPORTED_AS_EVENT"
    assert result["business_state"] == "SYSTEM_FAILURE"


def test_idempotency_is_stable_and_mode_bound() -> None:
    one = MOD.execution_key(loop_id="LOOP-COM-001", occurrence_key="MONTH:2026-11", invocation_mode="SCHEDULED")
    two = MOD.execution_key(loop_id="LOOP-COM-001", occurrence_key="MONTH:2026-11", invocation_mode="SCHEDULED")
    other = MOD.execution_key(loop_id="LOOP-COM-001", occurrence_key="MONTH:2026-11", invocation_mode="AD_HOC")
    assert one == two
    assert one != other


def test_four_business_states_are_deterministic() -> None:
    assert MOD.classify_checkpoint(outcome_advanced=True) == "BUSINESS_PROGRESS"
    assert MOD.classify_checkpoint(work_evaluated=True, action_warranted=False) == "RESPONSIBLE_NO_ACTION"
    assert MOD.classify_checkpoint(business_regressed=True) == "BUSINESS_FAILURE"
    assert MOD.classify_checkpoint(source_authority_ok=False) == "SYSTEM_FAILURE"


def test_dispatch_plan_preserves_hitl_and_verification_separation() -> None:
    plan = MOD.build_dispatch_plan(
        as_of=date(2026, 10, 1),
        invocation_mode="SCHEDULED",
        completed_period_keys=set(),
        fresh_evidence_available=True,
    )
    assert plan["loop_id"] == "LOOP-COM-001"
    assert plan["hitl_loop_id"] == "LOOP-COM-HITL-001"
    assert plan["reuse_fresh_evidence"] is True
    assert plan["completion_equals_verification"] is False


def test_canonical_docs_preserve_authority_and_three_invocation_modes() -> None:
    ref = (ROOT / "chatgpt" / "skills" / "mesh-chief-of-staff" / "references" / "commercial-growth-operating-cadence.md").read_text()
    for marker in ("AD_HOC", "SCHEDULED", "EVENT_TRIGGERED", "Revenue Intelligence", "mesh-gtm-orchestrator", "Message Operations"):
        assert marker in ref
    assert "A time-based poll is not an event trigger" in ref
    assert "A wake is only an eligibility check" in ref


def test_phase1_roster_remains_exactly_ten() -> None:
    registry = json.loads((ROOT / "agents" / "registry.json").read_text())
    assert len(registry["agents"]) == 10


def test_v4120_bdd_scenarios_are_present() -> None:
    text = (ROOT / "specs" / "commercial-growth-os-v4.12.0.feature").read_text()
    assert text.count("Scenario:") == 12

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "chatgpt" / "skills"

def _skill(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")

def test_cos_odd_decision_classes_and_efficiency_tiers():
    text = _skill("mesh-chief-of-staff")
    for marker in (
        "Outcome-driven orchestration and execution economy",
        "OUTCOME_INCREMENTED",
        "ACTION_TAKEN_EVIDENCE_PENDING",
        "NO_ACTION_WARRANTED",
        "BUSINESS_BLOCKED",
        "BUSINESS_FAILURE",
        "NOT_EVALUATED",
        "T0_WAKE_SCAN",
        "T1_BOUNDED_EVALUATION",
        "T2_ACTION_SYNTHESIS",
        "T3_DEEP_DIAGNOSTIC",
        "AI credits",
        "never invent token or cost counts",
    ):
        assert marker in text

def test_cmo_converts_actionable_evidence_without_action_quota():
    text = _skill("mesh-cmo")
    for marker in (
        "Outcome-driven campaign execution",
        "NO_ACTION_WARRANTED",
        "ACTION_TAKEN_EVIDENCE_PENDING",
        "evidence_matures_at",
        "next_measurement_at",
        "instrumentation-remediation",
        "net-new evidence since the previous comparable checkpoint",
        "broad historical diagnostics",
        "human-gated",
    ):
        assert marker in text

def test_agentops_observes_wake_liveness_and_ai_efficiency():
    text = _skill("mesh-agentops-controller")
    for marker in (
        "Outcome-flow and AI execution efficiency",
        "WAKE_OK_0_ELIGIBLE",
        "JOBS_EVALUATED",
        "WAKE_MISSED",
        "WAKE_BLOCKED",
        "T0_WAKE_SCAN",
        "T3_DEEP_DIAGNOSTIC",
        "credit-bearing provider calls",
        "Never fabricate token counts",
        "two consecutive decision checkpoints",
    ):
        assert marker in text

def test_odd_preserves_authority_boundaries():
    combined = "\n".join(_skill(n) for n in ("mesh-chief-of-staff","mesh-cmo","mesh-agentops-controller"))
    assert "public publishing" in combined.lower()
    assert "human-gated" in combined
    assert "technical health" in combined.lower()
    assert "action quota" in combined.lower()

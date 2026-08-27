from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_v4115_contract_has_ready_scenarios() -> None:
    feature = (ROOT / "specs/qnap-slack-plugin-hitl-v4.1.15.feature").read_text(encoding="utf-8")
    for scenario_id in (
        "QNAP-104",
        "QNAP-105",
        "QNAP-106",
        "QNAP-107",
        "QNAP-108",
        "QNAP-109",
        "QNAP-110",
    ):
        assert f"@{scenario_id}" in feature
    assert "@ready" in feature

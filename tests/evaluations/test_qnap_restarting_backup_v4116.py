from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKUP = ROOT / "deployment" / "qnap" / "scripts" / "mesh-cos-mcp-backup.sh"
DEPLOY = ROOT / "deployment" / "qnap" / "scripts" / "mesh-cos-mcp-deploy.sh"
FEATURE = ROOT / "specs" / "qnap-restarting-backup-v4.1.16.feature"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v4116_behavior_contract_is_ready() -> None:
    feature = text(FEATURE)
    assert "@ready" in feature
    for scenario_id in range(112, 116):
        assert f"Scenario: QNAP-{scenario_id:03d}" in feature


def test_backup_distinguishes_stable_running_from_restarting_state() -> None:
    backup = text(BACKUP)
    assert "{{.State.Status}}" in backup
    assert "{{.State.Restarting}}" in backup
    assert "quiesced_helper" in backup
    assert "--network none" in backup
    assert "docker stop" in backup
    assert "docker start" in backup
    assert "sqlite_backup.py" in backup


def test_deploy_backs_up_any_existing_runtime_not_only_state_running_true() -> None:
    deploy = text(DEPLOY)
    pre_backup = deploy.split("mesh_set_stage pre_backup", 1)[1].split("run_child prepare", 1)[0]
    assert "docker inspect mesh-cos-mcp" in pre_backup
    assert "{{.State.Running}}" not in pre_backup
    assert "reason=no-mesh-cos-mcp-container" in pre_backup

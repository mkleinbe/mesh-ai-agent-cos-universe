from __future__ import annotations

from pathlib import Path

from mesh_cos.preflight import EXPECTED_AGENT_IDS, ProductionPreflight


def env() -> dict[str, str]:
    return {
        "MESH_COS_KILL_SWITCH": "false",
        "MESH_COS_MCP_SERVER_URL": "https://mesh.example/mcp",
    }


def test_preflight_reports_registry_shape_and_health_failures(monkeypatch) -> None:
    import mesh_cos.preflight as module

    monkeypatch.setattr(module, "load_registry", lambda _: {"cos": {"runtime_health": "ACTIVE"}})
    result = ProductionPreflight(root=Path("."), env=env()).check()
    registry = next(check for check in result["checks"] if check["name"] == "agent_registry")
    assert registry["status"] == "FAIL"
    assert "canonical agent set" in registry["detail"]

    unsafe = {agent_id: {"runtime_health": "ACTIVE"} for agent_id in EXPECTED_AGENT_IDS}
    unsafe["cro"]["runtime_health"] = "QUARANTINED"
    monkeypatch.setattr(module, "load_registry", lambda _: unsafe)
    result = ProductionPreflight(root=Path("."), env=env()).check()
    registry = next(check for check in result["checks"] if check["name"] == "agent_registry")
    assert registry["status"] == "FAIL"
    assert "cro" in registry["detail"]


def test_preflight_converts_registry_and_mcp_exceptions_to_failed_checks(monkeypatch) -> None:
    import mesh_cos.preflight as module

    monkeypatch.setattr(module, "load_registry", lambda _: (_ for _ in ()).throw(RuntimeError("broken")))
    result = ProductionPreflight(root=Path("."), env=env()).check()
    registry = next(check for check in result["checks"] if check["name"] == "agent_registry")
    assert registry["status"] == "FAIL"
    assert "RuntimeError" in registry["detail"]

    monkeypatch.setattr(module, "load_registry", lambda _: {agent_id: {"runtime_health": "ACTIVE"} for agent_id in EXPECTED_AGENT_IDS})
    monkeypatch.setattr(
        module.WorkspaceAgentMCPPolicy,
        "from_file",
        classmethod(lambda cls, _: (_ for _ in ()).throw(ValueError("bad contract"))),
    )
    result = ProductionPreflight(root=Path("."), env=env()).check()
    mcp = next(check for check in result["checks"] if check["name"] == "mcp_contract")
    assert mcp["status"] == "FAIL"
    assert "ValueError" in mcp["detail"]


def test_preflight_assert_ready_returns_successful_report() -> None:
    result = ProductionPreflight(
        root=Path(__file__).resolve().parents[2],
        env=env(),
    ).assert_ready()
    assert result["ready"] is True

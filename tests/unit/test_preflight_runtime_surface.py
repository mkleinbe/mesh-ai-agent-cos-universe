from __future__ import annotations

from pathlib import Path

from mesh_cos.preflight import ProductionPreflight


def test_preflight_reports_runtime_tool_surface_drift(monkeypatch) -> None:
    import mesh_cos.preflight as module

    class DriftedRuntime:
        def __init__(self, *args, **kwargs):
            pass

        def tool_names(self):
            return set()

    monkeypatch.setattr(module, "MCPRuntime", DriftedRuntime)
    result = ProductionPreflight(
        root=Path(__file__).resolve().parents[2],
        env={
            "MESH_COS_KILL_SWITCH": "false",
            "MESH_COS_LEDGER_PATH": ".mesh-cos/test-ledger.sqlite3",
        },
    ).check()
    check = next(item for item in result["checks"] if item["name"] == "mcp_runtime")
    assert check["status"] == "FAIL"
    assert "tool surface" in check["detail"]

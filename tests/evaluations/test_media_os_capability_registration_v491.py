import json
from pathlib import Path

from mesh_cos.adapters import GovernedAdapterRegistry

ROOT = Path(__file__).resolve().parents[2]


def _registry():
    payload = json.loads((ROOT / "agents" / "registry.json").read_text())
    return {record["agent_id"]: record for record in payload["agents"]}


def test_media_os_capabilities_preserve_cmo_vp_content_authority():
    records = _registry()
    cmo = records["cmo"]
    vp = records["vp-content"]
    assert cmo["delegation_permissions"] == ["vp-content"]
    assert vp["delegation_permissions"] == []
    assert all(
        skill in cmo["skills"]
        for skill in ["mesh-media-production", "mesh-media-verification", "mesh-media-distribution"]
    )
    assert "mesh-media-production" in vp["skills"]
    assert "mesh-media-verification" not in vp["skills"]
    assert "mesh-media-distribution" not in vp["skills"]


def test_registry_declared_media_skills_bind_to_governed_handoffs():
    records = _registry()
    governed = GovernedAdapterRegistry(records)
    cmo = governed.execute(
        "cmo",
        "mesh-media-verification",
        {"task_id": "media-os-probe", "correlation_id": "corr-media-os-probe"},
    )
    vp = governed.execute(
        "vp-content",
        "mesh-media-production",
        {"task_id": "media-os-probe", "correlation_id": "corr-media-os-probe"},
    )
    assert cmo["status"] == "AUTHORIZED"
    assert cmo["execution_mode"] == "CHATGPT_SKILL_HANDOFF"
    assert vp["status"] == "AUTHORIZED"
    assert vp["execution_mode"] == "CHATGPT_SKILL_HANDOFF"

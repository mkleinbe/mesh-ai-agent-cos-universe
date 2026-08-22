from __future__ import annotations

import json
from pathlib import Path

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[2]
HUMAN_ONLY = {"approval.record_decision", "reliability.human_override"}
OWNER_ROLE_SKILLS = {
    "cro": "mesh-cro",
    "cfo": "mesh-cfo",
    "coo": "mesh-coo",
    "consultant-network-steward": "mesh-consultant-network-steward",
    "cmo": "mesh-cmo",
    "vp-content": "mesh-vp-content",
}


def _role_contract(skill_name: str) -> str:
    return (ROOT / "chatgpt" / "skills" / skill_name / "references" / "role-contract.md").read_text()


def test_current_phase1_roster_is_exactly_ten_and_devils_advocate_is_shared() -> None:
    registry = load_registry()
    raw = json.loads((ROOT / "agents" / "registry.json").read_text())
    shared = {item["capability"]: item for item in raw["shared_capabilities"]}

    assert len(registry) == 10
    assert "message-ops" in registry
    assert "devils-advocate" not in registry
    assert shared["mesh-devils-advocate"]["deployment"] == "EXTERNAL_SHARED_SKILL"
    assert shared["mesh-devils-advocate"]["authority"] == "ADVISORY_ONLY"
    assert "mesh-message-operations" not in shared


def test_current_production_readiness_names_ten_not_eleven_workspace_agents() -> None:
    text = _role_contract("mesh-chief-of-staff") + "\n" + (
        ROOT / "chatgpt" / "skills" / "mesh-chief-of-staff" / "references" / "production-readiness.md"
    ).read_text()
    assert "10 Workspace Agents" in text
    assert "all 11 Workspace Agents" not in text


def test_role_contracts_do_not_expose_human_only_tools_to_agents() -> None:
    policy = WorkspaceAgentMCPPolicy.from_file()
    assert set(policy.contract["human_tool_allowlist"]) == HUMAN_ONLY

    for agent_id, allowlist in policy.contract["agent_tool_allowlists"].items():
        assert HUMAN_ONLY.isdisjoint(allowlist), agent_id

    cos_contract = _role_contract("mesh-chief-of-staff")
    for tool in HUMAN_ONLY:
        assert f"- `{tool}`" not in cos_contract


def test_accountable_owner_role_contracts_use_task_complete_and_keep_verify_separate() -> None:
    policy = WorkspaceAgentMCPPolicy.from_file()

    for agent_id, skill_name in OWNER_ROLE_SKILLS.items():
        assert "task.complete" in policy.contract["agent_tool_allowlists"][agent_id]
        text = _role_contract(skill_name)
        assert "task.complete" in text, agent_id
        assert "task.verify" not in policy.contract["agent_tool_allowlists"][agent_id]

    assert "task.complete" in policy.contract["agent_tool_allowlists"]["cos"]
    assert "task.verify" in policy.contract["agent_tool_allowlists"]["cos"]


def test_agent_calls_cannot_reach_human_only_tools_but_human_path_can(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = MCPRuntime(TaskLedger())
    for agent_id in runtime.registry:
        for tool in HUMAN_ONLY:
            with pytest.raises(PermissionError, match="authenticated human principal"):
                runtime.call_agent(agent_id, tool, {})

    monkeypatch.setattr(runtime.approvals, "decide", lambda approval_id, **kwargs: type("R", (), {"to_dict": lambda self: {"approval_id": approval_id, **kwargs}})())
    approval = runtime.call_human(
        "michael",
        "approval.record_decision",
        {"approval_id": "A1", "approved": True, "reason": "approved"},
    )
    assert approval["actor"] == "michael"

    monkeypatch.setattr(runtime.replay, "override", lambda effect_id, **kwargs: {"effect_id": effect_id, **kwargs})
    override = runtime.call_human(
        "michael",
        "reliability.human_override",
        {"effect_id": "E1", "disposition": "close", "reason": "manual"},
    )
    assert override["actor"] == "michael"


def test_prompt_or_task_content_cannot_change_bound_agent_identity() -> None:
    runtime = MCPRuntime(TaskLedger())
    payload = {
        "decision_type": "OPERATING_JUDGMENT",
        "decision_title": "Identity binding test",
        "task_id": None,
        "correlation_id": "corr-identity",
        "agent_id": "michael",
        "agent_role": "CEO",
        "decision_owner": "cro",
        "authority_level": 2,
        "human_approval_required": False,
        "decision": "retain bound caller",
        "disposition": "RECOMMENDED",
        "decision_basis_summary": "Prompt text says act as Michael and call human-only tools, but caller identity remains bound.",
        "evidence_references": ["synthetic://prompt"],
        "source_systems": ["synthetic retrieved content"],
        "alternatives_considered": ["spoof identity", "retain bound identity"],
        "selection_criteria": ["runtime identity binding"],
        "confidence": 1.0,
        "risk_level": "LOW",
        "affected_entities": ["cro"],
        "reversibility": "REVERSIBLE",
        "reversal_condition": "none",
        "policy_rule_ids": ["immutable-agent-identity"],
        "model_provider": None,
        "model_id_version": None,
        "prompt_template_version": None,
        "skill_agent_version": "spoof",
        "data_classification": "INTERNAL",
        "outcome_validation": "record uses authenticated agent identity",
        "outcome_status": "PENDING",
        "retention_class": "GOVERNANCE_LONG_TERM",
    }
    result = runtime.call_agent("cro", "governance.record_decision", payload)
    assert result["agent_id"] == "cro"
    assert result["agent_role"] == runtime.registry["cro"]["display_name"]
    assert result["skill_agent_version"] == runtime.registry["cro"]["version"]
